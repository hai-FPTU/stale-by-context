# Chấm điểm câu trả lời theo phiên bản (notebook 03, v1.1). Dùng chung cho notebook 04, 05.
from __future__ import annotations
import json
import re

ID_RE = {
    "technique_set":  re.compile(r"\bT\d{4}(?:\.\d{3})?\b", re.I),
    "tactic_set":     re.compile(r"\bTA\d{4}\b", re.I),
    "mitigation_set": re.compile(r"\bM\d{4}\b", re.I),
}
ANY_ID = re.compile(r"\b(?:TA|T|M)\d{4}(?:\.\d{3})?\b", re.I)
MARKER_RE = re.compile(r"^[ \t>*_#-]*(?:final[ \t]+)?answer[ \t*_]*[:：][ \t*_]*", re.I | re.M)
BULLET_RE = re.compile(r"^\s*(?:[-*•+]|\d+[.)])\s+")

ABSTAIN_RE = re.compile(r"\b(?:not\s+sure|unsure|unknown|don'?t\s+know|do\s+not\s+know|cannot\s+(?:determine|answer)|"
                        r"can'?t\s+(?:determine|answer)|no\s+answer|n/?a|none)\b", re.I)

CONNECTORS = {"and", "or", "of", "for", "the", "to", "a", "an", "in", "on", "with", "via", "from", "by", "at"}
LIST_FILLER = {"and", "or", "the", "tactic", "tactics", "both"}

def _name_pattern(name: str, ignore_case: bool):
    # Gạch nối không phải ranh giới từ ("pre-execution" không khớp Execution).
    body = re.escape(name).replace(r"\ ", r"\s+")
    if ignore_case:
        return re.compile(r"(?<![\w-])" + body + r"(?![\w-])", re.I)
    return re.compile(r"(?<![\w-])(?:" + body + "|" + re.escape(name.upper()).replace(r"\ ", r"\s+") + r")(?![\w-])")

def _mask(text: str, tactic_alias: dict, mask=()) -> str:
    t = text
    official = {n.lower() for n in (tactic_alias or {})}
    for m in sorted(mask, key=len, reverse=True):          # che tên thực thể được hỏi (trọn từ)
        if m and m.lower() not in official:
            t = re.sub(r"(?<![\w-])" + re.escape(m) + r"(?![\w-])", " ", t, flags=re.I)
    return re.sub(r"\s*&\s*", " and ", t)                # "Command & Control"

def _is_pure_list(text: str, tactic_alias: dict) -> bool:
    # Đúng nếu đoạn chỉ gồm mã, tên tactic (hoa/thường tuỳ ý), dấu câu và vài từ nối — không có câu văn
    t = ANY_ID.sub(" ", text)
    for n in sorted(tactic_alias, key=len, reverse=True):
        t = _name_pattern(n, True).sub(" ", t)
    words = re.sub(r"[^\w\s]", " ", t).lower().split()
    return all(w in LIST_FILLER for w in words)

def _tactic_names(text: str, tactic_alias: dict, mask=(), lenient: bool = False) -> dict:
    # lenient=True (chỉ dùng cho dòng ANSWER là danh sách thuần): nhận tên viết hoa/thường tuỳ ý.
    # Còn lại: chỉ đúng cách viết của MITRE hoặc viết hoa toàn bộ, để chữ "impact", "stealth",
    # "initial access" trong câu văn không bị hiểu là tên tactic.
    t = _mask(text, tactic_alias, mask)
    ignore_case = lenient and _is_pure_list(t, tactic_alias)
    return {n: tid for n, tid in tactic_alias.items() if _name_pattern(n, ignore_case).search(t)}

def _has_answer(seg: str, answer_type, tactic_alias, mask) -> bool:
    if answer_type is None:
        return bool(seg.strip())
    if ID_RE[answer_type].search(seg):
        return True
    return answer_type == "tactic_set" and bool(tactic_alias) and bool(_tactic_names(seg, tactic_alias, mask, True))

def _is_list_item(line: str, answer_type, tactic_alias) -> bool:
    # Một dòng là "mục danh sách" nếu (sau gạch đầu dòng) bắt đầu bằng một mã và phần còn lại chỉ là
    # tên viết hoa (vd "M1041 Encrypt Sensitive Information"), hoặc là danh sách thuần các tên tactic.
    bullet = bool(BULLET_RE.match(line))
    body = re.sub(r"^[*_`]+", "", BULLET_RE.sub("", line, count=1).strip())
    m = ANY_ID.match(body)
    if m:
        if bullet:                                         # "- M1029: store logs remotely" vẫn là một mục
            return True
        words = re.findall(r"[A-Za-z][\w'/-]*", ANY_ID.sub(" ", body[m.end():]))
        return all(w[0].isupper() or w.lower() in CONNECTORS for w in words)
    return answer_type == "tactic_set" and bool(tactic_alias) and bool(body) and _is_pure_list(body, tactic_alias)

