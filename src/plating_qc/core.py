"""읽기 전용 영상 확인과 덮어쓰기 없는 ProRes 변환."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib


class QCError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def executable(name, config):
    selected = config.get(name + "_path") or shutil.which(name)
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


def load_config(path=None):
    if path:
        candidates = [Path(path)]
    else:
        candidates = [p / "plating-qc.toml" for p in (Path.cwd(), *Path.cwd().parents)]
    for candidate in candidates:
        if candidate.is_file():
            try:
                with candidate.open("rb") as stream:
                    data = tomllib.load(stream)
                return data
            except (OSError, tomllib.TOMLDecodeError) as exc:
                raise QCError(2, f"설정 오류: {exc}") from exc
    if path:
        raise QCError(2, f"설정 파일이 없습니다: {path}")
    return {}


def probe(path, config):
    path = Path(path).resolve()
    if not path.is_file():
        raise QCError(2, f"입력 파일이 없습니다: {path}")
    result = run([executable("ffprobe", config), "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)])
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
    if result.stderr.strip():
        warnings.append("디코딩 경고: " + result.stderr.strip()[-1000:])
    avg, rate = video.get("avg_frame_rate"), video.get("r_frame_rate")
    if avg and rate and avg != rate:
        warnings.append("가변 프레임 속도 의심: 타이밍을 확인하세요")
    return {"path": str(path), "video": {"codec": video.get("codec_name"), "width": video.get("width"), "height": video.get("height"), "pix_fmt": video.get("pix_fmt"), "r_frame_rate": rate, "avg_frame_rate": avg, "nb_frames_meta": int(meta) if meta and str(meta).isdigit() else None, "nb_frames_decoded": int(count), "duration_s": video.get("duration"), "profile": video.get("profile"), "color": {"primaries": video.get("color_primaries", "unknown"), "transfer": video.get("color_transfer", "unknown"), "space": video.get("color_space", "unknown")}}, "audio": None if audio is None else {"codec": audio.get("codec_name"), "sample_rate": audio.get("sample_rate"), "channels": audio.get("channels"), "duration_s": audio.get("duration")}, "warnings": warnings}


def convert(source, scene, config, suffix="", dry_run=False):
    if suffix and (not suffix.startswith("_") or any(c in suffix for c in ("/", "\\", ":")) or suffix in {"_", "_.."}):
        raise QCError(2, "접미사는 밑줄로 시작하는 파일 이름이어야 합니다")
    info = probe(source, config)
    source = Path(info["path"])
    layout = config.get("layout", {})
    raw, prores = layout.get("raw", "raw"), layout.get("prores", "prores")
    if any(not isinstance(x, str) or x in ("", ".", "..") or "/" in x or "\\" in x for x in (raw, prores)) or raw.casefold() == prores.casefold():
        raise QCError(2, "raw/prores 설정은 서로 다른 단일 폴더 이름이어야 합니다")
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
    if out.exists() or out.is_symlink():
        raise QCError(3, f"출력 파일이 이미 있습니다: {out}")
    colors = info["video"]["color"]
    if any(v not in (None, "unknown", "bt709") for v in colors.values()):
        raise QCError(1, f"입력 색 태그가 BT.709와 다릅니다: {colors}")
    ffmpeg = executable("ffmpeg", config)
    args = [ffmpeg, "-v", "error", "-nostdin", "-i", str(source), "-map", "0:v:0", "-map", "0:a:0?", "-vf", "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709", "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-vendor", "apl0", "-fps_mode", "passthrough", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+write_colr", "-c:a", "pcm_s16le"]
    if info["audio"]:
        duration = info["video"]["duration_s"]
        try:
            duration = float(duration)
            if duration <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise QCError(2, "영상 길이를 확인할 수 없어 오디오 패딩을 안전하게 적용할 수 없습니다")
        args += ["-af", f"apad=whole_dur={duration:.9f}"]
    if dry_run:
        return {"input": str(source), "output": str(out), "command": args + ["<임시 출력 파일>"]}
    out_dir.mkdir(exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".plating-qc-", suffix=".partial.mov", dir=out_dir)
    os.close(fd)
    temp = Path(temporary)
    try:
        run(args + ["-y", str(temp)])
        result = probe(temp, config)
        before, after = info["video"], result["video"]
        problems = []
        for key in ("width", "height", "nb_frames_decoded", "avg_frame_rate"):
            if before[key] != after[key]:
                problems.append(f"{key}: {before[key]} → {after[key]}")
        if after["profile"] != "HQ" or after["pix_fmt"] != "yuv422p10le" or any(v != "bt709" for v in after["color"].values()):
            problems.append("출력 프로파일·픽셀 형식·색 태그 불일치")
        if info["audio"]:
            try:
                if not result["audio"] or float(result["audio"]["duration_s"]) + 0.001 < float(before["duration_s"]):
                    problems.append("출력 오디오 길이 부족")
            except (TypeError, ValueError):
                problems.append("출력 오디오 길이 확인 불가")
        if problems:
            raise QCError(1, "변환 결과 검증 실패: " + "; ".join(problems))
        try:
            os.link(temp, out)
        except FileExistsError as exc:
            raise QCError(3, f"변환 중 출력 파일이 생겼습니다: {out}") from exc
        except OSError as exc:
            raise QCError(5, f"덮어쓰기 방지 저장 실패: {exc}") from exc
        result["path"] = str(out)
        return {"input": info, "output": result, "warnings": info["warnings"] + result["warnings"]}
    finally:
        temp.unlink(missing_ok=True)
