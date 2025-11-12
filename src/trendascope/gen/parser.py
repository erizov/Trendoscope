import json, re
from typing import Any, Dict

class JSONShapeError(ValueError):
    pass

SCHEMA_KEYS = ["summary","titles","ideas","leads","viral_potential"]

def coerce_json(text: str) -> Dict[str, Any]:
    if not text:
        raise JSONShapeError("Empty LLM output")
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.IGNORECASE|re.MULTILINE)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise JSONShapeError("No JSON object found")
    core = text[start:end+1]
    try:
        obj = json.loads(core)
    except json.JSONDecodeError:
        core = re.sub(r",\s*\}", "}", core)
        core = re.sub(r",\s*\]", "]", core)
        obj = json.loads(core)
    for k in SCHEMA_KEYS:
        if k not in obj:
            raise JSONShapeError(f"Missing '{k}' in JSON")
    return obj
