# PLATING BASE PROMPT

> 코렐라인st LAIKA 스타일 3D AI 애니메이션 / 벌레식량 디스토피아 계급물
> **최신본.** 날짜별 스냅샷은 `backups/base_prompt_MMDD.md`.

**Version:** v0901
**Updated:** 2026-09-01

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
`① STYLE` → `② HUMAN+MASK`(가면 캐릭터일 때만) → `[CHARACTER]`(④+⑤) → `[COMPOSITION]` → `① WORLD` → `① RENDER` → `③ AVOID`

---

## ① 고정 공통 블록 (복붙, 수정 금지)

```
[MEDIUM & STYLE] Stylized 3D animation in the LAIKA / Coraline tradition,
modeled on the film's HUMAN characters (not the button-eyed doll). Characters
have LAIKA's stylized-but-human proportions: tall, slightly elongated and
angular frames, long limbs, defined cheekbones, expressive naturalistic faces
with normal human-sized eyes. Subtle skin pores and cloth-weave texture,
cinematic craft feel.

[WORLD & TONE] a dystopian fable where insects are the only food left; a
class-divided society staged as a recurring contrast between a warm, grimy,
lived-in underclass and a cold, sterile, over-clean elite world; food plated
as art, people displayed behind glass; uncanny yet grounded, quiet unease,
socially critical.

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
단독:  single centered waist-up portrait, cold sterile over-clean elite setting behind glass.

몽타주: a montage triptych, three vertical panels of equal width divided by thin
       dark seams, each panel a waist-up portrait, unified cold lighting, matched eyeline.
```

---

## ⑤ 캐릭터 슬롯 프리셋 (부자손님 A/B/C — 확정본)

부자손님 A/B/C: 진우가 최상층 레스토랑에서 만나는 손님들. 언제나 반가면 착용, 권력 최상층. 최하층 손님들과 대비. 소품 동물은 택1.

| 손님 | 동물(택1 확정) | 체형 키워드 | 표정/성격 | 개별 avoid 추가 |
|---|---|---|---|---|
| **A** 귀부인 (30대 후반) | PEACOCK 공작새 | matronly, plump, heavy-set, double chin, ample bust, corpulent | vain class-obsessed hauteur, chin lifted | `thin slim build` |
| **B** 사업가 (50~60 신사) | BULLDOG 불독 | lean upright, silver hair | condescending smirk, quiet contempt | — |
| **C** 여자아이 (10살) | CAT 고양이 | age 8–10, round cheeks, small head-body ratio, short | bratty entitled pout | `adult-proportioned child, mature adult face` |

**동물 택일 근거:** A 공작새=허영/과시(돼지 대신 인간형 유지 용이) · C 고양이=도도(염소보다 "귀엽고 도도" 부합).

---

## 변경 이력

- **v0901** — 초기 구조화. HUMAN+MASK 조건부 블록 신설(인간+가면 명확화, 동물 morphology 차단). 부자손님 A/B/C 슬롯 프리셋 확정. AVOID 베이스/가면 분리.
