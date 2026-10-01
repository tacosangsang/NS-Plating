# 빛 배달 — 씬별 그리드 프롬프트 v2

모델 독립 초안. 아래 에셋은 명세이며 실제 이미지 참조는 아직 없다. 상태: PROMPT_COMPILED / references_pending.

## 필요한 에셋

- PIP: 청록 로봇, 바퀴2·팔2·눈등1
- BATTERY: 주황 배터리 한 개, 몸 왼쪽 장착
- PLANT: 붉은 이 빠진 화분·잎2
- HALL: 서쪽 출발→동쪽 작업실 문
- WORKSHOP: 남쪽 문·북쪽 창가·서쪽 공구대
- LAMP: 배터리 수직 도크·흰색 갓
- RAMP: 직사각 나무 판자
- CART: 낮은 바퀴 받침
- BOLT: 작은 시험용 볼트

## SC01_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC01, HALL, 오후, 폐쇄 온실.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC01_SH01_P01): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 볼트를 집은 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC01_SH01_P02): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 정리통 위의 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC01_SH02_P01): CU. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 꺼지기 직전 눈등.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC01_SH02_P02): CU. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 열린 집게와 꺼진 눈등.
이 순간의 상태: {"battery": "pip_left_body", "power": "off", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC01_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC01, HALL, 오후, 폐쇄 온실.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC01_SH03_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 약간 빠진 배터리.
이 순간의 상태: {"battery": "pip_left_body", "power": "off", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC01_SH03_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 몸 안에 고정된 배터리.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC01_SH04_P01): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 닫힌 오른 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC01_SH04_P02): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 화분 앞에 선 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC01_GRID03

```text
검수용 무성 3D 애니메이션 그림 콘티. SC01, HALL, 오후, 폐쇄 온실.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC01_SH05_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 잎 두 장 위 작은 빛이 사라진다..
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC01_SH06_P01): MS. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 잎 앞에서 멈춘 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC01_SH06_P02): MS. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 화분 바닥을 받친 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC01_SH07_P01): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 화분을 안은 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC01_GRID04

```text
검수용 무성 3D 애니메이션 그림 콘티. SC01, HALL, 오후, 폐쇄 온실.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC01_SH07_P02): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 동쪽을 향한 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC02_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC02, HALL, 잠시 후, 통로 중간.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC02_SH01_P01): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 평평하게 든 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC02_SH01_P02): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 테두리까지 기운 흙.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC02_SH02_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 화분을 바닥에 내리고 흙 한 톨이 깨진 테두리 옆으로 떨어진다..
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC02_SH03_P01): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 벽에서 당긴 판자.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC02_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC02, HALL, 잠시 후, 통로 중간.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC02_SH03_P02): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 턱 위 비스듬한 판자.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_unstable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC02_SH04_P01): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 한 바퀴가 오른 판자.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_unstable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC02_SH04_P02): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 돌아간 판자와 물러난 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_unstable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC02_SH05_P01): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 틈에 걸린 판자.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_unstable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC02_GRID03

```text
검수용 무성 3D 애니메이션 그림 콘티. SC02, HALL, 잠시 후, 통로 중간.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC02_SH05_P02): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 빈손으로 턱 위 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_stable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC02_SH06_P01): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 판자 아래 화분을 든 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "hall_before_step", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_stable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC02_SH06_P02): MS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 턱 위의 핍과 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_stable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC02_SH07_P01): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 턱 위 바닥 화분과 판자를 든 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "step_stable", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC02_GRID04

```text
검수용 무성 3D 애니메이션 그림 콘티. SC02, HALL, 잠시 후, 통로 중간.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC02_SH07_P02): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 다시 화분을 안은 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC03_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC03, WORKSHOP, 작업실 문 앞과 안, 연속.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC03_SH01_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 반쯤 열린 문과 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC03_SH01_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 문을 미는 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "door_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC03_SH02_P01): MS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 문을 버티는 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "door_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC03_SH02_P02): MS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 화분에 닿지 않는 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "door_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC03_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC03, WORKSHOP, 작업실 문 앞과 안, 연속.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC03_SH03_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 바퀴 앞의 걸쇠.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "door_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "ajar", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC03_SH03_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 내려간 걸쇠.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "door_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC03_SH04_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 문 안으로 향한 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "door_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC03_SH04_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 작업실 안 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC03_GRID03

