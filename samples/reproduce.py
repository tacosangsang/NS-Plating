"""임시 합성 영상으로 다섯 명령과 개별 실행 로그를 재현한다."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from plating_qc.core import QCError, executable, load_config


def main():
    parser = argparse.ArgumentParser(description="임시 합성 영상으로 PLATING QC 실행")
    parser.add_argument("--config", help="기존 plating-qc.toml 경로; 지정하지 않으면 상위 폴더에서 탐색")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        ffmpeg = executable("ffmpeg", config)
    except QCError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    work = Path(tempfile.mkdtemp(prefix="plating-qc-sample-"))
    raw = work / "scene" / "raw"
    raw.mkdir(parents=True)
    source = raw / "sample.mp4"
    print(f"임시 결과 폴더: {work}", flush=True)
    create = subprocess.run([ffmpeg, "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24:duration=2", "-c:v", "mpeg4", "-q:v", "4", str(source)], capture_output=True, text=True, errors="replace")
    if create.returncode:
        print("합성 영상 생성 실패: " + create.stderr[-2000:], file=sys.stderr)
        return 5
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    def run(name, command):
        prefix = [sys.executable, "-m", "plating_qc"]
        if args.config:
            prefix += ["--config", str(Path(args.config).resolve())]
        prefix += ["--log", str(work / (name + ".json"))]
        completed = subprocess.run([*prefix, *command], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if not completed.stdout:
            raise RuntimeError(f"{name}: 종료 {completed.returncode}; {completed.stderr.strip()}")
        try:
            data = json.loads(completed.stdout)
        except ValueError as exc:
            raise RuntimeError(f"{name}: JSON 응답을 읽지 못했습니다") from exc
        if completed.returncode not in (0, 1):
            raise RuntimeError(f"{name}: 종료 {completed.returncode}; {completed.stderr.strip()}")
        print(f"{name}: 종료 {completed.returncode}; 로그 {work / (name + '.json')}", flush=True)
        return data
    try:
        first = run("probe", ["probe", str(source)])
        result = run("convert", ["convert", str(source)])
        movie = Path(result["output"]["path"])
        # 같은 합성 영상을 양쪽에 넣어 출력 경로와 이미지 생성을 보여 주는 예시다.
        compared = run("compare", ["compare", str(source), str(source), "--search", "0", "--out", str(work / "comparison")])
        tiled = run("tiles", ["tiles", str(source), "--out", str(work / "tiles"), "--cuts", "24", "--around", "1"])
        limit = movie.stat().st_size / (1024 * 1024) * .55
        pieces = run("split", ["split", str(movie), "--out", str(work / "parts"), "--max-part-mb", str(limit)])
    except (RuntimeError, OSError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 5
    print(f"원본 {first[0]['video']['nb_frames_decoded']}프레임, 변환 {result['output']['video']['nb_frames_decoded']}프레임, 비교 이미지 {len(compared['comparison_images'])}장")
    print(f"타일 프레임 {[x['frame'] for x in tiled['samples']]}, 분할 {[x['frames'] for x in pieces['parts']]}프레임, 검증 {pieces['frames_verified']}프레임")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
