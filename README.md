# Stale by Context: ATT&CK version drift in retrieval-augmented CTI assistants

This repository accompanies the paper *"Stale by Context: How Superseded MITRE ATT&CK Passages and Their Labels Mislead Retrieval-Augmented CTI Assistants"* (IEEE CCWC 2027). It contains the release-diff analysis, the version-paired benchmark, every prompt, all raw model outputs, the scored results, the analysis plan with its full version history, and the notebooks that produced them.

Notebook comments and printed messages are partly in Vietnamese. Code, file names and result columns are in English.

## Contents

| Path | What it is |
|---|---|
| `01_thay_doi_phien_ban_ATTACK.ipynb` → `drift/` | Diff of consecutive ATT&CK Enterprise releases from the official STIX 2.1 bundles (counts behind the drift figure); `drift/manifest.json` records the SHA-256 of each downloaded bundle |
| `02_benchmark_*.ipynb` → `benchmark/attack-*` | Passage corpora per release (v6.3, v7.2, v18.1, v19.2) |
| `03_cap_cau_hoi_truoc_sau_*.ipynb` → `benchmark/drift-*` | Version-paired questions, gold answers for both releases and identifier lineage (`_6.3`: v6.3→v7.2; `_da_chay`: v18.1→v19.2) |
| `04_pilot_llm_rag.ipynb` → `results/pilot-18.1-19.2` | Exploratory pilot with BM25 retrieval (Sec. V-A) |
| `05_ngu_canh_kiem_soat.ipynb` → `results/ctx-18.1-19.2` | Exploratory oracle-context experiment |
| `06_co_che_nhan_phien_ban.ipynb` → `results/mech-18.1-19.2` | Exploratory label-mechanism experiment |
| `07_khang_dinh.ipynb` → `results/conf-18.1-19.2`, `results/conf-6.3-7.2` | Confirmatory study, branches A and B, including C7 |
| `08_mo_rong_qwen14b.ipynb` → `results/ext14b-*` | Pre-specified extension to Qwen3-14B (E1–E3) |
| `09_phong_thu_dau_cuoi.ipynb` → `results/e2e-*` | Pre-specified extension: end-to-end BM25 retrieval over a mixed-release index with defences (E4), conflict-reporting option (E5), and re-run reproducibility |
| `ctidrift_scoring.py`, `ctidrift_scoring_v13.py` | Scorers v1.2 (primary) and v1.3 (sensitivity) |
| `ctidrift_infer.py`, `ctidrift_infer_v2.py` | vLLM inference modules (v2 is used by notebooks 07–09) |
| `scripts/count_rule_repos.py` | Counts of ATT&CK release mixing in the Elastic and SigmaHQ rule repositories (Sec. I; clones at commits 195f15c and 7d8b152) |
| `scripts/consistency_check.py` | Metadata-free release-consistency check on the retrieved contexts of notebook 09 (Sec. VI; descriptive, post hoc) |
| `docs/` | Analysis plan with version history (v1.0–v1.5 addenda), annotation guideline, independent annotation of 150 confirmatory responses and the key that maps each annotated row to model and condition |
| `FILES.sha256` | SHA-256 of every file copied from the project |

Each `results/<run>/` folder contains `prompts/` (one JSONL per condition), `raw/` (model outputs), `scored.csv` (one row per response), summary and confirmatory CSVs, `manifest.json` (input/output hashes, model revisions, library versions) and `logs/`.

The raw STIX bundles are not included; notebook 01 downloads them from `mitre-attack/attack-stix-data` and checks them against `drift/manifest.json`. The notebooks are included exactly as run, with their outputs; the builder scripts that generated them are not included, so the builder hashes cited in the analysis plan cannot be checked from this repository.

## Citation

```
H. Ho, "Stale by Context: How Superseded MITRE ATT&CK Passages and Their Labels Mislead
Retrieval-Augmented CTI Assistants," in Proc. IEEE Computing and Communication Workshop
and Conference (CCWC), Las Vegas, NV, USA, Jan. 2027.
```

The version of this repository that accompanies the paper is tagged `ccwc2027`.

## Reproducing the runs

Hardware and software used: one NVIDIA RTX 4070 (12 GB), vLLM 0.31.0, PyTorch 2.13.0 (CUDA 13.0), Python 3.11. Model revisions are pinned in each `manifest.json`. Run the notebooks in order from the repository root. Inference is greedy but GPU batching makes it not fully deterministic (see the paper).

To check the statistics without rerunning inference, start from `results/<run>/scored.csv` (one row per response, with the lineage cluster of each item); the test functions are in the analysis cells of notebooks 07–09.

## Analysis plan

The confirmatory analysis plan was **pre-specified but not pre-registered**: each version was kept in a dated record and pinned the analysis code by hash, but it was not deposited in a public registry before the runs. `docs/analysis_plan_v1.5.md` contains the full version history, including the one deviation reported in the paper.

## Licences and attribution

- Code: MIT licence (`LICENSE`).
- Derived data (questions, prompts, model outputs, scores): CC BY 4.0.
- ATT&CK content: see `ATTACK_NOTICE.md`.
