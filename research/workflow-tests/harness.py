"""Authored screenplay/storyboard fixtures and deterministic checks; no model calls."""
import copy
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def shot(src, seconds, size, camera, action, purpose, audio="환경음", poses=None, **extra):
    return dict(source_index=src, duration_sec=seconds, size=size, camera_id=camera,
                action=action, purpose=purpose, audio=audio,
                poses=poses or [action], **extra)

def scene(sid, location, time, sources, shots, branch="present", **extra):
    return dict(id=sid, location_id=location, story_time=time, branch=branch,
                sources=sources, shots=shots, **extra)

def materialize(case):
    case = copy.deepcopy(case)
    states = copy.deepcopy(case["initial_states"])
    known = set()
    case["shots"] = []
    cursor = 0
    for sc in case["scenes"]:
        sc["source_ids"] = [f'{sc["id"]}_SRC{i+1:02}' for i in range(len(sc["sources"]))]
        for i, sh in enumerate(sc.pop("shots")):
            sh["id"] = f'{sc["id"]}_SH{i+1:02}'
            sh["scene_id"] = sc["id"]
            sh["location_id"] = sc["location_id"]
            sh["branch"] = sc["branch"]
            sh["source_refs"] = [sc["source_ids"][sh.pop("source_index") - 1]]
            sh["beat_id"] = sh["source_refs"][0].replace("SRC", "BEAT")
            sh["edit_order"] = len(case["shots"]) + 1
            sh["timeline_in"] = cursor
            cursor += sh["duration_sec"]
            sh["timeline_out"] = cursor
            sh["state_in"] = copy.deepcopy(states[sc["branch"]])
            states[sc["branch"]].update(sh.get("changes", {}))
            sh["state_out"] = copy.deepcopy(states[sc["branch"]])
            sh["audience_before"] = sorted(known)
            known.update(sh.get("reveals", []))
            sh["audience_after"] = sorted(known)
            poses = sh.pop("poses")
            sh["panels"] = [dict(id=f'{sh["id"]}_P{j+1:02}', pose=pose,
                                 at_sec=round(j * sh["duration_sec"] / len(poses), 3))
                            for j, pose in enumerate(poses)]
            case["shots"].append(sh)
    for i, sh in enumerate(case["shots"]):
        sh["next_shot"] = case["shots"][i+1]["id"] if i+1 < len(case["shots"]) else None
        if "cut_reason" not in sh:
            sh["cut_reason"] = ("다음 정보로 전환: " + case["shots"][i+1]["purpose"]
                                if sh["next_shot"] else "행동의 결과를 읽은 뒤 크레딧")
    case["runtime_sec"] = cursor
    case["total_sec"] = cursor + case["credits_sec"]
    return case

def reflow(case):
    """Recompute timing, states and audience history after a tracked edit."""
    states = copy.deepcopy(case["initial_states"])
    known = set()
    cursor = 0
    for i, sh in enumerate(case["shots"]):
        sh["edit_order"] = i + 1
        sh["timeline_in"] = cursor
        cursor += sh["duration_sec"]
        sh["timeline_out"] = cursor
        sh["state_in"] = copy.deepcopy(states[sh["branch"]])
        states[sh["branch"]].update(sh.get("changes", {}))
        sh["state_out"] = copy.deepcopy(states[sh["branch"]])
        sh["audience_before"] = sorted(known)
        known.update(sh.get("reveals", []))
        sh["audience_after"] = sorted(known)
        sh["next_shot"] = case["shots"][i+1]["id"] if i+1<len(case["shots"]) else None
    case["runtime_sec"] = cursor
    case["total_sec"] = cursor + case["credits_sec"]

