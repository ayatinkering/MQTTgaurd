import struct
import numpy as np
from research_core import apply_policy, audit, select_policies
from mqttset_data import mqtt_keepalive, packets, ConnectReassembly
from train_pipeline import make_capture
import csv


def cap(y,ids=None,runs=None):
    return {'name':'fixture','seconds':2,'y':np.array(y),
            'ids':np.arange(len(y)) if ids is None else np.array(ids),
            'valid':np.array(y)>=0,'end_us':np.arange(1,len(y)+1)*2000000,
            'runs':runs or []}


def test_filters_are_causal_and_reset_on_empty_and_missing_ids():
    p=[.9,.9,np.nan,.9,.9];ids=[0,1,2,4,5]
    assert apply_policy(p,ids,{'family':'consecutive','k':2}).tolist()==[False,True,False,False,True]
    assert apply_policy(p,ids,{'family':'majority','width':3}).tolist()==[False]*5
    q={'family':'bounded_evidence','h':.5,'decay':1.}
    assert apply_policy(p,ids,q).tolist()==[False,True,False,False,True]
    prefix=apply_policy(p[:2],ids[:2],q)
    assert np.array_equal(prefix,apply_policy(p,ids,q)[:2])


def test_benign_alarm_time_is_not_equivalent_to_benign_onsets():
    c=cap([1,0,0]);result=audit(c,np.array([True,True,False]))
    assert result['benign_alarm_onsets']==0
    assert result['benign_confirmed_windows']==1
    assert result['benign_alarm_seconds']==2
    assert result['benign_alarm_fraction']==.5


def test_gap_can_start_new_event_even_if_adjacent_array_entries_active():
    c=cap([0,0],[0,4]);result=audit(c,np.array([True,True]))
    assert result['total_alarm_onsets']==2


def test_coverage_and_new_attack_onset_are_distinct():
    c=cap([0,1,1],runs=[{'id':0,'start':2000001,'end':6000000}])
    result=audit(c,np.array([True,True,True]))
    assert result['covered_runs']==1 and result['runs_with_new_onset']==0
    assert result['benign_alarm_fraction']==1.


def test_candidate_selection_records_validation_only_constraint():
    c=cap([0,0,1,1,1],runs=[{'id':0,'start':4000000,'end':10000000}])
    selected,grid=select_policies(c,np.array([.1,.2,.9,.9,.9]))
    assert len(selected)==5 and len(grid)>40
    assert all(r['validation_constraint_met'] for r in selected)
    assert all(r['validation']['capture']=='fixture' for r in selected)


def test_pcap_tcp_length_and_connect_metadata(tmp_path):
    # Real protocol layout fixture, including an MQTT CONNECT keepalive of 60 seconds.
    mqtt=b'\x10\x0c\x00\x04MQTT\x04\x02\x00\x3c\x00\x00'
    assert mqtt_keepalive(mqtt)==60
    tcp=struct.pack('!HHIIHHHH',12345,1883,0,0,0x5018,8192,0,0)+mqtt
    ip=bytes([0x45,0])+struct.pack('!H',20+len(tcp))+b'\x00\x00\x40\x00\x40\x06\x00\x00'+bytes([127,0,0,1])*2
    ethernet=b'\x00'*12+b'\x08\x00'+ip+tcp
    header=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1)
    record=struct.pack('<IIII',100,123456,len(ethernet),len(ethernet))+ethernet
    path=tmp_path/'capture.pcap';path.write_bytes(header+record)
    assert list(packets(path))==[(100123456,len(mqtt),60,12345,1883)]


def test_fragmented_connect_metadata_belongs_to_completing_segment():
    decoder=ConnectReassembly();flow=('local',1,1883)
    message=b'\x10\x0e\x00\x04MQTT\x04\x02\x00\x3c\x00\x02ab'
    assert decoder.feed(flow,100,0x18,message[:-2])==0
    assert decoder.feed(flow,100,0x18,message[:-2])==0  # retransmission
    assert decoder.feed(flow,114,0x18,message[-2:])==60
    assert decoder.feed(flow,114,0x18,message[-2:])==0


def test_sensitivity_windows_preserve_exact_boundaries_and_mixed_labels(tmp_path):
    path=tmp_path/'windows.csv'
    with path.open('w') as f:
        w=csv.writer(f);w.writerow(['timestamp','label','tcp_len','mqtt_kalive'])
        w.writerows([['0','legitimate',10,0],['0.999999','legitimate',20,0],
                     ['1.000000','slowite',30,60],['4.999999','slowite',40,60],
                     ['5.000000','legitimate',50,0],['10.000000','legitimate',60,0]])
    one=make_capture(path,1,1)['windows'];five=make_capture(path,1,5)['windows']
    assert len(one)==10 and one[0]['x'][0]==2 and one[1]['y']==1
    assert not one[2]['valid']
    assert len(five)==2 and five[0]['valid'] and five[0]['y']==-1
    assert five[1]['y']==0 and five[1]['x'][0]==1
