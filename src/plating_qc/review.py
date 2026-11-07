"""원본을 변경하지 않는 프레임 비교와 검수 타일."""
import json
import os
import re
import tempfile
from pathlib import Path
from fractions import Fraction
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


def mixed_frame_hint(previous, current, candidate):
    """두 원본 프레임의 혼합에 가까운지만 검사한다. 최종 판정이 아니다."""
    separation = distance(previous, current)
    if separation < .12:
        return None
    endpoint_error = min(distance(previous, candidate), distance(current, candidate))
    if endpoint_error < .05:
        return None
    alternatives = []
    for numerator in (1, 2, 3):
        error = sum(abs((numerator*x + (4-numerator)*y)/4 - z) for x, y, z in zip(previous, current, candidate)) / (255 * len(previous))
        alternatives.append((error, numerator / 4))
    error, weight = min(alternatives)
    if error <= .04 and endpoint_error - error >= .04:
        return {"previous_weight": weight, "mixed_error": error, "nearest_source_error": endpoint_error}
    return None


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
    if any(x["timestamp_analysis"]["status"] != "observed" or x["timestamp_analysis"]["vfr_suspect"] is not False for x in (a, b)):
        warnings.append("PTS가 없거나 가변 속도가 의심되어 프레임 번호 기반 정렬을 확정할 수 없습니다")
        ambiguous = True
    if ambiguous:
        warnings.append("다른 소스이거나 반복 장면 등으로 정렬이 불확실합니다. 누락을 확정하지 않습니다")
    start, end = max(0, -offset), min(nb, na-offset)
    ranges = []
    changed = []
    current = None
    for i in range(start, end):
        if distance(af[i+offset], bf[i]) > threshold:
            changed.append(i)
            if current is None:
                current = [i, i]
            else:
                current[1] = i
        elif current is not None:
            ranges.append(current)
            current = None
    if current is not None:
        ranges.append(current)
    mix_suspects = []
    if not ambiguous:
        for i in changed[:1000]:
            j = i + offset
            for left, right in ((j-1, j), (j, j+1)):
                if left < 0 or right >= na:
                    continue
                hint = mixed_frame_hint(af[left], af[right], bf[i])
                if hint:
                    mix_suspects.append({"candidate_frame": i, "source_frames": [left, right], **hint})
                    break
    if len(changed) > 1000 and not ambiguous:
        warnings.append("차이 프레임이 1000개를 넘어 혼합 의심 검사는 앞 1000개만 수행했습니다")
    if mix_suspects:
        warnings.append("인접한 두 원본 프레임의 혼합과 유사한 프레임이 있습니다. 원본 해상도로 직접 확인하세요")
    if na != nb:
        warnings.append("디코딩 프레임 수가 다릅니다")
    if not ambiguous and offset != 0:
        warnings.append("정렬 후보가 0프레임이 아닙니다. 앞뒤 구간을 확인하세요")
    if ranges:
        warnings.append("정렬 후보에서 차이가 큰 구간이 있습니다. 원본 해상도로 검수하세요")
    return {"original": a, "candidate": b, "alignment": {"offset_candidate_to_original": None if ambiguous else offset, "score": best, "second_score": second, "uncertain": ambiguous, "estimated_missing_head": None if ambiguous else max(0, offset), "estimated_missing_tail": None if ambiguous else max(0, na - (offset + nb))}, "difference_ranges_candidate_frames": [] if ambiguous else ranges, "mixed_frame_suspects": mix_suspects, "threshold": threshold, "warnings": warnings, "notice": "축소 회색 프레임 기반의 검수 힌트입니다. 손상·누락·혼합 프레임의 확정 판정이 아닙니다."}


