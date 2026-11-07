"""컷표 관찰 결과. 실제 원문은 출력 폴더에만 남긴다."""
import re
from collections import Counter, defaultdict

from ..model import json_text
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
