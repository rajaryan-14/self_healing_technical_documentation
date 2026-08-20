import re
import subprocess
from pathlib import Path

from .models import CodeChunk, DocumentationIndex, Finding


def changed_python_paths(diff: str) -> set[str]:
    return {match.group(1) for match in re.finditer(r"^diff --git a/(.*?) b/.*$", diff, re.MULTILINE) if match.group(1).endswith(".py")}


def affected_chunks(index: DocumentationIndex, diff: str) -> set[str]:
    paths = changed_python_paths(diff)
    chunks: set[str] = set()
    for path in paths:
        changed_lines = [int(start) for start, _count in re.findall(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.MULTILINE)]
        for chunk in index.code_chunks:
            if chunk.path == path and any(chunk.start_line <= line <= chunk.end_line for line in changed_lines):
                chunks.add(chunk.stable_id)
            elif chunk.path == path and not changed_lines:
                chunks.add(chunk.stable_id)
    return chunks


def find_suspects(index: DocumentationIndex, diff: str) -> list[Finding]:
    paths = tuple(sorted(changed_python_paths(diff)))
    sections = index.linked_sections(affected_chunks(index, diff))
    return [Finding(section, paths, "linked Python symbol was changed", "medium") for section in sections]


def git_diff(root: Path, base: str = "HEAD~1") -> str:
    result = subprocess.run(["git", "diff", base, "--", "."], cwd=root, text=True, capture_output=True, check=True)
    return result.stdout
