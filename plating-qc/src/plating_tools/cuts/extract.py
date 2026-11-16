"""씬·표 선택과 대상/문맥 분리. 색 상태와 원문을 고치지 않는다."""
import re
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal

from ..errors import InputError
from ..model import DocFingerprint, Finding, Severity, SourceRef, Unknown
from ..profile_plating import COLUMNS, COLOR_NOTES, COLOR_STATES, CUT_PATTERN
from .sections import SceneSection, parse_sections
from .source import CutTableSource
from .table import Cell, ColorMark, HtmlDocument, ParsedTable, color


@dataclass(frozen=True, slots=True)
class FieldValue:
    kind: str
    cell: Cell | None


@dataclass(frozen=True, slots=True)
class TcValue:
    raw: str
    start_s: Decimal | Unknown
    end_s: Decimal | Unknown
    form: str | None
    minute_inherited: bool = False


@dataclass(frozen=True, slots=True)
class LengthValue:
    raw: str
    seconds: Decimal | Unknown


@dataclass(frozen=True, slots=True)
class CutRow:
    order: int
    cut_id: str | Unknown
    row_color: ColorMark | None
    row_state: str
    fields: dict[str, FieldValue]
    extra: tuple[Cell, ...]
    tc: TcValue
    length: LengthValue
    excluded_from_generation: bool
    where: SourceRef
    original_cut_id: str = ""


FIRST_SCENE_NO_PREV = "첫 씬이라 없음"
SCENE_NEIGHBOR_ROLES = ("prev_scene_last", "next_scene_first")


@dataclass(frozen=True, slots=True)
class ContextCut:
    role: str
    row: CutRow | None
    note: str


@dataclass(frozen=True, slots=True)
class SceneExtract:
    source: DocFingerprint
    scene_id: str
    selected: dict
    rejected: tuple[dict, ...]
    header_map: tuple[tuple[str, str], ...]
    targets: tuple[CutRow, ...]
    context: tuple[ContextCut, ...]
    findings: tuple[Finding, ...]


def section_summary(section: SceneSection):
    return {"title_raw": section.title_raw, "title_text": section.title_text, "container": section.container,
            "is_revision": section.is_revision, "where": section.where, "title_colors": section.title_colors,
            "title_annotations": section.title_annotations, "notes": section.notes,
            "tables": [{"line_start": t.line_start, "line_end": t.line_end, "header": t.header,
                        "is_cut_table": t.is_cut_table, "nested": t.nested} for t in section.tables]}


def choose_section(sections: list[SceneSection], scene: str, line: int | None) -> SceneSection:
    choices = [s for s in sections if s.scene_id == scene]
    revisions = [s for s in choices if s.is_revision]
    selected = [s for s in choices if s.where.line_start == line] if line is not None else (revisions or choices)
    if len(selected) != 1:
        code = "CT002" if choices else "CT001"
        raise InputError(f"{code} {scene} 섹션 선택 불가: {[(s.where.line_start, s.title_text) for s in choices]}")
    return selected[0]


def choose_table(section: SceneSection, line: int | None) -> ParsedTable:
    tables = [t for t in section.tables if t.is_cut_table and not t.nested and (line is None or t.line_start == line)]
    if len(tables) != 1:
        if section.tables and not any(t.header for t in section.tables):
            raise InputError(f"CT012 머리 행 없음: F:{section.where.line_start}")
        raise InputError(f"CT003 컷표 선택 불가: {section.title_text}, 후보 {[(t.line_start, t.header) for t in section.tables]}")
    return tables[0]


