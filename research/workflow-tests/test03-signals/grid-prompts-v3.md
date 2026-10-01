# 세 번의 불빛 — 씬별 그리드 프롬프트 v3

모델 독립 초안. 아래 에셋은 명세이며 실제 이미지 참조는 아직 없다. 상태: PROMPT_COMPILED / references_pending.

## 필요한 에셋

- INA_NOW: 36세 남색 외투·짧은 머리
- JUN_NOW: 31세 초록 코트·검은 가방
- INA_PAST: 12세 붉은 니트·두 갈래 머리
- JUN_PAST: 7세 노란 잠옷
- MOTHER_PAST: 회색 긴 치마, 과거 인물
- ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창
- ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼
- BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문
- BOAT_DECK: 서쪽 난간·객실 문
- RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이
- WHITE_TORCH: 준의 작은 흰 손전등
- PHONE: 준의 휴대전화
- PASSENGER: 얼굴이 보이지 않는 성인 승객의 하체 실루엣, 어두운 코트
- WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자

## SC01_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC01, ATTIC, 현재 18:40, 해 질 무렵.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH01_P01): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 벽의 사진을 잡은 이나.
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "on", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC01_SH01_P02): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 빈 사각형과 상자.
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "on", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC01_SH02_P01): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 상자 앞 이나.
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "on", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC01_SH02_P02): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 창틀 앞 이나.
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "on", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
```

## SC01_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC01, ATTIC, 현재 18:40, 해 질 무렵.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH03_P01): WS. 다락에서 바라본 먼 여객선의 객관적 망원 구도. 인물 얼굴은 식별하지 못한다. 포즈: 해질녘의 먼 배. 창틀이 앞에 남는다..
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "on", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC01_SH04_P01): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 켜진 다락.
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "on", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC01_SH04_P02): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 어두워진 다락.
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC01_SH05_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 서랍의 천 아래 빨간 손전등과 흰 흠집..
이 순간의 상태: {"red_torch": "attic_drawer", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 발견 순간은 서랍 안, 종료 시점에는 이나가 든다.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
```

## SC01_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC01, ATTIC, 현재 18:40, 해 질 무렵.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC01_SH06_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 이나의 엄지가 흠집을 문지르고 손잡이 앞에 멈춘다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC02_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC02, ATTIC, 20여 년 전 저녁, 기억.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: past. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH01_P01): WS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 과거 다락의 어린 이나·어머니·켜지는 빨간 등.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
슬롯 2 (SC02_SH02_P01): WS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 카펫 위 어린 이나와 어머니, 창밖 작은 준의 불빛..
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
슬롯 3 (SC02_SH03_P01): MS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 세 손가락을 든 이나.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
슬롯 4 (SC02_SH03_P02): MS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 손등에 닿은 어머니 손.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
```

## SC02_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC02, ATTIC, 20여 년 전 저녁, 기억.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: past. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH04_P01): WS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 창밖 어린 준의 흰 등 한 번이 켜진 순간.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none", "distant_white_on": "yes"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
중간 상태 근거: 점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 2 (SC02_SH04_P02): WS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 같은 구도에서 흰 등만 꺼진 순간.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none", "distant_white_on": "no"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
중간 상태 근거: 점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 3 (SC02_SH05_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 어머니 손에 든 빨간 등과 스위치에 닿은 어린 이나의 손가락.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "yes", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "none"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
슬롯 4 (SC02_SH05_P02): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 흰 흠집이 생긴 옆면.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "no", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
```

