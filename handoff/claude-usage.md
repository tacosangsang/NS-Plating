# Claude API 사용 기록

호출 전후 Console 잔액과 누적 비용은 사용자가 확인한 값으로 기록한다. 잔액이 US$5 이하면 호출하지 않는다.


호출 전 2026-11-07 15:36:08 +0900: handoff\claude-test-request.md, Console 잔액 $100, 누적 비용 미확인.

호출 후 2026-11-07 15:36:11 +0900: 모델 claude-opus-5-5, 입력 108 토큰, 출력 62 토큰, 결과 `handoff\claude-test-result.md`, Console 잔액 $99.99(사용자 화면 확인). 표시 잔액 기준 $0.01 감소, 정확한 누적 비용은 화면에 표시되지 않아 미확인.