def tiles(source, out, config, fps=1, width=320, columns=5, rows=2, cuts=(), around=3):
    if not 0 < fps <= 30 or not 16 <= width <= 4096 or not 1 <= columns <= 20 or not 1 <= rows <= 20 or columns*rows > 100 or not 0 <= around <= 10:
        raise QCError(2, "타일 설정 범위가 올바르지 않습니다")
    info = probe(source, config)
    if info["timestamp_analysis"]["status"] != "observed":
        raise QCError(2, "원본 PTS가 없거나 검사되지 않아 정확한 타일 시간을 표시할 수 없습니다")
    count = info["video"]["nb_frames_decoded"]
    if count > 100000:
        raise QCError(2, "타임스탬프 검증을 위해 100000프레임 이하의 영상만 처리합니다")
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
        return p.stderr
    try:
        # FFmpeg에는 경로 없이 고정 파일명만 전달한다. 폴더의 %를 패턴으로 해석하지 않는다.
        with tempfile.TemporaryDirectory(prefix=".plating-qc-", dir=dest) as work:
            stage = Path(work)
            # 원본 프레임의 n과 PTS를 select 전에 그린다. 선택 후 번호를 붙이면 원본 번호가 아니다.
            label = "drawtext=text='F %{n} T %{pts\\:flt}':x=3:y=3:fontsize=min(max(8\\,h/12)\\,w/25):fontcolor=white:box=1:boxcolor=black@0.75"
            select = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{1 / fps:.12f})'"
            graph = f"showinfo@source,{label},{select},showinfo@selected,scale={width}:-2,tile={columns}x{rows}"
            log = invoke([ffmpeg, "-v", "info", "-nostdin", "-copyts", "-i", info["path"], "-vf", graph, "-fps_mode", "passthrough", "-threads", "1", "-n", "tiles_%03d.png"], work)
            timebase_match = re.search(r"showinfo@source[^\n]*config in time_base: (\d+/\d+)", log)
            source_frames = re.findall(r"showinfo@source[^\n]* n:\s*(\d+) pts:\s*(-?\d+)\s+pts_time:", log)
            selected_frames = re.findall(r"showinfo@selected[^\n]* n:\s*(\d+) pts:\s*(-?\d+)\s+pts_time:", log)
            if not timebase_match or len(source_frames) != count or not selected_frames:
                raise QCError(5, "프레임 번호·타임스탬프를 확인하지 못했습니다. 출력하지 않습니다")
            timebase = Fraction(timebase_match.group(1))
            source_by_pts = {}
            for number, pts in source_frames:
                source_by_pts.setdefault(int(pts), []).append(int(number))
            samples = []
            for _, pts in selected_frames:
                matches = source_by_pts.get(int(pts), [])
                if len(matches) != 1:
                    raise QCError(5, "타임스탬프 중복 또는 누락으로 원본 프레임을 특정할 수 없습니다")
                number = matches[0]
                samples.append({"frame": number, "pts": int(pts), "time_base": str(timebase), "seconds": float(int(pts) * timebase)})
            for position, sample in enumerate(samples):
                sample["tile"] = f"tiles_{position // (columns * rows) + 1:03d}.png"
                sample["cell"] = position % (columns * rows)
            created = sorted(p.name for p in stage.glob("tiles_*.png"))
            if not created or len(created) != (len(samples) + columns * rows - 1) // (columns * rows):
                raise QCError(5, "선택한 프레임과 생성된 타일 수가 일치하지 않습니다")
            for cut in sorted(set(cuts)):
                lo, hi = max(0,cut-around), min(count-1,cut+around)
                name = f"cut_{cut:06d}_{lo:06d}-{hi:06d}.png"
                invoke([ffmpeg,"-v","error","-nostdin","-copyts","-i",info["path"],"-vf",f"{label},select=between(n\\,{lo}\\,{hi}),tile={hi-lo+1}x1","-frames:v","1","-threads","1","-n",name], work)
                if not (stage / name).is_file():
                    raise QCError(5, f"컷 {cut} 이미지를 만들지 못했습니다")
                created.append(name)
            cut_frames = {str(cut): [{"frame": n, "pts": int(source_frames[n][1]), "time_base": str(timebase), "seconds": float(int(source_frames[n][1]) * timebase)} for n in range(max(0, cut-around), min(count-1, cut+around)+1)] for cut in sorted(set(cuts))}
            report = {"input": info["path"], "fps": fps, "grid": [columns,rows], "width": width, "cuts": list(sorted(set(cuts))), "cut_frames": cut_frames, "around": around, "files": created, "samples": samples, "time_origin": "원본 PTS; F는 0부터 시작하는 디코딩 프레임 번호, T는 원본 PTS 초(소수 6자리)", "warnings": info["warnings"]}
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


