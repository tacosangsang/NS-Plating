# NS-PLATING

미디어아카데미 나뭇잎스콘팀, 3D 애니메이션 스타일 AI 하이브리드 영상 제작 프로젝트.
벌레식량 디스토피아 계급물 — 최하층/최상층 대비.

### 참여자 명단
(팀원)-**박서연**, 박한별, 정예서
(외부인원)- 문영길, 배민혁, 박상우, 김동현, 조석주



## 구조

```
NS-Plating/
├── prompts/                  # AI 이미지 생성 프롬프트
│   ├── base_prompt.md        #   최신본 (항상 여기 참조)
│   └── backups/              #   날짜별 스냅샷 base_prompt_MMDD.md
├── 00 resources/             # 리소스 파일 (미디어, 커밋 안 됨)
│   ├── 00 reference/         #   레퍼런스 (참고 자료, 스타일보드)
│   ├── 00 image/             #   이미지 (캐릭터 시트 등)
│   └── videos/               #   비디오
├── 01 docs/                  # 문서 (hwp·pdf 등 바이너리는 Drive)
│   ├── 운영측 전달 서류/       #   운영측 제출·수령 서류
│   │   ├── 양식·안내 서류/
│   │   └── 제출 서류/
│   ├── 리소스/                #   리소스 관련 문서
│   └── 기획/                  #   기획 문서
├── research/                 # 스토리보드 워크플로 리서치·테스트
└── workflow/                 # 작업 규칙·도구 함정·프롬프트 구조·검수 절차 정리 (재사용용)
```

## 워크플로우 정리 (다른 프로젝트 참고용)

`workflow/` 폴더에 핸드북(2026-11-06)과 프로젝트 메모리에서 뽑은 작업 규칙, 생성 함정, 프롬프트 블록 구조, 검수 절차, 실패 사례를 11개 문서로 정리했다. 프로젝트 고유 규칙은 `[예외: 이유]`로 표시했다. 시작은 [workflow/README.md](workflow/README.md).

## 미디어 관리 (팀 공유)

**미디어(이미지·비디오·바이너리)는 GitHub가 아닌 Google Drive에서 공유.**
GitHub는 프롬프트·문서(텍스트)만. 대용량 파일로 repo 무거워지는 것 방지.

- **Google Drive 공유 폴더:** https://drive.google.com/drive/folders/1Hf2_Uk_XoeJj5vSQxn_sWSumUwsXV5kR
- Drive 폴더 구조는 이 repo `00 resources/`와 동일하게 유지:
  `00 reference/`, `00 image/`, `videos/`
- 이미지·영상·pdf·hwp 등 바이너리는 `.gitignore` 처리 → 로컬 작업용, 커밋 안 됨.
- 각 폴더의 `.gitkeep`은 구조 표시용.

## 워크플로

**프롬프트 수정 시**
1. `prompts/base_prompt.md` 수정
2. `prompts/backups/base_prompt_MMDD.md`로 스냅샷 복사
3. commit + push

**문서 추가 시**
- `01 docs/` 해당 폴더에 넣고 commit + push (바이너리는 Drive)

**미디어 추가 시**
- Google Drive 공유 폴더의 해당 위치에 업로드 (GitHub 아님)
