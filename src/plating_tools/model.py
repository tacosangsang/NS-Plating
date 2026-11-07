"""공통 출처·미확인·소견 및 JSON 경계."""
import dataclasses
import json
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from pathlib import Path

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]


class Severity(StrEnum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class Mark(StrEnum):
    UNMARKED = "무표기"
    EXCEPTION = "예외"
    EXAMPLE = "예(PLATING)"
    FILE_EXCEPTION = "파일 단위 예외"


@dataclass(frozen=True, slots=True)
class Unknown:
    unknown: str


@dataclass(frozen=True, slots=True)
class DocFingerprint:
    key: str
    path: str
    size: int
    sha256: str
    authored_sha256: str | None = None
    declared_commit: str | None = None


@dataclass(frozen=True, slots=True)
class SourceRef:
    doc: str
    line_start: int
    line_end: int
    heading_path: tuple[str, ...] = ()
    mark: Mark | None = None
    mark_reason: str | None = None
    excerpt_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    severity: Severity
    message: str
    where: SourceRef | None = None


@dataclass(frozen=True, slots=True)
class RefEntry:
    index: int
    role: str
    local_path: str | None = None
    url: str | None = None
    file_id: str | None = None
    sheet: str = "시트 없음/만들어야 함"
    preview: str = "미검수"
    preview_by: str | None = None
    preview_at: str | None = None
    candidates: tuple[str, ...] = ()
    candidates_complete: bool = False
    candidates_basis: str | None = None


def _encode(value):
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, (Decimal, Path)):
        return str(value)
    raise TypeError(f"JSON 변환 불가: {type(value).__name__}")


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=_encode, allow_nan=False) + "\n"
