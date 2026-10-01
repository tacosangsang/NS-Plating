"""Apply explicitly documented editorial revisions to preserved v1 fixtures."""
import copy
import json
from pathlib import Path
from harness import ROOT, reflow, save, validate, grids, stamp

def get(c,sid): return next(s for s in c['shots'] if s['id']==sid)
def edit(c,sid,**changes):
    s=get(c,sid)
    old=s['duration_sec']
    poses=changes.pop('poses',None)
    s.update(changes)
    if poses is not None:
        s['panels']=[dict(id=f'{sid}_P{i+1:02}',pose=p,at_sec=round(i*s['duration_sec']/len(poses),3)) for i,p in enumerate(poses)]
    elif old!=s['duration_sec']:
        for p in s['panels']:p['at_sec']=round(p['at_sec']*s['duration_sec']/old,3)
    return s
def insert(c,after,newid,**changes):
    base=copy.deepcopy(get(c,after))
    base.update(id=newid,changes={},requires_state={},requires_known=[],reveals=[])
    for field in ['timed_cues','signal_event','powered_motion']:base.pop(field,None)
    c['shots'].insert(c['shots'].index(get(c,after))+1,base)
    return edit(c,newid,**changes)
def source(c,sid,old,new):
    for sc in c['scenes']:
        if sid in sc['source_ids']:
            i=sc['source_ids'].index(sid)
            assert old in sc['sources'][i],(sid,old)
            sc['sources'][i]=sc['sources'][i].replace(old,new)
            return
    raise KeyError(sid)
def finding(code,grade,target,problem,fix,limit='그림·연기·실제 재생 검증은 별도 필요'):
    return dict(id=code,severity=grade,target=target,problem=problem,fix=fix,remaining=limit)

