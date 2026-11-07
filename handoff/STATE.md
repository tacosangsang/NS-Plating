# STATE (2026-11-07)

다음 행동: 수정 커밋의 compare·tiles를 Windows C: 임시 폴더에서 재검증한다.
현재 단계: B. probe·convert·compare·tiles 초안. Linux 합성 테스트 15건 통과.
PR: https://github.com/tacosangsang/plating-qc-workflows/pull/1 (초안). main 병합 전.
Windows 기존 테스트: 커밋 677da27의 기본 12건 통과, 추가 14건 중 12건 통과. 잘못된 raw 설정, % 경로 이탈, 인코더 실패 시 부분 파일 잔류를 수정했으나 수정 후 Windows 재검증 대기. 실제 D: 저장·동기화 드라이브·편집기 재생도 미검증.
후속: split, Blender 폴백, PTS 기반 VFR 및 차이 이미지 미구현. 설계 차이는 design/review.md 참조.
Claude API: 호출하지 않음. 비용·인증 설정 변경 없음.