```text
검수용 무성 3D 애니메이션 그림 콘티. SC03, WORKSHOP, 작업실 문 앞과 안, 연속.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC03_SH05_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 바닥 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "pip_both_hands", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC03_SH05_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 창을 올려다보는 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "under_shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC03_SH06_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 작업등의 빈 수직 도크..
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "under_shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC03_SH07_P01): MS. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 빈 도크와 왼쪽 배터리.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "under_shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC03_GRID04

```text
검수용 무성 3D 애니메이션 그림 콘티. SC03, WORKSHOP, 작업실 문 앞과 안, 연속.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC03_SH07_P02): MS. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 다시 고정된 배터리.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "under_shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC04_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC04, WORKSHOP, 잠시 후, 빛을 찾는 마지막 시도.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC04_SH01_P01): MS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 받침 위 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "under_shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "workshop_floor", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC04_SH01_P02): MS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 받침 옆 바닥 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC04_SH02_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 한 바퀴를 올린 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC04_SH02_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 앞으로 밀린 받침.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC04_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC04, WORKSHOP, 잠시 후, 빛을 찾는 마지막 시도.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC04_SH03_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 바퀴 앞 조각.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC04_SH03_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 바퀴에 끼운 조각.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC04_SH04_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 빈손으로 받침에 오른 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC04_SH04_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 바닥에 돌아온 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC04_GRID03

```text
검수용 무성 3D 애니메이션 그림 콘티. SC04, WORKSHOP, 잠시 후, 빛을 찾는 마지막 시도.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC04_SH04B_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 바닥 화분을 든 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf_floor", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC04_SH04B_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 선반에 놓인 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC04_SH05_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 손잡이를 미는 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC04_SH05_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 회색빛 속 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC04_GRID04

```text
검수용 무성 3D 애니메이션 그림 콘티. SC04, WORKSHOP, 잠시 후, 빛을 찾는 마지막 시도.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC04_SH06_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 차광판 아래 손.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC04_SH06_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 안쪽으로 당겨진 화분.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC04_SH07_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 작업등을 든 핍.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "workshop_shelf", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC04_SH07_P02): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 화분 옆 작업등.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC05_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC05, WORKSHOP, 연속, 선반 앞 준비.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC05_SH01_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 화분 쪽으로 도는 갓.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC05_SH01_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 몸 왼쪽 슬롯 아래 도크.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC05_SH02_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 몸 앞을 가로지른 오른 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC05_SH02_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 집게 바로 아래 도크.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC05_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC05, WORKSHOP, 연속, 선반 앞 준비.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC05_SH03_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 집게가 도크 가장자리에 닿아 멈춘다..
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC05_SH04_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 도크 위 볼트.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC05_SH04_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 도크 안 볼트.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC05_SH05_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 흙을 모은 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC05_GRID03

