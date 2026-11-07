# STATE (2026-11-07)

다음 행동: 시작 시각 경고와 scene 후보 변경을 Windows C: 임시 폴더에서 합성 영상으로 재검증한다.
현재 단계: B. probe·convert·compare·tiles·split 초안. Linux 합성 테스트 36건 통과.
PR: https://github.com/tacosangsang/plating-qc-workflows/pull/1 (초안). main 병합 전.
Windows: 커밋 cfc06f5은 C: 기본 32/32 및 독립 검사 14/14 통과. 이후 장면 후보·시작 시각 경고 변경은 미검증. 실제 genpts 성공·실제 영상·D:·동기화·오디오 동기화·편집기 재생 미검증.
후속: Blender 폴백, 명령·샘플 로그, 설계 검수 등. 자세한 한계는 design/review.md 참조.
Claude API: 호출하지 않음. 비용·인증 설정 변경 없음.
