"""완성본의 원문 블록·자리표시·레퍼런스 및 실제 문자열 길이를 검사한다."""
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from ..model import Finding, Severity, SourceRef, Unknown
from ..textio import normalized
from .plan import ClipPlan
from .rules import RuleBook
from .select import select_blocks


@dataclass(frozen=True, slots=True)
class LengthCount:
    codepoints: int
    utf16_units: int
    utf8_bytes: int
    non_nfc: bool


@dataclass(frozen=True, slots=True)
class LengthReport:
    total: LengthCount
    per_block: dict[str, LengthCount]
    per_section: dict[str, LengthCount]
    placeholders: int
    limit: int | Unknown
    limit_basis: SourceRef | None
    verdict: str


@dataclass(frozen=True, slots=True)
class PromptCheck:
    lengths: LengthReport
    findings: tuple[Finding, ...]
    blocks: dict[str, str]
    reference_numbers: tuple[int, ...]


def count(text: str) -> LengthCount:
    text = normalized(text)
    return LengthCount(len(text), len(text.encode("utf-16-le")) // 2, len(text.encode("utf-8")), not unicodedata.is_normalized("NFC", text))


def length_report(text: str, kind: str, rules: RuleBook) -> LengthReport:
    text = normalized(text)
    total = count(text)
    placeholders = len(re.findall(r"\{\{", text))
    limit = rules.image_limit if kind == "image" else Unknown("상한 미확인")
    verdict = "no_limit"
    if kind == "image":
        verdict = "over" if total.codepoints > limit else "over_by_utf16_only" if total.utf16_units > limit else "within"
    if placeholders:
        verdict = "not_final"
    return LengthReport(total, {}, {}, placeholders, limit, rules.limit_basis if kind == "image" else None, verdict)


def check_prompt(text: str, plan: ClipPlan | None, rules: RuleBook, kind: str) -> PromptCheck:
    text = normalized(text)
    findings = list(rules.findings)
    blocks = {}
    decisions = select_blocks(plan, rules)
    chosen = {d.block_key for d in decisions if d.decision == "포함"}
    if kind == "image":
        chosen.add("WORLD")
    if "SCENE_D" in chosen:
        findings.extend(rules.scene_conflicts)
    for key in sorted(chosen):
        block = rules.catalog[key]
        present = block.text in text
        blocks[block.key] = "원문 일치" if present else "변형 의심" if block.text.split("\n")[0] in text else "원문 불일치"
        if not present:
            findings.append(Finding("PR001", Severity.ERROR, f"고정 블록 원문 불일치: {block.key}", block.where))
    lengths = length_report(text, kind, rules)
    if lengths.placeholders:
        findings.append(Finding("PR002", Severity.ERROR, "미결 자리표시 남음"))
    if re.search(r"@\[이미지\s*\d+\]\(image_\d+\)", text):
        findings.append(Finding("PR003", Severity.ERROR, "옛 이미지 표기"))
    references = tuple(int(n) for n in re.findall(r"@image(\d+)\b", text))
    if plan is not None:
        indices = [r.index for r in plan.references]
        registered = set(indices)
        if (set(references) != registered or registered != set(range(1, len(indices) + 1))
                or any(value > 1 for value in Counter(indices).values())):
            findings.append(Finding("PR004", Severity.ERROR, f"이미지 번호 누락·미사용·비연속·중복: 본문 {sorted(set(references))}, 계획 {indices}"))
    elif references:
        findings.append(Finding("PR004", Severity.WARN, "계획 없음: 이미지 번호 대조 미확인"))
    if lengths.verdict in {"over", "over_by_utf16_only"}:
        findings.append(Finding("PR005", Severity.ERROR, f"이미지 글자 수 초과: {lengths.verdict}"))
    if lengths.total.non_nfc:
        findings.append(Finding("PR006", Severity.WARN, "NFC 아님. 원문 정규화하지 않음"))
    return PromptCheck(lengths, tuple(findings), blocks, references)