def grids(case):
    pages = []
    for sc in case["scenes"]:
        groups = {}
        for sh in case['shots']:
            if sh['scene_id'] != sc['id']: continue
            key = (sh['location_id'], sh['branch'], sh.get('costume_version','default'))
            groups.setdefault(key, [])
            groups[key].extend(dict(**p,shot_id=sh['id'],camera_id=sh['camera_id'],size=sh['size']) for p in sh['panels'])
        page_n=0
        for (location,branch,costume),panels in groups.items():
            for start in range(0,len(panels),4):
                page_n+=1
                slots=panels[start:start+4]
                pages.append(dict(id=f'{sc["id"]}_GRID{page_n:02}',scene_id=sc['id'],
                    location_id=location,branch=branch,costume_version=costume,story_time=sc['story_time'],
                    rows=2,columns=2,slots=slots,empty_slots=list(range(len(slots)+1,5))))
    return pages

def validate(case, pages=None):
    errors = []
    checks = 0
    def check(ok, code, target, detail):
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(dict(code=code, target=target, detail=detail))
    ids = [s["id"] for s in case["shots"]]
    check(len(ids)==len(set(ids)), "DUPLICATE_SHOT", "project", "샷 ID 중복")
    srcs = {sid for sc in case["scenes"] for sid in sc["source_ids"]}
    covered = set()
    state = copy.deepcopy(case["initial_states"])
    known = set()
    cursor = 0
    all_panels = []
    scene_map = {sc["id"]:sc for sc in case["scenes"]}
    for i, sh in enumerate(case["shots"]):
        sid = sh["id"]
        check(sh["duration_sec"]>0, "INVALID_DURATION", sid, "길이는 양수")
        check(sh["timeline_in"]==cursor, "TIMELINE_GAP", sid, "하드컷 시간축 불연속")
        cursor += sh["duration_sec"]
        check(sh["timeline_out"]==cursor, "TIMELINE_END", sid, "종료 시간 불일치")
        check(sh["edit_order"]==i+1, "EDIT_ORDER", sid, "편집 순서 오류")
        check(sh["source_refs"] and set(sh["source_refs"])<=srcs, "SOURCE_MISSING", sid, "없는 원문 참조")
        covered.update(sh["source_refs"])
        check(sh["camera_id"] in case["cameras"], "CAMERA_MISSING", sid, "없는 카메라 설정")
        if case.get('camera_locations',{}).get(sh['camera_id']):
            check(sh['location_id'] in case['camera_locations'][sh['camera_id']], 'CAMERA_LOCATION',sid,'카메라 위치와 샷 장소 불일치')
        check(sh["state_in"]==state[sh["branch"]], "STATE_JUMP", sid, "해당 시간 분기의 이전 상태와 불일치")
        for key, value in sh.get("requires_state", {}).items():
            check(sh["state_in"].get(key)==value, "STATE_PRECONDITION", sid, f'{key} 필요값 {value}')
        state[sh["branch"]].update(sh.get("changes", {}))
        check(sh["state_out"]==state[sh["branch"]], "STATE_DELTA", sid, "기록된 변화와 종료 상태 불일치")
        check(set(sh.get("requires_known", []))<=known, "REVEAL_ORDER", sid, "앞에서 공개하지 않은 정보에 의존")
        known.update(sh.get("reveals", []))
        for asset in scene_map[sh["scene_id"]].get("asset_ids", case["assets"].keys()):
            check(asset in case["assets"], "ASSET_MISSING", sid, "없는 에셋")
        for p in sh["panels"]:
            all_panels.append(p["id"])
            check(0<=p["at_sec"]<sh["duration_sec"], "PANEL_TIME", p["id"], "샷 밖의 패널 시점")
            for aid in p.get('visible_assets',sh.get('visible_assets',[])):
                check(aid in case['assets'],'PANEL_ASSET',p['id'],'패널에 없는 에셋 참조')
        check(bool(sh["purpose"] and sh["cut_reason"]), "SHOT_PURPOSE", sid, "샷 기능·컷 동기 필요")
        if sh.get('powered_motion'):
            check(sh['state_in'].get('power')=='on' or sh.get('power_restored_within_shot'),'UNPOWERED_ACTION',sid,'무전원에서 능동 동작')
        for cue in sh.get('timed_cues',[]):
            check(0<=cue['at_sec']<sh['duration_sec'],'CUE_TIME',sid,'샷 밖의 음향/빛 큐')
            if 'on_duration_sec' in cue:
                check(cue['on_duration_sec']>0 and cue['at_sec']+cue['on_duration_sec']<=sh['duration_sec'],'CUE_DURATION',sid,'빛이 켜져 있는 구간이 샷을 벗어남')
    check(covered==srcs, "SOURCE_COVERAGE", "project", f'미참조 원문 {sorted(srcs-covered)}')
    check(len(all_panels)==len(set(all_panels)), "DUPLICATE_PANEL", "project", "패널 ID 중복")
    check(case["runtime_sec"]==cursor, "RUNTIME_SUM", "project", "본편 합계 불일치")
    check(case["total_sec"]==cursor+case["credits_sec"], "TOTAL_SUM", "project", "크레딧 합계 불일치")
    check(case["runtime_min"]<=case["total_sec"]<=case["runtime_max"], "RUNTIME_RANGE", "project", "목표 허용 범위 초과")
    pages = pages if pages is not None else grids(case)
    planned = []
    panel_map = {p["id"]:sh for sh in case["shots"] for p in sh["panels"]}
    for pg in pages:
        check(len(pg["slots"])+len(pg["empty_slots"])==4, "GRID_COUNT", pg["id"], "슬롯 수 불일치")
        for p in pg["slots"]:
            planned.append(p["id"])
            check(p["id"] in panel_map, "GRID_UNKNOWN_PANEL", pg["id"], "없는 패널")
            if p["id"] in panel_map:
                check(panel_map[p["id"]]["scene_id"]==pg["scene_id"], "GRID_SCENE", pg["id"], "다른 씬 혼입")
                check(panel_map[p['id']]['location_id']==pg['location_id'],'GRID_LOCATION',pg['id'],'같은 원문 씬 안의 다른 장소 혼입')
                if 'branch' in pg:
                    check(panel_map[p['id']]['branch']==pg['branch'],'GRID_BRANCH',pg['id'],'과거·현재 혼입')
    check(sorted(planned)==sorted(all_panels), "GRID_COVERAGE", "project", "패널 누락·중복")
    for ev in case.get('signal_events',[]):
        observed=[]
        times=[]
        for sh in case['shots']:
            for cue in sh.get('timed_cues',[]):
                if cue.get('event_id')==ev['id'] and cue.get('visible'):
                    observed.append(cue['pulse'])
                    times.append(sh['timeline_in']+cue['at_sec'])
        check(observed==ev['expected_pulses'],'SIGNAL_COUNT',ev['id'],'동일 신호의 점멸 중복·누락')
        if len(times)==len(ev['offsets']) and times:
            check([round(t-times[0],3) for t in times]==ev['offsets'],'SIGNAL_INTERVAL',ev['id'],'점멸 간격 불일치')
    norm=lambda t:re.sub(r'[^가-힣A-Za-z0-9]','',t)
    for sc in case['scenes']:
        for source_id,src in zip(sc['source_ids'],sc['sources']):
            audio=' '.join(re.sub(r'[가-힣]+(?: O\.S\.)?:\s*','',sh['audio']) for sh in case['shots'] if source_id in sh['source_refs'])
            for actor,line in re.findall(r'([가-힣]+): “([^”]+)”',src):
                check(norm(line) in norm(audio),'DIALOGUE_COVERAGE',source_id,f'{actor}: {line}')
    return dict(checks=checks, errors=errors, error_count=len(errors),
                scope="데이터의 선언값 검사. 자연어 의미·실제 그림·녹음·재생 품질은 판정하지 않음.")

