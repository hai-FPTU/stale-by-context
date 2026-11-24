"""Metadata-free release-consistency check on the mixed-index contexts of notebook 09 (descriptive, post hoc).
A passage is flagged as inconsistent with the requested release if it (a) is an ATT&CK technique passage whose
technique is not active in that release, or whose tactic set or tactic names differ from that release, or
(b) mentions any technique identifier that is not active in that release. Uses only the passage text and the
requested release's technique table, never the passage's version metadata (which is used only to score the check)."""
import json, re, sys, collections
def tables(corpus_path):
    tac, names = {}, set()
    for c in map(json.loads, open(corpus_path, encoding="utf-8")):
        if c["metadata"]["kind"] == "technique" and c["_id"].endswith("#0"):
            m = re.search(r"Tactics: (.*?)\.\n", c["text"])
            if m:
                tac[c["metadata"]["doc_id"]] = set(re.findall(r"\((TA\d{4})\)", m.group(1)))
                names |= {n.strip() for n in re.findall(r"([A-Za-z ]+) \(TA\d{4}\)", m.group(1))}
    return tac, names
def inconsistent(text, tac, names):
    m = re.match(r"(?:\[Source:[^\]]*\]\n)?ATT&CK Technique (T\d{4}(?:\.\d{3})?): .*?\nTactics: (.*?)\.\n", text)
    if m:
        tid, line = m.group(1), m.group(2)
        if tid not in tac or tac[tid] != set(re.findall(r"\((TA\d{4})\)", line)):
            return True
        if any(n.strip() not in names for n in re.findall(r"([A-Za-z ]+) \(TA\d{4}\)", line)):
            return True
    return any(t not in tac for t in re.findall(r"\bT\d{4}(?:\.\d{3})?\b", text))
def main(run_dir, corpus_new, v_old):
    tac, names = tables(corpus_new)
    Q = {json.loads(l)["query_id"]: json.loads(l) for l in open(f"{run_dir}/queries.jsonl", encoding="utf-8")}
    st = collections.Counter()
    for r in map(json.loads, open(f"{run_dir}/prompts/mixed.jsonl", encoding="utf-8")):
        ctx = r["messages"][1]["content"].split("\n\nQuestion:")[0].split("\n\n", 1)[1]
        ps = re.split(r"(?:^|\n\n)\[\d+\] ", ctx)[1:]
        assert len(ps) == len(r["retrieved"])
        g = Q[r["query_id"]]["group"]
        for pid, t in zip(r["retrieved"], ps):
            k = ("old-only" if pid.startswith(v_old + "|") else "current", g)
            st[k + ("n",)] += 1
            st[k + ("flag",)] += inconsistent(t, tac, names)
    for k in sorted({k[:2] for k in st}):
        n, f = st[k + ("n",)], st[k + ("flag",)]
        print(f"{k[0]:9s} {k[1]:8s} passages {n:5d} flagged {f:5d} ({f / n:.3f})")
if __name__ == "__main__":
    main(*sys.argv[1:4])
