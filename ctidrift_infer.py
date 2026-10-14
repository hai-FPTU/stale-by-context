# Chạy suy luận cho MỘT mô hình trên các điều kiện của pilot (notebook 04). Gọi từ notebook qua subprocess.
import argparse, hashlib, json, os, sys, time, platform
from pathlib import Path

os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")


def read_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def done_ok(path, meta_path, ids, run_key):
    # Kết quả cũ chỉ được dùng lại khi: đủ đúng các query_id theo đúng thứ tự VÀ cùng "khoá chạy"
    # (cùng file prompt, cùng mô hình/phiên bản, cùng tham số sinh). Đổi bất cứ thứ gì -> chạy lại.
    if not path.exists() or not meta_path.exists():
        return False
    try:
        got = [r["query_id"] for r in read_jsonl(path)]
        key = json.loads(meta_path.read_text()).get("run_key")
    except (ValueError, KeyError):
        return False
    return got == ids and key == run_key


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--revision", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--prompts-dir", required=True)
    ap.add_argument("--conditions", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-model-len", type=int, default=6144)
    ap.add_argument("--max-tokens", type=int, default=96)
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chat-template-kwargs", default="{}")
    a = ap.parse_args()

    conds = [c for c in a.conditions.split(",") if c]
    out_dir = Path(a.out_dir) / a.tag
    out_dir.mkdir(parents=True, exist_ok=True)
    ctk = json.loads(a.chat_template_kwargs)

    from importlib.metadata import version as pkg_version
    script_sha = sha256_file(Path(__file__))
    vllm_ver = pkg_version("vllm")
    jobs, keys = {}, {}
    for c in conds:
        pfile = Path(a.prompts_dir) / f"{c}.jsonl"
        rows = read_jsonl(pfile)
        if a.limit:
            rows = rows[:a.limit]
        ids = [r["query_id"] for r in rows]
        keys[c] = hashlib.sha256(json.dumps(dict(prompts=sha256_file(pfile), limit=a.limit, repo=a.repo,
                                                 revision=a.revision, max_model_len=a.max_model_len,
                                                 max_tokens=a.max_tokens, seed=a.seed, ctk=ctk, gpu_mem=a.gpu_mem,
                                                 script=script_sha, vllm=vllm_ver),
                                            sort_keys=True).encode()).hexdigest()
        if done_ok(out_dir / f"{c}.jsonl", out_dir / f"meta_{c}.json", ids, keys[c]):
            print(f"[{a.tag}] {c}: đã có đủ {len(ids)} kết quả cùng cấu hình — bỏ qua", flush=True)
            continue
        jobs[c] = rows
    if not jobs:
        print(f"[{a.tag}] không còn việc gì để chạy", flush=True)
        return

    from huggingface_hub import snapshot_download
    path = snapshot_download(a.repo, revision=a.revision)
    print(f"[{a.tag}] mô hình tại {path}", flush=True)

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path)
    budget = a.max_model_len - a.max_tokens
    for c, rows in jobs.items():
        lens = []
        for r in rows:
            text = tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, **ctk)
            lens.append(len(tok(text, add_special_tokens=False)["input_ids"]))
        too_long = [(r["query_id"], n) for r, n in zip(rows, lens) if n > budget]
        print(f"[{a.tag}] {c}: {len(rows)} prompt, dài nhất {max(lens)} token (giới hạn {budget})", flush=True)
        if too_long:
            sys.exit(f"LỖI: {len(too_long)} prompt vượt {budget} token, ví dụ {too_long[:3]} — tăng MAX_MODEL_LEN "
                     "hoặc giảm MAX_CHUNK_WORDS trong notebook")

    import torch
    import vllm
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import StructuredOutputsParams

    # disable_any_whitespace: JSON dạng gọn, mô hình không thể sinh khoảng trắng vô hạn rồi bị cắt ở max_tokens
    llm = LLM(model=path, tokenizer=path, max_model_len=a.max_model_len,
              gpu_memory_utilization=a.gpu_mem, seed=a.seed,
              structured_outputs_config={"backend": "xgrammar", "disable_any_whitespace": True})
    meta_base = dict(model_tag=a.tag, repo=a.repo, revision=a.revision, snapshot=Path(path).name,
                     vllm=vllm.__version__, torch=torch.__version__, cuda=torch.version.cuda,
                     gpu=torch.cuda.get_device_name(0), python=platform.python_version(),
                     max_model_len=a.max_model_len, max_tokens=a.max_tokens, gpu_mem=a.gpu_mem, seed=a.seed,
                     chat_template_kwargs=ctk, flashinfer_sampler=os.environ.get("VLLM_USE_FLASHINFER_SAMPLER"),
                     script_sha256=script_sha, structured_outputs="xgrammar, disable_any_whitespace")

    for c, rows in jobs.items():
        sps = [SamplingParams(temperature=0.0, max_tokens=a.max_tokens, seed=a.seed,
                              structured_outputs=StructuredOutputsParams(json=r["schema"])) for r in rows]
        t0 = time.time()
        outs = llm.chat([r["messages"] for r in rows], sps, use_tqdm=True, chat_template_kwargs=ctk or None)
        dt = time.time() - t0
        assert len(outs) == len(rows)
        tmp = out_dir / f".{c}.jsonl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r, o in zip(rows, outs):
                f.write(json.dumps(dict(query_id=r["query_id"], condition=c, model_tag=a.tag,
                                        text=o.outputs[0].text, finish_reason=o.outputs[0].finish_reason,
                                        n_prompt_tokens=len(o.prompt_token_ids or []),
                                        n_output_tokens=len(o.outputs[0].token_ids)), ensure_ascii=False) + "\n")
        os.replace(tmp, out_dir / f"{c}.jsonl")
        (out_dir / f"meta_{c}.json").write_text(json.dumps({**meta_base, "condition": c, "n": len(rows),
                                                            "run_key": keys[c], "seconds": round(dt, 1)}, indent=2))
        print(f"[{a.tag}] {c}: xong {len(rows)} truy vấn trong {dt / 60:.1f} phút", flush=True)


if __name__ == "__main__":
    main()
