import ast
import re
from pathlib import Path

from .models import CodeChunk, DocSection


def parse_python_file(path: Path, root: Path) -> list[CodeChunk]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    relative = path.relative_to(root).as_posix()
    chunks: list[CodeChunk] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        end_line = getattr(node, "end_lineno", node.lineno)
        signature = ast.get_source_segment(source, node) or node.name
        signature = signature.splitlines()[0].strip()
        names = tuple(sorted({name.id for name in ast.walk(node) if isinstance(name, ast.Name)}))
        chunks.append(CodeChunk(relative, kind, node.name, node.lineno, end_line, signature, names))

    return sorted(chunks, key=lambda chunk: (chunk.path, chunk.start_line))


def parse_markdown_file(path: Path, root: Path) -> list[DocSection]:
    lines = path.read_text(encoding="utf-8").splitlines()
    relative = path.relative_to(root).as_posix()
    sections: list[DocSection] = []
    headings: list[str] = []
    current_heading: tuple[str, ...] | None = None
    content_start = 1

    def finish(end_line: int) -> None:
        nonlocal current_heading, content_start
        if current_heading is None:
            return
        content = "\n".join(lines[content_start - 1:end_line]).strip()
        tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_.-]*", content))
        sections.append(DocSection(relative, current_heading, content_start, end_line, content, tuple(sorted(tokens))))

    for number, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        finish(number - 1)
        level, title = len(match.group(1)), match.group(2).strip()
        headings = headings[: level - 1] + [title]
        current_heading = tuple(headings)
        content_start = number + 1
    finish(len(lines))
    return sections


def discover(root: Path, ignored: set[str] | None = None) -> tuple[list[CodeChunk], list[DocSection]]:
    ignored = ignored or {".git", ".venv", "venv", "node_modules", "__pycache__"}
    files = [path for path in root.rglob("*") if path.is_file() and not ignored.intersection(path.parts)]
    code = [chunk for path in files if path.suffix == ".py" for chunk in parse_python_file(path, root)]
    docs = [section for path in files if path.suffix.lower() in {".md", ".markdown"} for section in parse_markdown_file(path, root)]
    return code, docs