## SC02_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC02, ATTIC, 20여 년 전 저녁, 기억.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: past. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC02_SH06_P01): MS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 등을 건네는 어머니.
이 순간의 상태: {"red_torch": "mother_hand", "red_on": "no", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
슬롯 2 (SC02_SH06_P02): MS. 과거 다락 북쪽 고정. 남쪽 창 구조는 현재와 같지만 카펫·사진·아이들의 모습이 보인다. 포즈: 등을 안은 어린 이나.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "ina_location": "attic", "jun_location": "garden", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_PAST: 12세 붉은 니트·두 갈래 머리; JUN_PAST: 7세 노란 잠옷; MOTHER_PAST: 회색 긴 치마, 과거 인물; ATTIC_PAST: 같은 창 구조·카펫·사진·펼친 커튼; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이.
유지/비공개 조건: 과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC03_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC03, BOAT_CABIN, 현재 18:43, 다락과 같은 저녁.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH01_P01): MS. 여객선 객실 동쪽에서 서쪽 창을 보는 고정 카메라. 준은 창 왼쪽. 포즈: 객실 창에 비친 준이 반응 없는 휴대전화를 누른다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_hand", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC03_SH02_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 준이 전화를 오른 주머니에 넣는다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC03_SH03_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 가방 속 흰 등.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 꺼내기 전 가방 속을 보여주는 순간.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 4 (SC03_SH03_P02): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 준 왼손의 흰 등.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
```

## SC03_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC03, BOAT_CABIN, 현재 18:43, 다락과 같은 저녁.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH04_P01): WS. 배에서 바라본 언덕 집의 먼 불빛. 집 안 인물 얼굴은 식별하지 못한다. 포즈: 정전 뒤 어두워진 언덕 집.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC03_SH05_P01): WS. 여객선 객실 동쪽에서 서쪽 창을 보는 고정 카메라. 준은 창 왼쪽. 포즈: 일어서는 준.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC03_SH05_P02): WS. 여객선 객실 동쪽에서 서쪽 창을 보는 고정 카메라. 준은 창 왼쪽. 포즈: 문 앞 준.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_CABIN: 서쪽 창·고정 의자·동쪽 출입문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
빈 슬롯: 4. 새 장면으로 채우지 않는다.
```

## SC03_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC03, BOAT_DECK, 현재 18:43, 다락과 같은 저녁.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC03_SH06_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 문 안의 준.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC03_SH06_P02): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 난간 앞 준.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC04_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC04, ATTIC, 현재 18:44.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH01_P01): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 손잡이를 돌리는 성인 이나.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC04_SH01_P02): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 바닥에 생긴 빛.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC04_SH02_P01): WS. 다락에서 바라본 먼 여객선의 객관적 망원 구도. 인물 얼굴은 식별하지 못한다. 포즈: 아직 멀리 있는 배..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC04_SH03_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 유리에 비친 이나 얼굴 위로 빛이 번진다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
```

## SC04_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC04, ATTIC, 현재 18:44.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH04_P01): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 흔들리는 커튼.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC04_SH04_P02): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 묶인 커튼과 오른손 등.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC04_SH05_P01): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 창밖으로 길게 켜 둔 등을 유지하며 기다린다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC04_SH06_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 꺼진 빨간 등.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 이미 끈 뒤 충전 손잡이를 펴는 순간.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
```

## SC04_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC04, ATTIC, 현재 18:44.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC04_SH06_P02): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 돌아가는 손잡이.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC05_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC05, BOAT_DECK, 현재 18:44, 같은 호출을 받는 쪽.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH01_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 어깨의 가방.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC05_SH01_P02): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 발 사이의 가방.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC05_SH02_P01): WS. 배에서 바라본 언덕 집의 먼 불빛. 집 안 인물 얼굴은 식별하지 못한다. 포즈: 집 불빛이 잠깐 켜졌다 사라진다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 4 (SC05_SH03_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 켜진 흰 등.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 등을 켠 뒤 빛이 난간에 걸리기 직전.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
```

## SC05_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC05, BOAT_DECK, 현재 18:44, 같은 호출을 받는 쪽.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH03_P02): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 난간에 닿은 빛.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC05_SH04_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 가방을 피해 가는 다리.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화; PASSENGER: 얼굴이 보이지 않는 성인 승객의 하체 실루엣, 어두운 코트.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC05_SH04_P02): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 준의 발 가까이 가방.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화; PASSENGER: 얼굴이 보이지 않는 성인 승객의 하체 실루엣, 어두운 코트.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 4 (SC05_SH05_P01): WS. 배에서 바라본 언덕 집의 먼 불빛. 집 안 인물 얼굴은 식별하지 못한다. 포즈: 같은 집에서 다시 길게 켜지는 빛..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
```