def parse_tc(raw: str, previous_end: Decimal | None = None) -> TcValue:
    """생략한 분은 명시된 시작 분 또는 같은 표의 마지막 성공 TC 끝에서 얻는다."""
    match = re.fullmatch(r"(?:(\d+):)?([0-5]\d(?:\.\d+)?)–(?:(\d+):)?([0-5]\d(?:\.\d+)?)", raw)
    if match:
        if match[1] is not None:
            minute = Decimal(match[1])
        elif previous_end is not None and match[3] is None:
            minute = previous_end // 60
        else:
            return TcValue(raw, Unknown("TC 해석 실패"), Unknown("TC 해석 실패"), None)
        start = minute * 60 + Decimal(match[2])
        end = (Decimal(match[3]) if match[3] is not None else minute) * 60 + Decimal(match[4])
        inherited = match[3] is None
        if end >= start:
            form = "mm:ss–mm:ss"
            if inherited:
                form = "mm:ss.f–ss.f" if match[1] is not None else "ss.f–ss.f"
            return TcValue(raw, start, end, form, inherited)
    return TcValue(raw, Unknown("TC 해석 실패"), Unknown("TC 해석 실패"), None)


def parse_rows(src: CutTableSource, section: SceneSection, table: ParsedTable):
    findings: list[Finding] = []
    rows: list[CutRow] = []
    previous_end: Decimal | None = None
    def finding(code: str, message: str, where: SourceRef = section.where) -> None:
        findings.append(Finding(code, Severity.WARN, message, where))
    if not table.header_row_present:
        findings.append(Finding("CT018", Severity.INFO, "header-row 속성 없음: 머리 내용으로 컷표 판정",
                                src.document.ref(table.line_start, table.line_end, (section.title_text,))))
    if len(set(table.header)) != len(table.header):
        finding("CT004", "열 이름 중복")
    for name in table.header:
        if name not in COLUMNS:
            finding("CT010", f"모르는 열: {name}")
    for nested in section.tables:
        if nested.nested:
            finding("CT015", f"중첩 표 제외: F:{nested.line_start}")
    excerpt = "\n".join(src.lines()[section.where.line_start - 1:section.where.line_end])
    if len(re.findall(r'\bcolor\s*=\s*["\']', excerpt)) != len(HtmlDocument(excerpt).colors()):
        finding("CT008", "선택 섹션 색 유실")
    for order, (node, cells) in enumerate(table.rows):
        end = src.document.text.count("\n", 0, node.stop) + 1
        where = src.document.ref(node.line, end, (section.title_text,))
        if len(cells) != len(table.header):
            finding("CT004", f"셀 수 {len(cells)} != 열 수 {len(table.header)}", where)
        fields = {field: FieldValue("absent", None) for field in COLUMNS.values()}
        mark = color(node) if "color" in dict(node.attrs) else None
        for cell in cells:
            if cell.field != "extra":
                fields[cell.field] = FieldValue("present" if cell.text else "empty", cell)
        marks = [(cell.column_raw, c) for cell in cells for c in cell.colors]
        if mark is not None:
            marks.append(("행", mark))
        for label, cell_mark in marks:
            if cell_mark.raw in COLOR_NOTES:
                if cell_mark.element in {"row", "cell"}:
                    findings.append(Finding("CT020", Severity.INFO,
                                            f"{COLOR_NOTES[cell_mark.raw]}: {label}", where))
            elif cell_mark.raw not in COLOR_STATES:
                note = "; 범례에 없음, 사용자 확인 필요" if cell_mark.raw == "orange_bg" else ""
                finding("CT009", f"미정의 색: {cell_mark.raw}{note}", where)
        def value(field: str) -> str:
            cell = fields[field].cell
            return cell.text if cell is not None else ""
        cut = value("cut_id")
        original_cut_id = ""
        if original := re.search(r"\s*\((S#\d{2}-C\d{3})\)$", cut):
            original_cut_id = original[1]
            cut = cut[:original.start()]
        if "~" in cut:
            finding("CT013", f"요약 표기 ID: {cut}", where)
        elif not re.fullmatch(CUT_PATTERN, cut):
            finding("CT011", f"컷 ID 형식 미확인: {cut}", where)
        cut_scene = re.match(r"(S#|RS#?)(\d{2})", cut)
        if cut_scene and f"{cut_scene[1].removesuffix('#')}#{cut_scene[2]}" != section.scene_id:
            finding("CT017", f"씬 ID 불일치: {cut}", where)
        state = mark.state if mark is not None else "unknown"
        tc = parse_tc(value("tc"), previous_end)
        if tc.form is not None:
            if previous_end is not None and tc.start_s < previous_end:
                finding("CT019", f"TC 순서 역행: {tc.raw} < 직전 끝 {previous_end}", where)
            previous_end = tc.end_s
        raw_length = value("length")
        seconds = Decimal(raw_length[:-1]) if re.fullmatch(r"\d+(?:\.\d+)?s", raw_length) else Unknown("길이 해석 실패")
        length = LengthValue(raw_length, seconds)
        if tc.form is None:
            finding("CT006", f"TC 해석 실패: {tc.raw}", where)
        if isinstance(seconds, Unknown):
            finding("CT007", f"길이 해석 실패: {raw_length}", where)
        elif tc.form is not None and tc.end_s - tc.start_s != seconds:
            finding("CT014", f"TC·길이 불일치: {tc.raw} / {raw_length}", where)
        rows.append(CutRow(order, cut or Unknown("컷 ID 빈 값"), mark, state, fields,
                           tuple(c for c in cells if c.field == "extra"), tc, length, state == "removed", where,
                           original_cut_id=original_cut_id))
    for cut, count in Counter(r.cut_id for r in rows if isinstance(r.cut_id, str)).items():
        if count > 1:
            finding("CT005", f"중복 컷 ID: {cut} ({count})")
    return tuple(rows), findings


