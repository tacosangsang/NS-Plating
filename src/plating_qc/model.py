"""미디어 검사 결과 계약."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ColorInfo:
    primaries: str
    transfer: str
    space: str


@dataclass(frozen=True, slots=True)
class VideoInfo:
    codec: str | None
    width: int | None
    height: int | None
    pix_fmt: str | None
    r_frame_rate: str | None
    avg_frame_rate: str | None
    nb_frames_meta: int | None
    nb_frames_decoded: int
    nb_read_packets: int | None
    decode_errors: int
    duration_s: str | None
    start_time_s: str | None
    profile: str | None
    color: ColorInfo


@dataclass(frozen=True, slots=True)
class AudioInfo:
    codec: str | None
    sample_rate: str | None
    channels: int | None
    duration_s: str | None
    start_time_s: str | None


@dataclass(frozen=True, slots=True)
class TimingInfo:
    status: str
    missing_count: int | None
    vfr_suspect: bool | None
    interval_stddev_s: float | None
    rates_differ: bool | None


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ProresRequest:
    source: Path
    output: Path | None
    generate_pts: bool
    audio_duration: float | None


@dataclass(frozen=True, slots=True)
class TileRenderRequest:
    source: Path
    work: Path
    fps: float
    width: int
    columns: int
    rows: int
    labels: bool


@dataclass(frozen=True, slots=True)
class CutRenderRequest:
    source: Path
    work: Path
    start: int
    end: int
    name: str
    labels: bool


@dataclass(frozen=True, slots=True)
class PairRenderRequest:
    original: Path
    candidate: Path
    work: Path
    source_frame: int
    candidate_frame: int
    width: int
    height: int
    name: str


@dataclass(frozen=True, slots=True)
class MediaInfo:
    path: str
    timestamp_analysis: TimingInfo
    video: VideoInfo
    audio: AudioInfo | None
    warnings: list[str]
