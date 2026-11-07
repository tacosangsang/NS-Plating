"""Notion HTML 부분 문법. 위치·속성과 셀 내부 원문을 보존한다."""
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser

from ..errors import InputError
from ..profile_plating import COLOR_STATES, COLUMNS


@dataclass(frozen=True, slots=True)
class ColorMark:
    element: str
    raw: str
    state: str
    rule: str
    line: int
    col: int


@dataclass(frozen=True, slots=True)
class Annotation:
    tag: str
    attrs: tuple[tuple[str, str | None], ...]
    text: str
    line: int
    col: int


class Node:
    """HTMLParser가 여닫는 동안 위치와 자식을 누적하는 내부 노드."""
    def __init__(self, tag: str, attrs, start: int, inner: int, position: tuple[int, int], ancestors: tuple[int, ...]):
        self.tag = tag
        self.attrs = tuple(attrs)
        self.start = start
        self.inner = inner
        self.end = inner
        self.stop = inner
        self.line, self.col = position
        self.ancestors = ancestors


class HtmlDocument(HTMLParser):
    """전체 문서를 한 번 읽으며 HTML 위치를 누적한다. 실행 기능 없음."""
    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.offsets = [0]
        for match in re.finditer("\n", text):
            self.offsets.append(match.end())
        self.nodes: list[Node] = []
        self.stack: list[int] = []
        self.feed(text)
        self.close()
        unclosed = [self.nodes[i] for i in self.stack if self.nodes[i].tag in {"toggle", "table", "tr", "td"}]
        if unclosed:
            raise InputError(f"CT004 미종결 {unclosed[0].tag}: F:{unclosed[0].line}")

    def absolute_offset(self) -> int:
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.absolute_offset()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()), self.getpos(), tuple(self.stack))
        self.nodes.append(node)
        if tag not in {"br", "col", "hr", "img", "meta", "link", "input"}:
            self.stack.append(len(self.nodes) - 1)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.nodes[self.stack[-1]].start == self.absolute_offset():
            self.stack.pop()

    def handle_endtag(self, tag):
        matches = [n for n, index in enumerate(self.stack) if self.nodes[index].tag == tag]
        if not matches:
            if tag in {"toggle", "table", "tr", "td"}:
                raise InputError(f"CT004 여는 태그 없는 {tag}: F:{self.getpos()[0]}")
            return
        position = matches[-1]
        dangling = [self.nodes[i].tag for i in self.stack[position + 1:] if self.nodes[i].tag in {"table", "tr", "td", "toggle"}]
        if dangling:
            raise InputError(f"CT004 잘못 닫힌 {tag}: F:{self.getpos()[0]}, {dangling}")
        node = self.nodes[self.stack[position]]
        node.end = self.absolute_offset()
        node.stop = self.text.find(">", node.end) + 1
        del self.stack[position:]

    def raw(self, node: Node) -> str:
        return self.text[node.inner:node.end]

    def colors(self, start: int = 0, end: int | None = None) -> tuple[ColorMark, ...]:
        return tuple(color(node) for node in self.nodes if start <= node.start < (end if end is not None else len(self.text)) and "color" in dict(node.attrs))


def color(node: Node) -> ColorMark:
    raw = dict(node.attrs)["color"] or ""
    element = {"tr": "row", "td": "cell", "span": "span"}.get(node.tag, "other")
    state = COLOR_STATES.get(raw, "unknown") if element != "other" else "unknown"
    return ColorMark(element, raw, state, "사용자 확정 2026-11-07" if state != "unknown" else "미정의 색/요소", node.line, node.col)


class InlineText(HTMLParser):
    """태그를 제외한 문자를 연결하고 br만 줄바꿈으로 바꾼다."""
    def __init__(self, raw: str):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.feed(raw)

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.parts.append("\n")


def plain(raw: str) -> str:
    return "".join(InlineText(raw).parts).strip()


def comparison(raw: str) -> str:
    return " ".join(plain(raw).split())


@dataclass(frozen=True, slots=True)
class Cell:
    column_raw: str
    field: str
    raw_html: str
    text: str
    colors: tuple[ColorMark, ...]
    annotations: tuple[Annotation, ...]
    line: int


@dataclass(frozen=True, slots=True)
class ParsedTable:
    line_start: int
    line_end: int
    header: tuple[str, ...]
    is_cut_table: bool
    nested: bool
    rows: tuple[tuple[Node, tuple[Cell, ...]], ...]


def parse_table(html: HtmlDocument, node: Node, nested: bool) -> ParsedTable:
    index = html.nodes.index(node)
    rows = [n for n in html.nodes if n.tag == "tr" and n.ancestors and n.ancestors[-1] == index]
    result = []
    header: tuple[str, ...] = ()
    for order, row in enumerate(rows):
        row_index = html.nodes.index(row)
        cells = [n for n in html.nodes if n.tag in {"td", "th"} and n.ancestors and n.ancestors[-1] == row_index]
        if order == 0:
            header = tuple(comparison(html.raw(cell)) for cell in cells)
        parsed = []
        for col, cell in enumerate(cells):
            descendants = [n for n in html.nodes if cell.start <= n.start < cell.stop]
            annotations = tuple(Annotation(n.tag, n.attrs, plain(html.raw(n)), n.line, n.col) for n in descendants if any(k not in {"color"} for k, _ in n.attrs))
            name = header[col] if col < len(header) else ""
            parsed.append(Cell(name, COLUMNS.get(name, "extra"), html.raw(cell), plain(html.raw(cell)), html.colors(cell.start, cell.stop), annotations, cell.line))
        result.append((row, tuple(parsed)))
    return ParsedTable(node.line, html.text.count("\n", 0, node.stop) + 1, header,
                       bool(dict(node.attrs).get("header-row") == "true" and header and header[0] == "컷" and "TC" in header), nested, tuple(result[1:]))