def revise_chair(c):
    issues=[
      finding('C01','major','SC03_SH08 이후','코트를 벗는 원문이 있는데 전역 에셋 설명에는 황토 코트만 있고 상태표에는 의상 변화가 없다.','코트 아래 회색 니트를 정의하고 의상 상태·패널별 에셋을 연결.'),
      finding('C02','major','SC05_SH04','발끝에서 작업대 손가락으로 바뀌는 두 화면을 하나의 고정 CU로 기록했다.','발과 손을 서로 다른 두 샷으로 분리하고 같은 두 박자 소리로 연결.'),
      finding('C03','major','SC03_SH08 → SC04_SH01','바닥에서 작업대로 의자가 이동하지만 들어 올리는 행동이 콘티에 빠져 있다.','공동으로 들어 올리는 샷과 원문 행동을 추가해 물리적 위치를 연결.'),
      finding('C04','major','SC04_SH08','남은 세 나사의 수리와 의자 세우기를 14초 한 샷으로 압축했다. 시간 생략인지 실제 연속 동작인지 불명확하다.','작업 시간 생략을 명시하고 마지막 나사와 세우기를 두 샷으로 분리.'),
      finding('C05','major','SC06_SH05~06','문 안과 골목 밖을 같은 장소값으로 묶어 실외 그림도 실내 그리드에 들어간다.','원문 씬은 보존하고 샷 장소를 SHOP_EXTERIOR로 분리.'),
      finding('C06','minor','SC02_SH03·SC03_SH06·SC05_SH08·SC06_SH03','짧은 발화 뒤 단일 표정을 12초씩 유지한 구간이 반복된다.','대사의 의미가 바뀌는 멈춤은 남기고 네 구간 및 공간 재설정의 여유 시간을 줄임.','단축이 감정을 훼손하지 않는지는 실제 리딩·애니매틱에서 확인')]
    c['initial_states']['present']['ha_wardrobe']='ochre_coat'
    c['assets']['HA_SHIRT']='하: 황토 코트를 벗은 뒤 회색 니트, 같은 얼굴·묶은 머리'
    c['assets']['SHOP_EXTERIOR']='동쪽 출입구 바깥 골목, 같은 가게 문과 유리'
    c['camera_locations']={'A':['SHOP','ENTRANCE'],'B':['SHOP','ENTRANCE'],'C':['SHOP'],'D':['SHOP'],'E':['SHOP','ENTRANCE'],'F':['SHOP_EXTERIOR'],'DF':['SHOP']}
    c['cameras']['DF']='작업대 남쪽 바닥 높이의 고정 카메라. 하의 두 발만 보인다.'
    c['render_bible']='절제된 2D. 북쪽 재봉틀·동쪽 문·서쪽 창. 윤은 짧은 머리 회색 작업복, 하는 묶은 머리. 하의 외투 착용 여부는 패널 상태를 따른다. 청록 의자의 오른쪽 뒤 다리 균열과 수리 상태를 유지. 실외 패널에는 골목을 표시한다.'
    edit(c,'SC03_SH08',changes={'chair':'floor_side','ha_wardrobe':'gray_knit'},
         action='하가 황토 코트를 벗어 접고 회색 니트 차림으로 윤 옆에 앉는다. 둘은 의자를 올릴 준비를 한다.',
         poses=['코트를 벗어 접는 하','회색 니트 차림으로 의자 옆에 앉은 하'])
    source(c,'SC03_SRC04','하가 같은 높이로 쪼그려 앉는다.','하가 회색 니트 차림으로 같은 높이에 쪼그려 앉는다. 둘이 의자를 들어 작업대 위에 옆으로 눕힌다.')
    insert(c,'SC03_SH08','SC03_SH08B',duration_sec=8,size='WS',camera_id='A',
           action='윤이 좌판을, 하가 등받이를 잡아 바닥의 의자를 작업대 위로 올린다.',purpose='수리 위치로 이동하는 공동 행동',audio='나무가 작업대에 닿는 소리',
           poses=['바닥의 의자를 나눠 잡은 자매','작업대에 옆으로 놓인 의자'],changes={'chair':'workbench_side'},cut_reason='작업대 위 의자가 안정된 뒤 도구를 잡는 동작으로')
    edit(c,'SC05_SH04',duration_sec=6,camera_id='DF',action='하의 발끝이 바닥에 두 박자를 친다.',audio='바닥 두 박자',poses=['바닥을 두드리는 하의 발'],cut_reason='두 박자 소리를 받아 윤의 손가락으로 컷')
    insert(c,'SC05_SH04','SC05_SH04B',duration_sec=6,size='CU',camera_id='D',action='윤의 손가락이 작업대에서 같은 두 박자를 돌려준다.',purpose='소리를 주고받는 공통 기억',audio='나무 위 같은 두 박자',poses=['작업대를 두드리는 윤의 두 손가락'],cut_reason='박자가 끝난 뒤 하의 식사 질문으로')
    edit(c,'SC04_SH08',duration_sec=10,size='CU',camera_id='D',action='작업 시간이 생략된 뒤, 이미 세 나사가 들어간 보강판의 마지막 나사를 하가 조인다. 윤의 충분하다는 손짓에 멈춘다.',
         audio='시간 생략 후 마지막 나사의 마찰',poses=['세 나사가 고정된 보강판과 마지막 나사','네 나사가 고정된 보강판'],
         changes={'chair_integrity':'braced_four_screws','brace':'chair_fixed'},
         continuity_exception='앞 샷 뒤 나사 작업 일부가 생략됨. 마지막 나사의 동작은 실제 연속.',cut_reason='드라이버가 멈춘 뒤 둘이 의자를 드는 넓은 화면으로')
    insert(c,'SC04_SH08','SC04_SH08B',duration_sec=8,size='MS',camera_id='A',action='둘이 수리한 의자를 작업대에서 들어 바닥에 세운다.',purpose='수리 완료와 다음 착석의 공간 연결',audio='네 다리가 바닥에 닿는 소리',
           poses=['작업대 위 의자를 든 두 사람','바닥에 바로 선 의자'],changes={'chair':'floor'},cut_reason='네 다리가 닿는 소리를 읽은 뒤 착석 시험으로')
    for sid,seconds in [('SC02_SH03',8),('SC03_SH06',9),('SC05_SH08',8),('SC06_SH03',8),('SC04_SH01',8)]:edit(c,sid,duration_sec=seconds)
    for sid in ['SC06_SH05','SC06_SH06']:edit(c,sid,location_id='SHOP_EXTERIOR')
    edit(c,'SC06_SH06',action='문밖 바닥에 의자를 내려놓고 윤이 등받이를 받친다. 하가 문으로 돌아갈 공간이 생긴다.',changes={'chair':'outside_ground_supported_by_yun'},poses=['문밖 바닥에 내려놓는 의자','의자를 받친 윤과 문으로 돌아서는 하'])
    for s in c['shots']:
        s['costume_version']='gray_knit' if c['shots'].index(s)>c['shots'].index(get(c,'SC03_SH08')) else 'ochre_coat'
        s['visible_assets']=['YUN','HA_SHIRT' if s['costume_version']=='gray_knit' else 'HA','CHAIR']
    return issues

