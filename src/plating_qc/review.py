"""원본을 변경하지 않는 프레임 비교와 검수 타일."""
import json
import os
import tempfile
from pathlib import Path
import subprocess

from .core import QCError, executable, layout_names, probe


def frames(path, config, width, height, count):
    # 작은 회색 프레임도 전체 길이에 비례한다. 예상 메모리가 크면 중단한다.
    if width * height * count > 128 * 1024 * 1024:
        raise QCError(2, "비교 영상이 너무 깁니다. 짧은 구간으로 나눠 확인하세요")
    cmd = [executable("ffmpeg", config), "-v", "error", "-nostdin", "-i", str(path), "-map", "0:v:0", "-vf", f"scale={width}:{height},format=gray", "-fps_mode", "passthrough", "-f", "rawvideo", "-"]
    try:
        result = subprocess.run(cmd, capture_output=True)
    except OSError as exc:
        raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
    if result.returncode:
        raise QCError(5, "프레임 디코딩 실패: " + result.stderr.decode(errors="replace")[-2000:])
    size = width * height
    if len(result.stdout) != count * size:
        raise QCError(5, "비교용 디코딩 프레임 수가 probe 결과와 다릅니다")
    return [memoryview(result.stdout)[i:i+size] for i in range(0, len(result.stdout), size)]


def distance(a, b):
    return sum(abs(x-y) for x, y in zip(a, b)) / (255 * len(a))


