import re
from typing import Dict, Any, List
from ..index.search_stub import search_similar

QUOTE_RE = re.compile(r'"(.+?)"')

def extract_quotes(text: str, min_len: int = 18, max_len: int = 320) -> List[str]:
    qs = []
    for m in QUOTE_RE.finditer(text or ""):
        q = (m.group(1) or "").strip()
        if len(q) >= min_len and len(q) <= max_len:
            qs.append(q)
    seen = set(); out = []
    for q in qs:
        if q in seen: continue
        seen.add(q); out.append(q)
    return out[:8]

def fact_check(summary: str, threshold: float = 0.65) -> Dict[str, Any]:
    quotes = extract_quotes(summary)
    results = []
    verified = 0
    for q in quotes:
        hits = search_similar(q, top_k=3)
        top = hits[0] if hits else None
        ok = bool(top and top.get("score", 0.0) >= threshold)
        if ok: verified += 1
        results.append({"quote": q, "ok": ok, "best": top})
    score = (verified / max(1, len(quotes))) if quotes else 1.0
    return {"quotes_checked": len(quotes), "verified_ratio": round(score, 3), "details": results}
