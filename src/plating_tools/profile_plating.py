"""PLATING 문법·정책만 둔다. 문서 본문과 요금 값은 복사하지 않는다."""
from typing import Final

COLUMNS: Final = {
    "컷": "cut_id", "TC": "tc", "길이": "length", "샷 / 앵글": "shot_angle",
    "화면": "picture", "사운드": "sound", "대사": "dialogue", "대사 / 사운드": "dialogue_sound",
}
COLOR_STATES: Final = {"red_bg": "todo", "green_bg": "done", "gray_bg": "removed", "yellow_bg": "revise"}
SCENE_PATTERN: Final = r"^S#(\d{2})(\s|$)"
CUT_PATTERN: Final = r"^S#\d{2}-C\d{3}(-\d+[A-Z]?)?$"
