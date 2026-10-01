# 의자 하나 — 씬별 그리드 프롬프트 v3

모델 독립 초안. 아래 에셋은 명세이며 실제 이미지 참조는 아직 없다. 상태: PROMPT_COMPILED / references_pending.

## 필요한 에셋

- YUN: 회색 작업복, 짧은 검은 머리, 성인 여성
- HA: 황토 코트, 묶은 머리, 성인 여성
- SHOP: 북쪽 재봉틀·동쪽 문·중앙 작업대·서쪽 창
- CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열
- BRACE: 작은 L자 금속판 두 장, 나사 네 개
- BAG: 빈 천 공구가방
- STOOL: 접이식 보조의자
- HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리
- SHOP_EXTERIOR: 동쪽 출입구 바깥 골목, 같은 가게 문과 유리

## SC01_GRID01

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC01, SHOP, 첫날 오후 15:00.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH01_P01): WS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 테이프 끝을 잡은 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "closed", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC01_SH01_P02): WS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 테이프가 사라진 벽과 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "closed", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC01_SH02_P01): MS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 문 밖에 선 하.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "closed", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC01_SH02_P02): MS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 문 안으로 들어온 하.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC01_GRID02

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC01, SHOP, 첫날 오후 15:00.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH03_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 윤은 테이프를 보며 하의 주차 위치를 지적한다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC01_SH04_P01): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 가방과 등받이 사이 공간.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC01_SH04_P02): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 윤의 손에 막힌 가방.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC01_SH05_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 하의 가방 손잡이.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "ha", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC01_GRID03

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC01, SHOP, 첫날 오후 15:00.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH05_P02): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 작업대 위 가방.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC01_SH06_P01): MS. 남서쪽에서 하를 보는 고정 카메라. 하의 시선은 화면 왼쪽의 윤. 포즈: 상자 안에 들어간 손.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC01_SH06_P02): MS. 남서쪽에서 하를 보는 고정 카메라. 하의 시선은 화면 왼쪽의 윤. 포즈: 같은 봉투로 돌아간 단추.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC01_SH07_P01): MCU. 남서쪽에서 하를 보는 고정 카메라. 하의 시선은 화면 왼쪽의 윤. 포즈: 하는 의자를 향해 시선을 내리며 집에 책상이 생겼다고 말한다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC01_GRID04

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC01, SHOP, 첫날 오후 15:00.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH08_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 테이프가 붙은 손.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC01_SH08_P02): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 테이프를 떼는 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC02_GRID01

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC02, SHOP, 같은 날 15:03, 정리 작업이 조금 진행된 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH01_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 가방을 펼친 하.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "folded_wall", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC02_SH01_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 보조의자를 내민 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "yun_hand", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC02_SH02_P01): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 윤이 보조의자를 내밀지만 하는 손을 내리지 않는다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "yun_hand", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC02_SH03_P01): MCU. 남서쪽에서 하를 보는 고정 카메라. 하의 시선은 화면 왼쪽의 윤. 포즈: 하는 윤을 똑바로 보며 말을 꺼낸다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "yun_hand", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC02_GRID02

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC02, SHOP, 같은 날 15:03, 정리 작업이 조금 진행된 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH04_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 반쯤 접힌 보조의자.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "yun_hand", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
중간 상태 근거: 아직 접는 중인 보조의자는 윤의 손에 있다.
슬롯 2 (SC02_SH04_P02): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 바닥에 닫힌 보조의자.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC02_SH05_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 좌판을 잡은 하.
이 순간의 상태: {"chair": "floor", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC02_SH05_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 문 쪽으로 든 의자.
이 순간의 상태: {"chair": "ha_hands", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC02_GRID03

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC02, SHOP, 같은 날 15:03, 정리 작업이 조금 진행된 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH06_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 윤의 손이 좌판 밑으로 들어감.
이 순간의 상태: {"chair": "ha_hands", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC02_SH06_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 두 사람 사이 기울어진 의자.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC02_SH07_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 의자 다리의 벌어진 이음새와 떨어지는 나무 가루..
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC02_SH08_P01): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 함께 내리는 의자.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC02_GRID04

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC02, SHOP, 같은 날 15:03, 정리 작업이 조금 진행된 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH08_P02): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 옆으로 누운 의자.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC03_GRID01

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC03, SHOP, 같은 날 15:06.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH01_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 서랍이 열리고 금속판과 나사가 보인다..
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "drawer", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
중간 상태 근거: 서랍을 연 대표 순간. 꺼내 작업대에 놓는 종료 상태와 구분.
슬롯 2 (SC03_SH02_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 다리 옆의 종이.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC03_SH02_P02): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 다리와 맞닿은 종이.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC03_SH03_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 윤은 나사 머리에 묻은 먼지를 닦으며 어제 일을 말한다..
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC03_GRID02

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC03, SHOP, 같은 날 15:06.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH04_P01): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 하가 의자를 보고 윤이 하를 보는 시선이 엇갈린다..
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC03_SH05_P01): MCU. 남서쪽에서 하를 보는 고정 카메라. 하의 시선은 화면 왼쪽의 윤. 포즈: 하의 손이 좌판의 매끈한 부분을 쓸어 본다..
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC03_SH06_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 윤은 나사를 하나씩 정렬하며 짧게 말한다..
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC03_SH07_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 닫힌 창 앞 하.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC03_GRID03

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC03, SHOP, 같은 날 15:06.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH07_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 틈이 생긴 창.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC03_GRID04

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC03, SHOP, 같은 날 15:06.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH08_P01): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 황토 코트를 벗기 직전 단추를 푼 하.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "ochre_coat"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA: 황토 코트, 묶은 머리, 성인 여성; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC03_SH08_P02): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 회색 니트 차림으로 의자 옆에 앉은 하.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC03_GRID05

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC03, SHOP, 같은 날 15:06.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH08B_P01): WS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 바닥의 의자를 나눠 잡은 자매.
이 순간의 상태: {"chair": "floor_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC03_SH08B_P02): WS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 작업대에 옆으로 놓인 의자.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC04_GRID01

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC04, SHOP, 같은 날 15:08, 작업대에서 수리 시작.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH01_P01): WS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 작업대 전체와 누운 의자, 역할이 나뉜 두 사람..
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC04_SH02_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 작업대 끝의 나사.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC04_SH02_P02): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 빈 끝과 바닥 나사.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC04_SH03_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 동시에 숙인 자매.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC04_GRID02

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC04, SHOP, 같은 날 15:08, 작업대에서 수리 시작.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH03_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 나사를 든 윤.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC04_SH04_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 드라이버를 가리는 손.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC04_SH04_P02): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 서로 겹치지 않는 손과 도구.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "cracked", "brace": "table", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC04_SH05_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 첫 나사가 보강판을 잡는다..
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "one_screw", "brace": "chair_partial", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC04_GRID03

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC04, SHOP, 같은 날 15:08, 작업대에서 수리 시작.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH06_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 윤이 손목을 멈추고 하를 본다..
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "one_screw", "brace": "chair_partial", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC04_SH07_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 윤이 도구를 내밈.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "one_screw", "brace": "chair_partial", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC04_SH07_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 하가 도구를 잡음.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "one_screw", "brace": "chair_partial", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC04_SH08_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 세 나사가 고정된 보강판과 마지막 나사.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "three_screws", "brace": "chair_partial", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
중간 상태 근거: 명시한 시간 생략 뒤의 첫 그림. 앞 샷 종료의 한 나사 상태에서 작업이 생략됨.
```

## SC04_GRID04

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC04, SHOP, 같은 날 15:08, 작업대에서 수리 시작.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH08_P02): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 네 나사가 고정된 보강판.
이 순간의 상태: {"chair": "workbench_side", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC04_SH08B_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 작업대 위 의자를 든 두 사람.
이 순간의 상태: {"chair": "both_hands_above_workbench", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
중간 상태 근거: 작업대에서 이미 들어 올린 중간 순간.
슬롯 3 (SC04_SH08B_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 바닥에 바로 선 의자.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 4. 새 장면으로 채우지 않는다.
```

