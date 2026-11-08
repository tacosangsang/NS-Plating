# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
# 실행: Blender Python Console에서 runpy.run_path(__file__ 경로)["main"]([인자...]).
# 외부 Python 3.12 이상 실행 파일을 --python으로 지정한다. 설치는 하지 않는다.
"""Blender 현재 장면의 사본을 저장하고 blockout new-version에 위임한다."""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Final
from uuid import uuid4

REPO: Final = Path(__file__).resolve().parents[2]
EXTERNAL_COLLECTIONS: Final = ("images", "libraries", "movieclips", "sounds", "fonts", "cache_files", "volumes")


class SaveError(RuntimeError):
    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        super().__init__(f"{reason}: {path}")


def main(argv: list[str] | None = None) -> int:
    """원본 .blend를 덮어쓰지 않는다. 실패한 임시 사본은 진단용으로 남긴다."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--change", required=True)
    parser.add_argument("--by", required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=REPO / "plating.toml")
    parser.add_argument("--set-current", action="store_true")
    if argv is None:
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[\w-]+", args.asset):
        parser.error("asset은 경로가 아닌 단일 이름이어야 함")
    if any(not value.strip() or "\n" in value or "\r" in value for value in (args.change, args.by)):
        parser.error("--change와 --by는 비어 있지 않은 한 줄이어야 함")
    python = args.python.resolve()
    config = args.config.resolve()
    if not python.is_file() or not config.is_file():
        parser.error("존재하는 --python 실행 파일과 --config TOML 필요")

    import bpy

    directory = (REPO / "out" / "blockout-save" / uuid4().hex).resolve()
    if not directory.is_relative_to(REPO):
        raise SaveError(directory, "저장소 밖 임시 저장 금지")
    directory.mkdir(parents=True, exist_ok=False)
    snapshot = directory / f"{args.asset}.blend"
    print(f"블록아웃 임시 사본: {snapshot}")
    # 사본은 versions/vNNN/로 옮겨지므로 원본 기준 상대 경로는 깨진다. 저장하는 동안만 절대 경로로 바꾸고 되돌린다.
    external = [item for collection in EXTERNAL_COLLECTIONS for item in getattr(bpy.data, collection)
                if item.library is None and item.filepath.startswith("//")]
    original = [item.filepath for item in external]
    try:
        for item in external:
            item.filepath = bpy.path.abspath(item.filepath)
        saved = bpy.ops.wm.save_as_mainfile(filepath=str(snapshot), copy=True, relative_remap=False, check_existing=False)
    finally:
        for item, path in zip(external, original):
            item.filepath = path
    if "FINISHED" not in saved or not snapshot.is_file():
        raise SaveError(snapshot, "Blender 임시 저장 실패")
    command = [str(python), "-m", "plating_tools", "--config", str(config), "blockout", "new-version", args.asset,
               "--root", str(args.root.resolve()), "--from", str(snapshot), "--change", args.change, "--by", args.by]
    if args.set_current:
        command.append("--set-current")
    inherited = os.environ.get("PYTHONPATH", "")
    env = {**os.environ, "PYTHONPATH": str(REPO / "src") + (os.pathsep + inherited if inherited else ""),
           "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(command, cwd=REPO, env=env, shell=False, check=False,
                            capture_output=True, text=True, encoding="utf-8")
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode == 0:
        snapshot.unlink()
        directory.rmdir()
    else:
        print(f"실패한 임시 사본 보존: {snapshot}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
