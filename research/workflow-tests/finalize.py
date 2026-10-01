"""Second editorial pass: inspect panel moments, not only shot boundary states."""
import copy
import json
from harness import ROOT, save, validate, grids, stamp

def sh(c,sid):return next(s for s in c['shots'] if s['id']==sid)
def pose_state(c,sid,index,delta,note):
    p=sh(c,sid)['panels'][index]
    p['state'].update(delta)
    p['state_note']=note

def finish(c):
    if c['id']=='test01-chair':
        pose_state(c,'SC02_SH04',0,{'stool':'yun_hand'},'아직 접는 중인 보조의자는 윤의 손에 있다.')
        pose_state(c,'SC03_SH01',0,{'brace':'drawer'},'서랍을 연 대표 순간. 꺼내 작업대에 놓는 종료 상태와 구분.')
        sh(c,'SC03_SH08')['panels'][0]['pose']='황토 코트를 벗기 직전 단추를 푼 하'
        pose_state(c,'SC04_SH08',0,{'chair_integrity':'three_screws','brace':'chair_partial'},'명시한 시간 생략 뒤의 첫 그림. 앞 샷 종료의 한 나사 상태에서 작업이 생략됨.')
        pose_state(c,'SC04_SH08B',0,{'chair':'both_hands_above_workbench'},'작업대에서 이미 들어 올린 중간 순간.')
        pose_state(c,'SC05_SH07',1,{'bag':'table'},'손잡이를 밀어 받기 직전. 가방의 최종 소유는 하, 대표 순간에는 작업대 위.')
        for s in c['shots']:
            for p in s['panels']:
                assets=s.get('visible_assets',[])
                p['visible_assets']=[('HA_SHIRT' if p['state']['ha_wardrobe']=='gray_knit' else 'HA') if a in ['HA','HA_SHIRT'] else a for a in assets]
    elif c['id']=='test02-light':
        c['render_bible']=c['render_bible'].replace('배터리 도크는 몸 왼쪽 슬롯 바로 아래.', '배터리 전달 구간 SC05 후반~SC07에서만 도크를 몸 왼쪽 슬롯 바로 아래에 정렬한다. 앞선 통로 구간에 도크를 추가하지 않는다.')
        for s in c['shots']:
            s['panel_constraints']=s.get('panel_constraints','').replace('도크는 배터리 슬롯 바로 아래.', '도크 정렬은 배터리 전달 구간 SC05 후반~SC07에만 적용한다.')
        for sid,idx,delta,note in [
          ('SC01_SH07',0,{'plant':'pip_both_hands'},'대표 시작 그림은 화분을 이미 들어 올린 순간.'),
          ('SC02_SH03',0,{'ramp':'pip_hands'},'벽에서 떼어 든 중간 상태.'),
          ('SC02_SH05',0,{'ramp':'step_stable'},'판자를 틈에 고정한 뒤 시험하기 직전.'),
          ('SC02_SH06',0,{'plant':'pip_both_hands'},'집어 든 뒤 경사로를 오르기 전.'),
          ('SC02_SH07',0,{'plant':'hall_after_step','ramp':'pip_hands'},'운반 후 화분을 내려놓고 판자를 회수하는 중간 상태.'),
          ('SC03_SH01',1,{'plant':'door_floor'},'문을 밀기 위해 화분을 바닥에 둔 상태.'),
          ('SC03_SH04',0,{'plant':'pip_both_hands'},'화분을 다시 들어 통과하기 시작한 순간.'),
          ('SC03_SH05',0,{'plant':'under_shelf'},'이미 내려놓은 화분. 이후 시선만 창으로 이동.'),
          ('SC04_SH01',0,{'plant':'on_cart','cart':'shelf_front'},'받침에 올렸다가 되돌리기 전의 중간 상태.'),
          ('SC04_SH04B',0,{'plant':'pip_both_hands'},'두 손으로 집어 든 순간.'),
          ('SC04_SH07',0,{'lamp':'pip_both_hands'},'램프를 옮기는 중간 상태.'),
        ]:pose_state(c,sid,idx,delta,note)
    else:
        past=next(sc for sc in c['scenes'] if sc['id']=='SC02')
        past['sources'][2]='이나는 어머니가 들고 있는 빨간 등의 스위치를 눌러 끈다. 의자에서 내려오다가 팔꿈치로 어머니의 손목을 스쳐, 어머니 손에 든 등 옆면이 창틀에 닿는다. 작은 흰 흠집이 생긴다. 어머니는 닦지 않고 손전등을 이나에게 건넨다. 이나는 손전등을 안고 마당으로 내려간다.'
        sh(c,'SC02_SH05')['action']='이나가 어머니 손에 든 등의 스위치를 끄고, 내려오며 손목을 스친다. 어머니 손의 등이 창틀에 닿아 흰 흠집이 생긴다.'
        sh(c,'SC02_SH05')['panels'][0]['pose']='어머니 손에 든 빨간 등과 스위치에 닿은 어린 이나의 손가락'
        pose_state(c,'SC01_SH05',0,{'red_torch':'attic_drawer'},'발견 순간은 서랍 안, 종료 시점에는 이나가 든다.')
        pose_state(c,'SC03_SH03',0,{'white_torch':'jun_bag'},'꺼내기 전 가방 속을 보여주는 순간.')
        pose_state(c,'SC04_SH06',0,{'red_on':'no'},'이미 끈 뒤 충전 손잡이를 펴는 순간.')
        pose_state(c,'SC05_SH03',0,{'white_on':'yes'},'등을 켠 뒤 빛이 난간에 걸리기 직전.')
        pose_state(c,'SC05_SH06',0,{'white_on':'no'},'꺼진 등 위에서 손가락으로 연습하는 순간.')
        pose_state(c,'SC08_SH06',0,{'red_torch':'window_sill','red_on':'no'},'등을 창틀에 놓은 뒤 의자를 옮기는 중간 순간.')
        # A flash is an event on the time line, not six new cinematic cuts.
        s=sh(c,'SC07_SH01');s['changes']['white_on']='no';s['state_out']['white_on']='no'
        sh(c,'SC07_SH02')['state_in']['white_on']='no'
        c['signal_events'].insert(0,dict(id='PAST_DEMO',expected_pulses=[1,2,3],offsets=[0,2,4]))
        sh(c,'SC02_SH04')['timed_cues']=[dict(event_id='PAST_DEMO',pulse=i+1,at_sec=i*2,visible=True) for i in range(3)]
        for sid,on_pose,off_pose,key in [
          ('SC02_SH04','창밖 어린 준의 흰 등 한 번이 켜진 순간','같은 구도에서 흰 등만 꺼진 순간','distant_white_on'),
          ('SC06_SH06','충전 중인 이나 뒤로 배의 첫 흰빛이 켜진 순간','같은 구도에서 먼 배의 흰빛이 꺼진 순간','white_on'),
          ('SC07_SH01','준의 손에 든 흰 등이 켜진 두 번째 점멸 순간','같은 흰 등이 꺼진 간격','white_on'),
          ('SC07_SH02','준의 흰 등이 켜진 세 번째 점멸 순간','점멸이 끝나 꺼진 흰 등을 든 준','white_on'),
          ('SC08_SH01','이나의 시점에서 먼 배의 흰빛이 켜진 순간','같은 배의 흰빛이 꺼진 순간','white_on'),
          ('SC08_SH03','이나의 빨간 등이 켜진 순간','같은 빨간 등이 꺼진 순간','red_on'),
        ]:
            s=sh(c,sid);cue=s['timed_cues'][0];on_t=cue['at_sec'];off_t=on_t+1
            base=copy.deepcopy(s['state_out'])
            s['panels']=[dict(id=sid+'_P01',pose=on_pose,at_sec=on_t,state=dict(base,**{key:'yes'}),state_note='점멸의 켜짐 대표 그림. 반복 횟수는 timed_cues에만 기록.'),
                         dict(id=sid+'_P02',pose=off_pose,at_sec=off_t,state=dict(base,**{key:'no'}),state_note='점멸의 꺼짐 대표 그림. 같은 샷 안에서 재사용할 수 있음.')]
            if sid=='SC06_SH06':
                # Keep the preparatory non-flashing part before the first pulse.
                s['panels'].insert(0,dict(id=sid+'_PRE',pose='아래를 보며 손잡이를 돌리는 이나. 배의 응답은 아직 없다.',at_sec=0,state=dict(base,white_on='no')))
            s['panel_constraints']=s.get('panel_constraints','')+' 불빛 on/off 두 그림은 같은 카메라다. 컷을 추가하지 말고 큐표의 횟수와 간격대로 변한다.'
        for s in c['shots']:
            for cue in s.get('timed_cues',[]):cue['on_duration_sec']=1
    c['revision']='v3'
    c['integration_review']='패널의 중간 상태와 샷 경계 상태를 재대조. 불빛 큐와 대표 패널 분리.'
    return c

