---
name: blockout-convention
description: 다음 프로젝트에서 블록아웃 자산을 시작하거나 새 버전·렌더·승인 고정을 관리할 때 폴더·manifest 규약 초안을 적용한다.
---

초안, 사용자 검토 대기

# blockout-convention

근거: `C:\Users\uicus\Dev\dot-handoff\blockout_plan_2026-11-07.md`.
이 규약은 아직 승인되지 않았다. 새 자산의 제안 구조로 사용하고 확정 규칙이라고 설명하지 않는다.
기존 프로젝트의 파일 이동·이름 변경·archive 정리는 자동으로 시작하지 않는다.
승인된 도면·치수·사용자 지시가 우선이다. PLATING의 수치·씬 번호·드라이브 경로는 다음 프로젝트에 복사하지 않는다.

## 새 자산 시작

1. 프로젝트·자산 이름과 쓰기 허용 루트를 확인한다. 작업 단위는 세션·에이전트·날짜가 아니라 자산이다.
2. 아래 구조를 제안한다. 사용자 검토 전에는 이 스킬을 읽었다는 이유만으로 기존 자산을 전환하지 않는다.

```text
<project>/
  blockout/<asset>/
    manifest.toml
    versions/v001/
      <asset>.blend
      build.py
      NOTES.md
    renders/v001/<view>/
    archive/
  generated/
```

3. 새 자산 작성이 요청된 범위에서 manifest와 첫 버전의 근거를 기록한다. 치수 가정은 가정으로 표시한다.

```toml
asset = "example_asset"
current = "v001"
variants = []
[versions.v001]
date = "" # 실제 작업 날짜 YYYY-MM-DD
change = "" # 실제 변경 내용
by = "" # 실제 작업자
[pins] # 기본 비어 있음
```

## 새 버전 만들기

1. manifest의 current와 기존 버전 폴더를 읽는다. 날짜·mtime·파일명 최댓값만으로 current를 덮어쓰지 않는다.
2. 다음 미사용 세 자리 `vNNN` 폴더를 만든다. `v2i`, `v32_seats`처럼 접미사를 버전으로 쓰지 않는다.
3. 새 폴더에 `<asset>.blend`, `build.py`, `NOTES.md`를 완성한다. 만들어진 버전 파일은 수정하지 않는다.
4. 실제 작성자·날짜·변경 근거를 `[versions.vNNN]`에 기록하고 current를 새 판으로 갱신한다.
5. 문서는 특정 최신 번호를 반복 기입하지 않고 “manifest의 current”를 참조한다.

Blender 직접 저장과 build.py의 사용 비중은 미확인이다. 원문 계획은 두 파일을 함께 두지만 재생성 방식은 사용자 검토가 필요하다.
기존 버전이 불완전하면 몰래 덮어쓰지 않고 새 버전 또는 미결로 기록한다.

## 변형·렌더

- 낮/밤·좌석 같은 변형은 우선 .blend 안 Scene/컬렉션으로 구분한다. 별도 파일이 필요하면 manifest의 variants에 명시한다.
- 렌더 위치는 `renders/vNNN/<view>/`, 변형 뷰 예는 `renders/v057/night/`다.
- 렌더·시트 이름은 `<asset>_vNNN_<view>[_<variant>].png`다. 날짜를 이름에 넣지 않는다.
- 사용 전 manifest current 또는 승인 pin과 비교한다. 기준보다 옛 렌더는 STALE로 표시한다.
- 렌더 이름의 버전이 없거나 manifest에 없는 판이면 규약 미확인으로 보고하고 구조 레퍼런스로 확정하지 않는다.

## 고정은 승인 문장이 있을 때만

1. 실제 사용자 승인 문장·승인자·날짜·대상 범위를 확보한다. 오래된 렌더를 썼다는 사실은 고정 승인이 아니다.
2. 명시한 대상만 `[pins]`에 기록한다. 아래는 형식 예이며 실제 승인이 아니다.

```toml
[pins]
# "<대상>" = { version = "v001", reason = "실제 승인 문장 인용", approved_by = "실제 승인자", date = "YYYY-MM-DD" }
```

3. 고정 대상 렌더만 pin 버전과 비교해 PINNED 또는 STALE로 표시한다. 다른 대상은 current 기준이다.

승인 문장 없는 pin·임의 씬 예외·기존 기록에서 추측한 고정은 만들지 않는다.

## 검사·보관·도구 경계

- 검사 후보는 manifest 미등록 판, 접미사·날짜 폴더, current/pin과 렌더 버전 차이, 파일 목록·해시 불일치다.
- 원문 계획은 해시 기록과 대조를 요구하지만 manifest의 해시 저장 필드 형식은 미확인이다. 기존 스키마처럼 지어내지 않는다.
- 원문 초안의 정리안은 current·pin이 가리키지 않는 버전을 archive로 이동하고 작업 폴더에는 최근 3버전 렌더만 두는 것이다.
- 이 보관안의 승인 여부와 Drive “최신 5개 묶음” 유지 여부는 미확인이다. 승인·이동 범위 확인 전 정리하지 않는다. 삭제하지 않는다.
- 실제 이동이 승인되면 대상 절대 경로가 허용된 자산 폴더 안인지 확인하고 current·pin 대상 보존을 먼저 확인한다.
- 현행 plating-tools의 `versions check`는 별도 spec의 파일명·README·근거 pin을 비교한다. manifest current·폴더 불변 해시 검사는 아직 없다.
- manifest `[pins]`와 plating-tools `pins.toml`의 `[[pin]]`은 다른 형식이다. 자동 변환·검사된 것으로 설명하지 않는다.
- 형상·치수는 실제 블록아웃 검산으로 확인한다. 파일명·해시 검사가 치수 검증을 대신하지 않는다.
