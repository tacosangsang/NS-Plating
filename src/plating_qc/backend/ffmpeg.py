"""FFmpeg 기반 미디어 검사."""

import json
from pathlib import Path
import subprocess

from .base import MediaBackend
from .ffmpeg_helpers import analyze_timestamps, executable, frame_timestamps, run
from ..errors import QCError
from ..layout import checked_path
from ..model import (AudioInfo, ColorInfo, CutRenderRequest, MediaInfo, PairRenderRequest,
                     ProresRequest, TileRenderRequest, TimingInfo, VideoInfo)

DRAW_TEXT = "drawtext=text='F %{n} T %{pts\\:flt}':x=3:y=3:fontsize=min(max(8\\,h/12)\\,w/25):fontcolor=white:box=1:boxcolor=black@0.75"


class FfmpegBackend(MediaBackend):
    def __init__(self, config):
        self.config = config

    def timestamps(self, path: Path, generated: bool = False) -> list[float | None]:
        return frame_timestamps(path, executable("ffprobe", self.config), generated)

    def prores_command(self, request: ProresRequest) -> list[str]:
        timestamp_options = ["-fflags", "+genpts"] if request.generate_pts else []
        args = [executable("ffmpeg", self.config), "-v", "error", "-nostdin",
                *timestamp_options, "-i", str(request.source), "-map", "0:v:0",
                "-map", "0:a:0?", "-vf",
                "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709",
                "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le",
                "-vendor", "apl0", "-fps_mode", "passthrough", "-color_primaries",
                "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-movflags", "+write_colr", "-c:a", "pcm_s16le"]
        if request.audio_duration is not None:
            args += ["-af", f"apad=whole_dur={request.audio_duration:.9f}"]
        if request.output is None:
            return args + ["<임시 출력 파일>"]
        return args + ["-y", str(request.output)]

    def encode_prores(self, request: ProresRequest) -> Path:
        if request.output is None:
            raise QCError(2, "변환 출력 경로가 없습니다")
        run(self.prores_command(request))
        return request.output

    def extract_frames(self, source: Path, width: int, height: int, count: int) -> list[memoryview]:
        if width * height * count > 128 * 1024 * 1024:
            raise QCError(2, "비교 영상이 너무 깁니다. 짧은 구간으로 나눠 확인하세요")
        cmd = [executable("ffmpeg", self.config), "-v", "error", "-nostdin", "-i",
               str(source), "-map", "0:v:0", "-vf", f"scale={width}:{height},format=gray",
               "-fps_mode", "passthrough", "-f", "rawvideo", "-"]
        try:
            result = subprocess.run(cmd, capture_output=True)
        except OSError as exc:
            raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
        if result.returncode:
            raise QCError(5, "프레임 디코딩 실패: " + result.stderr.decode(errors="replace")[-2000:])
        size = width * height
        if len(result.stdout) != count * size:
            raise QCError(5, "비교용 디코딩 프레임 수가 probe 결과와 다릅니다")
        return [memoryview(result.stdout)[i:i + size] for i in range(0, len(result.stdout), size)]

    def cut_copy(self, source: Path, output: Path, segment_time: float) -> list[Path]:
        ffmpeg = executable("ffmpeg", self.config)
        args = [ffmpeg, "-v", "error", "-nostdin", "-i", str(source), "-map", "0:v:0",
                "-map", "0:a?", "-c", "copy", "-f", "segment", "-segment_format", "mov",
                "-segment_time", f"{segment_time:.9f}", "-reset_timestamps", "1", "-n", "part_%03d.mov"]
        try:
            result = subprocess.run(args, cwd=output, capture_output=True, text=True, errors="replace")
        except OSError as exc:
            raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
        if result.returncode:
            raise QCError(5, "분할 실패: " + result.stderr[-2000:])
        return sorted(output.glob("part_*.mov"))

    def framemd5(self, source: Path) -> list[str]:
        ffmpeg = executable("ffmpeg", self.config)
        data = run([ffmpeg, "-v", "error", "-nostdin", "-i", str(source),
                         "-map", "0:v:0", "-f", "framemd5", "-"]).stdout
        hashes = []
        for line in data.splitlines():
            if line and not line.startswith("#"):
                fields = line.split(",")
                if len(fields) != 6 or len(fields[-1].strip()) != 32:
                    raise QCError(5, "프레임 검증 출력 형식이 올바르지 않습니다")
                hashes.append(fields[-1].strip())
        if not hashes:
            raise QCError(5, "비교할 프레임이 없습니다")
        return hashes

    def _render(self, args: list[str], work: Path) -> str:
        try:
            result = subprocess.run(args, cwd=work, capture_output=True, text=True, errors="replace")
        except OSError as exc:
            raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
        if result.returncode:
            raise QCError(5, "검수 이미지 생성 실패: " + result.stderr[-2000:])
        return result.stderr

    def render_tiles(self, request: TileRenderRequest) -> str:
        label = DRAW_TEXT if request.labels else "null"
        select = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{1 / request.fps:.12f})'"
        graph = f"showinfo@source,{label},{select},showinfo@selected,scale={request.width}:-2,tile={request.columns}x{request.rows}"
        return self._render([executable("ffmpeg", self.config), "-v", "info", "-nostdin",
                             "-copyts", "-i", str(request.source), "-vf", graph, "-fps_mode",
                             "passthrough", "-threads", "1", "-n", "tiles_%03d.png"], request.work)

    def render_cut(self, request: CutRenderRequest) -> None:
        label = DRAW_TEXT if request.labels else "null"
        graph = f"{label},select=between(n\\,{request.start}\\,{request.end}),tile={request.end-request.start+1}x1"
        self._render([executable("ffmpeg", self.config), "-v", "error", "-nostdin", "-copyts",
                      "-i", str(request.source), "-vf", graph, "-frames:v", "1", "-threads",
                      "1", "-n", request.name], request.work)

    def scene_candidates(self, source: Path, work: Path, threshold: float) -> str:
        graph = f"select='gt(scene\\,{threshold:.8f})',showinfo@scene"
        return self._render([executable("ffmpeg", self.config), "-v", "info", "-nostdin",
                             "-copyts", "-i", str(source), "-vf", graph, "-fps_mode",
                             "passthrough", "-f", "null", "-"], work)

    def render_pair(self, request: PairRenderRequest) -> None:
        graph = (f"[0:v]select=eq(n\\,{request.source_frame}),setpts=PTS-STARTPTS[left];"
                 f"[1:v]select=eq(n\\,{request.candidate_frame}),scale={request.width}:{request.height},setpts=PTS-STARTPTS[right];"
                 "[left][right]hstack=inputs=2[out]")
        self._render([executable("ffmpeg", self.config), "-v", "error", "-nostdin", "-i",
                      str(request.original), "-i", str(request.candidate), "-filter_complex",
                      graph, "-map", "[out]", "-frames:v", "1", "-threads", "1", "-n",
                      request.name], request.work)

    def probe(self, path: Path) -> MediaInfo:
        path = checked_path(Path(path))
        if not path.is_file():
            raise QCError(2, f"입력 파일이 없습니다: {path}")
        ffprobe = executable("ffprobe", self.config)
        result = run([ffprobe, "-v", "error", "-count_frames", "-count_packets",
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
        timing = analyze_timestamps(path, ffprobe, int(count), avg, rate)
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