if __name__=='__main__':
    summaries=[]
    for cid in ['test01-chair','test02-light','test03-signals']:
        c=finish(json.loads((ROOT/cid/'board-v2.json').read_text()))
        save(c,'v3')
        result=validate(c)
        print(json.dumps(dict(case=cid,**result),ensure_ascii=False))
        summaries.append(dict(case=cid,title=c['title'],runtime_sec=c['runtime_sec'],total_sec=c['total_sec'],
                             shots=len(c['shots']),panels=sum(len(s['panels']) for s in c['shots']),
                             grids=len(grids(c)),checks=result['checks'],errors=result['error_count']))
        text=['# 통합 재검토 v2 → v3','',
              'v2의 자동 검사는 통과했지만 생성 프롬프트를 읽으며 패널의 대표 순간과 샷 시작·종료 상태가 다를 수 있음을 확인했다.',
              '예: 물건을 이미 들어 올린 그림에 시작 상태인 바닥 위치를 붙이면 모순이다. 해당 순간의 상태와 이유를 패널에 명시했다.',
              '샷 경계 사이의 관찰 시점을 구체화했다. 핵심 사건과 러닝타임은 v2와 같다. 빛 배달의 도크 위치 조건은 배터리 전달 구간으로 한정했고, 세 번의 불빛에서는 흠집이 생길 때 어머니가 등을 들고 있음을 원문과 행동에 명시했다.','',
              '세 번째 작품에는 켜짐/꺼짐 대표 그림과 점멸 큐표를 분리했다. 한 신호를 다른 시점에서 반복해 새로운 신호처럼 보이게 하지 않는다.',
              f'최종 데이터 검사 {result["checks"]}건, 오류 {result["error_count"]}건. 실제 이미지·음성·애니매틱은 여전히 검증하지 않았다.']
        (ROOT/cid/'integration-review.md').write_text('\n'.join(text)+'\n')
    (ROOT/'final-summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')
