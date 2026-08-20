import json
from pathlib import Path
from urllib.request import Request, urlopen

from .models import CodeChunk, DocSection


def generate_repair(section: DocSection, code: list[CodeChunk], diagnosis: dict, model: str = "qwen2.5-coder:7b", endpoint: str = "http://127.0.0.1:11434/api/generate") -> dict:
    code_text = "\n".join(f"{chunk.path}:{chunk.start_line} {chunk.signature}" for chunk in code)
    prompt = f"""Repair one stale technical documentation section.
Return JSON only with keys: corrected_content (string), confidence (number from 0 to 1), notes (string).
Rewrite only what is inaccurate. Preserve the Markdown structure, tone, and accurate text.
Do not add facts unsupported by the code. Do not include the heading in corrected_content.

Current section:\n{section.content}\n\nReview diagnosis:\n{json.dumps(diagnosis)}\n\nCurrent code:\n{code_text}"""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json"}).encode()
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            outer = json.loads(response.read().decode("utf-8"))
        result = json.loads(outer.get("response", "{}"))
        corrected = str(result.get("corrected_content", "")).strip()
        if not corrected:
            raise ValueError("model returned empty corrected_content")
        return {"corrected_content": corrected, "confidence": float(result.get("confidence", 0)), "notes": str(result.get("notes", ""))}
    except (OSError, ValueError, json.JSONDecodeError):
        return {"corrected_content": "", "confidence": 0, "notes": "Repair unavailable; no files changed."}


def validate_repair(section: DocSection, replacement: dict, code: list[CodeChunk], model: str = "qwen2.5-coder:7b", endpoint: str = "http://127.0.0.1:11434/api/generate") -> dict:
    code_text = "\n".join(chunk.signature for chunk in code)
    prompt = f"""Validate a proposed documentation repair. Return JSON only with keys: valid (boolean), confidence (number from 0 to 1), reason (string).
The replacement must be supported by the code, preserve accurate information, and not contain a Markdown heading.

Original:\n{section.content}\n\nProposed replacement:\n{replacement.get('corrected_content', '')}\n\nCode:\n{code_text}"""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json"}).encode()
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            outer = json.loads(response.read().decode("utf-8"))
        result = json.loads(outer.get("response", "{}"))
        return {"valid": bool(result.get("valid", False)), "confidence": float(result.get("confidence", 0)), "reason": str(result.get("reason", ""))}
    except (OSError, ValueError, json.JSONDecodeError):
        return {"valid": False, "confidence": 0, "reason": "Validation unavailable; no files changed."}


def apply_repairs(root: Path, repairs: list[dict], minimum_confidence: float = 0.8) -> list[str]:
    changed: list[str] = []
    for repair in repairs:
        validation = repair.get("validation", {})
        if repair.get("confidence", 0) < minimum_confidence or not repair.get("corrected_content") or not validation.get("valid") or validation.get("confidence", 0) < minimum_confidence:
            continue
        path = root / repair["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        start, end = repair["start_line"] - 1, repair["end_line"]
        path.write_text("\n".join(lines[:start] + repair["corrected_content"].splitlines() + lines[end:]) + "\n", encoding="utf-8")
        changed.append(repair["path"])
    return changed
