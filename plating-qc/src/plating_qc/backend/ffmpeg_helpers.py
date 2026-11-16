"""FFmpeg 경로, 프로세스 및 타임스탬프 검사."""
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import subprocess
from fractions import Fraction

from ..errors import QCError


def executable(name, config):
    selected = config.get(name + "_path")
    if not selected and name == "ffprobe" and config.get("ffmpeg_path"):
        base = Path(config["ffmpeg_path"])
        selected = str(base if base.is_dir() else base.parent)
    selected = selected or shutil.which(name)
    if selected and Path(selected).is_dir():
        selected = str(Path(selected) / (name + (".exe" if os.name == "nt" else "")))
    if not selected or not Path(selected).is_file():
        raise QCError(4, f"{name} 실행 파일을 찾지 못했습니다: {selected or name}")
    return str(selected)


def run(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, errors="replace")
    except OSError as exc:
        raise QCError(4, f"실행 실패: {exc}") from exc
    if result.returncode:
        raise QCError(5, "미디어 처리 실패: " + result.stderr[-3000:])
    return result


def frame_timestamps(path, ffprobe, generated=False):
    options = ["-fflags", "+genpts"] if generated else []
    data = run([ffprobe, "-v", "error", *options, "-select_streams", "v:0", "-show_frames", "-show_entries", "frame=pts_time", "-of", "json", str(path)])
    try:
        rows = json.loads(data.stdout)["frames"]
        times = []
        for row in rows:
            try:
                value = float(row["pts_time"])
                times.append(value if math.isfinite(value) else None)
            except (KeyError, TypeError, ValueError):
                times.append(None)
        return times
    except (ValueError, KeyError, TypeError) as exc:
        raise QCError(5, "프레임 타임스탬프를 읽지 못했습니다") from exc


def analyze_timestamps(path, ffprobe, count, avg_rate, base_rate):
    if count > 100000:
        return {"status": "not_checked", "missing_count": None, "vfr_suspect": None, "interval_stddev_s": None, "rates_differ": None}
    times = frame_timestamps(path, ffprobe)
    if len(times) != count:
        raise QCError(5, "프레임 수와 타임스탬프 수가 다릅니다")
    missing = sum(t is None for t in times)
    if missing:
        generated = frame_timestamps(path, ffprobe, generated=True)
        recovered = len(generated) == count and all(t is not None for t in generated)
        return {"status": "generated" if recovered else "unavailable", "missing_count": missing, "vfr_suspect": None, "interval_stddev_s": None, "rates_differ": None}
    try:
        avg, base = Fraction(avg_rate), Fraction(base_rate)
        if avg <= 0 or base <= 0:
            raise ValueError
        nominal = float(1 / avg)
        rates_differ = avg != base
    except (TypeError, ValueError, ZeroDivisionError):
        nominal, rates_differ = None, None
    intervals = [b-a for a, b in zip(times, times[1:])]
    if not intervals:
        return {"status": "observed", "missing_count": 0, "vfr_suspect": bool(rates_differ) if rates_differ is not None else None, "interval_stddev_s": None, "rates_differ": rates_differ}
    stddev = statistics.pstdev(intervals)
    if nominal is None:
        positive = [d for d in intervals if d > 0]
        nominal = statistics.median(positive) if positive else None
    irregular = any(d <= 0 for d in intervals) or (nominal is not None and stddev > 0.05 * nominal)
    suspected = bool(rates_differ or irregular) if nominal is not None else None
    return {"status": "observed", "missing_count": 0, "vfr_suspect": suspected, "interval_stddev_s": stddev, "rates_differ": rates_differ}
