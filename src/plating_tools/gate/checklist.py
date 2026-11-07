"""8개 사람 응답, 기계 소견, 생성 승인 기록을 별도로 판정한다."""
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from decimal import Decimal

from ..cuts.extract import FIRST_SCENE_NO_PREV, SCENE_NEIGHBOR_ROLES
from ..docs import Anchor, DocStore, resolve
from ..errors import InputError
from ..model import Finding, Severity, SourceRef, Unknown, json_text
from ..profile_plating import ANCHOR_SPECS, APPROVAL_PATTERNS, DOC_TITLES
from ..textio import read_document
from .cost import CostSummary


@dataclass(frozen=True, slots=True)
class ChecklistLine:
    no: int
    text: str
    where: SourceRef


@dataclass(frozen=True, slots=True)
class GateRules:
    lines: tuple[ChecklistLine, ...]
    approval_words: tuple[str, ...]
    max_seconds: Decimal


@dataclass(frozen=True, slots=True)
class ItemInput:
    no: int
    answer: str | None
    reason: str
    alternative: str
    evidence: tuple[str, ...]
    reviewer: str


@dataclass(frozen=True, slots=True)
class ApprovalEvidence:
    quote: str
    where: str
    by: str
    at: str
    prompt_sha256: str


@dataclass(frozen=True, slots=True)
class ApprovalResult:
    status: str
    vocabulary_hits: tuple[str, ...]
    bound_to_prompt: bool
    evidence: ApprovalEvidence | None


@dataclass(frozen=True, slots=True)
class GateContext:
    prompt_sha256: str
    approval_words: tuple[str, ...]
    machine: dict[int, tuple[Finding, ...]]
    cost: CostSummary | None
    cuts_fresh: bool | Unknown


@dataclass(frozen=True, slots=True)
class ItemResult:
    line: ChecklistLine
    given: ItemInput | None
    machine: tuple[Finding, ...]
    human_required: tuple[str, ...]
    status: str
    problems: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GateResult:
    items: tuple[ItemResult, ...]
    checklist_complete: bool
    approval: ApprovalResult
    cost: CostSummary | None
    cuts_fresh: bool | Unknown
    label: str


def read_gate_rules(store: DocStore) -> GateRules:
    doc = store.load("W02")
    def extracted(name: str):
        key, headings, take, count = ANCHOR_SPECS[name]
        return resolve(doc, Anchor(key, (DOC_TITLES[key], *headings), take, count))
    lines = tuple(ChecklistLine(i, ext.text, ext.where) for i, ext in enumerate(extracted("checklist"), 1))
    if any(not line.text.startswith(f"{line.no}. ") for line in lines):
        raise InputError("W02 점검 번호 순서 변경")
    text = extracted("approval")[0].text
    words = tuple(word for pattern in APPROVAL_PATTERNS for match in re.finditer(pattern, text, re.MULTILINE) for word in match.groups())
    if not words:
        raise InputError("W02 승인 어휘 패턴 변경")
    key, headings, take, count = ANCHOR_SPECS["clip_limits"]
    limits = resolve(store.load(key), Anchor(key, (DOC_TITLES[key], *headings), take, count))[0]
    maximum = re.findall(r"한 클립 최대 (\d+(?:\.\d+)?)초", limits.text)
    if len(maximum) != 1:
        raise InputError("W05 생성 길이 상한 앵커 변경")
    return GateRules(lines, words, Decimal(maximum[0]))


def load_gate(path: Path):
    try:
        data = tomllib.loads(read_document(path, "gate").text)
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"점검 TOML 오류: {exc}") from exc
    inputs = []
    items = data.get("item", [])
    if not isinstance(items, list):
        raise InputError("점검 [[item]] 목록 필요")
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("no"), int) or isinstance(item.get("no"), bool):
            raise InputError("점검 no: 정수 필요")
        for field in ("answer", "reason", "alternative", "reviewer"):
            if not isinstance(item.get(field, ""), str):
                raise InputError(f"점검 {field}: 문자열 필요")
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(e, str) for e in evidence):
            raise InputError("점검 evidence: 문자열 목록 필요")
        inputs.append(ItemInput(item["no"], item.get("answer") or None, item.get("reason", ""), item.get("alternative", ""), tuple(evidence), item.get("reviewer", "")))
    approval = data.get("approval", {})
    if not isinstance(approval, dict) or any(not isinstance(v, str) for v in approval.values()):
        raise InputError("승인 증거: 문자열 필드 필요")
    proof = ApprovalEvidence(*(approval.get(key, "") for key in ("quote", "where", "by", "at", "prompt_sha256"))) if any(approval.values()) else None
    return tuple(inputs), proof


