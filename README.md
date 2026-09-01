# NS-PLATING

미디어아카데미 나뭇잎스콘팀, 3D 애니메이션 스타일 AI 하이브리드 영상 제작 프로젝트.
벌레식량 디스토피아 계급물 — 벌레만 식량으로 남은 세계, 최하층/최상층 대비.

### 참여자 명단
(팀원)-** 박서연**, 박한별, 정예서
(외부인원)- 문영길, 배민혁, 박상우, 김동현, 조석주



## 구조

```
plating/
├── prompts/                  # AI 이미지 생성 프롬프트
│   ├── base_prompt.md        #   최신본 (항상 여기 참조)
│   └── backups/              #   날짜별 스냅샷 base_prompt_MMDD.md
├── resources/                # 리소스 파일
│   ├── references/           #   레퍼런스 (참고 자료)
│   ├── images/               #   이미지
│   └── videos/               #   비디오
└── docs/                     # 기획·문서
```

## 워크플로

**프롬프트 수정 시**
1. `prompts/base_prompt.md` 수정
2. `prompts/backups/base_prompt_MMDD.md`로 스냅샷 복사
3. commit + push

**리소스/문서 추가 시**
- 해당 폴더에 파일 넣고 commit + push
