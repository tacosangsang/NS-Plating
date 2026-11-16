"""인증 없는 HTTPS GET. 자동 redirect를 끄고 매 hop과 한도를 검사한다."""
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .images import ImageInfo, inspect_image


class FetchError(StrEnum):
    NONE = "none"
    NOT_ATTEMPTED = "not_attempted"
    NON_HTTPS = "non_https"
    TIMEOUT = "timeout"
    TOO_MANY_REDIRECTS = "too_many_redirects"
    HTTP_STATUS = "http_status"
    HTML_PAGE = "html_page"
    NOT_IMAGE = "not_image"
    TOO_LARGE = "too_large"
    NETWORK = "network"


@dataclass(frozen=True, slots=True)
class Hop:
    url: str
    status: int
    location: str | None


@dataclass(frozen=True, slots=True)
class FetchResult:
    error: FetchError
    detail: str = ""
    hops: tuple[Hop, ...] = ()
    final_url: str | None = None
    status: int | None = None
    content_type: str | None = None
    body_size: int | None = None
    body_sha256: str | None = None
    image: ImageInfo | None = None


class HttpFetcher(ABC):
    @abstractmethod
    def get(self, url: str, *, timeout_s: float, max_redirects: int, max_bytes: int) -> FetchResult: ...


def inspect_response(status: int, content_type: str, body: bytes, url: str) -> FetchResult:
    image = inspect_image(body)
    content = content_type.partition(";")[0].strip().lower()
    error = FetchError.NONE
    if status != 200:
        error = FetchError.HTTP_STATUS
    elif content in {"text/html", "application/xhtml+xml"}:
        error = FetchError.HTML_PAGE
    elif not content.startswith("image/") or image is None:
        error = FetchError.NOT_IMAGE
    return FetchResult(error, final_url=url, status=status, content_type=content_type, body_size=len(body), body_sha256=sha256(body).hexdigest(), image=image if error == FetchError.NONE else None)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class UrllibFetcher(HttpFetcher):
    def get(self, url: str, *, timeout_s: float, max_redirects: int, max_bytes: int) -> FetchResult:
        deadline = time.monotonic() + timeout_s
        hops: list[Hop] = []
        opener = build_opener(NoRedirect())
        current = url
        while True:
            parsed = urlsplit(current)
            if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
                return FetchResult(FetchError.NON_HTTPS, hops=tuple(hops), final_url=current)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return FetchResult(FetchError.TIMEOUT, hops=tuple(hops), final_url=current)
            try:
                request = Request(current, headers={"User-Agent": "plating-tools/0.1"}, method="GET")
                try:
                    response = opener.open(request, timeout=remaining)
                except HTTPError as exc:
                    response = exc
                with response:
                    status = response.status
                    location = response.headers.get("Location")
                    hops.append(Hop(current, status, location))
                    if status in {301, 302, 303, 307, 308} and location:
                        if len(hops) > max_redirects:
                            return FetchResult(FetchError.TOO_MANY_REDIRECTS, hops=tuple(hops), final_url=current, status=status)
                        current = urljoin(current, location)
                        continue
                    chunks = bytearray()
                    while len(chunks) <= max_bytes:
                        if time.monotonic() >= deadline:
                            return FetchResult(FetchError.TIMEOUT, hops=tuple(hops), final_url=current, status=status)
                        chunk = response.read(min(65536, max_bytes + 1 - len(chunks)))
                        if not chunk:
                            break
                        chunks.extend(chunk)
                    content = response.headers.get("Content-Type", "")
                    if len(chunks) > max_bytes:
                        return FetchResult(FetchError.TOO_LARGE, hops=tuple(hops), final_url=current, status=status, content_type=content, body_size=len(chunks))
                    return replace(inspect_response(status, content, bytes(chunks), current), hops=tuple(hops))
            except (TimeoutError, URLError, OSError, ValueError) as exc:
                reason = exc.reason if isinstance(exc, URLError) else exc
                error = FetchError.TIMEOUT if isinstance(reason, TimeoutError) else FetchError.NETWORK
                return FetchResult(error, str(exc), tuple(hops), current)
