"""ProRes를 검증 가능한 조각으로 나누는 오프라인 도구."""
import json
import math
import os
from pathlib import Path
import tempfile

from .core import QCError, executable, layout_names, probe
from .layout import checked_path
from .publish import publish


def frame_hashes(path, ffmpeg):
    from .backend.ffmpeg import FfmpegBackend

    return FfmpegBackend({"ffmpeg_path": ffmpeg}).framemd5(Path(path))


def split(source, out, config, max_part_mb=400):
    if not math.isfinite(max_part_mb) or max_part_mb <= 0:
        raise QCError(2, "max-part-mb는 0보다 큰 숫자여야 합니다")
    info = probe(source, config)
    if info["video"]["codec"] != "prores":
        raise QCError(2, "ProRes 영상만 무재인코딩 분할할 수 있습니다")
    if info["timestamp_analysis"]["status"] != "observed" or info["timestamp_analysis"]["vfr_suspect"] is not False:
        raise QCError(2, "PTS가 없거나 가변 프레임 속도가 의심되어 안전하게 분할할 수 없습니다")
    try:
        duration = float(info["video"]["duration_s"])
        num, den = (int(x) for x in info["video"]["avg_frame_rate"].split("/"))
        fps = num / den
        if not math.isfinite(duration) or duration <= 0 or fps <= 0:
            raise ValueError
    except (ValueError, TypeError, ZeroDivisionError, AttributeError):
        raise QCError(2, "영상 길이 또는 프레임 속도를 확인할 수 없습니다")
    limit = int(max_part_mb * 1024 * 1024)
    size = Path(info["path"]).stat().st_size
    segment_time = duration * min(1.0, limit * .85 / max(size, 1))
    if segment_time < 1 / fps:
        raise QCError(2, "분할 크기가 한 프레임보다 작습니다")
    raw, _ = layout_names(config)
    dest = checked_path(Path(out))
    if any(p.name.casefold() == raw.casefold() for p in (dest, *dest.parents)):
        raise QCError(2, "raw 폴더에는 출력할 수 없습니다")
    if not dest.parent.is_dir():
        raise QCError(2, "출력 폴더의 상위 폴더가 없습니다")
    ffmpeg = executable("ffmpeg", config)
    try:
        dest.mkdir()
    except FileExistsError as exc:
        raise QCError(3, f"출력 폴더가 이미 있습니다: {dest}") from exc
    except OSError as exc:
        raise QCError(5, f"출력 폴더 생성 실패: {exc}") from exc
    published = []
    try:
        with tempfile.TemporaryDirectory(prefix=".plating-qc-", dir=dest) as work:
            stage = Path(work)
            from .backend.ffmpeg import FfmpegBackend

            parts = FfmpegBackend(config).cut_copy(Path(info["path"]), stage, segment_time)
            if not parts:
                raise QCError(5, "분할 파일이 생성되지 않았습니다")
            sizes = [p.stat().st_size for p in parts]
            if any(n > limit for n in sizes):
                raise QCError(1, "분할 파일이 지정한 최대 크기를 초과했습니다. 더 작은 설정으로 다시 시도하세요")
            original = frame_hashes(info["path"], ffmpeg)
            joined = []
            details = []
            for part, part_size in zip(parts, sizes):
                hashes = frame_hashes(part, ffmpeg)
                joined.extend(hashes)
                part_info = probe(part, config)
                video, audio = part_info["video"], part_info["audio"]
                timing = None if audio is None else {
                    "video_start_s": video["start_time_s"],
                    "video_duration_s": video["duration_s"],
                    "audio_start_s": audio["start_time_s"],
                    "audio_duration_s": audio["duration_s"],
                }
                details.append({"file": part.name, "bytes": part_size, "frames": len(hashes), "audio_timing_first_stream": timing})
            if joined != original or len(original) != info["video"]["nb_frames_decoded"]:
                raise QCError(1, "분할 전후 프레임 검증이 일치하지 않습니다. 결과를 저장하지 않았습니다")
            warnings = []
            if info["audio"] is not None:
                warnings.append("영상 프레임만 검증했습니다. 오디오는 패킷 단위로 분할되어 조각별 시작 시각과 길이가 영상 경계와 다를 수 있습니다. 음성 이음새는 보장되지 않으므로 편집기에서 별도 확인하세요. 시간 정보는 첫 번째 오디오 스트림만 표시합니다.")
            report = {"input": info["path"], "limit_bytes": limit, "parts": details, "frames_verified": len(original), "audio_boundary_verified": False if info["audio"] is not None else None, "warnings": warnings}
            (stage / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            for part in [*parts, stage / "manifest.json"]:
                target = dest / part.name
                checked_path(target)
                publish(part, target)
                stat = target.stat()
                published.append((target, stat.st_dev, stat.st_ino))
        return report
    except (QCError, OSError) as exc:
        for target, dev, ino in published:
            try:
                stat = target.stat()
                if (stat.st_dev, stat.st_ino) == (dev, ino):
                    target.unlink()
            except FileNotFoundError:
                pass
        try:
            dest.rmdir()
        except OSError:
            pass
        if isinstance(exc, QCError):
            raise
        raise QCError(5, f"분할 파일 저장 실패: {exc}") from exc
