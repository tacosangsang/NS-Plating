"""PLATING 문법·정책만 둔다. 문서 본문과 요금 값은 복사하지 않는다."""
from typing import Final

COLUMNS: Final = {
    "컷": "cut_id", "TC": "tc", "길이": "length", "샷 / 앵글": "shot_angle",
    "화면": "picture", "사운드": "sound", "대사": "dialogue", "대사 / 사운드": "dialogue_sound",
}
COLOR_STATES: Final = {"red_bg": "todo", "green_bg": "done", "gray_bg": "removed", "yellow_bg": "revise"}
SCENE_PATTERN: Final = r"^S#(\d{2})(\s|$)"
CUT_PATTERN: Final = r"^S#\d{2}-C\d{3}(-\d+[A-Z]?)?$"


def is_cut_table_header(header: tuple[str, ...], *, in_scene: bool) -> bool:
    """씬 안에서 첫 두 머리 칸이 컷·TC인 표만 선택한다."""
    return in_scene and header[:2] == ("컷", "TC")


DOC_FILES: Final = {
    "W04": "04_블록아웃_연출설계.md",
    "W02": "02_작업규칙과_의사결정.md", "W05": "05_영상_생성_워크플로우.md",
    "W06": "06_영상_edit_업스케일_변환.md", "W07": "07_도구_환경_제약.md",
    "W10": "10_고정_프롬프트_블록.md", "W11": "11_설정_고정값.md",
}
AUTHORED_SHA256: Final = {
    "W02": "2bc6c5d77cfbeddd62c9c22efdcb18a4d38f24091abe96b913d7790d6c8af8d6",
    "W05": "30129dded003070f57b209471cfe137fe0911ef805db0d3dabec20543a36d997",
    "W06": "96308bd869185e29acfb2d41922a570d6002137561f97cb9a407cfd2df259492",
    "W07": "4b3ae259f43f09a0afddefbd3fc321a4445ff3d291c044ead40ed9af15544d9f",
    "W10": "ba12aab620bb1ae7010ca973b6e4c131203591a0eb244635761ad4e168443b44",
    "W11": "5a918111676c1239a47bd5636895d70bb64c916628a6539fbcee5acbeb7b676c",
}
DOC_TITLES: Final = {
    "W02": "02. 작업 규칙과 의사결정", "W05": "05. 영상 생성 워크플로우 (Seedance 2.5, 레퍼런스 투 비디오)",
    "W06": "06. 영상 edit, 업스케일, 편집용 변환", "W07": "07. 도구·환경 제약",
    "W10": "10. 고정 프롬프트 블록 (원문)", "W11": "11. 설정 고정값 (프롬프트에 자주 필요한 것)",
}
ORDER_PREFIXES: Final = ("REFERENCE ROLES", "STYLE", "SUMMARY", "SPACE AND LIGHT", "TIMELINE", "(사람이 나오면)", "CONSISTENCY", "AVOID")
PEOPLE_BLOCKS: Final = ("FACE_EYES_HANDS", "EYES_CHILD", "FACE_REFLECTION", "IDENTICAL", "STAGING", "OUTFIT_CROWD", "OUTFIT_OFFERING", "BASE_OUTFIT", "COOK_APRON", "THIEF_APRON", "LAYOUT_TRUCK")
SCENE_BLOCKS: Final = ("SCENE_LOW", "SCENE_JINWOO", "SCENE_RABBIT", "SCENE_A", "SCENE_B", "SCENE_C", "SCENE_D", "SCENE_E", "SCENE_F", "SCENE_G", "SCENE_PLATING")
UPPER_SCENES: Final = ("SCENE_A", "SCENE_B", "SCENE_C", "SCENE_D", "SCENE_E", "SCENE_F", "SCENE_G")
BLOCK_SLOTS: Final = {"STYLE": 1, "AVOID": 7, "UPPER_AVOID": 7, "WORLD": 3,
                      **{key: 3 for key in SCENE_BLOCKS}, **{key: 5 for key in PEOPLE_BLOCKS},
                      "FACE_RULE": 5, "EYES": 5, "HANDS": 5, "LAYOUT_TRUCK": 3}
FORBID_NAMES: Final = ("진우", "최진우", "흰토끼", "흰토끼 가면남")
FORBID_GROUPS: Final = ("상류층", "흰토끼", "진우")
CHILD_GROUP: Final = "아이"
GROUP_BLOCKS: Final = {"OUTFIT_CROWD": {"하층민", "아이"}, "OUTFIT_OFFERING": {"공물"}, "BASE_OUTFIT": {"요리사", "도둑"}, "COOK_APRON": {"요리사"}, "THIEF_APRON": {"도둑"}, "HANDS": {"하층민", "아이", "요리사", "도둑"}}
FILE_EXCEPTION_KEYS: Final = ("W07", "W10", "W11")
ANCHOR_SPECS: Final = {
    "style": ("W10", ("2. STYLE (10-31판, 사용자 지시)",), "fences", 1),
    "world": ("W10", ("3. WORLD & TONE (이미지 공통)",), "fences", 1),
    "avoid": ("W10", ("4. AVOID (공통, 10-31)",), "fences", 2),
    "people": ("W10", ("5. 사람 블록 (하층민·요리사·도둑·공물. 진우·흰토끼·상류층 제외)",), "fences", len(PEOPLE_BLOCKS)),
    "scenes": ("W10", ("6. [SCENE] 모듈 (이미지)",), "fences", len(SCENE_BLOCKS)),
    "order": ("W05", ("2. 프롬프트 블록 구조", "섹션 순서"), "lines", 1),
    "image_limit": ("W05", ("2. 프롬프트 블록 구조", "글자 수"), "lines", 1),
    "checklist": ("W02", ("4. 크레딧 쓰기 전 점검 8줄",), "numbered", 8),
    "settings": ("W11", ("5. 최상층(연회장)",), "lines", 1),
    "cost": ("W07", ("1. 비용표 (Crons / 크레딧)",), "lines", 1),
    "edit_billing": ("W06", ("2. video_edit 특성 (AICRON 웹앱, 11-04 실사용)",), "lines", 1),
    "topaz": ("W06", ("4. 업스케일", "설정 (Higgsfield 웹앱 Topaz Video, 11-04 확정) `[예외: 사용 서비스]`"), "lines", 1),
    "approval": ("W02", ("2. 소통·결과물 규칙", "승인 어휘 (크레딧이 드는 일)"), "lines", 1),
    "clip_limits": ("W05", ("1. 씬 하나 워크플로우 (12단계)",), "lines", 1),
}
RATE_NEW_PATTERN: Final = r"^\| 영상 본 생성 \| (?P<model>.+?) (?P<low>\d+p) / (?P<high>\d+p) \| (?P<low_rate>\d+(?:\.\d+)?) / (?P<high_rate>\d+(?:\.\d+)?) per 초, 최소 (?P<minimum>\d+(?:\.\d+)?)초 \|$"
RATE_EDIT_PATTERN: Final = r"^\| 영상 edit \| (?P<model>.+?) video_edit (?P<resolution>\d+p) \| 입력 길이 초 올림 × (?P<rate>\d+(?:\.\d+)?)\([^|]+\) \|$"
APPROVAL_PATTERNS: Final = (r'^- "([^"]+)", "([^"]+)": 생성 승인\.$', r'^- "([^"]+)": 그 씬 한 바퀴 생성은 승인된 것')
