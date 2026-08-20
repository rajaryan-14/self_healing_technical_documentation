from pathlib import Path

from self_healing_docs.index import build_index
from self_healing_docs.parsers import parse_markdown_file, parse_python_file


def test_python_chunks_and_markdown_links(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("def greet(name: str = 'world'):\n    return name\n", encoding="utf-8")
    docs = tmp_path / "README.md"
    docs.write_text("# Usage\n\nCall `greet` with a name.\n", encoding="utf-8")

    code = parse_python_file(source, tmp_path)
    sections = parse_markdown_file(docs, tmp_path)
    index = build_index(code, sections)

    assert code[0].stable_id == "app.py:function:greet"
    assert index.links[code[0].stable_id] == [sections[0].stable_id]


def test_markdown_heading_paths(tmp_path: Path) -> None:
    docs = tmp_path / "docs.md"
    docs.write_text("# Config\n## Environment\nPORT defaults to 8000.\n", encoding="utf-8")
    sections = parse_markdown_file(docs, tmp_path)
    assert sections[0].heading_path == ("Config",)
    assert sections[1].heading_path == ("Config", "Environment")

