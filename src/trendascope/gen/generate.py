from typing import List, Dict
import json, os
from .llm.providers import call_llm
from .parser import coerce_json, JSONShapeError
from .rag_facts import fact_check
from ..utils.cache import get as cache_get, setex as cache_set

PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts.json")
with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

def _compose_fewshots(style_snippets: List[str], max_chars: int = 1200) -> str:
    out, total = [], 0
    for s in style_snippets:
        s = (s or "").strip()
        if not s: continue
        if total + len(s) > max_chars: break
        out.append(s); total += len(s)
    return "\n---\n".join(out)

def _render_prompt(mode: str, analyzed_posts: List[Dict]) -> str:
    prompt_tpl = PROMPTS.get(mode, PROMPTS["logospheric"])["prompt"]
    frags = [f"# {a.get('title','')}\n" + (a.get('text_plain','')[:900]) + "..." for a in analyzed_posts]
    style = _compose_fewshots([a.get('text_plain','')[:300] for a in analyzed_posts])
    return prompt_tpl.replace("{FRAGMENTS}", "\n\n".join(frags)).replace("{STYLE_FEWSHOTS}", style)

def generate_summary(analyzed_posts: List[Dict], mode: str = "logospheric", provider: str = "openai", model: str | None = None, temperature: float = 0.7) -> Dict:
    prompt = _render_prompt(mode, analyzed_posts)
    cache_payload = json.dumps({"provider":provider,"model":model,"mode":mode,"prompt":prompt}, ensure_ascii=False)
    cached = cache_get("llm", cache_payload)
    if cached:
        raw = cached
    else:
        raw = call_llm(provider=provider, model=model, prompt=prompt, temperature=temperature)
        cache_set("llm", cache_payload, raw, ttl_seconds=86400)

    data = coerce_json(raw)  # strict JSON (raises if invalid)
    fc = fact_check(data.get("summary",""))
    data["fact_check"] = fc
    return {"prompt_preview": prompt[:800] + ("..." if len(prompt) > 800 else ""), **data}
