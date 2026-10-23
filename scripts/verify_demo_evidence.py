"""Compare independently received Wokwi messages with the frozen host model.

Run train_pipeline.py first. This does not claim full simulated-target coverage:
it verifies only the actual received sample preserved in docs/evidence.
"""
from pathlib import Path
import json,argparse
import joblib
from train_pipeline import ROOT,make_capture,predict_capture,confirm

def main():
    artifact=ROOT/'reports/experiment/model.joblib'
    if not artifact.exists(): raise SystemExit('Run .venv/bin/python scripts/train_pipeline.py first.')
    saved=joblib.load(artifact)
    cap=make_capture(ROOT/'data/raw/MQTTEEB-D_dataset_loop_3.csv',3)
    prediction,_=predict_capture(cap,saved['imputer'],saved['model'])
    manifest=json.loads((ROOT/'docs/results/manifest.json').read_text()); clips=manifest['clips']
    parser=argparse.ArgumentParser();parser.add_argument('--file',type=Path,default=ROOT/'docs/evidence/mqtt_received.jsonl');parser.add_argument('--output',type=Path,default=ROOT/'docs/evidence/verification.json');args=parser.parse_args()
    evidence=args.file; checked=0
    for line in evidence.read_text().splitlines():
        p=json.loads(line)['payload']
        if p['mode']!='ACTUAL_MODEL':continue
        clip=clips[p['clip']];start=clip['start_window'];index=p['window'];offset=index-start
        assert 0<=offset<clip['count']
        assert p['prediction']==prediction[index],(index,p['prediction'],prediction[index])
        expected=[];totals=[];streak=[]
        for k in [1,2,3]:
            states,events=confirm(prediction[start:index+1],k);expected.append(int(states[-1]));totals.append(len(events))
            n=0
            for value in reversed(prediction[start:index+1]):
                if value!=1:break
                n+=1
            streak.append(min(n,k))
        assert p['confirmed']==expected,(index,p['confirmed'],expected)
        assert p['events']==totals,(index,p['events'],totals)
        assert p['streak']==streak
        checked+=1
    assert checked>0,'No actual-model messages checked'
    result={'received_actual_model_messages_checked':checked,'prediction_disagreements':0,'confirmation_disagreements':0,'scope':'Only checked-in received sample; host parity separately covers all recorded valid windows and boundary cases.'}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