def revise_light(c):
    issues=[
      finding('L01','major','SC01_SH02~03','원문에서 전원이 꺼졌다 돌아오지만 상태표는 계속 on으로 남는다.','꺼짐·복귀를 상태 변화로 기록하고 무전원 능동 동작 검사 추가.'),
      finding('L02','critical','SC05_SRC01 → SC06_SH01~03','배터리를 뺀 다음 도크 위로 옮기는 준비 동작은 즉시 정지하는 물성과 양립하지 않는다.','도크를 배터리 슬롯 바로 아래에 먼저 배치하고, 분리 뒤 수평 이동 없이 중력 낙하하도록 원문·구도 수정.'),
      finding('L03','major','SC04_SH04','발판 시험, 내려오기, 화분 들기, 다시 오르기와 배치가 14초 한 샷에 몰렸다.','빈손 시험과 실제 운반을 두 샷으로 나누고 총 24초로 재배정.','동작 시간은 추정. 모형 블로킹 또는 애니매틱으로 재확인'),
      finding('L04','major','SC06~07','희생 이후 두 씬이 164초다. 꺼진 로봇·그림자·반사·여정을 반복 확인해 결말이 늘어질 가능성이 높다.','중복 확인 두 샷을 통합·삭제하고 정적 구간을 단축. 잎의 최종 접촉은 보존.','조용한 결말의 적정 길이는 자기검토만으로 확정 불가'),
      finding('L05','major','SC06_SH01~04','핵심 전원 전환을 접점·배터리 CU로 나눠 보여주면 도크의 실제 위치와 낙하 원인이 약해진다.','결정 직전 중경에 슬롯·오른 집게·아래 도크를 함께 보이고 이후도 같은 배치를 고정.')]
    c['render_bible']=c['bible']+' 배터리 도크는 몸 왼쪽 슬롯 바로 아래. 분리 이후 배터리를 옆으로 옮기는 능동 동작은 없다.'
    edit(c,'SC01_SH02',changes={'power':'off','grip':'open'})
    edit(c,'SC01_SH03',changes={'power':'on','grip':'closed_when_powered'},power_restored_within_shot=True)
    source(c,'SC05_SRC01','몸 왼쪽 배터리를 빼 도크 위로 옮기는 동작을 빈손으로 따라 한다.','도크를 몸 왼쪽 배터리 슬롯의 바로 아래로 옮긴다. 오른손으로 몸 앞을 가로질러 배터리를 잡고 수평 이동 없이 떨어뜨릴 수 있는지 빈손으로 맞춰 본다.')
    source(c,'SC05_SRC02','이번에는 도크 가운데로 손이 들어온다.','이번에는 배터리 슬롯 바로 아래에 도크 중심이 온다.')
    edit(c,'SC05_SH01',action='갓을 화분 쪽으로 돌리고 도크를 몸 왼쪽 배터리 슬롯의 바로 아래에 맞춘다.',poses=['화분 쪽으로 도는 갓','몸 왼쪽 슬롯 아래 도크'])
    edit(c,'SC05_SH02',action='오른손으로 몸 앞을 가로질러 왼쪽 배터리 슬롯을 잡는 자세를 연습한다. 배터리가 빠지는 자리 바로 아래 도크가 있다.',poses=['몸 앞을 가로지른 오른 집게','집게 바로 아래 도크'],cut_reason='집게와 도크 벽의 간섭이 생기는 지점으로')
    edit(c,'SC05_SH07',action='왼손으로 선반을 짚고 오른손으로 몸 왼쪽 배터리를 잡는다. 도크는 배터리 바로 아래에 고정되어 있다.',poses=['슬롯·오른손·아래 도크가 함께 보이는 준비 자세'])
    edit(c,'SC06_SH01',size='MS',camera_id='E',action='배터리 슬롯·오른손·아래 도크를 한 화면에 유지한다. 핍이 배터리를 당기고 접점이 끊어지기 직전에 컷.',poses=['오른손이 잡은 배터리와 아래의 도크','접점이 아직 닿아 있는 분리 직전'],cut_reason='접점이 끊기는 순간의 수동적 집게 열림으로 연결')
    edit(c,'SC06_SH02',powered_motion=False,passive_motion='무전원 스프링으로 집게가 열림',cut_reason='집게에서 떨어진 배터리의 낙하를 같은 위치에서 이어받음')
    edit(c,'SC06_SH03',powered_motion=False,passive_motion='중력 낙하')
    edit(c,'SC04_SH04',duration_sec=12,action='고정한 받침에 빈손으로 올라 선반 높이를 확인하고 내려온다.',poses=['빈손으로 받침에 오른 핍','바닥에 돌아온 핍'],changes={},cut_reason='발판이 흔들리지 않음을 확인한 뒤 실제 운반으로')
    insert(c,'SC04_SH04','SC04_SH04B',duration_sec=12,size='WS',camera_id='D',action='바닥 화분을 두 손으로 들어 받침 중앙을 올라 선반에 놓는다.',purpose='시험한 경로로 화분을 운반',audio='바퀴 부하·도기 닿는 소리',poses=['바닥 화분을 든 핍','선반에 놓인 화분'],changes={'plant':'shelf'},requires_state={'cart':'chocked_shelf_front'},cut_reason='화분이 안정된 뒤 차광판 손잡이로')
    edit(c,'SC04_SH07',duration_sec=16)
    removed=['SC06_SH06','SC06_SH07']
    get(c,'SC06_SH04')['source_refs'].append('SC06_SRC04')
    edit(c,'SC06_SH04',action='켜진 램프가 화분·멈춘 핍·열린 집게·고정된 바퀴를 함께 비춘다. 깨진 테두리와 잎 두 장은 그대로다.',poses=['꺼진 램프와 정지한 핍','켜진 램프·꺼진 핍·변하지 않은 화분'])
    c['shots']=[s for s in c['shots'] if s['id'] not in removed]
    for sid,seconds in [('SC06_SH05',8),('SC07_SH01',6),('SC07_SH02',8),('SC07_SH03',8),('SC07_SH04',10),('SC07_SH06',8)]:edit(c,sid,duration_sec=seconds)
    for s in c['shots']:
        s['powered_motion']=s.get('powered_motion',s['scene_id'] not in ['SC06','SC07'])
        if s['scene_id']=='SC06' and s['id']=='SC06_SH01':s['powered_motion']=True
        s['panel_constraints']='배터리·화분 각각 하나. 잎 두 장. power=off이면 로봇의 표정·팔·바퀴는 능동적으로 움직이지 않는다. 도크는 배터리 슬롯 바로 아래.'
    return issues

