"""미디어 검사 결과 계약."""

from dataclasses import dataclass


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
class MediaInfo:
    path: str
    timestamp_analysis: TimingInfo
    video: VideoInfo
    audio: AudioInfo | None
    warnings: list[str]
