import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from .core import QCError, convert, layout_names, load_config, probe
from .layout import checked_path
from .review import compare, tiles, write_comparison
from .split import split
from .runlog import json_default, reserve_log, source_hashes, tool_versions


def main(argv=None):
    # 결과 JSON·메시지는 콘솔 코드페이지와 무관하게 UTF-8로 낸다(cp1252 등에서 한글 출력 실패 방지).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):  # 테스트 등에서 StringIO로 바뀐 경우 제외
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="plating-qc")
    parser.add_argument("--config")
    parser.add_argument("--backend", choices=("ffmpeg", "blender"), default="ffmpeg")
    parser.add_argument("--log", help="새 JSON 로그 파일 경로(raw·새 출력 폴더 밖)")
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("probe")
    p.add_argument("files", nargs="+")
    p.add_argument("--json", action="store_true")
    c = subs.add_parser("convert")
    c.add_argument("input")
    c.add_argument("--scene")
    c.add_argument("--suffix", default="")
    c.add_argument("--profile", choices=("hq",), default="hq")
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--json", action="store_true")
    comp = subs.add_parser("compare")
    comp.add_argument("original")
    comp.add_argument("candidate")
    comp.add_argument("--search", type=int)
    comp.add_argument("--threshold", type=float, default=.02)
    comp.add_argument("--json", action="store_true")
    comp.add_argument("--out")
    tile = subs.add_parser("tiles")
    tile.add_argument("input")
    tile.add_argument("--out", required=True)
    tile.add_argument("--fps", type=float, default=1)
    tile.add_argument("--width", type=int, default=320)
    tile.add_argument("--grid", default="5x2")
    tile.add_argument("--cuts", default="")
    tile.add_argument("--around", type=int, default=3)
    tile.add_argument("--scene-threshold", type=float, default=.3)
    part = subs.add_parser("split")
    part.add_argument("input")
    part.add_argument("--out", required=True)
    part.add_argument("--max-part-mb", type=float)
    part.add_argument("--verify", action="store_true", help="호환 옵션: 프레임 검증은 항상 실행")
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(arguments)
    try:
        config = load_config(args.config)
        if args.log:
            log_path = args.log
        else:
            log_dir = checked_path(Path(os.environ.get("PLATING_QC_LOG_DIR") or Path.cwd() / "plating-qc-logs"))
            raw, _ = layout_names(config)
            if any(part.name.casefold() == raw.casefold() for part in (log_dir, *log_dir.parents)):
                raise QCError(2, "raw 폴더에는 로그를 쓸 수 없습니다")
            try:
                log_dir.mkdir(exist_ok=True)
            except OSError as exc:
                raise QCError(5, f"로그 폴더 생성 실패: {exc}") from exc
            log_path = log_dir / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + args.command + ".json")
        log = reserve_log(log_path, config, getattr(args, "out", None))
    except QCError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    started = datetime.now(timezone.utc).isoformat()
    start_clock = time.monotonic()
    versions = tool_versions(config) if log else None
    hashes = source_hashes() if log else None
    result, error, status = None, None, 0
    try:
        if args.backend != "ffmpeg":
            raise QCError(4, "Blender 백엔드는 아직 지원하지 않습니다")
        if args.command == "probe":
            result = [probe(path, config) for path in args.files]
            warnings = any(item.warnings for item in result)
        elif args.command == "compare":
            compare_config = config.get("compare", {})
            if not isinstance(compare_config, dict):
                raise QCError(2, "설정의 compare는 TOML 테이블이어야 합니다")
            search = args.search if args.search is not None else compare_config.get("search", 30)
            if not isinstance(search, int):
                raise QCError(2, "compare.search는 정수여야 합니다")
            result = compare(args.original, args.candidate, config, search, args.threshold)
            if args.out:
                result = write_comparison(result, args.out, config)
            warnings = bool(result["warnings"])
        elif args.command == "tiles":
            try:
                columns, rows = map(int, args.grid.lower().split("x"))
                cuts = [int(c) for c in args.cuts.split(",")] if args.cuts else []
            except ValueError as exc:
                raise QCError(2, "grid 또는 cuts 형식이 올바르지 않습니다") from exc
            result = tiles(args.input, args.out, config, args.fps, args.width, columns, rows, cuts, args.around, args.scene_threshold)
            warnings = bool(result["warnings"])
        elif args.command == "split":
            limit = args.max_part_mb if args.max_part_mb is not None else config.get("max_part_mb", 400)
            if not isinstance(limit, (int, float)):
                raise QCError(2, "max_part_mb는 숫자여야 합니다")
            result = split(args.input, args.out, config, limit)
            warnings = bool(result["warnings"])
        else:
            result = convert(args.input, args.scene, config, args.suffix, args.dry_run)
            warnings = bool(result.get("warnings"))
        status = 1 if warnings else 0
    except QCError as exc:
        error, status = str(exc), exc.code
    if log:
        record = {"started_utc": started, "duration_s": round(time.monotonic()-start_clock, 6), "cwd": str(Path.cwd()), "argv": arguments, "tools": versions, "source_sha256": hashes, "exit_code": status, "result": result, "error": error}
        try:
            with log:
                json.dump(record, log, ensure_ascii=False, indent=2, allow_nan=False, default=json_default)
                log.write("\n")
        except (OSError, TypeError, ValueError) as exc:
            if result is not None:
                print(json.dumps(result, ensure_ascii=False, indent=2, default=json_default))
            print(f"작업 종료 코드 {status}; 로그 기록 실패: {exc}", file=sys.stderr)
            return 5
    if error is not None:
        print(error, file=sys.stderr)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=json_default))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
