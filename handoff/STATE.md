# STATE (2026-11-07)

다음 행동: PR #1의 probe·convert 설계를 검수하고 Windows 별도 테스트 폴더에서 FFmpeg와 하드링크 저장을 확인한다.
현재 단계: B. probe와 convert 1차 구현, 합성 영상 테스트 5건 통과.
PR: https://github.com/tacosangsang/plating-qc-workflows/pull/1 (초안). main 병합 전.
모델·사용 한도: 실제 선택 목록 및 잔여량 미확인.
막힘·후속: Windows 실행·동기화 드라이브 하드링크 미검증. compare, tiles, split, Blender 폴백 및 PTS 기반 VFR 검사는 미구현. 설계 차이는 design/review.md 참조.
Claude API: 호출하지 않음. 비용·인증 설정 변경 없음.