def evaluate_gate(lines, inputs, context: GateContext, approval: ApprovalEvidence | None) -> GateResult:
    if len(lines) != 8 or [line.no for line in lines] != list(range(1, 9)):
        raise InputError("점검 원문은 순서대로 8개 필요")
    if len({item.no for item in inputs}) != len(inputs) or any(item.no not in range(1, 9) for item in inputs):
        raise InputError("점검 입력 번호 중복/범위 오류")
    given = {item.no: item for item in inputs}
    results = []
    for line in lines:
        item = given.get(line.no)
        problems = []
        if item is None or item.answer in {None, "", "미확인"}:
            problems.append("응답 미입력/미확인")
        elif item.answer == "예":
            if not any(e.strip() for e in item.evidence):
                problems.append("근거 필요")
            if not item.reviewer.strip():
                problems.append("사람 검수 주체 필요")
        elif item.answer == "아니오":
            if not item.reason.strip() or not item.alternative.strip():
                problems.append("아니오: 이유와 대안 필요")
        elif item.answer == "해당 없음":
            if not item.reason.strip():
                problems.append("해당 없음: 이유 필요")
        else:
            problems.append("허용되지 않은 응답")
        machine = context.machine.get(line.no, ())
        status = "기계 소견과 충돌" if any(f.severity == Severity.ERROR for f in machine) else "미완료" if problems else "완료"
        results.append(ItemResult(line, item, machine, ("사람의 항목별 판단과 근거",), status, tuple(problems)))
    bound = approval is not None and approval.prompt_sha256 == context.prompt_sha256
    hits = tuple(word for word in context.approval_words if approval is not None and word in approval.quote)
    approval_status = "승인 기록 없음"
    if approval is not None:
        approval_status = "승인 기록 있음" if all((approval.quote, approval.where, approval.by, approval.at, approval.prompt_sha256)) and bound and hits else "승인 기록 불일치" if not bound else "어휘 불명확"
    complete = all(item.status == "완료" for item in results)
    label = "[점검 미완료]" if not complete else "[점검 완료·승인 기록 있음]" if approval_status == "승인 기록 있음" else "[점검 완료·승인 기록 없음]"
    return GateResult(tuple(results), complete, ApprovalResult(approval_status, hits, bound, approval), context.cost, context.cuts_fresh, label)