## SC05_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC05, BOAT_DECK, 현재 18:44, 같은 호출을 받는 쪽.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC05_SH06_P01): MCU. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 꺼진 흰 등과 손.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 꺼진 등 위에서 손가락으로 연습하는 순간.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC05_SH06_P02): MCU. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 스위치를 기억하는 손가락.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC06_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC06, ATTIC, 현재 18:45.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH01_P01): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 떨리는 손목을 창틀에 대고 배를 따라 등 방향을 옮긴다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC06_SH02_P01): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 창을 향한 등.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC06_SH02_P02): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 천장으로 향한 빛.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC06_SH03_P01): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 발 앞 상자.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
```

## SC06_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC06, ATTIC, 현재 18:45.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH03_P02): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 창 아래 앉은 이나.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC06_SH04_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 기울어진 사진을 그대로 두고 등 손잡이를 쥔다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC06_SH05_P01): MS. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 팔을 고정해 길게 비추며 기다린다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC06_SH06_PRE): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 아래를 보며 손잡이를 돌리는 이나. 배의 응답은 아직 없다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
```

## SC06_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC06, ATTIC, 현재 18:45.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC06_SH06_P01): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 충전 중인 이나 뒤로 배의 첫 흰빛이 켜진 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 2 (SC06_SH06_P02): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 같은 구도에서 먼 배의 흰빛이 꺼진 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC07_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC07, BOAT_DECK, 현재 18:45, 첫 응답 직후.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC07_SH01_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 준의 손에 든 흰 등이 켜진 두 번째 점멸 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 2 (SC07_SH01_P02): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 같은 흰 등이 꺼진 간격.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "none", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 3 (SC07_SH02_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 준의 흰 등이 켜진 세 번째 점멸 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "first_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 4 (SC07_SH02_P02): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 점멸이 끝나 꺼진 흰 등을 든 준.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "first_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
중간 상태 근거: 점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
```

## SC07_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC07, BOAT_DECK, 현재 18:45, 첫 응답 직후.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC07_SH03_P01): WS. 배에서 바라본 언덕 집의 먼 불빛. 집 안 인물 얼굴은 식별하지 못한다. 포즈: 아직 어두운 집의 창..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "first_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC07_SH04_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 등을 흔들려다 멈추고 가방 손잡이에 발을 댄다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "first_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC07_SH05_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 꺼진 흰 등 스위치 위의 손가락.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "second_armed", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 4 (SC07_SH06_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 준이 팔을 완전히 내리고 창을 바라본다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "second_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
```

## SC08_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC08, ATTIC, 현재 18:45, 두 번째 세 번을 보는 쪽.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC08_SH01_P01): WS. 다락에서 바라본 먼 여객선의 객관적 망원 구도. 인물 얼굴은 식별하지 못한다. 포즈: 이나의 시점에서 먼 배의 흰빛이 켜진 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "yes", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "second_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 2 (SC08_SH01_P02): WS. 다락에서 바라본 먼 여객선의 객관적 망원 구도. 인물 얼굴은 식별하지 못한다. 포즈: 같은 배의 흰빛이 꺼진 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "second_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 3 (SC08_SH02_P01): MCU. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 이나가 시선을 고정하고 손잡이를 멈춘다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "second_complete", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC08_SH03_P01): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 이나의 빨간 등이 켜진 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "yes", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
```

## SC08_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC08, ATTIC, 현재 18:45, 두 번째 세 번을 보는 쪽.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC08_SH03_P02): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 같은 빨간 등이 꺼진 순간.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용. 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.
슬롯 2 (SC08_SH04_P01): MCU. 현재 다락 동쪽 사선 고정. 이나와 남쪽 창의 거리를 읽게 한다. 포즈: 이나가 웃고 꺼진 천장등을 잠깐 올려다본다..
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 3 (SC08_SH05_P01): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 덮이기 전 상자.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 4 (SC08_SH05_P02): MS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 옆으로 접힌 뚜껑.
이 순간의 상태: {"red_torch": "ina_hand", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
```

