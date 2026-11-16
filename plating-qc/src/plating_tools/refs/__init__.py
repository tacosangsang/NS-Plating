"""refs check 실행 경계. P0에서는 이 패키지를 불러오지 않는다."""
import html
import math
import re
import tomllib
from argparse import Namespace
from dataclasses import replace
from pathlib import Path

from .. import __version__
from ..config import Config
from ..docs import Anchor, WorkflowDir, resolve as resolve_anchor
from ..errors import InputError, Unavailable
from ..model import Finding, RefEntry, Severity, json_text
from ..output import RunDir, new_target
from ..profile_plating import ANCHOR_SPECS, DOC_TITLES
from ..textio import read_document
from .check import RefResult, check_numbers, check_references, count_advice
from .fetch import UrllibFetcher
from .images import FFmpegImageTool, ImageInfo, ImageTool


def load_entries(path: Path) -> tuple[RefEntry, ...]:
    try:
        data = tomllib.loads(read_document(path, "refs").text)
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"레퍼런스 TOML 오류: {exc}") from exc
    rows = data.get("reference")
    if not isinstance(rows, list) or not rows:
        raise InputError("비어 있지 않은 [[reference]] 목록 필요")
    entries = []
    for row in rows:
        if not isinstance(row, dict) or type(row.get("index")) is not int or row["index"] < 1:
            raise InputError("reference.index: 양의 정수 필요")
        for key in ("role", "local_path", "url", "file_id", "sheet", "preview", "preview_by", "preview_at", "candidates_basis"):
            if key in row and not isinstance(row[key], str):
                raise InputError(f"reference.{key}: 문자열 필요")
        candidates = row.get("candidates", [])
        if not isinstance(candidates, list) or any(not isinstance(p, str) or not p for p in candidates):
            raise InputError("reference.candidates: 경로 문자열 목록 필요")
        if type(row.get("candidates_complete", False)) is not bool:
            raise InputError("reference.candidates_complete: 참/거짓 필요")
        def absolute(value: str) -> str:
            return str((path.resolve().parent / value).resolve())
        entries.append(RefEntry(row["index"], row.get("role", ""), absolute(row["local_path"]) if row.get("local_path") else None,
                                row.get("url") or None, row.get("file_id") or None, row.get("sheet", "시트 없음/만들어야 함"), row.get("preview", "미검수"),
                                row.get("preview_by"), row.get("preview_at"), tuple(absolute(p) for p in candidates), row.get("candidates_complete", False), row.get("candidates_basis")))
    return tuple(entries)


def contact_html(results: tuple[RefResult, ...]) -> str:
    rows = []
    for result in results:
        entry = result.entry
        values = (f"@image{entry.index}", Path(entry.local_path).name if entry.local_path else "미지정", entry.role, entry.sheet, entry.preview)
        cells = "".join(f"<td>{html.escape(v)}</td>" for v in values)
        image = f'<td><img src="thumbs/{entry.index}.png" alt="보기용"></td>' if isinstance(result.local, ImageInfo) and result.local.decode == "디코딩 확인" else "<td>썸네일 없음</td>"
        rows.append("<tr>" + cells + image + "</tr>")
    return '<!doctype html><html lang="ko"><meta charset="utf-8"><title>레퍼런스 검수</title><h1>보기용, 생성 입력 아님</h1><table><tr><th>번호</th><th>파일명</th><th>역할</th><th>시트 상태</th><th>검수 상태</th><th>보기용</th></tr>' + "".join(rows) + "</table></html>\n"


def thumbnails(results: tuple[RefResult, ...], run: RunDir, tool: ImageTool) -> tuple[RefResult, ...]:
    directory = run.policy.check(run.stage / "thumbs")
    directory.mkdir()
    updated = []
    for result in results:
        if isinstance(result.local, ImageInfo) and result.entry.local_path and not any(f.code == "REF_THUMB_INPUT" for f in result.findings):
            source = Path(result.entry.local_path)
            decoded = tool.decode_check(source)
            local = replace(result.local, decode="디코딩 확인" if decoded else "디코딩 실패")
            findings = result.findings
            if decoded:
                tool.thumbnail(source, run.policy.check(directory / f"{result.entry.index}.png"), 320)
            else:
                findings += (Finding("REF_DECODE", Severity.ERROR, "디코딩 실패"),)
            result = replace(result, local=local, findings=findings)
        updated.append(result)
    return tuple(updated)


