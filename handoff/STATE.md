# STATE (2026-11-07)

다음 행동: 오디오 경계 경고 변경을 Windows C: 임시 폴더에서 재검증한다.
현재 단계: B. probe·convert·compare·tiles·split 초안. Linux 합성 테스트 19건 통과.
PR: https://github.com/tacosangsang/plating-qc-workflows/pull/1 (초안). main 병합 전.
Windows: 커밋 9b01ddd의 split 합성 테스트 기본 18/18·추가 11/11 통과. PCM 샘플은 보존됐으나 각 조각 오디오 시작·길이가 영상 경계와 달랐고 이음새는 미검증. 이후 경고 변경은 Windows 미검증. D: 실제 저장·동기화 드라이브·편집기 재생 미검증.
후속: Blender 폴백, PTS 기반 VFR, 비교 차이 이미지 등 미구현. 설계 차이는 design/review.md 참조.
Claude API: 호출하지 않음. 비용·인증 설정 변경 없음.