## SC08_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC08, ATTIC, 현재 18:45, 두 번째 세 번을 보는 쪽.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC08_SH06_P01): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 의자를 놓는 이나.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
중간 상태 근거: 등을 창틀에 놓은 뒤 의자를 옮기는 중간 순간.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
슬롯 2 (SC08_SH06_P02): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 빈 의자 옆에 앉은 이나.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
빈 슬롯: 3, 4. 새 장면으로 채우지 않는다.
```

## SC09_GRID01

```text
검수용 2D 단편 애니메이션 그림 콘티. SC09, BOAT_DECK, 현재, 배가 섬에 더 가까워진 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC09_SH01_P01): MCU. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 응답이 끝난 뒤 어둠 속 준의 얼굴.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC09_SH02_P01): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 손바닥을 향한 꺼진 흰 등.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_left_hand", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC09_SH02_P02): CU. 손과 소품의 높은 사선 고정 인서트. 소유자·색·시간 버전을 명시한다. 포즈: 가방 안의 흰 등.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 4 (SC09_SH03_P01): MS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 도착 안내를 듣고 가방을 메며 객실로 향한다..
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
```

## SC09_GRID02

```text
검수용 2D 단편 애니메이션 그림 콘티. SC09, BOAT_DECK, 현재, 배가 섬에 더 가까워진 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC09_SH04_P01): WS. 배에서 바라본 언덕 집의 먼 불빛. 집 안 인물 얼굴은 식별하지 못한다. 포즈: 어두운 언덕 집 창을 다시 본다..
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 2 (SC09_SH05_P01): WS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 문 앞 준.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "deck", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
슬롯 3 (SC09_SH05_P02): WS. 갑판 동쪽에서 서쪽 난간과 준을 보는 고정 카메라. 해안은 배경. 포즈: 빈 갑판.
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): JUN_NOW: 31세 초록 코트·검은 가방; BOAT_DECK: 서쪽 난간·객실 문; WHITE_TORCH: 준의 작은 흰 손전등; PHONE: 준의 휴대전화.
유지/비공개 조건: 현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.
빈 슬롯: 4. 새 장면으로 채우지 않는다.
```

## SC09_GRID03

```text
검수용 2D 단편 애니메이션 그림 콘티. SC09, ATTIC, 현재, 배가 섬에 더 가까워진 뒤.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.
슬롯 1 (SC09_SH06_P01): WS. 현재 다락 북쪽에서 남쪽 창을 보는 고정 카메라. 이나는 창 오른쪽에 선다. 포즈: 이나와 빈 의자, 창틀의 빨간 등. 모두 조용히 남는다..
이 순간의 상태: {"red_torch": "window_sill", "red_on": "no", "white_torch": "jun_bag", "white_on": "no", "phone": "jun_right_pocket", "house_power": "off", "ina_location": "attic", "jun_location": "cabin", "reply": "acknowledged", "torch_scratch": "white_mark"}.
외형 참조 후보(모두 화면에 넣으라는 뜻 아님): INA_NOW: 36세 남색 외투·짧은 머리; ATTIC_NOW: 빈 벽·포장상자·남쪽 바다 창; RED_TORCH: 빨간 충전 손전등·흰 흠집·접이 손잡이; WAITING_CHAIR: 현재 다락에 남겨 둔 등받이 나무 의자.
유지/비공개 조건: 현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```
