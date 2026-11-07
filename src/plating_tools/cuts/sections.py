"""최상위 h3 토글과 Markdown h3 경계를 독립적으로 판독한다."""
import re
import unicodedata
from dataclasses import dataclass

from ..model import SourceRef
from ..profile_plating import SCENE_PATTERN
from .source import CutTableSource
from .table import Annotation, ColorMark, HtmlDocument, ParsedTable, comparison, parse_table, plain


@dataclass(frozen=True, slots=True)
class SceneSection:
    scene_id: str | None
    title_raw: str
    title_text: str
    container: str
    is_revision: bool
    title_colors: tuple[ColorMark, ...]
    title_annotations: tuple[Annotation, ...]
    tables: tuple[ParsedTable, ...]
    notes: tuple[SourceRef, ...]
    where: SourceRef


def parse_sections(src: CutTableSource) -> list[SceneSection]:
    doc = src.document
    html = HtmlDocument(doc.text)
    toggles = [n for n in html.nodes if n.tag == "toggle" and not any(html.nodes[a].tag == "toggle" for a in n.ancestors)]
    headings = [(i + 1, m.group(1), m.group(2)) for i, line in enumerate(doc.lines)
                if (m := re.match(r"^(#{1,3}) (.*)$", line))
                and not any(n.line <= i + 1 <= doc.text.count("\n", 0, n.stop) + 1 for n in toggles)]
    bounds = sorted([n.line for n in toggles if dict(n.attrs).get("heading") in {"h1", "h2", "h3"}] + [line for line, _, _ in headings])
    candidates = []
    for node in toggles:
        if dict(node.attrs).get("heading") != "h3":
            continue
        title_line = next((i + 1 for i in range(node.line, len(doc.lines)) if doc.lines[i].strip()), None)
        if title_line is None:
            continue
        candidates.append((node.line, doc.text.count("\n", 0, node.stop) + 1, title_line, doc.lines[title_line - 1], "toggle_h3", node))
    for line, level, raw in headings:
        if level != "###":
            continue
        end = next((b - 1 for b in bounds if b > line), len(doc.lines))
        candidates.append((line, end, line, raw, "md_h3", None))
    result = []
    for start, end, title_line, raw, container, toggle in sorted(candidates, key=lambda c: c[0]):
        title = unicodedata.normalize("NFC", comparison(raw))
        match = re.match(SCENE_PATTERN, title)
        scene = f"S#{match[1]}" if match else None
        tables = []
        for node in html.nodes:
            if node.tag != "table" or not start <= node.line <= end:
                continue
            nested = any(html.nodes[a].tag in {"toggle", "table"} and html.nodes[a] is not toggle for a in node.ancestors)
            nested = nested or any(re.match(r"^#{4,6} ", line) for line in doc.lines[title_line:node.line - 1])
            tables.append(parse_table(html, node, nested))
        title_nodes = [n for n in html.nodes if n.line == title_line]
        title_colors = tuple(c for c in html.colors() if c.line == title_line)
        annotations = tuple(Annotation(n.tag, n.attrs, plain(html.raw(n)), n.line, n.col) for n in title_nodes if any(k != "color" for k, _ in n.attrs))
        notes = tuple(doc.ref(i, i) for i in range(title_line + 1, end + 1) if doc.lines[i - 1].strip() and not doc.lines[i - 1].strip().startswith("<") and not any(t.line_start <= i <= t.line_end for t in tables))
        result.append(SceneSection(scene, raw, comparison(raw), container, title == f"{scene} 수정", title_colors, annotations, tuple(tables), notes, doc.ref(start, end, (comparison(raw),))))
    return result
