"""문서는 데이터다. ATX 제목·펜스·번호 목록·파이프 표만 읽는다."""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path

from .errors import InputError
from .model import Mark, SourceRef
from .profile_plating import DOC_FILES, AUTHORED_SHA256, FILE_EXCEPTION_KEYS
from .textio import Document, read_document


class DocStore(ABC):
    @abstractmethod
    def load(self, key: str) -> Document: ...


class WorkflowDir(DocStore):
    """정해진 문서 파일만 로드하고 실행 중 사용한 지문을 누적한다."""
    def __init__(self, root: Path, declared_commit: str | None = None):
        self.root = root.resolve()
        self.declared_commit = declared_commit
        self.used: dict[str, Document] = {}

    def load(self, key: str) -> Document:
        if key not in DOC_FILES:
            raise InputError(f"미등록 문서 키: {key}")
        if key not in self.used:
            doc = read_document(self.root / DOC_FILES[key], key)
            fingerprint = replace(doc.fingerprint, authored_sha256=AUTHORED_SHA256.get(key), declared_commit=self.declared_commit)
            self.used[key] = replace(doc, fingerprint=fingerprint)
        return self.used[key]


@dataclass(frozen=True, slots=True)
class Anchor:
    doc: str
    heading: tuple[str, ...]
    take: str
    count: int | None = None
    pattern: str | None = None
    fixed: tuple[tuple[str, str], ...] = ()
    hint_lines: tuple[int, int] | None = None


@dataclass(frozen=True, slots=True)
class Extract:
    text: str
    where: SourceRef
    groups: dict[str, str]


def structure(doc: Document):
    headings = []
    fences = []
    stack: list[tuple[int, str]] = []
    opened: tuple[str, int] | None = None
    for index, line in enumerate(doc.lines, 1):
        fence = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if opened is not None:
            if fence and fence[1] == opened[0] and not fence[2].strip():
                fences.append((opened[1] + 1, index - 1))
                opened = None
            continue
        if fence:
            opened = (fence[1], index)
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            level = len(match[1])
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, " ".join(match[2].split())))
            headings.append((index, level, tuple(title for _, title in stack)))
    if opened is not None:
        raise InputError(f"문서 펜스 미종결: {doc.fingerprint.key}:{opened[1]}")
    return headings, fences


def classify(doc: Document, where: SourceRef) -> tuple[Mark, str | None]:
    excerpt = "\n".join(doc.lines[where.line_start - 1:where.line_end])
    exception = re.search(r"\[예외:\s*([^\]]+)\]", excerpt)
    if exception:
        return Mark.EXCEPTION, exception[1]
    if "예(PLATING)" in excerpt:
        return Mark.EXAMPLE, "원문 표기"
    if doc.fingerprint.key in FILE_EXCEPTION_KEYS and re.search(r"\[예외:.*(?:전체|환경|스타일|설정)", "\n".join(doc.lines[:4])):
        return Mark.FILE_EXCEPTION, doc.lines[2]
    return Mark.UNMARKED, None


def resolve(doc: Document, anchor: Anchor) -> list[Extract]:
    headings, fences = structure(doc)
    choices = [(line, level) for line, level, path in headings if path == anchor.heading]
    if len(choices) != 1:
        raise InputError(f"앵커 제목 불일치: {anchor.doc}, {anchor.heading}, 후보 {headings}")
    start, level = choices[0]
    end = next((line - 1 for line, depth, _ in headings if line > start and depth <= level), len(doc.lines))
    ranges = []
    match anchor.take:
        case "fence" | "fences":
            ranges = [(a, b) for a, b in fences if start < a <= b < end + 1]
        case "numbered":
            ranges = [(i, i) for i in range(start + 1, end + 1) if re.match(r"^\d+\. ", doc.lines[i - 1])]
        case "table_rows":
            ranges = [(i, i) for i in range(start + 1, end + 1) if doc.lines[i - 1].startswith("|") and not re.match(r"^\|[\s:|-]+$", doc.lines[i - 1])]
        case "lines":
            ranges = [(start + 1, end)]
        case _:
            raise InputError(f"미지원 앵커 방식: {anchor.take}")
    result = []
    for first, last in ranges:
        text = "\n".join(doc.lines[first - 1:last])
        groups = {}
        if anchor.pattern:
            match = re.search(anchor.pattern, text, re.MULTILINE)
            if match is None:
                raise InputError(f"앵커 패턴 불일치: {anchor.doc}:{first} {anchor.pattern}")
            groups = match.groupdict()
            if any(groups.get(key) != value for key, value in anchor.fixed):
                raise InputError(f"앵커 단위/고정값 불일치: {anchor.doc}:{first}")
        where = doc.ref(first, last, anchor.heading)
        mark, reason = classify(doc, where)
        result.append(Extract(text, replace(where, mark=mark, mark_reason=reason), groups))
    if anchor.count is not None and len(result) != anchor.count:
        raise InputError(f"앵커 개수 불일치: {anchor.doc}:{start}, 기대 {anchor.count}, 실제 {len(result)}")
    return result