def execute(args: Namespace, argv: list[str], cfg: Config):
    settings = tomllib.loads(read_document(cfg.path, "config").text)
    network = settings.get("network", {})
    tools = settings.get("tools", {})
    if not isinstance(network, dict) or not isinstance(tools, dict):
        raise InputError("network/tools는 TOML 표여야 함")
    timeout = network.get("timeout_s", 20)
    redirects = network.get("max_redirects", 5)
    maximum = network.get("max_bytes", 52428800)
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0 or type(redirects) is not int or redirects < 0 or type(maximum) is not int or maximum < 1:
        raise InputError("network: 양의 timeout_s/max_bytes, 0 이상 max_redirects 필요")
    ffmpeg = tools.get("ffmpeg_path", "")
    if not isinstance(ffmpeg, str):
        raise InputError("tools.ffmpeg_path: 경로 문자열 필요")
    if ffmpeg:
        ffmpeg = str((cfg.path.parent / ffmpeg).resolve())
    image_tool = FFmpegImageTool(ffmpeg)
    if args.thumbs and not image_tool.available():
        raise Unavailable("ffmpeg 없음: tools.ffmpeg_path 확인")
    entries = load_entries(args.list)
    prompt = read_document(args.prompt, "prompt") if args.prompt else None
    store = WorkflowDir(cfg.workflow_dir, cfg.declared_commit)
    key, headings, take, count = ANCHOR_SPECS["checklist"]
    lines = resolve_anchor(store.load(key), Anchor(key, (DOC_TITLES[key], *headings), take, count))
    safe = re.search(r"안전선\s+(\d+)~(\d+)장", lines[1].text)
    if safe is None:
        raise InputError("W02 안전 권고 장수 형식 변경")
    findings = check_numbers(entries, prompt.text if prompt else None) + count_advice(len(entries), (int(safe[1]), int(safe[2])))
    results = check_references(entries, fetcher=UrllibFetcher(), allow_network=args.allow_network, timeout_s=timeout, max_redirects=redirects, max_bytes=maximum)
    inputs = (args.list, *((args.prompt,) if args.prompt else ()), *(Path(p) for e in entries for p in (e.local_path, *e.candidates) if p))
    inputs += tuple(Path(d.fingerprint.path) for d in store.used.values())
    target = args.out or new_target(cfg.output_root, "refs-check", "references")
    with RunDir(target, cfg.policy(inputs)) as run:
        if args.thumbs:
            if any(f.severity == Severity.ERROR for f in findings):
                raise InputError("썸네일 생성 전 레퍼런스 번호 수정 필요")
            results = thumbnails(results, run, image_tool)
            run.write_text("contact.html", contact_html(results))
        all_findings = (*findings, *(f for result in results for f in result.findings))
        code = int(any(f.severity != Severity.INFO for f in all_findings))
        report = {"results": results, "findings": all_findings, "references_complete": code == 0}
        run.write_json("refs.json", report)
        run.write_text("refs.md", "# [검수 대기] 레퍼런스 검사\n\n```json\n" + json_text(report) + "```\n\n## 내가 정한 것\nSHA-256이 같을 때만 바이트 동일.\n\n## 사용자 답이 필요한 것\n역할 적합성·후보 전수·육안 검수.\n\n## 근거\nW02 점검 2번, run.json 문서 지문.\n")
        run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256, "inputs": [read_document(args.list, "refs").fingerprint, *([prompt.fingerprint] if prompt else [])],
                    "docs": [d.fingerprint for d in store.used.values()], "exit_code": code, "status": "검수 대기"})
    return {"command": "refs check", "exit_code": code, "status": "검수 대기", "output": str(target.resolve()), "findings": len(all_findings)}
