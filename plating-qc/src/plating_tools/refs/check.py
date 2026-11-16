"""레퍼런스 대응·번호·최대 원본 조건을 검사한다."""
import re
from dataclasses import dataclass
from pathlib import Path

from ..model import Finding, RefEntry, Severity, Unknown
from .fetch import FetchError, FetchResult, HttpFetcher
from .images import ImageInfo, inspect_image
from .resolve import LocalReferenceResolver, ReferenceResolver


@dataclass(frozen=True, slots=True)
class RefResult:
    entry: RefEntry
    local: ImageInfo | Unknown
    remote: FetchResult
    correspondence: str
    largest_among_given: str | Unknown
    best_original: str
    findings: tuple[Finding, ...]


def check_numbers(entries: tuple[RefEntry, ...], prompt: str | None) -> tuple[Finding, ...]:
    indices = tuple(e.index for e in entries)
    findings = []
    if indices != tuple(range(1, len(entries) + 1)):
        findings.append(Finding("REF_NUMBER", Severity.ERROR, "첨부 순서는 @image1부터 연속·중복 없음이어야 함"))
    if prompt is not None:
        tokens = {int(n) for n in re.findall(r"@image(\d+)\b", prompt)}
        roles = re.search(r"(?ms)^REFERENCE ROLES[^\n]*\n(.*?)(?=^STYLE\b|\Z)", prompt)
        role_tokens = {int(n) for n in re.findall(r"@image(\d+)\b", roles[1])} if roles else set()
        if tokens - set(indices) or role_tokens != set(indices):
            findings.append(Finding("REF_PROMPT_NUMBER", Severity.ERROR, "REFERENCE ROLES·본문 번호와 첨부 목록 불일치"))
    return tuple(findings)


def count_advice(count: int, safe_range: tuple[int, int]) -> tuple[Finding, ...]:
    lower, upper = safe_range
    if count > upper:
        return (Finding("REF_SPLIT", Severity.WARN, f"{count}장: 분할 검토 사유, 안전 권고 {lower}~{upper}장(하드 한도 아님)"),)
    return (Finding("REF_COUNT", Severity.INFO, f"{count}장: 안전 권고 {lower}~{upper}장(하드 한도 아님)"),)


def check_references(entries: tuple[RefEntry, ...], *, fetcher: HttpFetcher, allow_network: bool = False,
                     resolver: ReferenceResolver | None = None, timeout_s: float = 20,
                     max_redirects: int = 5, max_bytes: int = 52428800) -> tuple[RefResult, ...]:
    """외부 처리는 주입 경계에 한정한다. 기본값은 GET 0회다."""
    resolver = resolver or LocalReferenceResolver()
    results = []
    for entry in entries:
        findings = []
        local: ImageInfo | Unknown = Unknown("로컬 파일 미지정")
        remote = FetchResult(FetchError.NOT_ATTEMPTED, "URL 미확인")
        path = Path(entry.local_path).resolve() if entry.local_path else None
        thumbnail_input = path is not None and "thumbs" in {p.casefold() for p in path.parts}
        if thumbnail_input:
            findings.append(Finding("REF_THUMB_INPUT", Severity.ERROR, "보기용 축소본은 생성 입력으로 사용 금지(W08 24)"))
        elif path is not None:
            local = inspect_image(path.read_bytes()) or Unknown("이미지 헤더 해석 불가")
            if isinstance(local, Unknown):
                findings.append(Finding("REF_LOCAL_IMAGE", Severity.ERROR, local.unknown))
        if allow_network and entry.url and not thumbnail_input:
            remote = fetcher.get(entry.url, timeout_s=timeout_s, max_redirects=max_redirects, max_bytes=max_bytes)
        if remote.error != FetchError.NONE:
            findings.append(Finding("REF_URL_" + remote.error.name, Severity.WARN, remote.detail or remote.error.value))
        correspondence = "미확인"
        if isinstance(local, ImageInfo) and remote.error == FetchError.NONE and remote.body_sha256:
            correspondence = "바이트 동일" if local.sha256 == remote.body_sha256 else "불일치"
            if correspondence == "불일치":
                findings.append(Finding("REF_MISMATCH", Severity.ERROR, "로컬 파일과 응답 바이트 불일치"))
        candidates = resolver.candidates(entry)
        infos = []
        for candidate in candidates.items:
            info = None if "thumbs" in {p.casefold() for p in candidate.parts} else inspect_image(candidate.read_bytes())
            infos.append((candidate, info))
        valid = [(p, i) for p, i in infos if i is not None]
        largest = Unknown("후보 없음")
        best = "최대 원본 미확인"
        if valid:
            maximum = max(i.width * i.height for _, i in valid)
            largest = f"제공된 후보 {len(infos)}개 중 최대: " + ", ".join(str(p) for p, i in valid if i.width * i.height == maximum)
            if candidates.complete and candidates.basis and candidates.basis.strip() and len(valid) == len(infos) and isinstance(local, ImageInfo) and path in candidates.items and local.width * local.height == maximum:
                best = "최대 원본 확인됨"
        if entry.sheet in {"", "없음", "시트 없음/만들어야 함"} or entry.preview != "검수 완료":
            findings.append(Finding("REF_HUMAN_REVIEW", Severity.WARN, f"{entry.sheet}; {entry.preview}"))
        results.append(RefResult(entry, local, remote, correspondence, largest, best, tuple(findings)))
    return tuple(results)
