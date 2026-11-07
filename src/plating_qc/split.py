"""ProRes를 검증 가능한 조각으로 나누는 오프라인 도구."""
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

from .core import QCError, executable, layout_names, probe


def run(args, cwd=None):
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, errors="replace")
    except OSError as exc:
        raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
    if result.returncode:
        raise QCError(5, "분할 또는 검증 실패: " + result.stderr[-2000:])
    return result.stdout


def frame_hashes(path, ffmpeg):
    data = run([ffmpeg, "-v", "error", "-nostdin", "-i", str(path), "-map", "0:v:0", "-f", "framemd5", "-"])
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


def split(source, out, config, max_part_mb=400):
    if not math.isfinite(max_part_mb) or max_part_mb <= 0:
        raise QCError(2, "max-part-mb는 0보다 큰 숫자여야 합니다")
    info = probe(source, config)
    if info["video"]["codec"] != "prores":
        raise QCError(2, "ProRes 영상만 무재인코딩 분할할 수 있습니다")
    if info["video"]["r_frame_rate"] != info["video"]["avg_frame_rate"]:
        raise QCError(2, "가변 프레임 속도 의심 영상은 분할 전 타이밍 검수가 필요합니다")
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
    dest = Path(out).resolve()
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
            run([ffmpeg, "-v", "error", "-nostdin", "-i", info["path"], "-map", "0:v:0", "-map", "0:a?", "-c", "copy", "-f", "segment", "-segment_format", "mov", "-segment_time", f"{segment_time:.9f}", "-reset_timestamps", "1", "-n", "part_%03d.mov"], cwd=work)
            parts = sorted(stage.glob("part_*.mov"))
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
                details.append({"file": part.name, "bytes": part_size, "frames": len(hashes)})
            if joined != original or len(original) != info["video"]["nb_frames_decoded"]:
                raise QCError(1, "분할 전후 프레임 검증이 일치하지 않습니다. 결과를 저장하지 않았습니다")
            report = {"input": info["path"], "limit_bytes": limit, "parts": details, "frames_verified": len(original), "warnings": ["영상 프레임만 검증했습니다. 오디오 및 편집기에서의 경계 재생은 별도 확인하세요."]}
            (stage / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            for part in [*parts, stage / "manifest.json"]:
                target = dest / part.name
                try:
                    os.link(part, target)
                except FileExistsError as exc:
                    raise QCError(3, f"출력 파일이 이미 있습니다: {target}") from exc
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
