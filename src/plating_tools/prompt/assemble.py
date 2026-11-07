"""고정 원문과 자리표시만 조립한다. 영어 액팅·길이 배분은 작성하지 않는다."""
from dataclasses import dataclass, replace
from decimal import Decimal

from ..errors import InputError
from ..model import Finding, Severity, Unknown, json_text
from ..profile_plating import BLOCK_SLOTS
from .check import LengthReport, count, length_report
from .plan import ClipPlan
from .rules import RuleBook
from .select import BlockDecision, select_blocks


@dataclass(frozen=True, slots=True)
class Slot:
    section: str
    kind: str
    text: str
    block_keys: tuple[str, ...]
    needs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Skeleton:
    scene_id: str
    clip: ClipPlan | Unknown
    order: tuple[str, ...]
    order_basis: dict
    slots: tuple[Slot, ...]
    decisions: tuple[BlockDecision, ...]
    length_table: tuple[dict, ...]
    checklist: tuple
    conflicts: tuple[Finding, ...]
    decided_by_tool: tuple[str, ...]
    needs_user: tuple[str, ...]
    lengths: LengthReport
    cuts_source: dict
    review_panel: tuple[dict, ...]
    prompt: str


def build_skeleton(cuts, plan: ClipPlan | None, rules: RuleBook) -> Skeleton:
    from dataclasses import asdict, is_dataclass
    data = asdict(cuts) if is_dataclass(cuts) else cuts
    if plan is not None and plan.kind != "video":
        raise InputError("이미지는 prompt check만 지원")
    for block in rules.catalog.values():
        if "{{" in block.text:
            raise InputError(f"정본 블록 자리표시 충돌: {block.key}")
    rows = data["targets"]
    ids = [r["cut_id"] for r in rows]
    if plan is not None:
        missing = set(plan.cuts) - {c for c in ids if isinstance(c, str)}
        if missing:
            raise InputError(f"계획 컷이 targets에 없음(문맥은 대상 아님): {missing}")
        rows = [r for r in rows if r["cut_id"] in plan.cuts]
    conflicts = list(rules.findings)
    if plan is not None and list(plan.cuts) != [r["cut_id"] for r in rows]:
        conflicts.append(Finding("PR_ORDER", Severity.WARN, "계획 컷 순서와 원문 순서 다름. 원문 순서 유지"))
    for row in rows:
        if row["row_state"] == "removed":
            conflicts.append(Finding("PR_REMOVED", Severity.ERROR, f"removed 컷 포함: {row['cut_id']}"))
        if row["row_state"] == "done":
            conflicts.append(Finding("PR_DONE", Severity.WARN, f"done 컷 포함: {row['cut_id']}"))
    decisions = select_blocks(plan, rules)
    chosen = [d.block_key for d in decisions if d.decision == "포함"]
    if "SCENE_D" in chosen:
        conflicts.extend(rules.scene_conflicts)
        chosen.remove("SCENE_D")
    slots = []
    for i, section in enumerate(rules.order):
        keys = tuple(k for k in chosen if BLOCK_SLOTS.get(k) == i)
        needs = []
        parts = [rules.catalog[k].text for k in keys]
        if i not in {1, 7}:
            if i == 4:
                needs = [f"{row['cut_id']}: 컷표 문장, Camera, Sound, Subtext, End state, 마지막 상태" for row in rows]
            else:
                needs = [section]
            parts += [f"{{{{미결: {need}}}}}" for need in needs]
        slots.append(Slot(section, "fixed" if not needs else "placeholder", "\n\n".join(parts), keys, tuple(needs)))
    prompt = "\n\n".join(slot.text for slot in slots)
    length_rows = []
    for row in rows:
        seconds = row["length"]["seconds"]
        parsed = Decimal(str(seconds)) if not isinstance(seconds, dict) else Unknown("컷표 길이 미확인")
        generated = plan.gen_seconds if plan is not None and len(rows) == 1 else Unknown("개별 생성 길이 미입력")
        slack = generated - parsed if isinstance(generated, Decimal) and isinstance(parsed, Decimal) else Unknown("생성 길이/컷표 길이 미확인")
        length_rows.append({"cut_id": row["cut_id"], "segment": plan.segment if plan else Unknown("구간 미입력"), "gen_seconds": generated,
                            "cut_length": row["length"], "slack": slack, "slack_basis": "도구 계산: 생성 길이 − 컷표 길이"})
    lengths = length_report(prompt, "video", rules)
    lengths = replace(lengths, per_block={k: count(rules.catalog[k].text) for k in chosen}, per_section={s.section: count(s.text) for s in slots})
    return Skeleton(data["scene_id"], plan or Unknown("계획 미입력"), rules.order, {"where": rules.order_basis}, tuple(slots), tuple(decisions),
                    tuple(length_rows), rules.checklist, tuple(conflicts), ("원문 순서 유지", "고정 블록 원문 삽입", "균등 배분 없음"),
                    tuple(need for slot in slots for need in slot.needs), lengths, data["source"], tuple(rows), prompt)


def gate_template() -> str:
    return "\n".join(f'[[item]]\nno = {i}\nanswer = ""\nreason = ""\nalternative = ""\nevidence = []\nreviewer = ""\n' for i in range(1, 9)) + '\n[approval]\nquote = ""\nwhere = ""\nby = ""\nat = ""\nprompt_sha256 = ""\n'


def skeleton_md(skeleton: Skeleton) -> str:
    checklist = "\n".join(line.text + "\n   응답: 미입력" for line in skeleton.checklist)
    return (f"# [검수 대기] {skeleton.scene_id} 프롬프트 골격 (전송본 아님)\n\n{checklist}\n\n"
            f"```text\n{skeleton.prompt}\n```\n\n## 길이 표\n```json\n{json_text(skeleton.length_table)}```\n\n"
            f"## 컷표 원문 검수 패널\n```json\n{json_text(skeleton.review_panel)}```\n\n## 글자 수\n```json\n{json_text(skeleton.lengths)}```\n\n"
            f"## 블록 선택 결정\n```json\n{json_text(skeleton.decisions)}```\n\n## 소견\n```json\n{json_text(skeleton.conflicts)}```\n\n"
            "## 내가 정한 것\n" + "\n".join(skeleton.decided_by_tool) + "\n\n## 사용자 답이 필요한 것\n" + "\n".join(skeleton.needs_user)
            + "\n\n## 근거\n" + json_text(skeleton.order_basis) + "\n")