def stamp(sec):
    return f'{int(sec)//60:02}:{int(sec)%60:02}'

def save(case, version):
    folder = ROOT / case["id"]
    folder.mkdir(exist_ok=True)
    pages = grids(case)
    for name, obj in [(f'board-{version}.json',case), (f'grids-{version}.json',pages),
                      (f'validation-{version}.json',validate(case,pages))]:
        (folder/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
    script = [f'# {case["title"]} — 시나리오 {version}', '', case['logline'], '',
              '직접 창작한 워크플로우 시험용 단편. 대사와 행동을 실제 녹음·공연한 시간은 아니다.', '',
              '## 인물·공간·물성', '', case['bible'], '']
    for sc in case['scenes']:
        script += [f'## {sc["id"]}. {sc["location_id"]} / {sc["story_time"]}', '']
        for sid, src in zip(sc['source_ids'],sc['sources']):
            script += [f'**{sid}**', '', src, '']
    sp = folder/f'screenplay-{version}.md'
    if not sp.exists() or version == 'v3': sp.write_text('\n'.join(script))
    board = [f'# {case["title"]} — 글콘티 {version}', '',
             f'본편 {stamp(case["runtime_sec"])} + 크레딧 {case["credits_sec"]}초 = {stamp(case["total_sec"])}. '
             f'{len(case["shots"])}샷 / {sum(len(x["panels"]) for x in case["shots"])}패널 / {len(pages)}개 2×2 그리드.', '',
             '**검증 범위:** 글콘티·시간 합계·참조·상태 선언. 실제 그림과 애니매틱은 미생성. 본문은 원문 씬별 묶음이며 실제 상영 순서는 아래 편집 순서 및 timeline 파일을 따른다.', '',
             '**편집 순서:** '+ ' → '.join(sh['id'] for sh in case['shots']), '',
             '## 카메라 설정', '']
    board += [f'- **{k}**: {v}' for k,v in case['cameras'].items()]
    for sc in case['scenes']:
        board += ['', f'## {sc["id"]} · {sc["location_id"]} · {sc["story_time"]}', '',
                  '| 샷/시간/원문 | 카메라 | 화면과 행동 | 목적·소리·컷 연결 |', '|---|---|---|---|']
        for sh in case['shots']:
            if sh['scene_id']!=sc['id']:continue
            board.append(f'| #{sh["edit_order"]} {sh["id"]}<br>{stamp(sh["timeline_in"])}–{stamp(sh["timeline_out"])} ({sh["duration_sec"]}초)<br>{sh["location_id"]}<br>{", ".join(sh["source_refs"])} '
                         f'| {sh["size"]} / {sh["camera_id"]} | {sh["action"]} '
                         f'| 목적: {sh["purpose"]}<br>소리: {sh["audio"]}<br>전환: {sh["cut_reason"]} |')
        board += ['', '**상태 변화·패널**', '']
        for sh in case['shots']:
            if sh['scene_id']!=sc['id']:continue
            delta = ', '.join(f'{k}: {sh["state_in"].get(k)} → {v}' for k,v in sh.get('changes',{}).items()) or '추적 중인 상태 유지'
            board += [f'- {sh["id"]}: {delta}. 패널: '+ ' / '.join(f'{p["id"]} (+{p["at_sec"]}초): {p["pose"]}' for p in sh['panels'])]
    (folder/f'board-{version}.md').write_text('\n'.join(board)+'\n')
    timeline=[f'# {case["title"]} — 실제 편집 순서 {version}','',
              '| 순서·시간 | 샷/장소 | 화면·소리 |','|---|---|---|']
    for sh in case['shots']:
        timeline.append(f'| {sh["edit_order"]} / {stamp(sh["timeline_in"])}–{stamp(sh["timeline_out"])} | {sh["id"]} / {sh["location_id"]} | {sh["action"]}<br>{sh["audio"]} |')
    (folder/f'timeline-{version}.md').write_text('\n'.join(timeline)+'\n')
    prompts = [f'# {case["title"]} — 씬별 그리드 프롬프트 {version}', '',
               '모델 독립 초안. 아래 에셋은 명세이며 실제 이미지 참조는 아직 없다. 상태: PROMPT_COMPILED / references_pending.', '',
               '## 필요한 에셋', '']
    prompts += [f'- {k}: {v}' for k,v in case['assets'].items()]
    sm = {x['id']:x for x in case['shots']}
    for pg in pages:
        prompts += ['', f'## {pg["id"]}', '', '```text',
                    f'검수용 {case["format"]} 그림 콘티. {pg["scene_id"]}, {pg["location_id"]}, {pg["story_time"]}.',
                    '2열×2행, 각 칸 유효 화면 16:9, 일정한 여백. 왼쪽부터 행 순서. 칸 안의 글씨·번호·말풍선 없음.',
                    '공통 설정: '+case.get('render_bible',case['bible']),
                    '시간 분기: '+pg.get('branch','present')+'. 이 분기의 인물·공간 버전만 사용한다.',
                    '그리드 칸은 독립적인 특정 순간이다. 한 칸 안에 연속 동작을 중복 인물로 그리지 않는다.',
                    '상태표는 화면 밖까지 포함한 세계의 기록이다. 나열된 인물·소품을 모두 그리지 말고, 해당 장소·카메라·포즈에 보이는 대상만 그린다.']
        for i,p in enumerate(pg['slots'],1):
            sh=sm[p['shot_id']]
            prompts += [f'슬롯 {i} ({p["id"]}): {p["size"]}. {case["cameras"][p["camera_id"]]} 포즈: {p["pose"]}.']
            if version!='v1':
                state = p.get('state', sh['state_in'] if p['at_sec']==0 and len(sh['panels'])>1 else sh['state_out'])
                prompts += ['이 순간의 상태: '+json.dumps(state,ensure_ascii=False)+'.']
                visible_assets=p.get('visible_assets',sh.get('visible_assets',[]))
                if visible_assets:
                    prompts += ['외형 참조 후보(모두 화면에 넣으라는 뜻 아님): '+'; '.join(f'{a}: {case["assets"][a]}' for a in visible_assets)+'.']
                if p.get('state_note'):prompts += ['중간 상태 근거: '+p['state_note']]
            if sh.get('panel_constraints'): prompts += ['유지/비공개 조건: '+sh['panel_constraints']]
        if pg['empty_slots']:prompts += ['빈 슬롯: '+', '.join(map(str,pg['empty_slots']))+'. 새 장면으로 채우지 않는다.']
        prompts += ['```']
    (folder/f'grid-prompts-{version}.md').write_text('\n'.join(prompts)+'\n')
    cue_sheet=[f'# {case["title"]} — 시간 지정 큐 {version}','','이미지 생성과 구분되는 타임라인 지시. 정지 패널의 개수로 점멸 횟수를 대신하지 않는다.','',
               '| 사건/점멸 | 샷 | 샷 내 시작 | 전체 시작 | 켜짐 길이 |','|---|---|---:|---:|---:|']
    for sh in case['shots']:
        for cue in sh.get('timed_cues',[]):
            cue_sheet.append(f'| {cue["event_id"]} / {cue["pulse"]} | {sh["id"]} | {cue["at_sec"]}초 | {sh["timeline_in"]+cue["at_sec"]}초 | {cue.get("on_duration_sec",1)}초 |')
    (folder/f'cue-sheet-{version}.md').write_text('\n'.join(cue_sheet)+'\n')

def load_case(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/(name+'.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CASE

if __name__=='__main__':
    import sys
    for name in sys.argv[1:] or ['case01','case02','case03']:
        c=materialize(load_case(name));save(c,'v1')
        result=validate(c)
        print(json.dumps(dict(case=c['id'],shots=len(c['shots']),runtime=c['total_sec'],**result),ensure_ascii=False))
