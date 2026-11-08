"""문서 단가로만 Decimal 계산한다. 대안과 요청안은 합산하지 않는다."""
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING

from ..docs import Anchor, DocStore, resolve
from ..errors import InputError
from ..model import DocFingerprint, Finding, Severity, SourceRef, Unknown
from ..profile_plating import ANCHOR_SPECS, DOC_TITLES, RATE_EDIT_PATTERN, RATE_NEW_PATTERN
from ..prompt.plan import ClipPlan
from ..textio import Document


@dataclass(frozen=True, slots=True)
class Rate:
    model: str
    mode: str
    resolution: str
    per_second: Decimal
    min_seconds: Decimal | None
    billing: str
    unit: str
    where: SourceRef


@dataclass(frozen=True, slots=True)
class CostTable:
    rates: tuple[Rate, ...]
    topaz_rate: Decimal
    topaz_per: Unknown
    topaz_basis: SourceRef
    doc_versions: tuple[DocFingerprint, ...]


@dataclass(frozen=True, slots=True)
class CostLine:
    label: str
    amount: Decimal | Unknown
    unit: str
    formula: str
    inputs: dict[str, str]
    where: SourceRef | None


@dataclass(frozen=True, slots=True)
class CostSummary:
    lines: tuple[CostLine, ...]
    totals: dict[str, Decimal]
    doc_versions: tuple[DocFingerprint, ...]
    not_checked: tuple[str, ...]
    findings: tuple[Finding, ...]


def section(doc: Document, name: str):
    key, headings, take, count = ANCHOR_SPECS[name]
    return resolve(doc, Anchor(key, (DOC_TITLES[key], *headings), take, count))[0]


def parse_rates(doc: Document) -> tuple[Rate, ...]:
    extracted = section(doc, "cost")
    unit = re.search(r"\((\w+) / 크레딧\)", extracted.where.heading_path[-1])
    if unit is None or unit[1] != "Crons":
        raise InputError("W07 비용 단위 변경")
    new = list(re.finditer(RATE_NEW_PATTERN, extracted.text, re.MULTILINE))
    edit = list(re.finditer(RATE_EDIT_PATTERN, extracted.text, re.MULTILINE))
    if len(new) != 1 or len(edit) != 1:
        raise InputError(f"W07:{extracted.where.line_start} 비용 행 패턴 불일치")
    rates = []
    for match, mode in ((new[0], "new"), (edit[0], "edit")):
        line = extracted.where.line_start + extracted.text.count("\n", 0, match.start())
        where = doc.ref(line, line, extracted.where.heading_path)
        from dataclasses import replace
        where = replace(where, mark=extracted.where.mark, mark_reason=extracted.where.mark_reason)
        if mode == "new":
            for resolution, rate in ((match["low"], match["low_rate"]), (match["high"], match["high_rate"])):
                rates.append(Rate(match["model"], mode, resolution, Decimal(rate), Decimal(match["minimum"]), "seconds_as_given", unit[1], where))
        else:
            rates.append(Rate(match["model"], mode, match["resolution"], Decimal(match["rate"]), None, "ceil_input_seconds", unit[1], where))
    return tuple(rates)


def read_cost_table(store: DocStore) -> CostTable:
    w07, w06 = store.load("W07"), store.load("W06")
    rates = parse_rates(w07)
    billing = section(w06, "edit_billing")
    if "입력 길이 기준, 초 단위로 올림" not in billing.text:
        raise InputError(f"W06:{billing.where.line_start} edit 과금 근거 변경")
    topaz = section(w06, "topaz")
    match = re.search(r"1K와 2K는 같은 (\d+(?:\.\d+)?)크레딧", topaz.text)
    if match is None:
        raise InputError(f"W06:{topaz.where.line_start} Topaz 단가 형식 변경")
    return CostTable(rates, Decimal(match[1]), Unknown("Topaz 적용 단위 미확인"), topaz.where, (w07.fingerprint, w06.fingerprint))


def cost_for(clip: ClipPlan, table: CostTable) -> CostSummary:
    matching = [r for r in table.rates if (r.model, r.mode, r.resolution) == (clip.model, clip.mode, clip.resolution)]
    findings = [Finding("DOC_CHANGED", Severity.WARN, f"작성 기준 지문 변경: {doc.key}") for doc in table.doc_versions
                if doc.changed_since_authored]
    requested = CostLine("요청안", Unknown("문서에 없음"), "Crons", "미확인", {"model": str(clip.model), "mode": str(clip.mode), "resolution": str(clip.resolution)}, None)
    seconds = clip.edit_input_seconds if clip.mode == "edit" else clip.gen_seconds
    if matching and isinstance(seconds, Decimal):
        rate = matching[0]
        if clip.mode == "new" and (seconds != seconds.to_integral_value() or seconds < rate.min_seconds):
            requested = CostLine("요청안", Unknown("정수 초 필요/최소 길이 의미 미확인"), rate.unit, "계산 보류", requested.inputs, rate.where)
        else:
            billed = seconds.to_integral_value(rounding=ROUND_CEILING) if rate.billing == "ceil_input_seconds" else seconds
            amount = billed * rate.per_second
            expression = f"ceil({seconds})" if rate.billing == "ceil_input_seconds" else str(seconds)
            requested = CostLine("요청안", amount, rate.unit, f"{expression} × {rate.per_second} = {amount}", {**requested.inputs, "seconds": str(seconds)}, rate.where)
    lines = [requested]
    if isinstance(requested.amount, Unknown):
        findings.append(Finding("COST_UNKNOWN", Severity.ERROR, requested.amount.unknown))
    elif clip.mode == "new":
        alternatives = [r for r in table.rates if r.model == clip.model and r.mode == "new" and r.resolution != clip.resolution and r.per_second < matching[0].per_second]
        if alternatives:
            rate = min(alternatives, key=lambda r: r.per_second)
            amount = seconds * rate.per_second
            lines.append(CostLine(f"대안: {rate.resolution} 새 생성", amount, rate.unit, f"{seconds} × {rate.per_second} = {amount}", {"model": rate.model, "resolution": rate.resolution}, rate.where))
            lines.append(CostLine("대안: Topaz 업스케일", table.topaz_per, "Higgsfield 크레딧", f"문서 단가 {table.topaz_rate}, 적용 단위 미확인", {}, table.topaz_basis))
            findings.append(Finding("COST_TOPAZ_UNIT", Severity.WARN, "Topaz 단위 미확인. Crons와 합산하지 않음", table.topaz_basis))
    totals = {requested.unit: requested.amount} if isinstance(requested.amount, Decimal) else {}
    return CostSummary(tuple(lines), totals, table.doc_versions, ("실제 잔여 Crons", "결제 가능 여부", "현재 서비스 요금", "Topaz 적용 단위"), tuple(findings))
