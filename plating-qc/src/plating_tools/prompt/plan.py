"""계획 파일에서 사람이 명시한 값만 읽는다. 이름으로 분류하지 않는다."""
import tomllib
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..errors import InputError
from ..model import RefEntry, Unknown
from ..textio import read_document


@dataclass(frozen=True, slots=True)
class CharacterMeta:
    name: str
    group: str | Unknown
    face: str | Unknown
    basis: str | None


@dataclass(frozen=True, slots=True)
class ClipPlan:
    clip_id: str
    kind: str
    cuts: tuple[str, ...]
    segment: str | Unknown
    gen_seconds: Decimal | Unknown
    mode: str | Unknown
    model: str | Unknown
    resolution: str | Unknown
    edit_input_seconds: Decimal | Unknown
    people: str | Unknown
    characters: tuple[CharacterMeta, ...]
    staging: dict[str, bool | Unknown]
    scene_module: str | Unknown
    props: tuple[str, ...] | Unknown
    references: tuple[RefEntry, ...]


def number(value, field: str) -> Decimal | Unknown:
    if value is None or value == "":
        return Unknown(f"{field} 미입력")
    if isinstance(value, bool):
        raise InputError(f"{field}: 숫자 필요")
    try:
        result = Decimal(repr(value) if isinstance(value, float) else str(value))
    except InvalidOperation as exc:
        raise InputError(f"{field}: 숫자 해석 실패") from exc
    if not result.is_finite() or result <= 0:
        raise InputError(f"{field}: 양의 유한 숫자 필요")
    return result


def choice(value, options: tuple[str, ...], field: str) -> str | Unknown:
    if value is None or value == "":
        return Unknown(f"{field} 미입력")
    if value not in options:
        raise InputError(f"{field}: 허용값 {options}, 입력 {value}")
    return value


def load_plan(path: Path | None, clip: str | None) -> ClipPlan | None:
    if path is None:
        return None
    try:
        data = tomllib.loads(read_document(path, "plan").text)
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"계획 TOML 오류: {path}: {exc}") from exc
    clips = data.get("clip", [])
    if not isinstance(clips, list) or any(not isinstance(c, dict) for c in clips):
        raise InputError("계획에 [[clip]] 목록 필요")
    choices = [c for c in clips if clip is None or c.get("id") == clip]
    if len(choices) != 1:
        raise InputError(f"클립 선택 필요: --clip, 후보 {[c.get('id') for c in clips]}")
    selected = choices[0]
    def text(field: str):
        value = selected.get(field, "")
        if not isinstance(value, str):
            raise InputError(f"계획 {field}: 문자열 필요")
        return value or Unknown(f"{field} 미입력")
    cuts = selected.get("cuts", [])
    if not isinstance(cuts, list) or any(not isinstance(c, str) for c in cuts):
        raise InputError("계획 cuts: 문자열 목록 필요")
    characters = []
    for c in selected.get("character", []):
        characters.append(CharacterMeta(c.get("name", ""), c.get("group") or Unknown("인물 분류 미입력"),
                                        choice(c.get("face"), ("close", "far", "none"), "face"), c.get("basis")))
    staging = {}
    for key, value in selected.get("staging", {}).items():
        if value != "" and not isinstance(value, bool):
            raise InputError(f"staging.{key}: 참/거짓 또는 빈 값 필요")
        staging[key] = value if isinstance(value, bool) else Unknown(f"{key} 미입력")
    refs = []
    for r in selected.get("reference", []):
        if not isinstance(r.get("index"), int) or isinstance(r.get("index"), bool) or r["index"] < 1:
            raise InputError("레퍼런스 index: 양의 정수 필요")
        refs.append(RefEntry(r["index"], r.get("role", ""), r.get("local_path") or None, r.get("url") or None,
                             r.get("file_id") or None, r.get("sheet", "시트 없음/만들어야 함"), r.get("preview", "미검수"),
                             r.get("preview_by"), r.get("preview_at"), tuple(r.get("candidates", [])), r.get("candidates_complete", False), r.get("candidates_basis")))
    kind = selected.get("kind", "video")
    if kind not in {"video", "image"}:
        raise InputError("계획 kind: video/image 필요")
    props = selected.get("props", None)
    if props is not None and (not isinstance(props, list) or any(not isinstance(p, str) for p in props)):
        raise InputError("계획 props: 문자열 목록 필요")
    return ClipPlan(str(selected.get("id", "")), kind, tuple(cuts), text("segment"), number(selected.get("gen_seconds"), "gen_seconds"),
                    choice(selected.get("mode"), ("new", "edit", "code"), "mode"), text("model"), text("resolution"),
                    number(selected.get("edit_input_seconds"), "edit_input_seconds"), choice(selected.get("people"), ("있음", "없음"), "people"),
                    tuple(characters), staging, text("scene_module"), tuple(props) if props is not None else Unknown("소품 미입력"), tuple(refs))
