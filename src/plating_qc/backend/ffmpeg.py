"""FFmpeg 기반 미디어 검사."""

import json
from pathlib import Path

from .base import MediaBackend
from .. import core
from ..errors import QCError
from ..model import AudioInfo, ColorInfo, MediaInfo, TimingInfo, VideoInfo


class FfmpegBackend(MediaBackend):
    def __init__(self, config):
        self.config = config

    def probe(self, path: Path) -> MediaInfo:
        path = Path(path).resolve()
        if not path.is_file():
            raise QCError(2, f"입력 파일이 없습니다: {path}")
        ffprobe = core.executable("ffprobe", self.config)
        result = core.run([ffprobe, "-v", "error", "-count_frames", "-count_packets",
                           "-show_streams", "-show_format", "-of", "json", str(path)])
        if result.stderr.strip():
            raise QCError(5, "디코딩 오류: " + result.stderr.strip()[-1000:])
        try:
            data = json.loads(result.stdout)
            video = next(s for s in data["streams"] if s["codec_type"] == "video")
        except (ValueError, KeyError, StopIteration) as exc:
            raise QCError(5, "영상 스트림을 읽지 못했습니다") from exc
        count = video.get("nb_read_frames")
        if not count or not str(count).isdigit():
            raise QCError(5, "디코딩 프레임 수를 확인하지 못했습니다")
        audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
        warnings = []
        meta = video.get("nb_frames")
        if meta and str(meta).isdigit() and int(meta) != int(count):
            warnings.append("컨테이너 프레임 수와 디코딩 프레임 수가 다릅니다")
        packets = video.get("nb_read_packets")
        packet_count = int(packets) if packets and str(packets).isdigit() else None
        if packet_count is not None and packet_count != int(count):
            warnings.append("패킷 수와 디코딩 프레임 수가 다릅니다")
        avg, rate = video.get("avg_frame_rate"), video.get("r_frame_rate")
        timing = core.analyze_timestamps(path, ffprobe, int(count), avg, rate)
        if timing["status"] == "generated":
            warnings.append("원본 PTS 일부가 없어 genpts로 생성한 시간입니다. 원래 타이밍은 확인할 수 없습니다")
        elif timing["status"] == "unavailable":
            warnings.append("원본 PTS가 없고 genpts로도 복구되지 않았습니다. 타이밍을 확인할 수 없습니다")
        elif timing["status"] == "not_checked":
            warnings.append("100000프레임 초과로 PTS 간격을 검사하지 못했습니다")
        if timing["vfr_suspect"]:
            warnings.append("PTS 간격 또는 프레임 속도 차이로 가변 프레임 속도가 의심됩니다")
        color = ColorInfo(video.get("color_primaries", "unknown"),
                          video.get("color_transfer", "unknown"),
                          video.get("color_space", "unknown"))
        video_info = VideoInfo(video.get("codec_name"), video.get("width"), video.get("height"),
                               video.get("pix_fmt"), rate, avg,
                               int(meta) if meta and str(meta).isdigit() else None,
                               int(count), packet_count, 0, video.get("duration"),
                               video.get("start_time"), video.get("profile"), color)
        audio_info = None if audio is None else AudioInfo(audio.get("codec_name"),
                         audio.get("sample_rate"), audio.get("channels"), audio.get("duration"),
                         audio.get("start_time"))
        return MediaInfo(str(path), TimingInfo(**timing), video_info, audio_info, warnings)
