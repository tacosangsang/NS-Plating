# STATE (2026-11-07)

다음 행동: split 변경을 Windows C: 임시 폴더에서 합성 영상으로 재검증한다.
현재 단계: B. probe·convert·compare·tiles·split 초안. Linux 합성 테스트 18건 통과.
PR: https://github.com/tacosangsang/plating-qc-workflows/pull/1 (초안). main 병합 전.
Windows 검증: 커밋 1f5bc63은 C: 임시 폴더에서 기본 15/15 및 독립 재현 3/3 통과. 이후 split 변경은 Windows 미검증. 실제 D: 저장·동기화 드라이브·오디오 경계·편집기 재생 미검증.
후속: Blender 폴백, PTS 기반 VFR 및 차이 이미지 등 미구현. 설계 차이는 design/review.md 참조.
Claude API: 호출하지 않음. 비용·인증 설정 변경 없음.
