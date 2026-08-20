from pathlib import Path

from self_healing_docs.diff import find_suspects
from self_healing_docs.index import build_index
from self_healing_docs.parsers import parse_markdown_file, parse_python_file


def test_find_suspects_for_changed_symbol(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text(
        "def greet(name):\n    return f'Hello {name}'\n\n"
        "def untouched():\n    return True\n",
        encoding="utf-8",
    )
    docs = tmp_path / "README.md"
    docs.write_text("# API\n\nUse `greet` to say hello.\n\n# Health\n\n`untouched` returns a health flag.\n", encoding="utf-8")
    index = build_index(parse_python_file(source, tmp_path), parse_markdown_file(docs, tmp_path))
    diff = """diff --git a/app.py b/app.py
index 1111111..2222222 100644
--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
 def greet(name):
-    return f'Hello {name}'
+    return f'Hi {name}'
"""

    findings = find_suspects(index, diff)
    assert [finding.section.heading_path for finding in findings] == [("API",)]


def test_later_line_in_hunk_is_detected(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("def greet(name):\n    message = 'Hello'\n    return message + name\n", encoding="utf-8")
    docs = tmp_path / "README.md"
    docs.write_text("# API\n\n`greet` returns a greeting.\n", encoding="utf-8")
    index = build_index(parse_python_file(source, tmp_path), parse_markdown_file(docs, tmp_path))
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,3 +1,3 @@
 def greet(name):
     message = 'Hello'
-    return message + name
+    return message.upper() + name
"""
    assert len(find_suspects(index, diff)) == 1