## SC05_GRID01

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC05, SHOP, 같은 날 15:15, 도구를 치운 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH01_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 의자를 누르는 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC05_SH01_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 앉기 직전 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC05_SH02_P01): MS. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 앉은 윤.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC05_SH02_P02): MS. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 허공에서 멈춘 발.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC05_GRID02

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC05, SHOP, 같은 날 15:15, 도구를 치운 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH03_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 펼치는 보조의자.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "floor_folded", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC05_SH03_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 나란히 앉은 자매.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC05_SH04_P01): CU. 작업대 남쪽 바닥 높이의 고정 카메라. 하의 두 발만 보인다. 포즈: 바닥을 두드리는 하의 발.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC05_SH04B_P01): CU. 작업대 남쪽 높은 사선 인서트. 인물들의 손과 물체 방향은 투샷과 동일. 포즈: 작업대를 두드리는 윤의 두 손가락.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC05_GRID03

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC05, SHOP, 같은 날 15:15, 도구를 치운 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH05_P01): MCU. 남서쪽에서 하를 보는 고정 카메라. 하의 시선은 화면 왼쪽의 윤. 포즈: 하가 윤에게 오늘의 식사를 묻는다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC05_SH06_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 윤은 시간을 확인하려던 시선을 하에게 돌린다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC05_SH07_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 가방에 들어가는 장갑.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "undecided", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC05_SH07_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 하 쪽으로 밀린 손잡이.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "table", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
중간 상태 근거: 손잡이를 밀어 받기 직전. 가방의 최종 소유는 하, 대표 순간에는 작업대 위.
```

## SC05_GRID04

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC05, SHOP, 같은 날 15:15, 도구를 치운 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH08_P01): 2SHOT. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 하의 마지막 질문에 윤이 고개를 들고 대답한다..
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC06_GRID01

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC06, ENTRANCE, 같은 날 15:20, 출발.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH01_P01): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 서로 다른 쪽을 잡은 손.
이 순간의 상태: {"chair": "floor", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC06_SH01_P02): MS. 남쪽 고정 투샷. 윤 왼쪽·하 오른쪽, 동쪽 문은 화면 오른쪽. 포즈: 같이 든 의자.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC06_SH02_P01): WS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 문 앞의 가로 의자.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC06_SH02_P02): WS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 문틀 안 세로 의자.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC06_GRID02

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC06, ENTRANCE, 같은 날 15:20, 출발.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH03_P01): MCU. 남동쪽에서 윤을 보는 고정 카메라. 윤의 시선은 화면 오른쪽의 하. 포즈: 윤이 빈 작업대를 마지막으로 본다..
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC06_SH04_P01): MS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 혼자 당기지 않는 하.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC06_SH04_P02): MS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 윤의 손이 돌아온 의자.
이 순간의 상태: {"chair": "both_hands", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 4 (SC06_SH07_P01): WS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 열린 빈 출입구.
이 순간의 상태: {"chair": "outside_ground_supported_by_yun", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
```