def write_comparison(report, out, config):
    """새 폴더에 보고서와 정렬된 원본 크기의 나란히 보기 이미지를 저장한다."""
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
    try:
        with tempfile.TemporaryDirectory(prefix=".plating-qc-", dir=dest) as work:
            stage = Path(work)
            a, b = report["original"], report["candidate"]
            alignment = report["alignment"]
            images = []
            ranges = report["difference_ranges_candidate_frames"]
            if not alignment["uncertain"]:
                offset = alignment["offset_candidate_to_original"]
                positions = [(lo + hi) // 2 for lo, hi in ranges[:10]] if ranges else [max(0, -offset)]
                width, height = a["video"]["width"], a["video"]["height"]
                if not width or not height:
                    raise QCError(5, "원본 크기를 확인하지 못했습니다")
                for frame in positions:
                    src = frame + offset
                    name = f"pair_original_{src:06d}_candidate_{frame:06d}.png"
                    # 왼쪽 원본은 그대로, 오른쪽 후보는 원본 크기로 축소한다.
                    graph = (f"[0:v]select=eq(n\\,{src}),setpts=PTS-STARTPTS[left];"
                             f"[1:v]select=eq(n\\,{frame}),scale={width}:{height},setpts=PTS-STARTPTS[right];"
                             "[left][right]hstack=inputs=2[out]")
                    args = [ffmpeg, "-v", "error", "-nostdin", "-i", a["path"], "-i", b["path"], "-filter_complex", graph, "-map", "[out]", "-frames:v", "1", "-threads", "1", "-n", name]
                    try:
                        result = subprocess.run(args, cwd=work, capture_output=True, text=True, errors="replace")
                    except OSError as exc:
                        raise QCError(4, f"ffmpeg 실행 실패: {exc}") from exc
                    if result.returncode or not (stage / name).is_file():
                        raise QCError(5, "비교 이미지 생성 실패: " + result.stderr[-2000:])
                    images.append({"file": name, "original_frame": src, "candidate_frame": frame})
            report["comparison_images"] = images
            report["comparison_images_truncated"] = len(ranges) > 10
            report["comparison_image_note"] = "왼쪽 원본, 오른쪽 원본 해상도로 맞춘 후보. 번호는 0부터 시작합니다." if images else "정렬이 불확실하여 비교 이미지를 만들지 않았습니다."
            (stage / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            lines = ["PLATING 프레임 비교", f"원본: {a['path']}", f"후보: {b['path']}", f"디코딩 프레임 수: 원본 {a['video']['nb_frames_decoded']}, 후보 {b['video']['nb_frames_decoded']}", f"해상도: 원본 {a['video']['width']}x{a['video']['height']}, 후보 {b['video']['width']}x{b['video']['height']}", f"평균 프레임 속도: 원본 {a['video']['avg_frame_rate']}, 후보 {b['video']['avg_frame_rate']}", f"정렬 점수: {alignment['score']}, 차순위 점수: {alignment['second_score']}", f"원본 대비 후보 정렬 오프셋: {alignment['offset_candidate_to_original']}", f"앞 누락 추정: {alignment['estimated_missing_head']}, 뒤 누락 추정: {alignment['estimated_missing_tail']}", f"차이 구간(후보 프레임, 0부터): {ranges}", f"혼합 의심 프레임: {report['mixed_frame_suspects']}", report["notice"], report["comparison_image_note"], *["경고: " + warning for warning in report["warnings"]], *["이미지: " + image["file"] for image in images]]
            if report["comparison_images_truncated"]:
                lines.append("이미지는 최대 10개만 저장했습니다. 전체 차이 구간은 JSON을 확인하세요.")
            (stage / "report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            for name in ["report.json", "report.txt", *[image["file"] for image in images]]:
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
        raise QCError(5, f"비교 보고서 저장 실패: {exc}") from exc