def extract_scene(src: CutTableSource, scene_id: str, *, cut_ids: tuple[str, ...] | None = None,
                  section_line: int | None = None, table_line: int | None = None) -> SceneExtract:
    if not re.fullmatch(r"(?:(?:S|RS)#)?\d{2}", scene_id):
        raise InputError(f"씬 ID 형식 오류: {scene_id}")
    scene = scene_id if "#" in scene_id else "S#" + scene_id
    if cut_ids and any("~" in cut for cut in cut_ids):
        raise InputError("CT013 요약 ID는 단일 컷으로 지정할 수 없음")
    sections = parse_sections(src)
    selected = choose_section(sections, scene, section_line)
    table = choose_table(selected, table_line)
    rows, findings = parse_rows(src, selected, table)
    targets = tuple(r for r in rows if cut_ids is None or r.cut_id in cut_ids)
    if cut_ids and set(cut_ids) - {r.cut_id for r in targets if isinstance(r.cut_id, str)}:
        raise InputError(f"지정 컷 ID 없음: {cut_ids}")
    context: list[ContextCut] = []
    prefix, digits = scene.split("#")
    number = int(digits)
    for delta, role in zip((-1, 1), SCENE_NEIGHBOR_ROLES):
        neighbor = f"{prefix}#{number + delta:02d}"
        try:
            neighbor_section = choose_section(sections, neighbor, None)
            neighbor_table = choose_table(neighbor_section, None)
            candidates, _ = parse_rows(src, neighbor_section, neighbor_table)
        except InputError as exc:
            context.append(ContextCut(role, None, FIRST_SCENE_NO_PREV if number == 1 and delta == -1 else str(exc)))
            continue
        if not candidates:
            context.append(ContextCut(role, None, f"{neighbor} 표에 데이터 행 없음"))
            continue
        chosen = candidates[-1] if delta == -1 else candidates[0]
        context.append(ContextCut(role, chosen, "생성 대상 아님"))
        if chosen.excluded_from_generation:
            remaining = [r for r in candidates if not r.excluded_from_generation]
            if remaining:
                context.append(ContextCut(role, remaining[-1] if delta == -1 else remaining[0], "경계 행 removed. 인접 비제거 행 추가"))
    if cut_ids and targets:
        for offset, role in ((targets[0].order - 1, "prev_in_scene"), (targets[-1].order + 1, "next_in_scene")):
            context.append(ContextCut(role, rows[offset] if 0 <= offset < len(rows) else None, "같은 씬 인접 행"))
    rejected = tuple({"where": s.where, "title": s.title_text, "reason": "다른 후보 선택"} for s in sections if s.scene_id == scene and s is not selected)
    return SceneExtract(src.fingerprint(), scene, section_summary(selected), rejected,
                        tuple((name, COLUMNS.get(name, "extra")) for name in table.header), targets, tuple(context), tuple(findings))
