"""사람이 지정한 로컬 후보만 읽는다. 파일 이름에서 대응을 추정하지 않는다."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..model import RefEntry


@dataclass(frozen=True, slots=True)
class CandidateSet:
    entry_index: int
    items: tuple[Path, ...]
    complete: bool
    basis: str | None


class ReferenceResolver(ABC):
    @abstractmethod
    def candidates(self, entry: RefEntry) -> CandidateSet: ...


class LocalReferenceResolver(ReferenceResolver):
    def candidates(self, entry: RefEntry) -> CandidateSet:
        return CandidateSet(entry.index, tuple(Path(p).resolve() for p in entry.candidates), entry.candidates_complete, entry.candidates_basis)
