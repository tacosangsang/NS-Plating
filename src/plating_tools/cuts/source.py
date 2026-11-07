"""로컬 파일 입력 경계. 파일은 바이트 읽기로만 연다."""
from abc import ABC, abstractmethod
from pathlib import Path

from ..model import DocFingerprint
from ..textio import Document, read_document


class CutTableSource(ABC):
    @property
    @abstractmethod
    def document(self) -> Document: ...

    def fingerprint(self) -> DocFingerprint:
        return self.document.fingerprint

    def lines(self) -> tuple[str, ...]:
        return self.document.lines


class NotionMdFile(CutTableSource):
    def __init__(self, path: Path):
        self._document = read_document(path, "F")

    @property
    def document(self) -> Document:
        return self._document
