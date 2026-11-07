"""읽기 전용 영상 확인과 덮어쓰기 없는 ProRes 변환."""
import math
import os
from pathlib import Path
import tempfile
from .config import load_config
from .errors import QCError
from .layout import SceneLayout, checked_path
from .model import ProresRequest
from .publish import publish


from .backend.ffmpeg_helpers import analyze_timestamps, executable, frame_timestamps, run


def probe(path, config):
    from .backend import make_backend

    return make_backend(config).probe(Path(path))


def layout_names(config):
    return SceneLayout.from_config(config).names()


def convert(source, scene, config, suffix="", dry_run=False):
    if suffix and (not suffix.startswith("_") or any(c in suffix for c in ("/", "\\", ":")) or suffix in {"_", "_.."}):
        raise QCError(2, "접미사는 밑줄로 시작하는 파일 이름이어야 합니다")
    info = probe(source, config)
    if info.timestamp_analysis.status in ("unavailable", "not_checked"):
        raise QCError(2, "원본 PTS를 확인하거나 생성할 수 없어 안전하게 변환할 수 없습니다")
    source = Path(info.path)
    raw, prores = layout_names(config)
    if scene is None:
        raw_dir = next((p for p in source.parents if p.name.casefold() == raw.casefold()), None)
        if raw_dir is None:
            raise QCError(2, "씬 폴더를 지정하거나 raw 폴더 안의 입력을 사용하세요")
        scene = raw_dir.parent
    scene = Path(scene).resolve()
    if not scene.is_dir():
        raise QCError(2, "씬 폴더가 없습니다")
    out_dir = (scene / prores).resolve()
    if any(p.name.casefold() == raw.casefold() for p in (out_dir, *out_dir.parents)) or out_dir.parent != scene:
        raise QCError(2, "raw 폴더 또는 씬 밖으로 출력할 수 없습니다")
    base_suffix = config.get("suffix", "_prores422hq")
    if not isinstance(base_suffix, str) or not base_suffix.startswith("_") or any(c in base_suffix for c in ("/", "\\", ":")):
        raise QCError(2, "설정의 suffix는 밑줄로 시작하는 파일 이름이어야 합니다")
    out = out_dir / (source.stem + base_suffix + suffix + ".mov")
    checked_path(out)
    if out.exists() or out.is_symlink():
        raise QCError(3, f"출력 파일이 이미 있습니다: {out}")
    colors = info.video.color
    if any(v not in (None, "unknown", "bt709") for v in (colors.primaries, colors.transfer, colors.space)):
        raise QCError(1, f"입력 색 태그가 BT.709와 다릅니다: {colors}")
    from .backend import make_backend

    backend = make_backend(config)
    duration = None
    if info.audio:
        duration = info.video.duration_s
        try:
            duration = float(duration)
            if duration <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise QCError(2, "영상 길이를 확인할 수 없어 오디오 패딩을 안전하게 적용할 수 없습니다")
    request = ProresRequest(source, None, info.timestamp_analysis.status == "generated", duration)
    if dry_run:
        return {"input": str(source), "output": str(out), "command": backend.describe_prores(request)}
    try:
        out_dir.mkdir(exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".plating-qc-", suffix=".partial.mov", dir=out_dir)
        os.close(fd)
    except OSError as exc:
        raise QCError(5, f"출력 폴더 또는 임시 파일 생성 실패: {exc}") from exc
    temp = Path(temporary)
    try:
        request = ProresRequest(source, temp, request.generate_pts, request.audio_duration)
        backend.encode_prores(request)
        result = probe(temp, config)
        before, after = info.video, result.video
        problems = []
        extra_warnings = []
        for key in ("width", "height", "nb_frames_decoded"):
            if getattr(before, key) != getattr(after, key):
                problems.append(f"{key}: {getattr(before, key)} → {getattr(after, key)}")
        if before.avg_frame_rate != after.avg_frame_rate:
            if info.timestamp_analysis.vfr_suspect:
                extra_warnings.append("가변 속도 영상의 평균 fps 메타데이터가 변했습니다. 프레임별 상대 PTS를 별도로 검증했습니다")
            else:
                problems.append(f"avg_frame_rate: {before.avg_frame_rate} → {after.avg_frame_rate}")
        # 시작점 차이를 제외한 모든 프레임의 상대 PTS를 검증한다.
        source_pts = backend.timestamps(source, generated=info.timestamp_analysis.status == "generated")
        result_pts = backend.timestamps(temp)
        if (len(source_pts) != len(result_pts) or not source_pts or
                any(x is None for x in source_pts) or any(x is None for x in result_pts)):
            problems.append("프레임별 PTS를 비교할 수 없음")
        else:
            max_error = max(abs((a-source_pts[0])-(b-result_pts[0])) for a, b in zip(source_pts, result_pts))
            if max_error > .001:
                problems.append(f"프레임별 상대 PTS 최대 차이 {max_error:.6f}초")
        try:
            input_start, output_start = float(before.start_time_s), float(after.start_time_s)
            if not math.isfinite(input_start) or not math.isfinite(output_start):
                raise ValueError
            if abs(input_start - output_start) > .001:
                extra_warnings.append(f"영상 절대 시작 시각이 {input_start:.6f}초에서 {output_start:.6f}초로 이동했습니다")
        except (TypeError, ValueError):
            extra_warnings.append("영상 절대 시작 시각을 비교하지 못했습니다")
        if info.audio:
            try:
                in_audio = float(info.audio.start_time_s)
                out_audio = float(result.audio.start_time_s)
                if not all(math.isfinite(x) for x in (in_audio, out_audio, input_start, output_start)):
                    raise ValueError
                if abs((in_audio-input_start)-(out_audio-output_start)) > .001:
                    extra_warnings.append("오디오와 영상의 상대 시작 시각이 달라졌습니다. 편집기에서 동기화를 확인하세요")
            except (TypeError, ValueError, AttributeError, UnboundLocalError):
                extra_warnings.append("오디오와 영상의 상대 시작 시각을 확인하지 못했습니다")
        if after.profile != "HQ" or after.pix_fmt != "yuv422p10le" or any(v != "bt709" for v in (after.color.primaries, after.color.transfer, after.color.space)):
            problems.append("출력 프로파일·픽셀 형식·색 태그 불일치")
        if info.audio:
            try:
                if not result.audio or float(result.audio.duration_s) + 0.001 < float(before.duration_s):
                    problems.append("출력 오디오 길이 부족")
            except (TypeError, ValueError):
                problems.append("출력 오디오 길이 확인 불가")
        if problems:
            raise QCError(1, "변환 결과 검증 실패: " + "; ".join(problems))
        publish(temp, out)
        from dataclasses import replace

        result = replace(result, path=str(out))
        return {"input": info, "output": result, "warnings": [*info.warnings, *result.warnings, *extra_warnings]}
    finally:
        temp.unlink(missing_ok=True)
