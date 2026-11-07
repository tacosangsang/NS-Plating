"""미디어 백엔드 계약."""

from abc import ABC
from pathlib import Path

from ..errors import QCError
from ..model import CutRenderRequest, MediaInfo, PairRenderRequest, ProresRequest, TileRenderRequest


class MediaBackend(ABC):
    """지원하지 않는 작업은 백엔드 부재 종료 코드로 보고한다."""

    def probe(self, path: Path) -> MediaInfo:
        raise QCError(4, "이 백엔드는 probe를 지원하지 않습니다")

    def timestamps(self, path: Path, generated: bool = False) -> list[float | None]:
        raise QCError(4, "이 백엔드는 타임스탬프 검사를 지원하지 않습니다")

    def encode_prores(self, request: ProresRequest) -> Path:
        raise QCError(4, "이 백엔드는 ProRes 변환을 지원하지 않습니다")

    def describe_prores(self, request: ProresRequest) -> str:
        raise QCError(4, "이 백엔드는 ProRes 변환을 지원하지 않습니다")

    def extract_frames(self, source: Path, width: int, height: int, count: int) -> list[memoryview]:
        raise QCError(4, "이 백엔드는 프레임 추출을 지원하지 않습니다")

    def cut_copy(self, source: Path, output: Path, segment_time: float) -> list[Path]:
        raise QCError(4, "이 백엔드는 분할을 지원하지 않습니다")

    def framemd5(self, source: Path) -> list[str]:
        raise QCError(4, "이 백엔드는 프레임 해시를 지원하지 않습니다")

    def render_tiles(self, request: TileRenderRequest) -> str:
        raise QCError(4, "이 백엔드는 타일 생성을 지원하지 않습니다")

    def render_cut(self, request: CutRenderRequest) -> None:
        raise QCError(4, "이 백엔드는 컷 생성을 지원하지 않습니다")

    def scene_candidates(self, source: Path, work: Path, threshold: float) -> str:
        raise QCError(4, "이 백엔드는 장면 후보 검출을 지원하지 않습니다")

    def render_pair(self, request: PairRenderRequest) -> None:
        raise QCError(4, "이 백엔드는 비교 이미지 생성을 지원하지 않습니다")
