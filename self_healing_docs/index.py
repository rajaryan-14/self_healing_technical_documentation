import json
from pathlib import Path

from .models import CodeChunk, DocSection, DocumentationIndex


def build_index(code_chunks: list[CodeChunk], doc_sections: list[DocSection]) -> DocumentationIndex:
    links: dict[str, list[str]] = {chunk.stable_id: [] for chunk in code_chunks}
    for chunk in code_chunks:
        searchable = {chunk.name, *chunk.references}
        for section in doc_sections:
            if searchable.intersection(section.references):
                links[chunk.stable_id].append(section.stable_id)
    return DocumentationIndex(code_chunks, doc_sections, links)


def save_index(index: DocumentationIndex, path: Path) -> None:
    payload = {
        "code_chunks": [chunk.__dict__ | {"references": list(chunk.references)} for chunk in index.code_chunks],
        "doc_sections": [section.__dict__ | {"heading_path": list(section.heading_path), "references": list(section.references)} for section in index.doc_sections],
        "links": index.links,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_index(path: Path) -> DocumentationIndex:
    data = json.loads(path.read_text(encoding="utf-8"))
    code = [CodeChunk(**item, references=tuple(item.get("references", []))) for item in data["code_chunks"]]
    docs = [DocSection(**item, heading_path=tuple(item["heading_path"]), references=tuple(item.get("references", []))) for item in data["doc_sections"]]
    return DocumentationIndex(code, docs, data["links"])

