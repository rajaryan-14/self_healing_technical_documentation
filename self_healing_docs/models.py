from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CodeChunk:
    path: str
    kind: str
    name: str
    start_line: int
    end_line: int
    signature: str
    references: tuple[str, ...] = ()

    @property
    def stable_id(self) -> str:
        return f"{self.path}:{self.kind}:{self.name}"


@dataclass(frozen=True)
class DocSection:
    path: str
    heading_path: tuple[str, ...]
    start_line: int
    end_line: int
    content: str
    references: tuple[str, ...] = ()

    @property
    def stable_id(self) -> str:
        return f"{self.path}:{'>'.join(self.heading_path)}"


@dataclass
class DocumentationIndex:
    code_chunks: list[CodeChunk] = field(default_factory=list)
    doc_sections: list[DocSection] = field(default_factory=list)
    links: dict[str, list[str]] = field(default_factory=dict)

    def linked_sections(self, chunk_ids: set[str]) -> list[DocSection]:
        section_ids = {
            section_id
            for chunk_id in chunk_ids
            for section_id in self.links.get(chunk_id, [])
        }
        return [section for section in self.doc_sections if section.stable_id in section_ids]


@dataclass(frozen=True)
class Finding:
    section: DocSection
    changed_paths: tuple[str, ...]
    reason: str
    confidence: str = "medium"