```text
검수용 무성 3D 애니메이션 그림 콘티. SC05, WORKSHOP, 연속, 선반 앞 준비.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC05_SH05_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 잎 옆 빈 집게.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC05_SH06_P01): MCU. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 약해진 눈등.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC05_SH06_P02): MCU. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 배터리를 누른 왼손.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC05_SH07_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 슬롯·오른손·아래 도크가 함께 보이는 준비 자세.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC06_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC06, WORKSHOP, 연속, 전원 전환.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC06_SH01_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 오른손이 잡은 배터리와 아래의 도크.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC06_SH01_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 접점이 아직 닿아 있는 분리 직전.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC06_SH02_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 접점 끝의 배터리.
이 순간의 상태: {"battery": "pip_left_body", "power": "on", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "closed_when_powered"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC06_SH02_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 벌어진 집게.
이 순간의 상태: {"battery": "falling", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC06_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC06, WORKSHOP, 연속, 전원 전환.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC06_SH03_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 도크 위 떨어지는 배터리.
이 순간의 상태: {"battery": "falling", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC06_SH03_P02): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 도크에 앉은 배터리.
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC06_SH04_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 꺼진 램프와 정지한 핍.
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "no", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC06_SH04_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 켜진 램프·꺼진 핍·변하지 않은 화분.
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC06_GRID03

```text
검수용 무성 3D 애니메이션 그림 콘티. SC06, WORKSHOP, 연속, 전원 전환.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC06_SH05_P01): CU. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 잎 그림자가 꺼진 눈등을 가로지른다..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
빈 슬롯: 2, 3, 4. 새 장면으로 채우지 않는다.
```

## SC07_GRID01

```text
검수용 무성 3D 애니메이션 그림 콘티. SC07, WORKSHOP, 몇 분 뒤, 같은 저녁.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC07_SH01_P01): CU. 피사체 앞 높은 사선 고정 인서트. 손·접촉 위치를 읽을 수 있게 한다. 포즈: 창 아래 물방울이 바닥에서 작은 길을 만든다..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC07_SH02_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 도크의 배터리와 램프, 정지한 핍을 한 화면에 둔다..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC07_SH03_P01): WS. 온실 통로 남쪽 고정. 진행은 화면 왼쪽→오른쪽. 포즈: 벽에 돌려놓은 판자와 어두운 통로..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC07_SH04_P01): WS. 작업실 남쪽에서 북쪽 창을 보는 고정 카메라. 창가 선반은 배경 중앙. 포즈: 열린 문 너머 작은 선반의 빛..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```

## SC07_GRID02

```text
검수용 무성 3D 애니메이션 그림 콘티. SC07, WORKSHOP, 몇 분 뒤, 같은 저녁.
2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.
공통 설정: 작은 청록색 로봇 핍: 바퀴 두 개, 짧은 집게 팔 두 개, 눈 역할의 흰 표시등 하나. 몸 왼쪽에 주황색 배터리 한 개. 배터리가 빠지면 구동·눈등은 즉시 멎고 집게는 무전원 열린 상태로 돌아간다. 움직임이 멎은 뒤의 낙하는 중력·스프링만 가능. 붉은 화분은 테두리 한 곳이 깨졌고 잎 두 장. 새 잎·개화는 생기지 않는다. 주 통로는 서→동, 작업실은 동쪽, 창가 선반은 작업실 북쪽. 폭풍의 회색빛. 작업등은 주황 배터리와 같은 규격의 수직 도크 하나. 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.
시간 분기: present. 이 분기의 인물·공간 버전만 사용한다.
그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.
슬롯 1 (SC07_SH05_P01): CU. 로봇 오른쪽 앞 사선 고정. 몸 왼쪽 배터리 위치는 세계 기준으로 유지. 포즈: 잎 그림자가 정지한 팔에 걸린다..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 2 (SC07_SH06_P01): WS. 창 안쪽에서 실내를 보는 역방향 카메라. 전환 전에 공간 관계를 다시 설정한다. 포즈: 창에서 본 핍·화분·램프의 실루엣..
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 3 (SC07_SH07_P01): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 머리에 닿은 잎.
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
슬롯 4 (SC07_SH07_P02): MS. 선반 동쪽에서 서쪽을 보는 고정 카메라. 램프 도크와 로봇 오른손을 함께 볼 수 있다. 포즈: 떨어진 잎과 정지한 핍.
이 순간의 상태: {"battery": "lamp_dock", "power": "off", "plant": "shelf", "lamp": "shelf_next_to_plant", "lamp_on": "yes", "door": "latched_open", "ramp": "wall_after_step", "cart": "chocked_shelf_front", "grip": "open"}.
유지/비공개 조건: 배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.
```
