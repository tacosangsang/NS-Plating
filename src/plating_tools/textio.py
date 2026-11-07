"""UTF-8 입력과 원문 행·지문. U+2028은 줄 구분자가 아니다."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json

from .errors import InputError, IoFailure
from .model import DocFingerprint, SourceRef


@dataclass(frozen=True, slots=True)
class Document:
    fingerprint: DocFingerprint
    lines: tuple[str, ...]
    newline: str

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def ref(self, start: int, end: int, headings: tuple[str, ...] = ()) -> SourceRef:
        excerpt = "\n".join(self.lines[start - 1:end])
        return SourceRef(self.fingerprint.key, start, end, headings,
                         excerpt_sha256=sha256(excerpt.encode("utf-8")).hexdigest())


def read_document(path: Path, key: str) -> Document:
    try:
        data = path.resolve().read_bytes()
    except FileNotFoundError as exc:
        raise InputError(f"입력 파일 없음: {path}") from exc
    except OSError as exc:
        raise IoFailure(f"입력 읽기 실패: {path}: {exc}") from exc
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"UTF-8 해석 실패: {path}, 바이트 {exc.start}") from exc
    lines = tuple(line.removesuffix("\r") for line in text.split("\n"))
    newline = "CRLF" if b"\r\n" in data else "LF"
    if b"\r\n" in data and b"\n" in data.replace(b"\r\n", b""):
        newline = "mixed"
    return Document(DocFingerprint(key, str(path.resolve()), len(data), sha256(data).hexdigest()), lines, newline)


def normalized(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def read_json(path: Path):
    try:
        value = json.loads(read_document(path, "json").text)
    except json.JSONDecodeError as exc:
        raise InputError(f"JSON 입력 오류: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"JSON 객체 필요: {path}")
    return value
