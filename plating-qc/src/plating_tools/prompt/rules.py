"""W05·W10·W02의 정확한 앵커에서 값과 본문을 읽는다."""
import re
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path

from ..docs import Anchor, DocStore, Extract, resolve
from ..errors import InputError
from ..model import DocFingerprint, Finding, Severity, SourceRef
from ..profile_plating import ANCHOR_SPECS, DOC_TITLES, ORDER_PREFIXES, PEOPLE_BLOCKS, SCENE_BLOCKS


@dataclass(frozen=True, slots=True)
class Block:
    key: str
    text: str
    sha256: str
    where: SourceRef


@dataclass(frozen=True, slots=True)
class ChecklistLine:
    no: int
    text: str
    where: SourceRef


@dataclass(frozen=True, slots=True)
class RuleBook:
    order: tuple[str, ...]
    order_basis: SourceRef
    catalog: dict[str, Block]
    checklist: tuple[ChecklistLine, ...]
    image_limit: int
    limit_basis: SourceRef
    scene_conflicts: tuple[Finding, ...]
    fingerprints: tuple[DocFingerprint, ...]
    documents: dict[str, Path]
    findings: tuple[Finding, ...]


def read_rules(store: DocStore) -> RuleBook:
    docs = {key: store.load(key) for key in ("W05", "W10", "W02", "W11")}
    def extracts(name: str):
        key, headings, take, count = ANCHOR_SPECS[name]
        return resolve(docs[key], Anchor(key, (DOC_TITLES[key], *headings), take, count))
    catalog = {}
    def add(key: str, extracted: Extract) -> None:
        catalog[key] = Block(key, extracted.text, sha256(extracted.text.encode("utf-8")).hexdigest(), extracted.where)
    style, underclass = extracts("style")
    if not underclass.text.startswith("UNDERCLASS PROPORTIONS:"):
        raise InputError("W10 2-1 하층민 비율 블록 구조 변경: UNDERCLASS PROPORTIONS 필요")
    add("STYLE", style)
    add("UNDERCLASS_PROPORTIONS", underclass)
    add("WORLD", extracts("world")[0])
    for key, ext in zip(("AVOID", "UPPER_AVOID"), extracts("avoid"), strict=True):
        add(key, ext)
    people = extracts("people")
    for key, ext in zip(PEOPLE_BLOCKS, people, strict=True):
        add(key, ext)
    face_lines = people[0].text.split("\n")
    if len(face_lines) != 3 or not face_lines[0].startswith("FACE RULE:") or not face_lines[1].startswith("EYES:"):
        raise InputError("W10 사람 블록 구조 변경: FACE RULE/EYES/손 3줄 필요")
    for offset, (key, text) in enumerate(zip(("FACE_RULE", "EYES", "HANDS"), face_lines, strict=True)):
        line = people[0].where.line_start + offset
        where = docs["W10"].ref(line, line, people[0].where.heading_path)
        add(key, Extract(text, replace(where, mark=people[0].where.mark, mark_reason=people[0].where.mark_reason), {}))
    del catalog["FACE_EYES_HANDS"]
    for key, ext in zip(SCENE_BLOCKS, extracts("scenes"), strict=True):
        add(key, ext)
    order_ext = extracts("order")[0]
    order_lines = [line for line in order_ext.text.split("\n") if " → " in line]
    if len(order_lines) != 1:
        raise InputError("W05 섹션 순서 행 개수 변경")
    order = tuple(order_lines[0].split(" → "))
    if len(order) != len(ORDER_PREFIXES) or any(not part.startswith(prefix) for part, prefix in zip(order, ORDER_PREFIXES, strict=True)):
        raise InputError(f"W05 섹션 순서 변경: {order}")
    limit = extracts("image_limit")[0]
    limit_match = re.search(r"이미지 프롬프트는 공통 블록 포함 (\d+)자 이하", limit.text)
    if limit_match is None:
        raise InputError(f"W05:{limit.where.line_start} 이미지 한도 형식 변경")
    checklist = tuple(ChecklistLine(i, ext.text, ext.where) for i, ext in enumerate(extracts("checklist"), 1))
    if any(not line.text.startswith(f"{line.no}. ") for line in checklist):
        raise InputError("W02 점검 번호 순서 변경")
    settings = extracts("settings")[0]
    conflict_message = "SCENE_D 조리대 수치가 W11 설정과 충돌. 원문 치환 금지"
    if "6.0 x 1.4" not in catalog["SCENE_D"].text or "2.4×0.9" not in settings.text:
        conflict_message = "SCENE_D 충돌 기록 재확인 필요"
    conflict = Finding("PR_CONFLICT", Severity.ERROR, conflict_message, settings.where)
    changed = tuple(Finding("DOC_CHANGED", Severity.WARN, f"작성 기준 지문 변경: {key}") for key, doc in docs.items()
                    if doc.fingerprint.changed_since_authored)
    return RuleBook(order, order_ext.where, catalog, checklist, int(limit_match[1]), limit.where,
                    (conflict,), tuple(d.fingerprint for d in docs.values()), {k: Path(d.fingerprint.path) for k, d in docs.items()}, changed)
