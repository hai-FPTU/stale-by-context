# Bộ chấm v1.3 (notebook 06). Gọi lại score_drift của v1.2, bổ sung kiểm tra mã–tên và lỗi thời theo tên.
from __future__ import annotations
import re
from ctidrift_scoring import score_drift, json_answer

SCORER_VERSION = "1.3"
_TA_ITEM = re.compile(r"^\s*(TA\d{4})\b\s*[:\-–]?\s*(.*?)\s*$", re.I)
_NAME_TA = re.compile(r"^\s*(.*?)\s*\(\s*(TA\d{4})\s*\)\s*$", re.I)      # "Impact (TA0040)"
_TA_START = re.compile(r"^\s*TA\d{4}\b", re.I)

def _split_items(items):
    # Tách mục gộp: "TA0005, TA0112", "TA0005/TA0112", "TA0005 Stealth, TA0112 Impact".
    # Trả về (phần, mục_gốc_có_bị_tách_không) để chỉ ghép "mã trần + mục kế tiếp" giữa các mục KHÔNG bị tách.
    out = []
    for x in items:
        parts = []
        for part in re.split(r"[,;/]", str(x)):
            parts += [p.strip() for p in re.split(r"(?<!\()(?<!\( )(?=\bTA\d{4}\b)", part, flags=re.I) if p.strip()]
        out += [(p, len(parts) > 1) for p in parts]
    return out

def tactic_pairs(answer: str) -> list:
    # Trả về danh sách (mã TA, tên đi kèm hoặc ""). Các dạng: "TA0005 Stealth", ["TA0005", "Stealth"],
    # "Stealth (TA0005)". Dạng tên đứng trước mã trong hai mục rời (["Stealth", "TA0005"]) không được ghép.
    items = json_answer(answer or "")
    if not items:
        return []
    toks = _split_items(items)
    items = [t for t, _ in toks]
    out, i = [], 0
    while i < len(items):
        m = _TA_ITEM.match(items[i])
        if not m:
            mn = _NAME_TA.match(items[i])
            if mn:
                out.append((mn.group(2).upper(), mn.group(1).strip(" ()")))
            i += 1
            continue
        tid, name = m.group(1).upper(), m.group(2).strip(" ()")
        if name:
            out.append((tid, name)); i += 1
        elif (i + 1 < len(items) and not _TA_START.match(items[i + 1])
              and not toks[i][1] and not toks[i + 1][1]):
            out.append((tid, items[i + 1].strip(" ()"))); i += 2
        else:
            out.append((tid, "")); i += 1
    return out

def _norm(s: str) -> str:
    # So tên: không phân biệt hoa thường, "&" = "and", "Defence" = "Defense"; gạch nối vẫn là một phần của từ (như v1.2)
    s = s.lower().replace("&", " and ").replace("defence", "defense")
    return re.sub(r"\s+", " ", s).strip()

def _names_of(tactic_alias: dict) -> dict:
    by_id = {}
    for n, t in tactic_alias.items():
        by_id.setdefault(t, set()).add(_norm(n))
    return by_id

def bad_pairs(answer: str, tactic_alias: dict) -> list:
    # Cặp mã–tên không nhất quán (tên không thuộc mã ở phiên bản nào) hoặc mã không tồn tại
    by_id, out = _names_of(tactic_alias), []
    for tid, name in tactic_pairs(answer):
        valid = by_id.get(tid)
        if valid is None:
            out.append((tid, name)); continue
        n = _norm(name)
        if n and not any(re.search(r"(?<![\w-])" + re.escape(v) + r"(?![\w-])", n) for v in valid):
            out.append((tid, name))
    return out

def score_v13(q: dict, answer: str, tactic_alias: dict) -> dict:
    s = score_drift(q, answer, tactic_alias)
    pred, gold, other = set(s["pred"]), set(q["gold"]), set(q["other_gold"])
    other_exact = bool(pred) and pred == other and other != gold
    drift_ext = s["outcome"] in ("STALE", "ANACHRONISM") or other_exact
    bad = bad_pairs(answer, tactic_alias) if q["answer_type"] == "tactic_set" else []
    # Tên cũ viết khác chính tả ("Defence Evasion") mà v1.2 không bắt được
    old = [_norm(x) for x in q.get("other_only_labels", [])]
    name_stale = q["answer_type"] == "tactic_set" and any(
        re.search(r"(?<![\w-])" + re.escape(o) + r"(?![\w-])", _norm(n)) for _, n in tactic_pairs(answer) for o in old)
    if s["outcome"] == "NO_ANSWER":
        o13 = "NO_ANSWER"
    elif bad:
        o13 = "INCONSISTENT"
    elif drift_ext or s["label_drift"] or name_stale:
        o13 = "STALE"
    elif s["em"]:
        o13 = "CORRECT"
    elif s["outcome"] == "PARTIAL":
        o13 = "PARTIAL"
    else:
        o13 = "WRONG"
    return {**s, "other_exact": other_exact, "drift_ext": drift_ext, "inconsistent": bool(bad),
            "bad_pairs": bad, "outcome13": o13, "stale13": o13 == "STALE", "scorer": SCORER_VERSION}