def machine_findings(plan, cuts, check, refs, current_f_sha: str | None, prompt_sha: str, *, max_seconds: Decimal | None = None):
    machine: dict[int, list[Finding]] = {i: [] for i in range(1, 9)}
    def add(no: int, code: str, severity: Severity, message: str) -> None:
        machine[no].append(Finding(code, severity, message))
    fresh = Unknown("컷표 지문 미확인")
    if cuts is not None and current_f_sha is not None:
        fresh = cuts.get("source", {}).get("sha256") == current_f_sha
        if not fresh:
            add(4, "GATE_STALE", Severity.ERROR, "cuts.json과 현재 F 지문 다름")
    if plan is None:
        add(1, "GATE_PLAN", Severity.WARN, "계획 미입력")
    else:
        if isinstance(plan.mode, Unknown):
            add(1, "GATE_MODE", Severity.ERROR, "생성/edit/코드 모드 미입력")
        if len(plan.references) >= 6:
            add(2, "GATE_SPLIT", Severity.WARN, "레퍼런스 6장 이상: 분할 검토")
        if max_seconds is not None and isinstance(plan.gen_seconds, Decimal) and plan.mode == "new" and plan.gen_seconds > max_seconds:
            add(2, "GATE_DURATION", Severity.ERROR, f"문서의 한 클립 상한 {max_seconds}초 초과. 분할 필요")
        if any(r.sheet != "있음" for r in plan.references):
            add(3, "GATE_SHEET", Severity.ERROR, "시트 없음/만들어야 함")
        if not isinstance(plan.props, Unknown) and any(not any(prop in r.role and r.sheet == "있음" for r in plan.references) for prop in plan.props):
            add(3, "GATE_PROP", Severity.ERROR, "중요 소품 시트 역할 대응 없음")
        if cuts is not None:
            selected = [r for r in cuts.get("targets", []) if r.get("cut_id") in plan.cuts]
            if set(plan.cuts) - {r.get("cut_id") for r in selected} or any(r.get("excluded_from_generation") for r in selected):
                add(4, "GATE_REMOVED", Severity.ERROR, "대상에 없는 컷 또는 removed 컷 포함")
            if [r.get("cut_id") for r in selected] != list(plan.cuts):
                add(5, "GATE_ORDER", Severity.ERROR, "계획과 원문 컷 순서 다름")
    if cuts is None:
        add(4, "GATE_CUTS", Severity.WARN, "컷표 추출 결과 없음")
    if cuts is None or not cuts.get("context"):
        add(6, "GATE_CONTEXT", Severity.WARN, "연결 문맥 미확인")
    else:
        for c in cuts["context"]:
            if c.get("role") in SCENE_NEIGHBOR_ROLES and c.get("row") is None and c.get("note") != FIRST_SCENE_NO_PREV:
                add(6, "GATE_CONTEXT", Severity.WARN, f"연결 문맥 미확인: {c.get('role')} ({c.get('note')})")
    if refs is None:
        add(7, "GATE_REFS", Severity.WARN, "레퍼런스 검사 결과 없음")
    else:
        results = refs.get("results", [])
        if not results or any(r.get("best_original") != "최대 원본 확인됨" for r in results):
            add(7, "GATE_ORIGINAL", Severity.WARN, "최대 원본 미확인")
        for finding in refs.get("findings", []):
            if finding.get("severity") != Severity.INFO:
                add(7, finding.get("code", "GATE_REFS"), Severity(finding.get("severity", "warn")), finding.get("message", "미확인"))
    if check is None:
        add(4, "GATE_CHECK", Severity.WARN, "프롬프트 검사 결과 없음")
    else:
        if check.get("prompt_sha256") != prompt_sha:
            add(4, "GATE_PROMPT_STALE", Severity.ERROR, "검사 결과와 현재 프롬프트 지문 다름")
        for finding in check.get("result", {}).get("findings", []):
            no = 7 if finding.get("code") == "PR004" else 8 if finding.get("code") == "PR005" else 4
            add(no, finding.get("code", "GATE_CHECK"), Severity(finding.get("severity", "warn")), finding.get("message", "미확인"))
    return {no: tuple(items) for no, items in machine.items()}, fresh


def gate_md(result: GateResult, prompt: str) -> str:
    lines = [f"# {result.label} 점검 게이트", ""]
    for item in result.items:
        lines += [item.line.text, f"   응답: {item.given.answer if item.given else '미입력'} / {item.status}",
                  "   근거·주체·기계 소견: " + json_text(item).replace("\n", " ")]
    fence = "`" * max(3, max((len(m[0]) + 1 for m in re.finditer(r"`+", prompt)), default=3))
    lines += ["", fence + "text", prompt, fence, "", "## 비용", json_text(result.cost), "## 승인 상태", json_text(result.approval),
              "## 내가 정한 것", "기계 통과로 사람 응답을 채우지 않음. 최종 승인 판단은 사람.", "", "## 사용자 답이 필요한 것", "미입력·미완료 항목과 승인 증거 확인.", "", "## 근거", "각 점검 항목의 문서·행·발췌 지문 및 비용표 지문 참조."]
    return "\n".join(lines) + "\n"
