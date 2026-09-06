# NS-PLATING

미디어아카데미 나뭇잎스콘팀, 3D 애니메이션 스타일 AI 하이브리드 영상 제작 프로젝트.
벌레식량 디스토피아 계급물 — 벌레만 식량으로 남은 세계, 최하층/최상층 대비.

### 참여자 명단
(팀원)-**박서연**, 박한별, 정예서
(외부인원)- 문영길, 배민혁, 박상우, 김동현, 조석주



## 구조

```
NS-Plating/
├── prompts/                  # AI 이미지 생성 프롬프트
│   ├── base_prompt.md        #   최신본 (항상 여기 참조)
│   └── backups/              #   날짜별 스냅샷 base_prompt_MMDD.md
├── resources/                # 리소스 파일 (미디어)
│   ├── references/           #   레퍼런스 (참고 자료, 스타일보드)
│   ├── images/               #   이미지 (character/ 등)
│   └── videos/               #   비디오
└── docs/                     # 문서
    ├── 운영측 전달 서류/       #   운영측 제출·수령 서류
    │   ├── 양식·안내 서류/
    │   └── 제출 서류/
    ├── 리소스/                #   리소스 관련 문서
    └── 기획/                  #   기획 문서
```

## 미디어 관리 (팀 공유)

**미디어(이미지·비디오·바이너리)는 GitHub가 아닌 Google Drive에서 공유.**
GitHub는 프롬프트·문서(텍스트)만. 대용량 파일로 repo 무거워지는 것 방지.

- **Google Drive 공유 폴더:** https://drive.google.com/drive/folders/1Hf2_Uk_XoeJj5vSQxn_sWSumUwsXV5kR
- Drive 폴더 구조는 이 repo `resources/`와 동일하게 유지:
  `references/`, `images/` (하위 `character/` 등), `videos/`
- repo의 `resources/**` 미디어는 `.gitignore` 처리 → 로컬 작업용, 커밋 안 됨.
- 각 폴더의 `.gitkeep`은 구조 표시용.

## 워크플로

**프롬프트 수정 시**
1. `prompts/base_prompt.md` 수정
2. `prompts/backups/base_prompt_MMDD.md`로 스냅샷 복사
3. commit + push

**문서 추가 시**
- `docs/` 해당 폴더에 넣고 commit + push

**미디어 추가 시**
- Google Drive 공유 폴더의 해당 위치에 업로드 (GitHub 아님)
