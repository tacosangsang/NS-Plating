"""이미 올라간 프롬프트 아티팩트 HTML을 점검한다(prompt-page로 만들지 않은 옛 페이지 포함).

    python3 audit_page.py index.html [index2.html ...]

prompt-page로 만든 페이지는 펼쳐진 생성(최신·생성 대기) 섹션을 모두 본다.
손으로 만든 옛 페이지는 맨 위 생성(첫 h2 섹션)만 본다. 걸린 항목이 있으면 종료 코드 1.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"@(image\d+|video\d*)")
VAGUE_CAMERA = {"계속", "동일", "같음", "위와 같음", "유지", "-", "continue", "same"}
SHOT_WORDS = ("샷 크기", "앵글", "렌즈", "mm", "카메라 위치", "눈높이", "화면 배치", "빛 방향")


def live_blocks(doc: str) -> list[tuple[str, str]]:
    """점검할 (섹션, 범위) 목록. 생성기 페이지는 접힌 '이전 판·대안' 앞의 프롬프트 섹션 전부,
    옛 페이지는 첫 프롬프트 섹션과 그 앞의 프롬프트 없는 섹션(메모·입력 목록)."""
    chunks = re.split(r"(?=<h2\b)", doc)[1:]
    if '<p class="meta">' in doc:
        live = re.split(r"<details><summary>이전 판·대안", doc)[0]
        return [(c, c) for c in re.split(r"(?=<h2\b)", live)[1:] if re.search(r"<pre\b", c)]
    for i, c in enumerate(chunks):
        if re.search(r"<pre\b", c):
            return [(c, "".join(chunks[:i]) + c)]
    return []


def _camera_problems(body: str, prompt: str) -> list[str]:
    """영상 생성 구간 표의 카메라 칸과 프롬프트 TIMELINE의 Camera: 줄을 본다."""
    table = next((t for t in re.findall(r"<table\b.*?</table>", body, re.S)
                  if re.search(r"<th[^>]*>\s*(초|구간|시간)", t)), None)
    if table is None:
        return ["영상인데 한글 구간 표(초 단위)가 없음"]
    heads = [html.unescape(re.sub(r"<.*?>", "", h)).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", table, re.S)]
    col = next((i for i, h in enumerate(heads) if h.startswith("카메라") or h.lower().startswith("camera")), None)
    if col is None:
        return ["구간 표에 카메라 칸이 없음(구간마다 카메라가 어떻게 바뀌는지)"]
    problems = []
    rows = [r for r in re.findall(r"<tr\b.*?</tr>", table, re.S) if "<td" in r]
    for i, r in enumerate(rows, 1):
        cells = [html.unescape(re.sub(r"<.*?>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        cam = cells[col] if col < len(cells) else ""
        if not cam or cam.rstrip(". ").lower() in VAGUE_CAMERA:
            problems.append(f"구간 {i}의 카메라 칸이 비었거나 빈말({cam or '빈 칸'})")
    n_cam = len(re.findall(r"\bCamera\s*:", prompt))
    if n_cam < len(rows):
        problems.append(f"프롬프트 TIMELINE의 Camera: 줄이 구간 {len(rows)}개 중 {n_cam}개뿐")
    return problems


def audit(doc: str) -> list[str]:
    blocks = live_blocks(doc)
    if not blocks:
        return ["프롬프트 칸(<pre>)이 있는 섹션이 없음"]
    problems: list[str] = []
    if re.search(r"grid-template-columns:\s*(repeat\(|1fr\s+1fr)", doc):
        problems.append("그림이 작은 격자(2열 이상)로 배치됨")
    for first, scope in blocks:
        found = audit_section(first, scope)
        if len(blocks) > 1:
            name = html.unescape(re.sub(r"<.*?>", "", (re.search(r"<h2[^>]*>(.*?)</h2>", first, re.S) or [None, "?"])[1]))[:40]
            found = [f"[{name}] {p}" for p in found]
        problems += found
    return problems


def audit_section(first: str, scope: str) -> list[str]:
    problems: list[str] = []
    title = re.sub(r"<.*?>", "", html.unescape((re.search(r"<h2[^>]*>(.*?)</h2>", first, re.S) or [None, ""])[1]))
    if not re.search(r"\[(최신|생성 대기)", title):
        problems.append(f"생성 제목에 [최신]/[생성 대기]가 없음: {title[:60]}")
    prompt = html.unescape("".join(re.findall(r"<pre[^>]*>(.*?)</pre>", first, re.S)))
    body = re.sub(r"<pre.*?</pre>", "", scope, flags=re.S)
    refs = sorted(set(TAG_RE.findall(prompt)))
    # 태그마다 그 태그가 붙은 그림·영상이 있는지 본다. 레퍼런스·결과 그림은 입력으로 치지 않는다.
    figures = [f for f in re.findall(r"<figure\b.*?</figure>", body, re.S) if re.search(r"<(?:img|video)\b", f)]
    alts = re.findall(r"<(?:img|video)\b[^>]*\balt=\"([^\"]*)\"", body)
    missing = [r for r in refs
               if not any(re.search(rf"@{r}\b", f) for f in figures) and not any(re.search(rf"@{r}\b", a) for a in alts)]
    if missing:
        problems.append(f"입력 그림 없음: @{', @'.join(missing)}에 해당하는 그림이 안 보임(그림 설명에 태그 필요)")
    text = html.unescape(re.sub(r"<.*?>", " ", body))
    for r in refs:
        if not re.search(rf"@{r}\b[^\n]{{0,200}}\.(png|jpe?g|webp|mp4)", text, re.I):
            problems.append(f"@{r}의 파일 경로가 프롬프트 밖 본문에 없음")
    hits = [w for w in SHOT_WORDS if w in text]
    if len(hits) < 3 and 'class="shot-same"' not in body:
        problems.append(f"한글 촬영 정보가 거의 없음(찾은 말: {', '.join(hits) or '없음'})")
    answers = re.findall(r"<td[^>]*>\s*(예|아니오|해당 없음)\s*</td>", body)
    if len(answers) < 8:
        problems.append(f"점검 8줄 칸이 없음(표 안의 예/아니오/해당 없음 답 {len(answers)}개)")
    shown = len(re.findall(r"<(?:img|video)\b", body))
    # 컨트롤(button·a) 하나를 한 번만 센다. class와 글자가 둘 다 맞아도 1개.
    controls = re.findall(r"<(button|a)\b([^>]*)>(.*?)</\1>", body, re.S)
    dls = sum(1 for _, attrs, inner in controls
              if re.search(r'class="[^"]*\bdl\b', attrs) or re.search(r"원본 (받기|다운로드)", inner))
    if dls < shown:
        problems.append(f"원본 다운로드가 빠짐: 그림·영상 {shown}개에 원본 받기 {dls}개")
    copies = [c for c in re.findall(r"<button\b([^>]*)>(.*?)</button>", first, re.S)
              if "복사" in c[1] or re.search(r"copy", c[0], re.I)]
    if not copies:
        problems.append("프롬프트 복사 버튼이 없음")
    # 제목과 바로 아래 설명(첫 표·소제목·프롬프트 전까지)만 본다. 점검 표의 "edit인가" 같은 말에 걸리지 않게.
    head = html.unescape(re.sub(r"<.*?>", " ", re.split(r"<(?:h3|table|pre|div class=\"prompt)\b", first)[0]))
    meta = re.search(r'<p class="meta">(.*?)</p>', first, re.S)
    if meta:  # 생성기 페이지: 메타 줄의 종류를 그대로 믿는다
        is_video = html.unescape(meta.group(1)).startswith("영상 생성")
    else:  # 손으로 만든 옛 페이지: 추정
        is_edit = re.search(r"edit", title + head, re.I) or "@video" in prompt
        is_video = not is_edit and re.search(r"Seedance|영상 생성|video", title + head + prompt[:300], re.I)
    if is_video:
        problems += _camera_problems(body, prompt)
    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    bad = 0
    for f in argv[1:]:
        problems = audit(Path(f).read_text(encoding="utf-8"))
        print(f"== {f}: " + ("통과" if not problems else f"{len(problems)}건"))
        for p in problems:
            print(f"- {p}")
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
