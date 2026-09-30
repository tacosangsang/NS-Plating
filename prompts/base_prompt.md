# PLATING BASE PROMPT

> 코렐라인st LAIKA 스타일 3D AI 애니메이션 / 벌레식량 디스토피아 계급물
> **최신본.** 날짜별 스냅샷은 `backups/base_prompt_MMDD.md`.

**Version:** v0930
**Updated:** 2026-09-30

---

## 구조 개요

```
[STYLE] ─┐
[HUMAN+MASK] ├─ 고정 공통 블록 (모든 캐릭터 동일)
[WORLD] │
[RENDER] │
[AVOID] ─┘
[CHARACTER] ─── 슬롯 (캐릭터별 교체)
[COMPOSITION] ─ 슬롯 (단독/몽타주 전환)
```

**조립 순서:**
`① STYLE` → `② HUMAN+MASK`(가면 캐릭터일 때만) → `[CHARACTER]`(④) → `[COMPOSITION]` → `① WORLD` → `① RENDER` → `③ AVOID`

---

## ① 고정 공통 블록 (복붙, 수정 금지)

```
[MEDIUM & STYLE] Stylized 3D animation in the LAIKA / Coraline tradition,
modeled on the film's HUMAN characters (not the button-eyed doll). Characters
have LAIKA's stylized-but-human proportions: tall, slightly elongated and
angular frames, long limbs, defined cheekbones, expressive naturalistic faces
with normal human-sized eyes. Subtle skin pores and cloth-weave texture,
cinematic craft feel.

[WORLD & TONE] a dystopian fable; a class-divided society staged as a
recurring contrast between a warm, grimy, lived-in underclass and the elite
world; food plated as art; uncanny yet grounded, quiet unease, socially
critical.

[RENDER & CAMERA] naturalistic cinematic lighting, high contrast, controlled
palette, subtle shallow depth of field, volumetric haze and dust, filmic
composition.
```

---

## ② 조건부 블록 — 가면 캐릭터일 때만 삽입

```
[CRITICAL — HUMAN + MASK] UNMISTAKABLY A HUMAN BEING WEARING A DECORATIVE MASK.
The animal identity exists ONLY as a crafted mask object worn over the upper
face — a separate prop with a visible rim where mask meets bare human skin.
Everything else fully human: human skin, human hair, human ears at the sides of
the head, human neck, human hands, human body. NO fur, NO snout on the face, NO
paws, NO tail, NO animal ears growing from the head, NO hybrid anatomy. Mask is
worn, not fused.
```

---

## ③ AVOID — 베이스(항상) + 가면(조건부)

```
avoid [BASE]: puppet, doll, toy figurine, felt/clay doll, visible stitching
seams, oversized anime eyes, chibi, caricature, glossy plastic skin, miniature
diorama look.

avoid [MASK, 가면 캐릭터 추가]: full-face mask, mask covering the mouth, animal
snout on the face, fur on skin, animal ears growing from the head,
furry/anthropomorphic hybrid, animal-human fusion.
```

---

## ④ 슬롯 템플릿

**[CHARACTER]** — 아래 순서로 채움:

```
[CHARACTER] a [나이/성별/체형], [체형 상세 — 살집/마른/키], [의상 + 계급 신호],
[손/장신구]. He/She wears a [ANIMAL] half-MASK over the upper face — [가면
디테일: 재질·형태], a visible rim on [bare human 부위], own human ears and
hair(line) visible beside it — exposed [하관 인간 부위], [표정 + 성격].
```

**[COMPOSITION]** — 택1:

```
단독:  single centered waist-up portrait.

몽타주: a montage triptych, three vertical panels of equal width divided by thin
       dark seams, each panel a waist-up portrait, unified cold lighting, matched eyeline.
```

---

## 변경 이력

- **v0901** — 초기 구조화. HUMAN+MASK 조건부 블록 신설(인간+가면 명확화, 동물 morphology 차단). 부자손님 A/C 프리셋 확정, B 미확정. AVOID 베이스/가면 분리. 흰 토끼 가면(귀 없는 버전) 개별 프롬포트 추가.
- **v0930** — 3-2차 시나리오 (수정본) 기준으로 옛 기획 삭제. [WORLD & TONE]의 "insects are the only food left", "cold, sterile, over-clean elite world", "people displayed behind glass" 삭제. [COMPOSITION] 단독의 유리 뒤 배경 삭제. ⑤ 부자손님 A/B/C 프리셋(공작/불독/고양이) 삭제. ⑥ 흰 토끼 가면 귀 없는 버전 삭제.
