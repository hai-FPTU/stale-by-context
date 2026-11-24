"""Count ATT&CK release mixing in public detection-rule repositories (reported in the paper's Introduction).
Usage: python3 count_rule_repos.py <items.jsonl of drift-18.1-19.2> <elastic detection-rules clone> <SigmaHQ clone>
Clones used in the paper: elastic/detection-rules @ 195f15c (9 Oct 2026), SigmaHQ/sigma @ 7d8b152 (14 Oct 2026)."""
import sys, json, glob, re, tomllib, yaml
items_path, elastic, sigma = sys.argv[1:4]
items = [json.loads(l) for l in open(items_path, encoding="utf-8")]
moved = {it["anchor_old"] for it in items if it["template"] == "D1_tech_tactic" and it["anchor_old"]
         and "TA0005" in it["gold_old"] and "TA0112" in it["gold_new"] and "TA0005" not in it["gold_new"]}
revoked = {it["anchor_old"] for it in items if it["anchor_old"] and it["anchor_status_new"] != "active"}
n = ta5 = moved_ta5 = rev = 0
for f in glob.glob(f"{elastic}/rules/**/*.toml", recursive=True) + glob.glob(f"{elastic}/rules_building_block/**/*.toml", recursive=True):
    thr = tomllib.load(open(f, "rb")).get("rule", {}).get("threat", [])
    if not thr:
        continue
    n += 1
    pairs = [(t.get("tactic", {}).get("id"), i) for t in thr for te in (t.get("technique") or [])
             for i in [te.get("id")] + [s.get("id") for s in (te.get("subtechnique") or [])]]
    ta5 += any(t.get("tactic", {}).get("id") == "TA0005" and t.get("tactic", {}).get("name") == "Defense Evasion" for t in thr)
    moved_ta5 += any(tac == "TA0005" and i in moved for tac, i in pairs)
    rev += bool({i for _, i in pairs} & revoked)
print(f"Elastic: {n} rules with ATT&CK mappings; {ta5} use 'TA0005 Defense Evasion'; {moved_ta5} file a technique moved "
      f"to TA0112 under TA0005; {rev} cite a technique ID revoked in v19 ({len(moved)} moved, {len(revoked)} revoked IDs)")
tags = {"attack.defense-evasion": 0, "attack.stealth": 0, "attack.defense-impairment": 0}
for d in ("rules", "rules-emerging-threats", "rules-threat-hunting", "rules-dfir", "rules-compliance", "rules-placeholder"):
    for f in glob.glob(f"{sigma}/{d}/**/*.yml", recursive=True):
        try:
            y = yaml.safe_load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for t in (y or {}).get("tags", []) if isinstance(y, dict) else []:
            if str(t).lower() in tags:
                tags[str(t).lower()] += 1
print("SigmaHQ (active rule folders), tag counts:", tags)