## SC06_GRID03

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC06, ENTRANCE, 같은 날 15:20, 출발.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH07_P02): WS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 지퍼를 보는 하.
이 순간의 상태: {"chair": "outside_ground_supported_by_yun", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC06_SH08_P01): MS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 열린 가방의 하.
이 순간의 상태: {"chair": "outside_ground_supported_by_yun", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC06_SH08_P02): MS. 수선집 남서쪽에서 동쪽 출입문을 보는 고정 카메라. 출구 방향은 화면 오른쪽. 포즈: 닫힌 문 유리 너머 두 자매.
이 순간의 상태: {"chair": "outside_ground_supported_by_yun", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "closed", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 4. 새 장면으로 채우지 않는다.
```

## SC06_GRID04

```text
검수용 절제된 2D 애니메이션 그림 콘티. SC06, SHOP_EXTERIOR, 같은 날 15:20, 출발.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH05_P01): WS. 건물 바깥 남쪽에서 출입구를 보는 넓은 고정 카메라. 새 공간을 먼저 설정한다. 포즈: 문밖에서 의자 양쪽 높이를 맞추고 골목으로 향한다..
이 순간의 상태: {"chair": "both_outside", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 2 (SC06_SH06_P01): MS. 건물 바깥 남쪽에서 출입구를 보는 넓은 고정 카메라. 새 공간을 먼저 설정한다. 포즈: 문밖 바닥에 내려놓는 의자.
이 순간의 상태: {"chair": "both_outside", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
슬롯 3 (SC06_SH06_P02): MS. 건물 바깥 남쪽에서 출입구를 보는 넓은 고정 카메라. 새 공간을 먼저 설정한다. 포즈: 의자를 받친 윤과 문으로 돌아서는 하.
이 순간의 상태: {"chair": "outside_ground_supported_by_yun", "chair_integrity": "braced_four_screws", "brace": "chair_fixed", "bag": "ha", "door": "open", "ownership": "ha", "stool": "open_next_to_chair", "ha_wardrobe": "gray_knit"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): YUN: 회색 작업복, 짧은 검은 머리, 성인 여성; HA_SHIRT: 하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리; CHAIR: 청록 좌판, 오른쪽 뒤 다리 균열.
빈 슬롯: 4. 새 장면으로 채우지 않는다.
```
