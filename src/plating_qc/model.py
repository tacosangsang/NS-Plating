"""미디어 검사 결과 계약."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class VideoInfo:
    codec: str | None
    width: int | None
    height: int | None
    frames_decoded: int
    frames_metadata: int | None
    frames_packets: int | None
    frame_rate: str | None


@dataclass(frozen=True, slots=True)
class AudioInfo:
    codec: str | None
    sample_rate: int | None
    channels: int | None


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class MediaInfo:
    path: Path
    video: VideoInfo
    audio: AudioInfo | None
    findings: tuple[Finding, ...]
