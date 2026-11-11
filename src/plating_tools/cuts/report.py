"""컷표 관찰 결과. 실제 원문은 출력 폴더에만 남긴다."""
import re
import csv
import io
from collections import Counter, defaultdict

from ..model import json_text
from ..profile_plating import COLOR_LEGEND_SOURCE, COLUMNS
from .sections import parse_sections
from .source import CutTableSource
from .table import HtmlDocument


def inventory(src: CutTableSource):
    html = HtmlDocument(src.document.text)
    sections = parse_sections(src)
    counts = defaultdict(Counter)
    for node in html.nodes:
        attrs = dict(node.attrs)
        if "color" in attrs:
            counts[node.tag][attrs["color"]] += 1
    raw_count = len(re.findall(r'\bcolor\s*=\s*["\']', src.document.text))
    return {
        "source": src.fingerprint(), "newline": src.document.newline,
        "metadata": {"fetch": src.lines()[0], "properties": next((line for line in src.lines()[:12] if '"title"' in line), None)},
        "sections": [{"scene_id": s.scene_id, "title": s.title_text, "container": s.container, "revision": s.is_revision,
                      "line_start": s.where.line_start, "line_end": s.where.line_end,
                      "tables": [{"line_start": t.line_start, "line_end": t.line_end, "header": t.header, "cut_table": t.is_cut_table, "nested": t.nested, "rows": len(t.rows)} for t in s.tables]} for s in sections],
        "colors": dict(counts), "color_loss": raw_count - sum(sum(c.values()) for c in counts.values()),
        "span_attributes": [{"tag": n.tag, "attrs": n.attrs, "line": n.line} for n in html.nodes if any(k in {"rowspan", "colspan"} for k, _ in n.attrs)],
        "headers": sorted({t.header for s in sections for t in s.tables}),
    }


def inventory_md(result) -> str:
    return "# [검수 대기] 컷표 inventory\n\n```json\n" + json_text(result) + "```\n\n## 내가 정한 것\n문법과 위치만 집계.\n\n## 사용자 답이 필요한 것\n집계 결과 검수.\n\n## 근거\nF 지문과 각 섹션의 행 범위는 위 JSON 참조.\n"


def cuts_md(result) -> str:
    def escape(text: str) -> str:
        return text.replace("|", "\\|").replace("\n", "<br>")
    lines = [f"# [검수 대기] {result.scene_id} 컷표 추출", "", "| 순서 | 컷 | 행 상태 | 행 색 | 셀·span 색 | TC | 길이 | 원문 필드 | 비고 |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in result.targets:
        marks = "; ".join(f"{name}: {c.raw} → {c.state}" for name, value in row.fields.items() if value.cell for c in value.cell.colors)
        fields = "; ".join(f"{name}: {value.cell.text}" for name, value in row.fields.items() if value.cell)
        remarks = row.fields["remarks"].cell
        lines.append(f"| {row.order} | {row.cut_id} | {row.row_state} | {row.row_color.raw if row.row_color else ''} | {escape(marks)} | {row.tc.raw} | {row.length.raw} | {escape(fields)} | {escape(remarks.text) if remarks else ''} |")
    lines += ["", "## 연결 문맥(생성 대상 아님)"]
    lines += [f"- {c.role}: {c.row.cut_id if c.row else '없음'} — {c.note}" for c in result.context]
    lines += ["", "## 제외 후보", json_text(result.rejected), "## 소견"]
    lines += [f"- {f.code}: {f.message}" for f in result.findings]
    lines += ["", "## 내가 정한 것", "씬 번호 ±1을 연결 문맥으로 사용. 원문 순서 유지.", "", "## 사용자 답이 필요한 것", "대상 범위와 연결 문맥 검수.", "", "## 근거", f"F SHA-256: {result.source.sha256}", f"F:{result.selected['where'].line_start}~{result.selected['where'].line_end}. 색은 {COLOR_LEGEND_SOURCE} 및 사용자 확정 규칙(2026-11-07)."]
    return "\n".join(lines) + "\n"


def cuts_csv(result) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["order", "cut", "row_state", *COLUMNS.values()])
    for row in result.targets:
        writer.writerow([row.order, row.cut_id, row.row_state, *(v.cell.text if v.cell else "" for v in row.fields.values())])
    return stream.getvalue()
