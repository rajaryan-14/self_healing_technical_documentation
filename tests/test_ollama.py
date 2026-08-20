import json
from pathlib import Path

from self_healing_docs.models import DocSection
from self_healing_docs.ollama import review_section


def test_ollama_response_is_normalized(monkeypatch) -> None:
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"response": json.dumps({"stale": True, "confidence": 0.91, "reason": "default changed", "suggestion": "Update it"})}).encode()

    monkeypatch.setattr("self_healing_docs.ollama.urlopen", lambda *args, **kwargs: Response())
    section = DocSection("README.md", ("Config",), 1, 2, "PORT defaults to 8000.")
    result = review_section(section, [])
    assert result["stale"] is True
    assert result["confidence"] == 0.91

