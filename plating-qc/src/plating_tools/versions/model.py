"""버전·계열·고정 예외의 값 객체."""
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ..model import Unknown


@dataclass(frozen=True, slots=True)
class VersionTag:
    raw: str
    number: int
    suffix: str


@dataclass(frozen=True, slots=True)
class FamilySpec:
    name: str
    root: Path
    blend_glob: str = "v*_*.blend"
    script_glob: str = "v*_*.py"
    readme_glob: str = "v*_README*"
    readme_version_pattern: str | None = None
    exclude_dirs: tuple[str, ...] = ()
    explicit_order: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class Pin:
    family: str
    version: str
    scope: tuple[str, ...]
    basis_doc: str
    basis_line: int
    basis_contains: str
    approved_by: str


@dataclass(frozen=True, slots=True)
class FamilyState:
    family: str
    blend: VersionTag | Unknown
    script: VersionTag | Unknown
    readme: VersionTag | Unknown
    latest: VersionTag | Unknown
    order_unknown: tuple[str, ...]
    files: tuple[tuple[str, str], ...]


class Verdict(StrEnum):
    LATEST = "최신 일치"
    STALE = "옛 판"
    PINNED = "고정 예외 일치"
    PIN_MISMATCH = "고정 예외 불일치"
    NO_VERSION = "판 없음"
    ORDER_UNKNOWN = "순서 불명"
    CONFLICT = "출처 충돌"
    FAMILY_UNKNOWN = "계열 미지정"


@dataclass(frozen=True, slots=True)
class RenderSpec:
    family: str
    path: Path
    scene: str | None
    version_from: str = "접두사"


@dataclass(frozen=True, slots=True)
class RenderCheck:
    path: str
    scene: str | None
    version: VersionTag | Unknown
    version_from: str | None
    verdict: Verdict
    compared_to: str | None = None
    diff: int | None = None
    not_verified: tuple[str, ...] = ("형상 동일성", "실제 치수")
