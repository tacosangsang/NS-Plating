"""미디어 처리 백엔드."""

from .base import MediaBackend
from .ffmpeg import FfmpegBackend


def make_backend(config: dict) -> MediaBackend:
    return FfmpegBackend(config)
