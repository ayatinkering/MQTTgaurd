"""Verify observed extended Wokwi serial and independently received MQTT records."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import joblib
import numpy as np
from train_pipeline import ROOT,make_capture
from verify_wokwi_serial import verify,ROW,SCENARIO
from research_core import apply_policy


def main():
    parser=argparse.ArgumentParser();parser.add_argument('serial_file',type=Path)
    parser.add_argument('--mqtt',type=Path,default=ROOT/'docs/evidence/research_mqtt.jsonl')
    args=parser.parse_args();text=args.serial_file.read_text()
    build_path=ROOT/'firmware/wokwi_research/build.json';build=json.loads(build_path.read_text())
    result=verify(text,build_path)
    saved=joblib.load(ROOT/'reports/experiment/model.joblib')
    cap=make_capture(ROOT/'data/raw/MQTTEEB-D_dataset_loop_3.csv',3)
    windows=cap['windows'];scores=np.full(len(windows),np.nan)
    valid=[i for i,w in enumerate(windows) if w['valid']]
    X=saved['imputer'].transform(np.array([windows[i]['x'] for i in valid])).astype(np.float32)
    scores[valid]=saved['model'].predict_proba(X)[:,1]
    clips=json.loads((ROOT/'docs/results/manifest.json').read_text())['clips']
    evidence_row=re.compile(r'EVIDENCE window=(\d+) value=([\d.]+) confirmed=(\d+) events=(\d+) accepted=(\d+)')
    h=build['policy']['h'];decay=build['policy']['decay']
    last=None;value=0.;active=False;events=0;expected=None;count=0
    for line in text.splitlines():
        if SCENARIO.search(line):last=None;value=0.;active=False;events=0;expected=None
        m=ROW.search(line)
        if m:
            kind,idx,pred,*_=m.groups();idx=int(idx);pred=int(pred)
            score=scores[idx] if kind=='MODEL' else (np.nan if pred<0 else float(pred))
            accepted=last is None or idx>last
            if accepted:
                if last is not None and idx!=last+1:value=0.;active=False
                last=idx
                value=min(h,max(0.,decay*value+score-.5)) if np.isfinite(score) else 0.
                confirmed=value>=h;events+=int(confirmed and not active);active=confirmed
            expected=(idx,value,int(active),events,int(accepted));continue
        m=evidence_row.search(line)
        if m:
            assert expected is not None,'Evidence row without paired observed model row'
            idx,v,a,e,accepted=m.groups()
            assert int(idx)==expected[0] and abs(float(v)-expected[1])<5.1e-9
            assert list(map(int,[a,e,accepted]))==list(expected[2:]),(m.groups(),expected)
            count+=1;expected=None
    assert count==result['observed_model_rows']+result['observed_scripted_rows']
    mqtt_count=0
    for line in args.mqtt.read_text().splitlines():
        row=json.loads(line)['payload']
        if row['mode']!='ACTUAL_MODEL':continue
        clip=clips[row['clip']];start=clip['start_window'];ids=np.arange(start,start+clip['count'])
        policy_active=apply_policy(scores[ids],ids,build['policy']);state=0.;history=[]
        for score in scores[ids]:
            state=min(h,max(0.,decay*state+score-.5)) if np.isfinite(score) else 0.;history.append(state)
        j=row['window']-start;assert 0<=j<len(ids)
        expected_prediction=-1 if not np.isfinite(scores[row['window']]) else int(scores[row['window']]>.5)
        assert row['prediction']==expected_prediction
        assert abs(row['evidence']-history[j])<=5.1e-7
        assert row['evidence_confirmed']==int(policy_active[j])
        starts=policy_active & ~np.r_[False,policy_active[:-1]]
        assert row['evidence_events']==int(starts[:j+1].sum())
        predictions=np.where(np.isfinite(scores[ids]),scores[ids]>.5,-1)
        for k in [1,2,3]:
            streak=0;event_count=0;was=False
            for p in predictions[:j+1]:
                streak=min(streak+1,k) if p==1 else 0
                now=streak>=k;event_count+=int(now and not was);was=now
            assert row['streak'][k-1]==streak and row['confirmed'][k-1]==int(was) and row['events'][k-1]==event_count
        mqtt_count+=1
    assert mqtt_count>0
    result.update({'evidence_policy':build['policy'],'observed_evidence_rows':count,
        'evidence_state_disagreements':0,'independently_received_mqtt_model_rows':mqtt_count,
        'mqtt_prediction_state_disagreements':0,'mqtt_sha256':hashlib.sha256(args.mqtt.read_bytes()).hexdigest(),
        'scope':'Actual extended Wokwi replay and independent MQTT reception; simulated timing, no physical measurements'})
    path=ROOT/'docs/evidence/research_target_verification.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
