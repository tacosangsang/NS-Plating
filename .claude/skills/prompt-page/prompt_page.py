"""PLATING 프롬프트 페이지 생성기 + 검사기.

컷 하나의 JSON을 읽어 검사하고, 통과하면 아티팩트용 HTML과 그림 폴더를 만든다.
검사에 하나라도 걸리면 HTML을 만들지 않고 빠진 칸을 출력한다(종료 코드 1).

    python3 prompt_page.py page.json OUT_DIR
    python3 prompt_page.py page.json --check   # 검사만
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

CHECK_ITEMS = (
    "edit인가 새 생성인가 코드 합성인가",
    "나눌까",
    "중요 소품에 시트가 붙었나",
    "노션 컷표 문장과 맞나",
    "비트마다 원인이 앞에 있나",
    "앞뒤 클립이 이어지나",
    "입력 파일이 가장 큰 원본인가",
    "해상도와 길이",
)
ANSWERS = ("예", "아니오", "해당 없음")
SHOT_KEYS = ("샷 크기", "카메라 위치·높이", "앵글", "렌즈", "카메라 움직임", "화면 배치", "빛 방향")
INPUT_KEYS = ("tag", "role", "path", "resolution", "file")
STATUSES = ("최신", "생성 대기", "대안", "완료", "옛 판", "실패")
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_EDGE = 1600
TAG_RE = re.compile(r"@(image\d+|video\d*)")


class Kind(ABC):
    """생성 종류. 종류마다 필수 칸이 다르다. 새 종류는 이 클래스를 하나 더 만들어 KINDS에 넣는다."""

    name: str
    label: str

    @abstractmethod
    def needs_beats(self) -> bool: ...

    def check(self, g: dict, where: str) -> list[str]:
        errs: list[str] = []
        if self.needs_beats() or g.get("beats"):  # 필수가 아니어도 넣었으면 같은 규칙으로 검사
            errs += _check_beats(g, where, need_camera=self.needs_beats())
        return errs


class VideoGen(Kind):
    name, label = "video", "영상 생성"

    def needs_beats(self) -> bool:
        return True


class VideoEdit(Kind):
    name, label = "video_edit", "영상 edit"

    def needs_beats(self) -> bool:
        return False


class ImageGen(Kind):
    name, label = "image", "이미지 Edit·Combine"

    def needs_beats(self) -> bool:
        return False


KINDS: dict[str, Kind] = {k.name: k for k in (VideoGen(), VideoEdit(), ImageGen())}


def _filled(v) -> bool:
    """null·빈 문자열·공백만 있는 값은 빈 칸. str(None) == "None"으로 통과하는 것을 막는다."""
    return v is not None and str(v).strip() != ""


VAGUE_CAMERA = {"계속", "동일", "같음", "위와 같음", "유지", "-", "continue", "same"}


def _check_beats(g: dict, where: str, need_camera: bool) -> list[str]:
    beats = g.get("beats") or []
    if not beats:
        return [f"{where}: 영상 생성인데 구간 표(beats)가 없음"]
    errs = []
    keys = ("t", "camera", "action", "end") if need_camera else ("t", "action", "end")
    for i, b in enumerate(beats, 1):
        for k in keys:
            if not _filled(b.get(k)):
                errs.append(f"{where}: 구간 {i}의 {k} 빈 칸")
        cam = str(b.get("camera") or "").strip()
        if cam and cam.rstrip(". ").lower() in VAGUE_CAMERA:
            errs.append(f"{where}: 구간 {i}의 camera가 빈말({cam}). 무엇이 어느 쪽으로 얼마나 밀리는지 쓴다")
    if need_camera:
        n_cam = len(re.findall(r"\bCamera\s*:", str(g.get("prompt") or "")))
        if n_cam < len(beats):
            errs.append(f"{where}: 프롬프트 TIMELINE 줄 끝 \"Camera: ...\"가 구간 {len(beats)}개 중 {n_cam}개뿐")
    nums = re.findall(r"\d+(?:\.\d+)?", str(beats[-1].get("t", "")))
    if not nums:
        errs.append(f"{where}: 마지막 구간 t에 끝 초(숫자)가 없음. 예: \"2–7\"")
    elif g.get("length_s") is not None and float(nums[-1]) != float(g["length_s"]):
        errs.append(f"{where}: 마지막 구간 끝({nums[-1]}초)이 길이({g['length_s']}초)와 다름")
    return errs


def validate(page: dict, base: Path) -> list[str]:
    errs: list[str] = []
    for k in ("title", "cut"):
        if not _filled(page.get(k)):
            errs.append(f"페이지: {k} 빈 칸")
    gens = page.get("generations") or []
    if not gens:
        return errs + ["페이지: generations 없음"]
    if gens[0].get("status") not in ("최신", "생성 대기"):
        errs.append("페이지: 맨 위 생성의 status가 최신·생성 대기가 아님(지금 돌릴 판을 맨 위에)")
    for n, g in enumerate(gens):
        where = f"[{g.get('id') or n + 1}]"
        if g.get("status") not in STATUSES:
            errs.append(f"{where}: status는 {'/'.join(STATUSES)} 중 하나")
        if n > 0 and g.get("status") == "최신":
            errs.append(f"{where}: 최신이 둘 이상. 아래 판은 대안·완료·옛 판으로")
        kind = KINDS.get(g.get("kind", ""))
        if kind is None:
            errs.append(f"{where}: kind는 {'/'.join(KINDS)} 중 하나")
            continue
        for k in ("id", "what", "model", "resolution", "prompt"):
            if not _filled(g.get(k)):
                errs.append(f"{where}: {k} 빈 칸")
        if kind.name != "image" and g.get("length_s") is None:
            errs.append(f"{where}: length_s 빈 칸")
        errs += _check_inputs(g, where, base)
        errs += _check_media(g, where, base)
        errs += _check_shot(g, where)
        errs += _check_answers(g, where)
        errs += kind.check(g, where)
    return errs


def _check_inputs(g: dict, where: str, base: Path) -> list[str]:
    errs = []
    inputs = g.get("inputs") or []
    have = {i.get("tag", "").lstrip("@") for i in inputs}
    for tag in sorted(set(TAG_RE.findall(g.get("prompt", "")))):
        if tag not in have:
            errs.append(f"{where}: 프롬프트의 @{tag}에 입력 칸이 없음")
    for i in inputs:
        t = i.get("tag", "?")
        for k in INPUT_KEYS:
            if not _filled(i.get(k)):
                errs.append(f"{where}: 입력 {t}의 {k} 빈 칸")
        f = i.get("file")
        if f:
            p = _resolve(f, base)
            if not p.is_file():
                errs.append(f"{where}: 입력 {t}의 file 없음: {p}")
            elif p.suffix.lower() not in IMAGE_EXT:
                errs.append(f"{where}: 입력 {t}의 file은 그림이어야 함(@video는 첫 프레임을 뽑아 넣기)")
            else:
                errs += _check_size(p, f"입력 {t}", where)
        o = i.get("original")
        if o:
            op = _resolve(o, base)
            errs += [f"{where}: 입력 {t}의 original 없음: {op}"] if not op.is_file() else _check_size(op, f"입력 {t}", where)
    return errs


MAX_FILE = 15 * 1_048_576  # 아티팩트 파일 하나 상한(바이너리 15MB)


def _check_size(p: Path, label: str, where: str) -> list[str]:
    if p.is_file() and p.stat().st_size > MAX_FILE:
        return [f"{where}: {label} 원본이 15MB를 넘어 아티팩트에 못 올림({p.stat().st_size / 1_048_576:.1f}MB). 원본 다운로드 칸을 달 수 없으니 나눠 올리거나 드라이브 경로로"]
    return []


def _check_media(g: dict, where: str, base: Path) -> list[str]:
    """촬영 레퍼런스와 결과 파일이 실제로 있는지 본다(--check가 통과했는데 만들 때 터지지 않게)."""
    errs = []
    for i, r in enumerate((g.get("shot") or {}).get("refs") or [], 1):
        f = str(r.get("file") or "").strip()
        if not f:
            errs.append(f"{where}: 촬영 레퍼런스 {i}의 file 빈 칸")
        elif not _resolve(f, base).is_file():
            errs.append(f"{where}: 촬영 레퍼런스 {i}의 file 없음: {_resolve(f, base)}")
        else:
            errs += _check_size(_resolve(f, base), f"촬영 레퍼런스 {i}", where)
    for m in (g.get("result") or {}).get("media") or []:
        if not _resolve(m, base).is_file():
            errs.append(f"{where}: 결과 파일 없음: {_resolve(m, base)}")
        else:
            errs += _check_size(_resolve(m, base), "결과", where)
    return errs


def _check_shot(g: dict, where: str) -> list[str]:
    shot = g.get("shot") or {}
    if _filled(shot.get("same_as")):
        return []
    return [f"{where}: 촬영 표 '{k}' 빈 칸" for k in SHOT_KEYS if not _filled(shot.get(k))]


def _check_answers(g: dict, where: str) -> list[str]:
    errs = []
    check = g.get("check") or []
    if len(check) != len(CHECK_ITEMS):
        return [f"{where}: 점검 칸은 {len(CHECK_ITEMS)}줄이어야 함(지금 {len(check)}줄)"]
    for i, c in enumerate(check, 1):
        a = c.get("answer")
        if a not in ANSWERS:
            errs.append(f"{where}: 점검 {i}번 답이 예/아니오/해당 없음이 아님")
        elif a == "아니오" and not _filled(c.get("note")):
            errs.append(f"{where}: 점검 {i}번 아니오인데 이유·대안 없음")
    return errs


def _resolve(f: str, base: Path) -> Path:
    p = Path(f)
    return p if p.is_absolute() else base / p


def _media(src: Path, out: Path, stem: str, alt: str, caption: str = "", original: Path | None = None) -> str:
    """보기용(그림은 긴 변 1600px JPEG)과 원본(손대지 않은 복사본)을 함께 두고, 원본 받기 버튼이 달린 figure를 돌려준다."""
    (out / "img").mkdir(parents=True, exist_ok=True)
    (out / "orig").mkdir(parents=True, exist_ok=True)
    keep = original or src  # 받을 파일. @video처럼 보기용 그림과 원본이 다르면 original
    orig = f"orig/{stem}{keep.suffix.lower()}"
    shutil.copyfile(keep, out / orig)
    size = f"{keep.stat().st_size / 1_048_576:.1f}MB"
    if src.suffix.lower() in IMAGE_EXT:
        from PIL import Image, ImageOps

        view = f"img/{stem}.jpg"
        with Image.open(src) as raw:
            im = ImageOps.exif_transpose(raw)  # 보이는 방향 그대로(EXIF 회전 반영)
            dims = f"{im.width}×{im.height} · "
            if original is not None:
                dims = ""
            if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
                rgba = im.convert("RGBA")  # 투명 부분은 흰 바탕에 합쳐 JPEG로(검은 배경에 묻히지 않게)
                im = Image.new("RGB", rgba.size, (255, 255, 255))
                im.paste(rgba, mask=rgba.getchannel("A"))
            else:
                im = im.convert("RGB")
            im.thumbnail((MAX_EDGE, MAX_EDGE))
            im.save(out / view, quality=88)
        tag = f'<img src="{E(view)}" alt="{E(alt)}" loading="lazy">'
    else:
        dims = ""
        tag = f'<video src="{E(orig)}" controls playsinline></video>'
    btn = f'<button type="button" class="dl" data-src="{E(orig)}" data-name="{E(keep.name)}">원본 받기 ({dims}{size})</button>'
    sep = " · " if caption else ""
    return f"<figure>{tag}<figcaption>{caption}{sep}{btn}</figcaption></figure>"


E = html.escape


def _render_gen(g: dict, base: Path, out: Path, n: int) -> str:
    kind = KINDS[g["kind"]]
    meta = [g["model"]]
    if g.get("length_s") is not None:
        meta.append(f"{g['length_s']}초")
    meta.append(g["resolution"])
    if g.get("crons") is not None:
        meta.append(f"{g['crons']} Crons")
    parts = [f'<section id="g{n}"><h2>{E(g["id"])} · {E(g["what"])} <span class="tag">[{E(g["status"])}]</span></h2>',
             f'<p class="meta">{E(kind.label)} · {E(" · ".join(meta))}</p>']

    parts.append("<h3>입력 그림</h3>")
    for i, inp in enumerate(g.get("inputs") or []):
        bo = f' · 블록아웃 {E(inp["blockout"])}' if inp.get("blockout") else ""
        cap = (f'<b>{E(inp["tag"])}</b> · {E(inp["role"])} · <code>{E(inp["path"])}</code> · '
               f'{E(inp["resolution"])}{bo}')
        original = _resolve(inp["original"], base) if inp.get("original") else None
        parts.append(_media(_resolve(inp["file"], base), out, f"g{n}_in{i}", inp["tag"], cap, original))

    shot = g.get("shot") or {}
    parts.append("<h3>촬영</h3>")
    if _filled(shot.get("same_as")):
        parts.append(f'<p class="shot-same">{E(shot["same_as"])}</p>')
    else:
        rows = "".join(f"<tr><th>{E(k)}</th><td>{E(str(shot[k]))}</td></tr>" for k in SHOT_KEYS)
        parts.append(f'<div class="tw"><table>{rows}</table></div>')
    for i, r in enumerate(shot.get("refs") or []):
        parts.append(_media(_resolve(r["file"], base), out, f"g{n}_ref{i}", r.get("caption", ""), E(r.get("caption", ""))))

    if g.get("beats"):
        parts.append("<h3>구간</h3>")
        cam = any(_filled(b.get("camera")) for b in g["beats"])
        rows = "".join(f"<tr><td>{E(str(b['t']))}초</td>" + (f"<td>{E(b.get('camera') or '')}</td>" if cam else "")
                       + f"<td>{E(b['action'])}</td><td>{E(b.get('sound', ''))}</td><td>{E(b['end'])}</td></tr>"
                       for b in g["beats"])
        head = "<th>초</th>" + ("<th>카메라</th>" if cam else "") + "<th>원인 → 행동</th><th>대사·효과음</th><th>끝 상태</th>"
        parts.append(f'<div class="tw"><table class="beats"><tr>{head}</tr>{rows}</table></div>')

    parts.append("<h3>점검</h3>")
    rows = "".join(f'<tr><td>{i}. {E(item)}</td><td class="a-{E(c["answer"])}">{E(c["answer"])}</td><td>{E(c.get("note", ""))}</td></tr>'
                   for i, (item, c) in enumerate(zip(CHECK_ITEMS, g["check"]), 1))
    parts.append(f'<div class="tw"><table>{rows}</table></div>')

    prompt = g["prompt"]
    n_img = len(g.get("inputs") or [])
    parts.append(f'<div class="prompt"><div class="ph"><span>{E(g["model"])} · {n_img}장 · {len(prompt):,}자</span>'
                 f'<button type="button" data-t="p{n}">복사</button></div><pre id="p{n}">{E(prompt)}</pre></div>')

    res = g.get("result") or {}
    if res.get("media") or res.get("verdict"):
        parts.append("<h3>결과</h3>")
        for i, m in enumerate(res.get("media") or []):
            parts.append(_media(_resolve(m, base), out, f"g{n}_res{i}", "결과", "결과"))
        if res.get("verdict"):
            parts.append(f'<p>{E(res["verdict"])}</p>')
    if _filled(g.get("notes")):
        parts.append(f'<details><summary>메모·비평</summary><p class="pre">{E(g["notes"])}</p></details>')
    parts.append("</section>")
    return "\n".join(parts)


CSS = """:root{--bg:#eef0f2;--paper:#fff;--fg:#1d232b;--muted:#5b6672;--line:#d3d8de;--accent:#2f5d7c;--code:#f4f6f8;--no:#b3261e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#13171c;--paper:#1b2027;--fg:#e3e8ee;--muted:#9aa6b2;--line:#2e3640;--accent:#8fb8d6;--code:#11151a;--no:#f2b8b5}}
:root[data-theme="dark"]{--bg:#13171c;--paper:#1b2027;--fg:#e3e8ee;--muted:#9aa6b2;--line:#2e3640;--accent:#8fb8d6;--code:#11151a;--no:#f2b8b5}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 system-ui,sans-serif;padding:24px 16px 64px}
.wrap{max-width:920px;margin:0 auto;display:grid;gap:20px}h1{font-size:22px;margin:0}.sub,.meta{color:var(--muted);margin:0}
section{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:20px;display:grid;gap:10px;min-width:0}
h2{font-size:18px;margin:0;color:var(--accent)}h3{font-size:15px;margin:8px 0 0}.tag{font-weight:600}
figure{margin:0}img,video{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:4px}
figcaption{font-size:13.5px;color:var(--muted);margin-top:4px}code{font:12.5px ui-monospace,monospace;background:var(--code);padding:1px 4px;border-radius:3px;word-break:break-all}
.tw{overflow-x:auto}table{border-collapse:collapse;font-size:13.5px;width:100%}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{color:var(--muted);font-weight:600;white-space:nowrap}
.beats td:first-child{white-space:nowrap}
.a-아니오{color:var(--no);font-weight:600}
.prompt{border:1px solid var(--line);border-radius:6px;overflow:hidden}.ph{display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:var(--code);font-size:12.5px;color:var(--muted)}
button.dl{font:600 12px system-ui;color:var(--accent);background:none;border:1px solid var(--accent);border-radius:4px;padding:2px 8px;margin-left:2px;cursor:pointer}button.dl:disabled{opacity:.5;cursor:default}
.ph button{font:600 12.5px system-ui;color:var(--paper);background:var(--accent);border:0;border-radius:4px;padding:5px 12px;cursor:pointer}
pre{margin:0;padding:12px;font:12.5px/1.6 ui-monospace,monospace;white-space:pre-wrap;word-break:break-word;max-height:480px;overflow:auto}
.pre{white-space:pre-wrap}details>summary{cursor:pointer;color:var(--accent);font-weight:600}"""

JS = """(async()=>{const dl=await window.claude?.use?.("downloads");document.querySelectorAll('button.dl').forEach(b=>{
if(!dl){b.disabled=true;b.title='이 화면에서는 저장할 수 없음';return}
b.addEventListener('click',async()=>{const t=b.textContent;b.textContent='준비 중';try{const r=await fetch(b.dataset.src);
await dl.save({filename:b.dataset.name,data:await r.blob()});b.textContent='저장함'}catch(e){b.textContent=(e&&e.code==='declined')?'취소함':'저장 실패: '+((e&&e.code)||'오류')}
setTimeout(()=>b.textContent=t,2500)})})})();
document.querySelectorAll('.ph button').forEach(b=>b.addEventListener('click',()=>{const el=document.getElementById(b.dataset.t);
navigator.clipboard.writeText(el.textContent).then(()=>{b.textContent='복사됨';setTimeout(()=>b.textContent='복사',1500)}).catch(()=>{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='선택됨'})}));"""


def _sources(page: dict, base: Path) -> list[Path]:
    paths = []
    for g in page["generations"]:
        paths += [_resolve(i["file"], base) for i in g.get("inputs") or []]
        paths += [_resolve(i["original"], base) for i in g.get("inputs") or [] if i.get("original")]
        paths += [_resolve(r["file"], base) for r in (g.get("shot") or {}).get("refs") or []]
        paths += [_resolve(m, base) for m in (g.get("result") or {}).get("media") or []]
    return [p.resolve() for p in paths]


def render(page: dict, base: Path, out: Path) -> Path:
    """임시 폴더에 다 만든 뒤 out/index.html과 out/img만 바꾼다. 원본 그림이 out/img 안에 있으면 거부한다."""
    owned = [(out / sub).resolve() for sub in ("img", "orig")]
    inside = [p for p in _sources(page, base) if any(d == p or d in p.parents for d in owned)]
    if inside:
        raise SystemExit(f"원본 그림이 출력 폴더 img/·orig/ 안에 있음(덮어써짐): {inside[0]}. 출력 폴더를 따로 정한다.")
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".prompt_page_", dir=out))
    try:
        index = _render_into(page, base, tmp)
        for sub in ("img", "orig"):
            shutil.rmtree(out / sub, ignore_errors=True)
            if (tmp / sub).exists():
                shutil.move(str(tmp / sub), str(out / sub))
        shutil.move(str(index), str(out / "index.html"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out / "index.html"


def _render_into(page: dict, base: Path, out: Path) -> Path:
    (out / "img").mkdir(parents=True, exist_ok=True)
    gens = page["generations"]
    # 지금 돌릴 판(최신·생성 대기)은 모두 펼치고, 대안·완료·옛 판·실패만 접는다(한 페이지에 컷 여러 개)
    live = [n for n, g in enumerate(gens) if n == 0 or g.get("status") in ("최신", "생성 대기")]
    rest = [n for n in range(len(gens)) if n not in live]
    body = [_render_gen(gens[n], base, out, n) for n in live]
    if rest:
        old = "\n".join(_render_gen(gens[n], base, out, n) for n in rest)
        body.append(f'<details><summary>이전 판·대안 {len(rest)}개</summary><div class="wrap">{old}</div></details>')
    sub = f'<p class="sub">{E(page["cut"])}' + (f' · 원본 <code>{E(page["source"])}</code>' if page.get("source") else "") + "</p>"
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{E(page["title"])}</title><style>{CSS}</style></head><body><div class="wrap"><h1>{E(page["title"])}</h1>{sub}'
           + "\n".join(body) + f"</div><script>{JS}</script></body></html>")
    (out / "index.html").write_text(doc, encoding="utf-8")
    return out / "index.html"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    src = Path(argv[1]).resolve()
    page = json.loads(src.read_text(encoding="utf-8"))
    errs = validate(page, src.parent)
    if errs:
        print("검사 실패, 페이지를 만들지 않음:")
        print("\n".join(f"- {e}" for e in errs))
        return 1
    if argv[2] == "--check":
        print("검사 통과")
        return 0
    out = Path(argv[2]).resolve()
    index = render(page, src.parent, out)
    files = {f"{sub}/{p.name}": str(p) for sub in ("img", "orig") for p in sorted((out / sub).glob("*"))}
    print(json.dumps({"file_path": str(index), "files": files, "capabilities": {"downloads": True}}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
