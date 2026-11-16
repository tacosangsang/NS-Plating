"""프레임 정렬과 밝기 정규화 비교."""
import math
from pathlib import Path

from .core import QCError, probe


def frames(path, config, width, height, count):
    from .backend import make_backend

    return make_backend(config).extract_frames(Path(path), width, height, count)


def distance(a, b):
    return sum(abs(x-y) for x, y in zip(a, b)) / (255 * len(a))


def normalized_distance(a, b):
    mean_a, mean_b = sum(a) / len(a), sum(b) / len(b)
    std_a = math.sqrt(sum((x - mean_a) ** 2 for x in a) / len(a))
    std_b = math.sqrt(sum((x - mean_b) ** 2 for x in b) / len(b))
    if not std_a or not std_b:
        return distance(a, b)
    return sum(abs((x - mean_a) / std_a - (y - mean_b) / std_b)
               for x, y in zip(a, b)) / (6 * len(a))


def mixed_frame_hint(previous, current, candidate):
    """두 원본 프레임의 혼합에 가까운지만 검사한다. 최종 판정이 아니다."""
    separation = distance(previous, current)
    if separation < .12:
        return None
    endpoint_error = min(distance(previous, candidate), distance(current, candidate))
    if endpoint_error < .05:
        return None
    alternatives = []
    for numerator in (1, 2, 3):
        error = sum(abs((numerator*x + (4-numerator)*y)/4 - z) for x, y, z in zip(previous, current, candidate)) / (255 * len(previous))
        alternatives.append((error, numerator / 4))
    error, weight = min(alternatives)
    if error <= .04 and endpoint_error - error >= .04:
        return {"previous_weight": weight, "mixed_error": error, "nearest_source_error": endpoint_error}
    return None


def compare(original, candidate, config, search=30, threshold=.02):
    if not 0 <= search <= 300 or not 0 <= threshold <= 1:
        raise QCError(2, "search는 0~300, threshold는 0~1이어야 합니다")
    a, b = probe(original, config), probe(candidate, config)
    na, nb = a.video.nb_frames_decoded, b.video.nb_frames_decoded
    if na < 1 or nb < 1:
        raise QCError(5, "비교할 프레임이 없습니다")
    af = frames(a.path, config, 64, 36, na)
    bf = frames(b.path, config, 64, 36, nb)
    # 전체 겹치는 구간에서 최대 12개의 표본을 비교한다. 반복 장면은 애매함으로 처리한다.
    scores = []
    for offset in range(-min(search, nb-1), min(search, na-1)+1):
        start, end = max(0, -offset), min(nb, na-offset)
        overlap = end - start
        if overlap < min(5, na, nb):
            continue
        positions = sorted({start + (overlap-1)*i//11 for i in range(12)})
        score = sum(normalized_distance(af[i+offset], bf[i]) for i in positions)/len(positions)
        scores.append((score, offset))
    if not scores:
        raise QCError(5, "정렬할 겹치는 프레임이 부족합니다")
    scores.sort()
    best, offset = scores[0]
    second = scores[1][0] if len(scores)>1 else None
    ambiguous = best > .15 or (second is not None and second-best < .002)
    warnings = list(a.warnings) + list(b.warnings)
    if a.video.avg_frame_rate != b.video.avg_frame_rate:
        warnings.append("프레임 속도가 다릅니다. 프레임 정렬 결과를 신뢰할 수 없습니다")
        ambiguous = True
    if any(x.timestamp_analysis.status != "observed" or x.timestamp_analysis.vfr_suspect is not False for x in (a, b)):
        warnings.append("PTS가 없거나 가변 속도가 의심되어 프레임 번호 기반 정렬을 확정할 수 없습니다")
        ambiguous = True
    if ambiguous:
        warnings.append("다른 소스이거나 반복 장면 등으로 정렬이 불확실합니다. 누락을 확정하지 않습니다")
    start, end = max(0, -offset), min(nb, na-offset)
    ranges = []
    changed = []
    current = None
    for i in range(start, end):
        if normalized_distance(af[i+offset], bf[i]) > threshold:
            changed.append(i)
            if current is None:
                current = [i, i]
            else:
                current[1] = i
        elif current is not None:
            ranges.append(current)
            current = None
    if current is not None:
        ranges.append(current)
    mix_suspects = []
    if not ambiguous:
        for i in changed[:1000]:
            j = i + offset
            for left, right in ((j-1, j), (j, j+1)):
                if left < 0 or right >= na:
                    continue
                hint = mixed_frame_hint(af[left], af[right], bf[i])
                if hint:
                    mix_suspects.append({"candidate_frame": i, "source_frames": [left, right], **hint})
                    break
    if len(changed) > 1000 and not ambiguous:
        warnings.append("차이 프레임이 1000개를 넘어 혼합 의심 검사는 앞 1000개만 수행했습니다")
    if mix_suspects:
        warnings.append("인접한 두 원본 프레임의 혼합과 유사한 프레임이 있습니다. 원본 해상도로 직접 확인하세요")
    if na != nb:
        warnings.append("디코딩 프레임 수가 다릅니다")
    if not ambiguous and offset != 0:
        warnings.append("정렬 후보가 0프레임이 아닙니다. 앞뒤 구간을 확인하세요")
    if ranges:
        warnings.append("정렬 후보에서 차이가 큰 구간이 있습니다. 원본 해상도로 검수하세요")
    return {"original": a, "candidate": b, "alignment": {"offset_candidate_to_original": None if ambiguous else offset, "score": best, "second_score": second, "uncertain": ambiguous, "estimated_missing_head": None if ambiguous else max(0, offset), "estimated_missing_tail": None if ambiguous else max(0, na - (offset + nb))}, "difference_ranges_candidate_frames": [] if ambiguous else ranges, "mixed_frame_suspects": mix_suspects, "threshold": threshold, "warnings": warnings, "notice": "축소 회색 프레임 기반의 검수 힌트입니다. 손상·누락·혼합 프레임의 확정 판정이 아닙니다."}
