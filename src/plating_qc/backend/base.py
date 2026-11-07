"""미디어 백엔드 계약."""

from abc import ABC
from pathlib import Path

from ..errors import QCError
from ..model import MediaInfo


class MediaBackend(ABC):
    """지원하지 않는 작업은 백엔드 부재 종료 코드로 보고한다."""

    def probe(self, path: Path) -> MediaInfo:
        raise QCError(4, "이 백엔드는 probe를 지원하지 않습니다")

    def encode_prores(self, source: Path, output: Path) -> Path:
        raise QCError(4, "이 백엔드는 ProRes 변환을 지원하지 않습니다")

    def extract_frames(self, source: Path, output: Path) -> list[Path]:
        raise QCError(4, "이 백엔드는 프레임 추출을 지원하지 않습니다")

    def cut_copy(self, source: Path, output: Path) -> Path:
        raise QCError(4, "이 백엔드는 분할을 지원하지 않습니다")

    def framemd5(self, source: Path) -> list[str]:
        raise QCError(4, "이 백엔드는 프레임 해시를 지원하지 않습니다")