def revise_signals(c):
    issues=[
      finding('S01','critical','SC03_SH06·SC09_SH06','객실 원문 씬에 갑판 샷, 갑판 원문 씬에 다락 마지막 샷이 포함되어 장소별 그리드가 섞인다.','원문 씬과 샷 장소를 분리하고 장소별 페이지를 생성.'),
      finding('S02','major','SC02_SH01·SC02_SH05','과거 첫 패널은 손전등 CU뿐이고 전역 설정에는 흠집·현재 인물도 함께 있다. 과거 전환이 늦게 읽히거나 아직 생기지 않은 흠집이 그려질 수 있다.','과거 진입을 아이·어머니·카펫이 보이는 샷으로 바꾸고 흠집 전후 상태·시간별 에셋 제한을 추가.'),
      finding('S03','critical','SC07_SH05 → SC08_SH01','두 번째 세 번의 응답을 보내는 컷과 받는 컷에서 각각 세 번 보여줘 여섯 번으로 읽힐 수 있다.','송신 컷은 누르기 직전에서 자르고 수신 시점에서 세 번 전체를 한 번만 표시. 신호 ID·점멸 번호·간격을 기록.'),
      finding('S04','major','SC04~SC06','장소별로 씬 전체를 이어 붙여 호출·충전·수신의 선후가 모호하다.','공통 사건 기준으로 샷을 교차 배열하고 실제 편집 순서표를 별도 출력.'),
      finding('S05','major','SC09_SH01','확인 응답도 다락의 세 번 뒤 얼굴 반사로 또 세 번 보여준다.','배 쪽은 빛이 끝난 뒤의 반응으로 이어 사건을 중복하지 않음.'),
      finding('S06','minor','SC05_SH04','원문에는 지나가는 승객이 있지만 에셋 목록에 없다.','얼굴이 드러나지 않는 성인 승객 실루엣 에셋을 등록.')]
    c['camera_locations']={'A':['ATTIC'],'B':['ATTIC'],'P':['ATTIC'],'D':['BOAT_CABIN'],'E':['BOAT_DECK'],'F':['ATTIC'],'G':['BOAT_CABIN','BOAT_DECK']}
    edit(c,'SC03_SH06',location_id='BOAT_DECK')
    edit(c,'SC09_SH06',location_id='ATTIC')
    c['assets']['PASSENGER']='얼굴이 보이지 않는 성인 승객의 하체 실루엣, 어두운 코트'
    c['assets']['WAITING_CHAIR']='현재 다락에 남겨 둔 등받이 나무 의자'
    c['initial_states']['past']['torch_scratch']='none'
    c['initial_states']['present']['torch_scratch']='white_mark'
    edit(c,'SC02_SH01',size='WS',camera_id='P',action='카펫·사진·긴 커튼이 있는 과거 다락. 붉은 니트의 어린 이나와 어머니가 함께 보이고 빨간 등을 켠다.',poses=['과거 다락의 어린 이나·어머니·켜지는 빨간 등'],changes={'red_on':'yes'},cut_reason='아이와 어머니로 시간 변화를 확인한 뒤 신호 설명으로')
    get(c,'SC02_SH05')['changes']['torch_scratch']='white_mark'
    c['render_bible']='2D. 다락은 남쪽 바다 창·북쪽 장·동쪽 문. 과거는 카펫·사진·어린 이나·어머니, 현재는 빈 벽·상자·성인 이나. 과거와 현재 인물을 한 패널에 섞지 않는다. 빨간 등은 이나 쪽, 흰 등은 준 쪽. 흠집은 패널 상태에 따른다.'
    edit(c,'SC03_SH04',action='이미 꺼져 있는 언덕 불빛과 어두운 집을 준의 위치에서 본다.',poses=['정전 뒤 어두워진 언덕 집'])
    source(c,'SC03_SRC02','창밖 언덕의 불빛 몇 개가 동시에 사라진다.','창밖 언덕의 불빛은 이미 꺼져 있다.')
    edit(c,'SC07_SH05',duration_sec=5,action='준이 왼팔을 고정하고 스위치 위에 손가락을 둔다. 누르기 직전에 컷. 이 샷에서는 아직 점멸하지 않는다.',audio='바람, 스위치는 아직 누르지 않음',poses=['꺼진 흰 등 스위치 위의 손가락'],changes={'reply':'second_armed'},reveals=['second_reply_armed'],cut_reason='누르기 직전에 받는 이나의 시점으로 전환')
    edit(c,'SC08_SH01',duration_sec=8,action='이나의 시점에서 배의 흰빛 세 번을 끊지 않고 본다. 1초 빛·1초 어둠의 간격, 마지막 뒤 3초는 어둠.',poses=['배의 첫 흰빛','배의 세 번째 흰빛 뒤 어둠'],requires_known=['second_reply_armed'],reveals=['second_reply_sent','ina_saw_reply'],changes={'reply':'second_complete'},cut_reason='세 번째 점멸이 끝난 뒤 준이 팔을 내리는 결과로')
    edit(c,'SC09_SH01',action='집의 세 번이 모두 끝난 어둠 속에서 준의 긴장이 풀린다. 얼굴에 새 점멸 반사를 추가하지 않는다.',poses=['응답이 끝난 뒤 어둠 속 준의 얼굴'])
    source(c,'SC09_SRC01','준의 얼굴에 집에서 돌아온 세 번의 빛이 작게 스친다.','집에서 돌아온 세 번이 끝난 뒤 준의 얼굴에서 긴장이 풀린다.')
    c['signal_events']=[dict(id='REPLY_1',expected_pulses=[1,2,3],offsets=[0,12,24]),dict(id='REPLY_2',expected_pulses=[1,2,3],offsets=[0,2,4]),dict(id='ACK',expected_pulses=[1,2,3],offsets=[0,2,4])]
    # First reply is intentionally read as an uncertain, widely spaced attempt;
    # exact cue offsets are set after edit order and durations are fixed below.
    get(c,'SC06_SH06')['timed_cues']=[dict(event_id='REPLY_1',pulse=1,at_sec=10,visible=True)]
    get(c,'SC07_SH01')['timed_cues']=[dict(event_id='REPLY_1',pulse=2,at_sec=0,visible=True)]
    get(c,'SC07_SH02')['timed_cues']=[dict(event_id='REPLY_1',pulse=3,at_sec=0,visible=True)]
    get(c,'SC08_SH01')['timed_cues']=[dict(event_id='REPLY_2',pulse=i+1,at_sec=i*2,visible=True) for i in range(3)]
    get(c,'SC08_SH03')['timed_cues']=[dict(event_id='ACK',pulse=i+1,at_sec=i*2,visible=True) for i in range(3)]
    original={s['id']:s for s in c['shots']}
    order=[s['id'] for s in c['shots'] if s['scene_id'] in ['SC01','SC02','SC03']]
    order += ['SC04_SH01','SC04_SH02','SC04_SH03','SC04_SH04','SC04_SH05',
              'SC05_SH01','SC05_SH02','SC04_SH06','SC05_SH03','SC05_SH04',
              'SC06_SH01','SC05_SH05','SC05_SH06','SC06_SH02','SC06_SH03',
              'SC06_SH04','SC06_SH05','SC06_SH06','SC07_SH01','SC07_SH02',
              'SC07_SH03','SC07_SH04','SC07_SH05','SC08_SH01','SC07_SH06',
              'SC08_SH02','SC08_SH03','SC08_SH04','SC08_SH05','SC08_SH06']
    order += [f'SC09_SH{i:02}' for i in range(1,7)]
    assert len(order)==len(set(order))==len(c['shots'])
    c['shots']=[original[s] for s in order]
    # The first attempt: pulse 1 at the end of Ina's shot, then pulses 2/3 at
    # starts of Jun's shots. Shorten those shots so the spacing is intentional.
    edit(c,'SC06_SH06',duration_sec=12)
    edit(c,'SC07_SH01',duration_sec=2)
    edit(c,'SC07_SH02',duration_sec=6)
    c['signal_events'][0]['offsets']=[0,2,4]
    for s in c['shots']:
        sc=next(x for x in c['scenes'] if x['id']==s['scene_id'])
        s['visible_assets']=list(sc.get('asset_ids',[]))
        if s['branch']=='past':
            s['panel_constraints']='과거 인물만 등장. 이나는 붉은 니트의 아이, 어머니는 회색 긴 치마. torch_scratch=none 순간에는 흰 흠집을 그리지 않는다.'
        elif s['location_id']=='ATTIC':
            s['visible_assets']=['INA_NOW','ATTIC_NOW','RED_TORCH','WAITING_CHAIR']
            s['panel_constraints']='현재의 성인 이나. 어머니·어린 이나·어린 준은 없다. 빨간 등만 사용.'
        else:
            s['visible_assets']=['JUN_NOW',s['location_id'],'WHITE_TORCH','PHONE']
            s['panel_constraints']='현재의 성인 준. 빨간 손전등과 이나는 이 공간에 없다.'
        if s['id']=='SC05_SH04':s['visible_assets'].append('PASSENGER')
    return issues

