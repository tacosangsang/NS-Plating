"""검증된 pin의 적용 범위와 계열별 최신 판을 비교한다."""
from ..docs import DocStore
from ..errors import InputError
from ..model import Unknown
from .model import FamilySpec, FamilyState, Pin, RenderCheck, RenderSpec, Verdict, VersionTag
from .scan import order_unknown, parse_version, readme_version, version_key


def validate_pins(pins: tuple[Pin, ...], store: DocStore) -> None:
    seen = set()
    for pin in pins:
        if not pin.basis_contains.strip() or not pin.basis_doc or pin.basis_line < 1 or not pin.scope or pin.approved_by != "ts" or isinstance(parse_version(pin.version, prefix=False), Unknown):
            raise InputError("pin: 근거·범위·유효한 판·승인자 ts 필요")
        document = store.load(pin.basis_doc)
        if pin.basis_line > len(document.lines) or pin.basis_contains not in document.lines[pin.basis_line - 1]:
            raise InputError(f"pin 근거 행 불일치: {pin.basis_doc}:{pin.basis_line}")
        for scene in pin.scope:
            if (pin.family, scene) in seen:
                raise InputError(f"중복 pin 범위: {pin.family}/{scene}")
            seen.add((pin.family, scene))


def check_render(render: RenderSpec, family: FamilySpec | None, state: FamilyState | None, pins: tuple[Pin, ...] = ()) -> RenderCheck:
    version = parse_version(render.path.name)
    if family is None or state is None:
        return RenderCheck(str(render.path), render.scene, version, render.version_from, Verdict.FAMILY_UNKNOWN)
    if render.version_from == "README":
        candidates = [p for p in render.path.parent.glob(family.readme_glob.removeprefix("**/")) if p.is_file()]
        versions = [readme_version(p, family) for p in candidates]
        known = {v.raw: v for v in versions if isinstance(v, VersionTag)}
        version = next(iter(known.values())) if len(known) == 1 else Unknown("README 기준 판 없음 또는 충돌")
    verdict = Verdict.NO_VERSION
    compared = None
    difference = None
    pin = next((p for p in pins if p.family == family.name and render.scene in p.scope), None)
    if isinstance(version, VersionTag):
        if pin:
            compared = pin.version
            verdict = Verdict.PINNED if version.raw == pin.version else Verdict.PIN_MISMATCH
        elif state.order_unknown or order_unknown((version, *((state.latest,) if isinstance(state.latest, VersionTag) else ())), family):
            verdict = Verdict.ORDER_UNKNOWN
        elif isinstance(state.latest, Unknown):
            verdict = Verdict.CONFLICT if state.latest.unknown == "출처 충돌" else Verdict.NO_VERSION
        else:
            compared = state.latest.raw
            difference = state.latest.number - version.number
            if version.raw == state.latest.raw:
                verdict = Verdict.LATEST
            else:
                verdict = Verdict.STALE if version_key(version, family) < version_key(state.latest, family) else Verdict.CONFLICT
    return RenderCheck(str(render.path), render.scene, version, render.version_from, verdict, compared, difference)
