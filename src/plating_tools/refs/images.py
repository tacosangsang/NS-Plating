"""PNG·JPEG·WebP 헤더와 기존 FFmpeg 이미지 경계."""
import shutil
import struct
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ..errors import IoFailure, OutputConflict, Unavailable


@dataclass(frozen=True, slots=True)
class ImageInfo:
    format: str
    width: int
    height: int
    decode: str
    size: int
    sha256: str


def inspect_image(data: bytes) -> ImageInfo | None:
    """헤더 정보만 판독한다. 완전한 디코딩 성공을 주장하지 않는다."""
    dimensions = None
    kind = ""
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        kind, dimensions = "png", struct.unpack(">II", data[16:24])
    elif data[:2] == b"\xff\xd8":
        offset = 2
        while offset + 4 <= len(data):
            if data[offset] != 255:
                break
            marker = data[offset + 1]
            if marker == 255:
                offset += 1
                continue
            length = int.from_bytes(data[offset + 2:offset + 4], "big")
            if length < 2 or offset + 2 + length > len(data):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF} and length >= 7:
                height, width = struct.unpack(">HH", data[offset + 5:offset + 9])
                kind, dimensions = "jpeg", (width, height)
                break
            offset += 2 + length
    elif len(data) >= 25 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk, payload = data[12:16], data[20:]
        if chunk == b"VP8X" and len(payload) >= 10:
            dimensions = (1 + int.from_bytes(payload[4:7], "little"), 1 + int.from_bytes(payload[7:10], "little"))
        elif chunk == b"VP8L" and payload[0] == 0x2F:
            bits = int.from_bytes(payload[1:5], "little")
            dimensions = ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        elif chunk == b"VP8 " and len(payload) >= 10 and payload[3:6] == b"\x9d\x01\x2a":
            dimensions = tuple(value & 0x3FFF for value in struct.unpack("<HH", payload[6:10]))
        kind = "webp"
    if dimensions is None or min(dimensions) <= 0:
        return None
    return ImageInfo(kind, dimensions[0], dimensions[1], "헤더만 확인", len(data), sha256(data).hexdigest())


class ImageTool(ABC):
    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def decode_check(self, path: Path) -> bool: ...

    @abstractmethod
    def thumbnail(self, src: Path, dst: Path, max_side: int) -> None: ...


class FFmpegImageTool(ImageTool):
    def __init__(self, ffmpeg_path: str = ""):
        configured = Path(ffmpeg_path) if ffmpeg_path else None
        candidate = str(configured / "ffmpeg") if configured and configured.is_dir() else ffmpeg_path or "ffmpeg"
        self.executable = shutil.which(candidate)

    def available(self) -> bool:
        return self.executable is not None

    def decode_check(self, path: Path) -> bool:
        if not self.executable:
            raise Unavailable("ffmpeg 없음: tools.ffmpeg_path 확인")
        try:
            result = subprocess.run([self.executable, "-v", "error", "-i", str(path), "-f", "null", "-"], shell=False, capture_output=True, timeout=60, check=False)
        except subprocess.TimeoutExpired:
            return False
        return result.returncode == 0

    def thumbnail(self, src: Path, dst: Path, max_side: int) -> None:
        if dst.exists():
            raise OutputConflict(f"썸네일 충돌: {dst}")
        if not self.executable:
            raise Unavailable("ffmpeg 없음: tools.ffmpeg_path 확인")
        try:
            result = subprocess.run([self.executable, "-n", "-v", "error", "-i", str(src), "-vf", f"scale={max_side}:{max_side}:force_original_aspect_ratio=decrease", "-frames:v", "1", str(dst)], shell=False, capture_output=True, timeout=60, check=False)
        except subprocess.TimeoutExpired as exc:
            raise IoFailure(f"썸네일 시간 초과: {src}") from exc
        if result.returncode:
            raise IoFailure(f"썸네일 디코딩 실패: {src}")
