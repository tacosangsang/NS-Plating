"""블록아웃 정본 모델과 입력 규칙."""
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import PurePosixPath
from typing import Final

from ..errors import InputError

VERSION: Final = re.compile(r"v[0-9]{3}")


def version_number(value: str) -> int:
    if not isinstance(value, str) or not VERSION.fullmatch(value) or value == "v000":
        raise InputError(f"버전은 v001~v999, 접미사 금지: {value}")
    return int(value[1:])


def next_version(versions: tuple[str, ...]) -> str:
    number = max((version_number(v) for v in versions), default=0) + 1
    if number > 999:
        raise InputError("버전 v999 초과")
    return f"v{number:03d}"


def asset_name(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[\w-]+", value) or value.casefold() in {"raw", "con", "prn", "aux", "nul"} or re.fullmatch(r"(?:com|lpt)[1-9]", value, re.I):
        raise InputError(f"자산 이름은 경로가 아닌 단일 이름이어야 함: {value}")
    return value


def required_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise InputError(f"{label}: 비어 있지 않은 한 줄 문자열 필요")
    return value


def iso_date(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise InputError(f"YYYY-MM-DD 날짜 필요: {value}")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"유효하지 않은 날짜: {value}") from exc
    return value


@dataclass(frozen=True, slots=True)
class Version:
    date: str
    change: str
    by: str
    files: dict[str, str]

    def __post_init__(self) -> None:
        iso_date(self.date)
        required_text(self.change, "change")
        required_text(self.by, "by")
        if not isinstance(self.files, dict) or not self.files:
            raise InputError("versions.files: 비어 있지 않은 파일·SHA-256 표 필요")
        for name, digest in self.files.items():
            if (not isinstance(name, str) or not name or "\\" in name or ":" in name
                    or PurePosixPath(name).is_absolute() or any(p in {"", ".", ".."} for p in name.split("/"))
                    or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
                raise InputError(f"versions.files: 상대 파일 경로·SHA-256 오류: {name}")


@dataclass(frozen=True, slots=True)
class Pin:
    version: str
    reason: str
    approved_by: str
    date: str

    def __post_init__(self) -> None:
        version_number(self.version)
        required_text(self.reason, "reason(승인 문장 인용)")
        required_text(self.approved_by, "approved_by")
        iso_date(self.date)


@dataclass(frozen=True, slots=True)
class Manifest:
    asset: str
    current: str = ""
    variants: tuple[str, ...] = ()
    versions: dict[str, Version] = field(default_factory=dict)
    pins: dict[str, Pin] = field(default_factory=dict)

    def __post_init__(self) -> None:
        asset_name(self.asset)
        if not isinstance(self.current, str) or (self.current and self.current not in self.versions):
            raise InputError("current가 manifest versions에 없음")
        for version in self.versions:
            version_number(version)
        if not isinstance(self.variants, tuple) or any(not isinstance(v, str) or not v.strip() for v in self.variants):
            raise InputError("variants: 비어 있지 않은 문자열 목록 필요")
        for scene, pin in self.pins.items():
            if not re.fullmatch(r"S#[0-9]{2}", scene) or pin.version not in self.versions:
                raise InputError(f"pin 씬 형식 또는 참조 오류: {scene}")