def compare(original, candidate, config, search=30, threshold=.02):
    if not 0 <= search <= 300 or not 0 <= threshold <= 1:
        raise QCError(2, "search는 0~300, threshold는 0~1이어야 합니다")
    a, b = probe(original, config), probe(candidate, config)
    na, nb = a["video"]["nb_frames_decoded"], b["video"]["nb_frames_decoded"]
    if na < 1 or nb < 1:
        raise QCError(5, "비교할 프레임이 없습니다")
    af = frames(a["path"], config, 64, 36, na)
    bf = frames(b["path"], config, 64, 36, nb)
    # 전체 겹치는 구간에서 최대 12개의 표본을 비교한다. 반복 장면은 애매함으로 처리한다.
    scores = []
    for offset in range(-min(search, nb-1), min(search, na-1)+1):
        start, end = max(0, -offset), min(nb, na-offset)
        overlap = end - start
        if overlap < min(5, na, nb):
            continue
        positions = sorted({start + (overlap-1)*i//11 for i in range(12)})
        score = sum(distance(af[i+offset], bf[i]) for i in positions)/len(positions)
        scores.append((score, offset))
    if not scores:
        raise QCError(5, "정렬할 겹치는 프레임이 부족합니다")
    scores.sort()
    best, offset = scores[0]
    second = scores[1][0] if len(scores)>1 else None
    ambiguous = best > .15 or (second is not None and second-best < .002)
    warnings = list(a["warnings"]) + list(b["warnings"])
    if a["video"]["avg_frame_rate"] != b["video"]["avg_frame_rate"]:
        warnings.append("프레임 속도가 다릅니다. 프레임 정렬 결과를 신뢰할 수 없습니다")
        ambiguous = True
    if ambiguous:
        warnings.append("다른 소스이거나 반복 장면 등으로 정렬이 불확실합니다. 누락을 확정하지 않습니다")
    start, end = max(0, -offset), min(nb, na-offset)
    ranges = []
    current = None
    for i in range(start, end):
        if distance(af[i+offset], bf[i]) > threshold:
            if current is None:
                current = [i, i]
            else:
                current[1] = i
        elif current is not None:
            ranges.append(current)
            current = None
    if current is not None:
        ranges.append(current)
    if na != nb:
        warnings.append("디코딩 프레임 수가 다릅니다")
    if not ambiguous and offset != 0:
        warnings.append("정렬 후보가 0프레임이 아닙니다. 앞뒤 구간을 확인하세요")
    if ranges:
        warnings.append("정렬 후보에서 차이가 큰 구간이 있습니다. 원본 해상도로 검수하세요")
    return {"original": a, "candidate": b, "alignment": {"offset_candidate_to_original": None if ambiguous else offset, "score": best, "second_score": second, "uncertain": ambiguous, "estimated_missing_head": None if ambiguous else max(0, offset), "estimated_missing_tail": None if ambiguous else max(0, na - (offset + nb))}, "difference_ranges_candidate_frames": [] if ambiguous else ranges, "threshold": threshold, "warnings": warnings, "notice": "축소 회색 프레임 기반의 검수 힌트입니다. 손상·누락·혼합 프레임의 확정 판정이 아닙니다."}


def tiles(source, out, config, fps=1, width=320, columns=5, rows=2, cuts=(), around=3):
    if not 0 < fps <= 30 or not 16 <= width <= 4096 or not 1 <= columns <= 20 or not 1 <= rows <= 20 or columns*rows > 100 or not 0 <= around <= 10:
        raise QCError(2, "타일 설정 범위가 올바르지 않습니다")
    info = probe(source, config)
    count = info["video"]["nb_frames_decoded"]
    if any(not isinstance(c, int) or c < 0 or c >= count for c in cuts):
        raise QCError(2, "컷 번호는 영상의 실제 프레임 범위 안에 있어야 합니다")
    dest = Path(out).resolve()
    raw, _ = layout_names(config)
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
    def invoke(args, workdir):
        try:
            p = subprocess.run(args, cwd=workdir, capture_output=True, text=True, errors="replace")
        except OSError as exc:
            raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
        if p.returncode:
            raise QCError(5, "타일 생성 실패: " + p.stderr[-2000:])
    try:
        # FFmpeg에는 경로 없이 고정 파일명만 전달한다. 폴더의 %를 패턴으로 해석하지 않는다.
        with tempfile.TemporaryDirectory(prefix=".plating-qc-", dir=dest) as work:
            stage = Path(work)
            invoke([ffmpeg, "-v", "error", "-nostdin", "-i", info["path"], "-vf", f"fps={fps},scale={width}:-2,tile={columns}x{rows}", "-fps_mode", "passthrough", "-threads", "1", "-n", "tiles_%03d.png"], work)
            created = sorted(p.name for p in stage.glob("tiles_*.png"))
            if not created:
                raise QCError(5, "타일 이미지가 생성되지 않았습니다")
            for cut in sorted(set(cuts)):
                lo, hi = max(0,cut-around), min(count-1,cut+around)
                name = f"cut_{cut:06d}_{lo:06d}-{hi:06d}.png"
                invoke([ffmpeg,"-v","error","-nostdin","-i",info["path"],"-vf",f"select=between(n\\,{lo}\\,{hi}),tile={hi-lo+1}x1","-frames:v","1","-threads","1","-n",name], work)
                if not (stage / name).is_file():
                    raise QCError(5, f"컷 {cut} 이미지를 만들지 못했습니다")
                created.append(name)
            report = {"input": info["path"], "fps": fps, "grid": [columns,rows], "width": width, "cuts": list(sorted(set(cuts))), "around": around, "files": created, "warnings": info["warnings"] + ["타일 칸에 프레임 번호와 타임코드는 표시되지 않습니다. 컷 이미지 파일명은 0부터 시작하는 원본 프레임 범위입니다."]}
            (stage / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            # 하드링크는 같은 이름의 기존 파일이 생겨도 덮어쓰지 않는다.
            for name in [*created, "manifest.json"]:
                target = dest / name
                try:
                    os.link(stage / name, target)
                except FileExistsError as exc:
                    raise QCError(3, f"출력 파일이 이미 있습니다: {target}") from exc
                stat = target.stat()
                published.append((target, stat.st_dev, stat.st_ino))
        return report
    except (QCError, OSError) as exc:
        for target, device, inode in published:
            try:
                stat = target.stat()
                if (stat.st_dev, stat.st_ino) == (device, inode):
                    target.unlink()
            except FileNotFoundError:
                pass
        try:
            dest.rmdir()
        except OSError:
            pass
        if isinstance(exc, QCError):
            raise
        raise QCError(5, f"타일 저장 실패: {exc}") from exc
