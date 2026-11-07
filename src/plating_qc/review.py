"""원본을 변경하지 않는 프레임 비교와 검수 타일."""
import json
import os
import re
import tempfile
from pathlib import Path
from fractions import Fraction
import subprocess

from .core import QCError, executable, layout_names, probe
from .layout import checked_path
from .publish import publish


from .compare import compare, distance, frames, mixed_frame_hint, normalized_distance


def tiles(source, out, config, fps=1, width=320, columns=5, rows=2, cuts=(), around=3, scene_threshold=.3):
    if not 0 < fps <= 30 or not 16 <= width <= 4096 or not 1 <= columns <= 20 or not 1 <= rows <= 20 or columns*rows > 100 or not 0 <= around <= 10 or not 0 <= scene_threshold <= 1:
        raise QCError(2, "타일 설정 범위가 올바르지 않습니다")
    info = probe(source, config)
    if info["timestamp_analysis"]["status"] != "observed":
        raise QCError(2, "원본 PTS가 없거나 검사되지 않아 정확한 타일 시간을 표시할 수 없습니다")
    count = info["video"]["nb_frames_decoded"]
    if count > 100000:
        raise QCError(2, "타임스탬프 검증을 위해 100000프레임 이하의 영상만 처리합니다")
    if any(not isinstance(c, int) or c < 0 or c >= count for c in cuts):
        raise QCError(2, "컷 번호는 영상의 실제 프레임 범위 안에 있어야 합니다")
    dest = checked_path(Path(out))
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
            label_mode = "drawtext"
            select = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{1 / fps:.12f})'"
            graph = f"showinfo@source,{label},{select},showinfo@selected,scale={width}:-2,tile={columns}x{rows}"
            args = [ffmpeg, "-v", "info", "-nostdin", "-copyts", "-i", info["path"], "-vf", graph, "-fps_mode", "passthrough", "-threads", "1", "-n", "tiles_%03d.png"]
            try:
                log = invoke(args, work)
            except QCError as exc:
                font_errors = ("cannot find a valid font", "failed to load font",
                               "could not load font", "could not find font",
                               "no usable font", "fontconfig error")
                if exc.code != 5 or not any(message in str(exc).lower() for message in font_errors):
                    raise
                for partial in stage.glob("tiles_*.png"):
                    partial.unlink()
                label, label_mode = "null", "manifest"
                args[args.index("-vf") + 1] = f"showinfo@source,{label},{select},showinfo@selected,scale={width}:-2,tile={columns}x{rows}"
                log = invoke(args, work)
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
            # 장면 전환 점수는 후보일 뿐이며, 원본 PTS를 통해 프레임 번호와 매칭한다.
            scene_graph = f"select='gt(scene\\,{scene_threshold:.8f})',showinfo@scene"
            scene_log = invoke([ffmpeg, "-v", "info", "-nostdin", "-copyts", "-i", info["path"], "-vf", scene_graph, "-fps_mode", "passthrough", "-f", "null", "-"], work)
            scene_base = re.search(r"showinfo@scene[^\n]*config in time_base: (\d+/\d+)", scene_log)
            if not scene_base or Fraction(scene_base.group(1)) != timebase:
                raise QCError(5, "장면 후보의 시간 기준을 확인하지 못했습니다")
            scene_pts = re.findall(r"showinfo@scene[^\n]* n:\s*(\d+) pts:\s*(-?\d+)\s+pts_time:", scene_log)
            candidates = []
            for _, pts in scene_pts:
                matches = source_by_pts.get(int(pts), [])
                if len(matches) != 1:
                    raise QCError(5, "장면 후보의 원본 프레임을 특정할 수 없습니다")
                candidates.append({"frame": matches[0], "pts": int(pts), "time_base": str(timebase), "seconds": float(int(pts)*timebase)})
            scene_lines = ["장면 전환 후보입니다. 빠른 움직임일 수 있으므로 직접 확인하세요.", "frame (0 기반)\tPTS\ttime_base\t초"]
            scene_lines += [f"{item['frame']}\t{item['pts']}\t{item['time_base']}\t{item['seconds']:.6f}" for item in candidates]
            (stage / "scene_candidates.txt").write_text("\n".join(scene_lines) + "\n", encoding="utf-8")
            created.append("scene_candidates.txt")
            cut_frames = {str(cut): [{"frame": n, "pts": int(source_frames[n][1]), "time_base": str(timebase), "seconds": float(int(source_frames[n][1]) * timebase)} for n in range(max(0, cut-around), min(count-1, cut+around)+1)] for cut in sorted(set(cuts))}
            report = {"input": info["path"], "fps": fps, "grid": [columns,rows], "width": width, "cuts": list(sorted(set(cuts))), "cut_frames": cut_frames, "around": around, "scene_threshold": scene_threshold, "scene_candidates": candidates, "files": created, "samples": samples, "label_mode": label_mode, "time_origin": "원본 PTS; F는 0부터 시작하는 디코딩 프레임 번호, T는 원본 PTS 초(소수 6자리)", "warnings": info["warnings"]}
            (stage / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            # 하드링크는 같은 이름의 기존 파일이 생겨도 덮어쓰지 않는다.
            for name in [*created, "manifest.json"]:
                target = dest / name
                checked_path(target)
                publish(stage / name, target)
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
    dest = checked_path(Path(out))
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
                checked_path(target)
                publish(stage / name, target)
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