def main():
    summaries=[]
    for cid,fn in [('test01-chair',revise_chair),('test02-light',revise_light),('test03-signals',revise_signals)]:
        old=json.loads((ROOT/cid/'board-v1.json').read_text())
        c=copy.deepcopy(old)
        issues=fn(c)
        c['revision']='v2'
        c['review_method']='동일 작성자의 후속 자기검토. 독립 심사·관객 시험 아님.'
        reflow(c)
        # Resolve dynamic panel constraints after state propagation.
        for sh in c['shots']:
            if cid=='test01-chair':
                sh['costume_version']=sh['state_in']['ha_wardrobe'] if sh['id']!='SC03_SH08' else 'wardrobe_transition'
            for p in sh['panels']:
                p['state']=copy.deepcopy(sh['state_in'] if len(sh['panels'])>1 and p['at_sec']==0 else sh['state_out'])
        save(c,'v2')
        result=validate(c)
        (ROOT/cid/'review-findings.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n')
        old_map={s['id']:s for s in old['shots']};new_map={s['id']:s for s in c['shots']}
        changes=[]
        fields=['duration_sec','action','camera_id','location_id','audio','changes','source_refs','cut_reason','panels','timed_cues']
        for sid in sorted(old_map.keys()|new_map.keys()):
            if sid not in old_map: changes.append(dict(shot_id=sid,kind='added',after=new_map[sid]))
            elif sid not in new_map: changes.append(dict(shot_id=sid,kind='removed',before=old_map[sid]))
            else:
                diff={f:dict(before=old_map[sid].get(f),after=new_map[sid].get(f)) for f in fields if old_map[sid].get(f)!=new_map[sid].get(f)}
                if diff:changes.append(dict(shot_id=sid,kind='changed',fields=diff))
        (ROOT/cid/'changes-v1-v2.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
        report=[f'# {c["title"]} — 자기검토와 개선','',c['review_method'],'',
                f'초안 {len(old["shots"])}샷·총 {stamp(old["total_sec"])} → 수정본 {len(c["shots"])}샷·총 {stamp(c["total_sec"])}. 크레딧 {c["credits_sec"]}초 포함. 시간은 연출 추정치.','',
                '초안의 자동 검사 통과는 ID·선언된 상태·참조·시간 합계에 한정됐다. 아래는 원문과 실제 문장을 다시 대조해 찾은 편집·설계 문제다. 오류를 일부러 심은 시험은 별도 mutation 테스트에만 존재한다.','',
                '| ID/등급 | 대상 | 초기 문제 | 적용한 개선 | 남은 검증 |','|---|---|---|---|---|']
        for f in issues: report.append(f'| {f["id"]} / {f["severity"]} | {f["target"]} | {f["problem"]} | {f["fix"]} | {f["remaining"]} |')
        report += ['',f'수정본 데이터 검사: {result["checks"]}개 검사, 오류 {result["error_count"]}건. 검사 수는 샷·패널 수에 따라 달라지며 품질 점수가 아니다.','',
                   '## 여전히 확인하지 못한 것','',
                   '- 실제 그림에서 얼굴·손·공간·미세 동작이 맞는지.',
                   '- 배우 리딩/임시 음성의 실제 길이와 표정의 전달력.',
                   '- 애니매틱을 처음 보는 관객의 이해와 감정 반응.',
                   '- 이미지 모델의 그리드 준수율과 재생성 비용. 참조 이미지는 아직 준비하지 않았다.']
        (ROOT/cid/'review.md').write_text('\n'.join(report)+'\n')
        summaries.append(dict(case=cid,title=c['title'],v1_seconds=old['total_sec'],v2_seconds=c['total_sec'],
           v1_shots=len(old['shots']),v2_shots=len(c['shots']),panels=sum(len(s['panels']) for s in c['shots']),grids=len(grids(c)),
           editorial_findings=len(issues),checks=result['checks'],errors=result['error_count']))
        print(json.dumps(dict(case=cid,**result),ensure_ascii=False))
    (ROOT/'summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
