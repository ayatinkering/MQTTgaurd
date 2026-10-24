"""Verify actually observed Wokwi serial traces; does not manufacture target outputs."""
import argparse,json,re,hashlib
from pathlib import Path
import joblib,numpy as np
from train_pipeline import ROOT,make_capture,predict_capture,confirm

ROW=re.compile(r'(MODEL|TEST) window=(\d+) pred=(-?\d+) probability=(-?[\d.]+) accepted=(\d+) streak=(\d+)/(\d+)/(\d+) confirmed=(\d+)/(\d+)/(\d+) events=(\d+)/(\d+)/(\d+) inference_us_simulated=(\d+)')
SCENARIO=re.compile(r'SCENARIO mode=(ACTUAL_MODEL|SCRIPTED_TEST).*?clip=([^\n]+?) capture=3;')

def verify(text, build_path=None):
    saved=joblib.load(ROOT/'reports/experiment/model.joblib')
    cap=make_capture(ROOT/'data/raw/MQTTEEB-D_dataset_loop_3.csv',3)
    preds,_=predict_capture(cap,saved['imputer'],saved['model'])
    manifest=json.loads((ROOT/'docs/results/manifest.json').read_text());clips={c['name']:c for c in manifest['clips']}
    build=json.loads((build_path or ROOT/'firmware/wokwi/build.json').read_text())['build_id']
    assert 'BUILD='+build in text,'Observed firmware build does not match local bundle'
    current=None;counter=[0,0,0];active=[False]*3;events=[0]*3;last=None;counts={};timings=[];models=0;tests=0
    scenarios=[]; fault=False;during_fault=0;failed=False;recovered=False;fault_start_index=None
    for line in text.splitlines():
        if 'FAULT_BEGIN simulated_ms=' in line:fault=True;fault_start_index=models
        if 'MQTT_CONNECT_FAILED' in line and 'fault=1' in line:failed=True
        if 'FAULT_END simulated_ms=' in line:fault=False
        if 'MQTT_CONNECTED' in line and 'fault=0' in line and fault_start_index is not None and not fault:recovered=True
        match=SCENARIO.search(line)
        if match:
            mode,name=match.groups();current=clips[name];counter=[0,0,0];active=[False]*3;events=[0]*3;last=None
            scenarios.append({'mode':mode,'clip':name,'ids':[]});continue
        match=ROW.search(line)
        if not match:continue
        assert current is not None,'Record without scenario origin'
        kind,idx,p,prob,accepted,*tail=match.groups();idx=int(idx);p=int(p);prob=float(prob);accepted=int(accepted);values=list(map(int,tail))
        if kind=='MODEL':
            assert current['start_window']<=idx<current['start_window']+current['count']
            assert p==preds[idx],('Prediction mismatch',idx,p,preds[idx])
            w=cap['windows'][idx]
            if w['valid']:
                X=saved['imputer'].transform(np.array([w['x']])).astype(np.float32)
                expected=saved['model'].predict_proba(X)[0,1]
                assert abs(prob-expected)<=0.00000051,(idx,prob,expected)
                timings.append(values[9])
            else:assert prob==-1.0
            models+=1;scenarios[-1]['ids'].append(idx);counts[current['name']]=counts.get(current['name'],0)+1
            if fault:during_fault+=1
        else:tests+=1
        accept=last is None or idx>last
        assert accepted==int(accept)
        if accept:
            if last is not None and idx!=last+1:counter=[0]*3;active=[False]*3
            for k in range(1,4):
                counter[k-1]=min(counter[k-1]+1,k) if p==1 else 0
                nxt=counter[k-1]>=k
                events[k-1]+=int(nxt and not active[k-1]);active[k-1]=nxt
            last=idx
        assert values[:3]==counter,(idx,'streak',values[:3],counter)
        assert values[3:6]==list(map(int,active)),(idx,'confirmation')
        assert values[6:9]==events,(idx,'events',values[6:9],events)
    complete=[s['clip'] for s in scenarios if s['mode']=='ACTUAL_MODEL' and s['ids']==list(range(clips[s['clip']]['start_window'],clips[s['clip']]['start_window']+clips[s['clip']]['count']))]
    resources=[]
    for line in text.splitlines():
        if 'METRICS build=' in line:resources.append(dict(re.findall(r'(\w+)=([^\s]+)',line[line.index('METRICS'):])) )
    return {'build_id':build,'observed_model_rows':models,'observed_scripted_rows':tests,'complete_clip_passes':complete,'model_rows_by_clip':counts,'prediction_or_state_disagreements':0,'simulated_inference_us':{'count':len(timings),'min':min(timings) if timings else None,'median':float(np.median(timings)) if timings else None,'p95':float(np.percentile(timings,95)) if timings else None,'max':max(timings) if timings else None},'controlled_failure':{'failed_connection_observed':failed,'model_rows_processed_while_fault_active':during_fault,'reconnected_after_recovery':recovered},'resource_snapshots':resources,'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'scope':'Observed Wokwi replay only; simulated timing, not physical hardware. Controlled target-resolution fault, not an outage induced at the public broker.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('serial_file',type=Path);p.add_argument('--output',type=Path,default=ROOT/'docs/evidence/target_verification.json');a=p.parse_args()
    result=verify(a.serial_file.read_text());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
