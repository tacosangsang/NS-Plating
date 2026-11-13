#!/usr/bin/env python3
"""assets/current.toml 형식 검사와 프롬프트 입력 대조.

사용:
  python3 assets/check_assets.py                      목록 형식 + 문서 속 폐기 문자열 검사
  python3 assets/check_assets.py --prompt-json X.json  prompt-page JSON의 입력 그림을 목록과 대조

종료 코드 0 통과, 1 실패. 외부 패키지 없음(Python 3.11+).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = Path(__file__).resolve().parent / "current.toml"
KINDS = {"character", "prop", "bg", "blockout_render", "style_ref"}
STATUS = {"confirmed", "temp"}
MD5 = re.compile(r"^[0-9a-f]{32}$")
UUID = re.compile(r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
# 폐기 문자열을 검색할 문서 위치
SCAN_DIRS = (".claude/skills", "workflow")


@dataclass
class Catalog:
    assets: list[dict] = field(default_factory=list)
    retired: list[dict] = field(default_factory=list)
    banned: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Catalog":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != 1:
            raise ValueError("schema = 1 이 필요하다")
        return cls(data.get("asset", []), data.get("retired", []), data.get("banned_source", []))


class Rule(ABC):
    """목록 규칙 하나. 새 규칙은 이 클래스를 구현해 RULES에 넣는다."""

    @abstractmethod
    def run(self, cat: Catalog) -> list[str]: ...


def _dups(values: list[str]) -> set[str]:
    return {v for v in values if values.count(v) > 1}


class AssetFields(Rule):
    def run(self, cat: Catalog) -> list[str]:
        errs: list[str] = []
        for a in cat.assets:
            k = a.get("key", "?")
            if a.get("kind") not in KINDS:
                errs.append(f"{k}: kind는 {sorted(KINDS)} 중 하나")
            if a.get("status") not in STATUS:
                errs.append(f"{k}: status는 confirmed 또는 temp")
            if not a.get("drive_id"):
                errs.append(f"{k}: drive_id 필요 (소스는 드라이브에서만)")
            if a.get("md5") and not MD5.match(a["md5"]):
                errs.append(f"{k}: md5 형식이 32자리 16진수가 아니다")
            if a.get("hf_media_id") and not UUID.match(a["hf_media_id"]):
                errs.append(f"{k}: hf_media_id 형식 오류")
            if a.get("status") == "confirmed":
                for f in ("quote", "confirmed_by", "confirmed_at"):
                    if not a.get(f):
                        errs.append(f"{k}: confirmed는 {f} 필요 (사용자 확정 문장)")
            if a.get("kind") == "blockout_render" and not a.get("blockout"):
                errs.append(f"{k}: blockout_render는 기준 블록아웃 판(blockout) 필요")
        return errs


class Uniqueness(Rule):
    def run(self, cat: Catalog) -> list[str]:
        errs = [f"key 중복: {d}" for d in _dups([a.get("key", "") for a in cat.assets])]
        md5s = [a["md5"] for a in cat.assets if a.get("md5")]
        errs += [f"md5 중복(같은 파일이 다른 key로 올라감): {d}" for d in _dups(md5s)]
        return errs


class RetiredRules(Rule):
    def run(self, cat: Catalog) -> list[str]:
        errs: list[str] = []
        keys = {a.get("key") for a in cat.assets}
        live_md5 = {a.get("md5") for a in cat.assets if a.get("md5")}
        live_names = {a.get("name") for a in cat.assets}
        for r in cat.retired:
            who = r.get("name") or r.get("md5") or "?"
            if not (r.get("name") or r.get("md5")):
                errs.append("retired: name 또는 md5 필요")
            if not r.get("reason"):
                errs.append(f"retired {who}: reason 필요")
            if r.get("replaced_by") and r["replaced_by"] not in keys:
                errs.append(f"retired {who}: replaced_by '{r['replaced_by']}'가 목록에 없다")
            if r.get("md5") in live_md5 or r.get("name") in live_names:
                errs.append(f"retired {who}: 현재본과 같은 파일이다")
        return errs


class BannedSources(Rule):
    def run(self, cat: Catalog) -> list[str]:
        errs = []
        for b in cat.banned:
            if not (b.get("drive_id") or b.get("path_prefix")) or not b.get("reason"):
                errs.append("banned_source: drive_id 또는 path_prefix, 그리고 reason 필요")
        return errs


RULES: list[Rule] = [AssetFields(), Uniqueness(), RetiredRules(), BannedSources()]


def check_catalog(cat: Catalog) -> list[str]:
    return [e for rule in RULES for e in rule.run(cat)]


def scan_docs(cat: Catalog, root: Path) -> list[str]:
    """스킬·workflow 문서가 폐기 파일 이름을 가리키면 실패."""
    needles = [r["name"] for r in cat.retired if r.get("name")]
    errs: list[str] = []
    for d in SCAN_DIRS:
        for p in sorted((root / d).rglob("*")) if (root / d).is_dir() else []:
            if not p.is_file() or p.suffix not in {".md", ".py", ".json", ".toml"}:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            errs += [f"{p.relative_to(root)}: 폐기 파일 이름 '{n}'" for n in needles if n in text]
    return errs


def check_prompt_inputs(cat: Catalog, data: dict) -> list[str]:
    """prompt-page JSON의 입력 그림이 폐기본이거나 현재본과 다르면 실패한다.

    입력 항목 필드: asset(목록 key), path, file, media_id, md5 (모두 선택).
    asset이 있으면 media_id/md5가 목록의 값과 같아야 한다.
    asset이 없는 입력은 임시본이므로 경고 대신 실패시킨다(구조 레퍼런스는 목록에서만).
    """
    by_key = {a["key"]: a for a in cat.assets}
    errs: list[str] = []
    for g in data.get("generations", []):
        if g.get("status") in {"완료", "실패"}:
            continue
        for i in g.get("inputs", []):
            tag = f"{g.get('id', '?')} {i.get('tag', '?')}"
            locations = [str(i[f]) for f in ("path", "file") if i.get(f)]
            # 확장자 있는 이름과 없는 이름을 모두 비교한다
            names = {n for loc in locations for n in (Path(loc).name, Path(loc).stem)}
            for r in cat.retired:
                if (r.get("name") and r["name"] in names) or (r.get("md5") and r["md5"] == i.get("md5")):
                    errs.append(f"{tag}: 폐기된 자료 {r.get('name') or r.get('md5')} ({r.get('reason', '')})")
            for b in cat.banned:
                if b.get("path_prefix") and any(loc.startswith(b["path_prefix"]) for loc in locations):
                    errs.append(f"{tag}: 읽기 금지 출처 {b['path_prefix']} ({b['reason']})")
            key = i.get("asset")
            if not key:
                errs.append(f"{tag}: asset 키 없음 (목록에 없는 그림은 입력으로 쓰지 않는다. 필요하면 사용자에게 묻는다)")
                continue
            a = by_key.get(key)
            if a is None:
                errs.append(f"{tag}: asset '{key}'가 목록에 없다")
                continue
            if a["status"] != "confirmed":
                errs.append(f"{tag}: '{key}'는 확정본이 아니다(temp)")
            for f, kname in (("media_id", "hf_media_id"), ("md5", "md5")):
                if i.get(f) and a.get(kname) and i[f] != a[kname]:
                    errs.append(f"{tag}: {f}가 목록의 '{key}'와 다르다")
    return errs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", type=Path, default=CATALOG)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--prompt-json", type=Path)
    args = ap.parse_args(argv)
    try:
        cat = Catalog.load(args.catalog)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as e:
        print(f"목록을 읽지 못했다: {e}")
        return 1
    errs = check_catalog(cat)
    if args.prompt_json:
        errs += check_prompt_inputs(cat, json.loads(args.prompt_json.read_text(encoding="utf-8")))
    else:
        errs += scan_docs(cat, args.root)
    for e in errs:
        print("실패:", e)
    if not errs:
        print(f"통과 (자산 {len(cat.assets)}, 폐기 {len(cat.retired)}, 금지 출처 {len(cat.banned)})")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
