"""Intentional corruptions test the validator, not the films' creative quality."""
import copy
import json
from harness import ROOT, validate, grids

cases={n:json.loads((ROOT/n/'board-v3.json').read_text()) for n in ['test01-chair','test02-light','test03-signals']}
tests=[]
def run(label,cid,expected,mutator,page_mutator=None):
    c=copy.deepcopy(cases[cid]);mutator(c)
    pages=grids(c)
    if page_mutator:page_mutator(pages)
    result=validate(c,pages)
    codes={e['code'] for e in result['errors']}
    tests.append(dict(name=label,expected=expected,detected=sorted(codes),passed=expected in codes))
def at(c,sid):return next(s for s in c['shots'] if s['id']==sid)
noop=lambda x:None

run('샷 ID 중복','test01-chair','DUPLICATE_SHOT',lambda c:c['shots'][1].update(id=c['shots'][0]['id']))
run('음수 길이','test01-chair','INVALID_DURATION',lambda c:c['shots'][0].update(duration_sec=-1))
run('타임라인 구멍','test01-chair','TIMELINE_GAP',lambda c:c['shots'][2].update(timeline_in=99))
run('없는 원문 참조','test01-chair','SOURCE_MISSING',lambda c:c['shots'][0].update(source_refs=['NO_SOURCE']))
def drop_source(c):
    for s in c['shots']:s['source_refs']=[r for r in s['source_refs'] if r!='SC01_SRC01']
run('원문 단위 전체 누락','test01-chair','SOURCE_COVERAGE',drop_source)
run('대사 누락','test01-chair','DIALOGUE_COVERAGE',lambda c:at(c,'SC01_SH03').update(audio='환경음'))
run('없는 카메라','test01-chair','CAMERA_MISSING',lambda c:c['shots'][0].update(camera_id='NO_CAMERA'))
run('선행 상태 없이 소품 이동','test01-chair','STATE_JUMP',lambda c:c['shots'][1]['state_in'].update(chair='in_another_house'))
run('패널 시점 초과','test01-chair','PANEL_TIME',lambda c:c['shots'][0]['panels'][0].update(at_sec=999))
run('없는 패널 에셋','test01-chair','PANEL_ASSET',lambda c:c['shots'][0]['panels'][0].update(visible_assets=['NO_ASSET']))
run('필수 정보 이전에 반응','test03-signals','REVEAL_ORDER',lambda c:c['shots'][0].update(requires_known=['ina_saw_reply']))
run('갑판 카메라를 다락에 배치','test03-signals','CAMERA_LOCATION',lambda c:at(c,'SC09_SH06').update(location_id='BOAT_DECK'))
run('그리드에 다른 장소 혼입','test03-signals','GRID_LOCATION',noop,lambda pages:pages[0].update(location_id='BOAT_DECK'))
run('그리드 패널 누락','test03-signals','GRID_COVERAGE',noop,lambda pages:pages[0]['slots'].pop())
run('꺼진 로봇의 능동 동작','test02-light','UNPOWERED_ACTION',lambda c:at(c,'SC06_SH04').update(powered_motion=True))
run('같은 신호의 점멸 중복','test03-signals','SIGNAL_COUNT',lambda c:at(c,'SC08_SH01')['timed_cues'].append(copy.deepcopy(at(c,'SC08_SH01')['timed_cues'][0])))
run('점멸 간격 어긋남','test03-signals','SIGNAL_INTERVAL',lambda c:at(c,'SC08_SH01')['timed_cues'][1].update(at_sec=2.5))
run('켜짐 길이가 샷 초과','test03-signals','CUE_DURATION',lambda c:at(c,'SC08_SH01')['timed_cues'][0].update(on_duration_sec=99))
run('목표 전체 시간 초과','test01-chair','RUNTIME_RANGE',lambda c:c.update(total_sec=900))

result=dict(scope='검수기 검출 능력을 확인하는 인위적 오류 시험. 창작 초안의 실제 오류 수와 합산하지 않는다.',
            total=len(tests),passed=sum(t['passed'] for t in tests),tests=tests)
(ROOT/'mutation-test-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['total']==result['passed'], '일부 검수기 시험 실패'
