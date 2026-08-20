"""Small, dependency-free Ollama client for optional local review."""

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from .models import CodeChunk, DocSection


def review_section(
    section: DocSection,
    code: list[CodeChunk],
    model: str = "qwen2.5-coder:7b",
    endpoint: str = "http://127.0.0.1:11434/api/generate",
) -> dict:
    code_text = "\n".join(f"{chunk.path}:{chunk.start_line} {chunk.signature}" for chunk in code)
    prompt = f"""You are reviewing technical documentation for staleness.
Return JSON only with keys: stale (boolean), confidence (number from 0 to 1), reason (string), suggestion (string).

Documentation section ({section.path} > {' > '.join(section.heading_path)}):
{section.content}

Changed or linked code:
{code_text}

Decide whether the documentation is inaccurate for the code shown. Do not invent behavior."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json"}).encode()
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
        parsed = json.loads(result.get("response", "{}"))
        return {
            "stale": bool(parsed.get("stale", False)),
            "confidence": float(parsed.get("confidence", 0)),
            "reason": str(parsed.get("reason", "")),
            "suggestion": str(parsed.get("suggestion", "")),
        }
    except (OSError, URLError, ValueError, json.JSONDecodeError) as error:
        return {"stale": False, "confidence": 0, "reason": f"Ollama unavailable: {error}", "suggestion": ""}