def _segment(text_after_marker: str, answer_type=None, tactic_alias=None, mask=()) -> str:
    # Phần trả lời = phần còn lại của dòng ANSWER, cộng các dòng ngay sau nếu là MỤC DANH SÁCH.
    # Nếu dòng ANSWER không chứa đáp án (trống, hoặc chỉ là câu dẫn "The following mitigations apply:"),
    # bỏ qua dòng trống và lấy các mục danh sách của đoạn kế tiếp.
    lines = text_after_marker.split("\n")
    first, rest = lines[0], lines[1:]
    seg, i = [first], 0
    if not _has_answer(first, answer_type, tactic_alias, mask):
        while i < len(rest) and not rest[i].strip():
            i += 1
        para = []
        while i < len(rest) and rest[i].strip() and not MARKER_RE.match(rest[i]):
            para.append(rest[i]); i += 1
        # Dòng ANSWER chỉ là câu dẫn: lấy CẢ đoạn kế tiếp (bảng, chữ đậm, "tên (mã)"…)
        return "\n".join([first] + para)
    while i < len(rest) and rest[i].strip() and not MARKER_RE.match(rest[i]) \
            and _is_list_item(rest[i], answer_type, tactic_alias):
        seg.append(rest[i]); i += 1
    return "\n".join(seg)

def _json_objects(text: str) -> list:
    # Mọi đối tượng JSON cấp ngoài cùng trong văn bản (giải mã bằng json.JSONDecoder, chịu được JSON lồng nhau,
    # dấu ngoặc trong chuỗi, khối ```json ... ```)
    dec, out, i = json.JSONDecoder(), [], 0
    while True:
        j = text.find("{", i)
        if j < 0:
            return out
        try:
            obj, end = dec.raw_decode(text, j)
        except ValueError:
            i = j + 1
            continue
        if isinstance(obj, dict):
            out.append(obj)
        i = end

def json_answer(answer: str):
    """Định dạng CHÍNH (notebook 04 dùng guided decoding): {"answer": ["T1686", ...]}.
    Lấy đối tượng JSON CUỐI CÙNG có khoá "answer" (không phân biệt hoa/thường) và CHỈ đọc khoá đó —
    các khoá khác (reasoning, note…) không được chấm. Trả về list chuỗi, hoặc None nếu không có JSON hợp lệ."""
    for obj in reversed(_json_objects(answer or "")):
        low = {str(k).lower(): v for k, v in obj.items()}
        if "answer" not in low:
            continue
        v = low["answer"]
        if v is None:
            return []
        if isinstance(v, (str, int, float)):
            return [str(v)]
        if isinstance(v, list):
            items = []
            for x in v:
                if isinstance(x, dict):                    # [{"id": "T1686", ...}] -> chỉ lấy "id"
                    xl = {str(k).lower(): y for k, y in x.items()}
                    if "id" in xl:
                        items.append(str(xl["id"]))
                elif x is not None:
                    items.append(str(x))
            return items
        return []
    return None

def final_part(answer: str, answer_type: str | None = None, tactic_alias: dict | None = None, mask=()):
    """Trả về (phần trả lời, có_dòng_ANSWER). Không có dòng ANSWER thì trả lại toàn bộ câu trả lời.
    Có nhiều dòng ANSWER: lấy dòng cuối; nếu dòng cuối là từ chối trả lời ("not sure") thì coi là không trả lời;
    nếu dòng cuối không chứa đáp án (vd "ANSWER: done") thì lùi về dòng ANSWER gần nhất có đáp án."""
    a = answer or ""
    marks = list(MARKER_RE.finditer(a))
    if not marks:
        return a, False
    segs = [_segment(a[m.end():], answer_type, tactic_alias, mask) for m in marks]
    last = segs[-1]
    if _has_answer(last, answer_type, tactic_alias, mask) or ABSTAIN_RE.search(last):
        return last, True
    for sg in reversed(segs[:-1]):
        if _has_answer(sg, answer_type, tactic_alias, mask):
            return sg, True
    return last, True

def extract(answer: str, answer_type: str, tactic_alias: dict | None = None, mask=()):
    """Trả về (tập mã, tập tên tactic đã dùng). tactic_alias: tên chính thức -> mã TA, gồm tên của CẢ HAI phiên bản."""
    ja = json_answer(answer)
    if ja is not None:                                     # định dạng chính: JSON
        a, marked = "\n".join(ja), True
    else:                                                  # dự phòng: dòng ANSWER hoặc văn bản tự do
        a, marked = final_part(answer, answer_type, tactic_alias, mask)
    ids = {x.upper() for x in ID_RE[answer_type].findall(a)}
    names = set()
    if answer_type == "tactic_set" and tactic_alias:
        found = _tactic_names(a, tactic_alias, mask, lenient=marked)
        names = set(found)
        if not ids:                                        # chỉ suy mã từ tên khi không có mã TA nào
            ids = set(found.values())
    return ids, names

def score_drift(q: dict, answer: str, tactic_alias: dict | None = None) -> dict:
    """q là một dòng của queries_*.jsonl (gold, other_gold, direction, other_only_labels, entity_names)."""
    pred, names = extract(answer, q["answer_type"], tactic_alias, q.get("entity_names", ()))
    fmt = "json" if json_answer(answer) is not None else ("marker" if MARKER_RE.search(answer or "") else "free")
    target, other = set(q["gold"]), set(q["other_gold"])
    tp = len(pred & target)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(target) if target else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    drift = pred & (other - target)
    if pred == target:
        outcome = "CORRECT"
    elif drift:
        outcome = "STALE" if q["direction"] == "current" else "ANACHRONISM"
    elif tp:
        outcome = "PARTIAL"
    elif not pred:
        outcome = "NO_ANSWER"
    else:
        outcome = "WRONG"
    return dict(pred=sorted(pred), em=pred == target, precision=p, recall=r, f1=f1,
                drift_hit=bool(drift), drift_ids=sorted(drift), drift_possible=bool(other - target),
                label_drift=bool(names & set(q.get("other_only_labels", []))), outcome=outcome, format=fmt)
