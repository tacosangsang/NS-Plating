"""프로필 조건과 사람이 입력한 메타데이터로만 블록을 선택한다."""
from dataclasses import dataclass

from ..model import SourceRef, Unknown
from ..profile_plating import FORBID_GROUPS, FORBID_NAMES, CHILD_GROUP, GROUP_BLOCKS, UPPER_SCENES
from .plan import ClipPlan
from .rules import RuleBook


@dataclass(frozen=True, slots=True)
class BlockDecision:
    block_key: str
    decision: str
    reason: str
    inputs: dict[str, str]
    basis: SourceRef


def select_blocks(clip: ClipPlan | None, rules: RuleBook) -> list[BlockDecision]:
    result = []
    for key, block in rules.catalog.items():
        decision, reason = "미결", "사람 메타데이터 미입력"
        if key in {"STYLE", "AVOID"}:
            decision, reason = "포함", "공통 고정 블록"
        elif key == "WORLD":
            decision, reason = ("포함", "이미지 공통") if clip is not None and clip.kind == "image" else ("제외", "영상 골격")
        elif key == "UPPER_AVOID" and clip is not None and clip.scene_module in UPPER_SCENES:
            decision, reason = "포함", "최상층 전용 금지"
        elif key == "UPPER_AVOID" or key.startswith("SCENE_") or key == "LAYOUT_TRUCK":
            if clip is not None and not isinstance(clip.scene_module, Unknown):
                decision, reason = ("포함", "사람이 지정한 모듈") if clip.scene_module == key else ("제외", "지정한 모듈 아님")
        elif clip is not None and clip.people == "없음":
            decision, reason = "제외", "사람 없음"
        elif clip is not None and clip.people == "있음" and clip.characters:
            eligible = [c for c in clip.characters if c.name not in FORBID_NAMES and c.group not in FORBID_GROUPS]
            groups = {c.group for c in eligible if isinstance(c.group, str)}
            if not eligible:
                decision, reason = "제외", "하층민 블록 제외 대상"
            elif any(isinstance(c.group, Unknown) for c in eligible):
                decision, reason = "미결", "인물 분류 미입력"
            elif key in {"FACE_RULE", "EYES", "EYES_CHILD", "FACE_REFLECTION"}:
                near = [c for c in eligible if c.face == "close"]
                if all(c.face in {"far", "none"} for c in eligible):
                    decision, reason = "제외", "얼굴 안 보임/먼 컷"
                elif near:
                    if key == "EYES_CHILD":
                        decision = "포함" if CHILD_GROUP in {c.group for c in near} else "제외"
                    elif key == "EYES":
                        decision = "포함" if any(c.group != CHILD_GROUP for c in near) else "제외"
                    elif key == "FACE_REFLECTION":
                        decision = "포함" if clip.staging.get("face_reflection") is True else "미결"
                    else:
                        decision = "포함"
                    reason = "얼굴 거리·아이 여부에 따른 선택"
            elif key == "STAGING":
                if clip.staging.get("seated") is True or clip.staging.get("procession") is True:
                    decision, reason = "제외", "착석/행렬 배치는 사람이 직접 작성"
                elif clip.staging.get("seated") is False and clip.staging.get("procession") is False:
                    decision, reason = "포함", "서 있는 비행렬 배치"
            elif key == "IDENTICAL":
                decision, reason = ("포함", "군중 둘 이상") if len(eligible) > 1 or clip.staging.get("crowd") is True else ("미결", "군중 수 미입력")
            else:
                wanted = GROUP_BLOCKS
                if key in wanted:
                    decision, reason = ("포함", "사람이 적은 인물 분류") if groups & wanted[key] else ("제외", "해당 인물 분류 아님")
        result.append(BlockDecision(key, decision, reason, {"people": str(clip.people) if clip else "미입력"}, block.where))
    return result
