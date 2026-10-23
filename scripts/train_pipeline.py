"""Reproducible capture-separated MQTTGuard experiment and verified C++ export."""
from pathlib import Path
import csv, json, hashlib, ctypes, subprocess, time, platform
from decimal import Decimal
from collections import Counter
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import f1_score, confusion_matrix, precision_recall_fscore_support
import joblib

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['count', 'mean_tcp_len', 'mean_interarrival_s', 'mean_mqtt_kalive']
TARGETS = {'legitimate', 'slowite'}

def number(s):
    try:
        v=float(s)
        return v if np.isfinite(v) else np.nan
    except (ValueError, TypeError): return np.nan

def make_capture(path, capture):
    bins={}; runs=[]; previous=None; current=None; origin=None; last=None
    with path.open() as f:
        for row in csv.DictReader(f):
            ts=int(Decimal(row['timestamp'])*1000000)
            if last is not None and ts<last: raise ValueError('Unordered timestamp')
            last=ts
            if origin is None: origin=ts
            label=row['label'].strip().lower()
            if label!=previous:
                current=None
                if label=='slowite':
                    current=len(runs); runs.append({'id':current,'start':ts,'end':ts})
            if current is not None: runs[current]['end']=ts
            previous=label
            j=(ts-origin)//2000000
            b=bins.setdefault(j, {'times':[], 'lengths':[], 'keepalive':[], 'labels':Counter(), 'runs':set()})
            b['times'].append(ts); b['lengths'].append(number(row['tcp_len'])); b['keepalive'].append(number(row['mqtt_kalive'])); b['labels'][label]+=1
            if current is not None: b['runs'].add(current)
    complete=(last-origin)//2000000
    windows=[]
    def mean(a):
        a=np.asarray(a); return float(np.nanmean(a)) if np.isfinite(a).any() else np.nan
    for j in range(complete):
        b=bins.get(j)
        if not b:
            windows.append({'id':j,'end':origin+(j+1)*2000000,'valid':False,'x':[np.nan]*4,'y':-1,'labels':{},'runs':set()}); continue
        n=len(b['times']); labels=set(b['labels'])
        x=[n,mean(b['lengths']), (b['times'][-1]-b['times'][0])/1e6/(n-1) if n>1 else np.nan,mean(b['keepalive'])]
        windows.append({'id':j,'end':origin+(j+1)*2000000,'valid':True,'x':x,'y':0 if labels=={'legitimate'} else 1 if labels=={'slowite'} else -1,'labels':dict(b['labels']),'runs':b['runs']})
    return {'id':capture,'origin':origin,'windows':windows,'runs':runs,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def cohort(captures, ids):
    ws=[w for i in ids for w in captures[i]['windows'] if w['valid'] and w['y']>=0]
    return np.array([w['x'] for w in ws]), np.array([w['y'] for w in ws])

def fit(captures, train, val):
    X,y=cohort(captures,train); V,vy=cohort(captures,[val])
    imp=SimpleImputer(strategy='median',keep_empty_features=True).fit(X)
    if np.isnan(X).all(axis=0).any(): raise ValueError('All-missing training feature')
    rawX=X.copy()
    X=imp.transform(X).astype(np.float32); V=imp.transform(V).astype(np.float32)
    candidates=[]
    for trees in [8,16]:
        for depth in [3,5]:
            pipeline=Pipeline([('imputer',SimpleImputer(strategy='median',keep_empty_features=True)),('float32',FunctionTransformer(np.float32)),('forest',RandomForestClassifier(n_estimators=trees,max_depth=depth,min_samples_leaf=2,class_weight='balanced',random_state=42,n_jobs=1))]).fit(rawX,y)
            m=pipeline.named_steps['forest']
            score=float(f1_score(vy,m.predict(V),zero_division=0)); nodes=sum(e.tree_.node_count for e in m.estimators_)
            candidates.append((score,-nodes,-trees,-depth,m))
    best=max(candidates,key=lambda c:c[:4]); model=best[-1]
    thresholds=np.unique(np.quantile(X[:,0],np.linspace(0,1,101)))
    rate=max(((float(f1_score(vy, ((V[:,0]>=t) if direction==1 else (V[:,0]<=t)).astype(int),zero_division=0)),float(t),direction) for t in thresholds for direction in [-1,1]),key=lambda c:(c[0],-c[1],c[2]))
    return imp, model, {'threshold':rate[1],'direction':rate[2],'validation_f1':rate[0]}, [{'f1':a,'nodes':-b,'trees':-c,'depth':-d} for a,b,c,d,_ in candidates]

def confirm(predictions, k):
    streak=0; active=False; states=[]; events=[]
    for i,p in enumerate(predictions):
        streak=min(streak+1,k) if p==1 else 0
        confirmed=streak>=k
        if confirmed and not active: events.append(i)
        states.append(confirmed); active=confirmed
    return states,events

def evaluate(cap, predictions, name):
    ws=cap['windows']; pure=np.array([w['y'] for w in ws]); pred=np.array(predictions)
    mask=pure>=0
    cm=confusion_matrix(pure[mask],pred[mask],labels=[0,1]).tolist()
    p,r,f,_=precision_recall_fscore_support(pure[mask],pred[mask],average='binary',zero_division=0)
    tn,fp=cm[0]; result=[]
    for k in [1,2,3]:
        states,events=confirm(predictions,k); detected={}; late=set(); false=0; ambiguous=0
        for i in events:
            evidence=ws[i-k+1:i+1]; t=ws[i]['end']
            if len(evidence)==k and all(w['y']==0 for w in evidence): false+=1; continue
            attributable=[run for run in cap['runs'] if all(run['id'] in w['runs'] and set(w['labels'])<=TARGETS for w in evidence)]
            hits=[run for run in attributable if run['start']<=t<=run['end']]
            if hits:
                for run in hits: detected.setdefault(run['id'],(t-run['start'])/1e6)
            else:
                ambiguous+=1
                for run in attributable:
                    if t>run['end']: late.add(run['id'])
        lat=list(detected.values()); benign=int(sum(pure==0)); eligible=benign*2/3600
        result.append({'capture':cap['id'],'model':name,'k':k,'classification':{'confusion_matrix':cm,'precision':float(p),'recall':float(r),'f1':float(f),'fpr':fp/(tn+fp) if tn+fp else None},'false_events':false,'benign_confirmed_windows':sum(bool(s) and w['y']==0 for s,w in zip(states,ws)),'benign_hours':eligible,'false_events_per_benign_hour':false/eligible if eligible else None,'total_events':len(events),'ambiguous_or_out_of_scope_events':ambiguous,'label_runs':len(cap['runs']),'detected_runs':len(detected),'label_run_recall':len(detected)/len(cap['runs']) if cap['runs'] else None,'missed_runs':len(cap['runs'])-len(detected),'detected_run_ids':sorted(detected),'missed_run_ids':[r['id'] for r in cap['runs'] if r['id'] not in detected],'detected_run_latency_s':{str(key):value for key,value in detected.items()},'late_runs':len(late-set(detected)),'median_latency_s':float(np.median(lat)) if lat else None,'mean_latency_s':float(np.mean(lat)) if lat else None,'coverage':{'complete_windows':len(ws),'empty_windows':sum(not w['valid'] for w in ws),'pure_benign':benign,'pure_slowite':int(sum(pure==1)),'mixed_unknown_other':sum(w['valid'] and w['y']<0 for w in ws),'adjacent_benign_pairs':sum(a['y']==0 and b['y']==0 for a,b in zip(ws,ws[1:]))}})
    return result

def predict_capture(cap, imp, model, rate=None):
    ws=cap['windows']; valid=[i for i,w in enumerate(ws) if w['valid']]; predictions=[-1]*len(ws)
    X=imp.transform(np.array([ws[i]['x'] for i in valid])).astype(np.float32)
    start=time.perf_counter()
    ys=model.predict(X) if rate is None else ((X[:,0]>=rate['threshold']) if rate['direction']==1 else (X[:,0]<=rate['threshold'])).astype(int)
    elapsed=time.perf_counter()-start
    for i,y in zip(valid,ys): predictions[i]=int(y)
    return predictions, elapsed/max(len(valid),1)*1e6

def export_model(model, imputer, path):
    lines=['#pragma once','#include <stdint.h>','#include <math.h>','// Generated from the frozen sklearn model; soft voting, no quantization.', 'static const float MQTTGUARD_MEDIANS[4] = {'+', '.join(float(v).hex()+'f' for v in imputer.statistics_)+'};','static inline double mqttguard_probability(const float *x) {','double sum = 0.0;']
    for e in model.estimators_:
        t=e.tree_
        def node(i,indent=''):
            if t.children_left[i]<0:
                a=t.value[i][0]; prob=float(a[1]/sum(a)); lines.append(indent+'sum += '+prob.hex()+';')
            else:
                lines.append(indent+f'if ((double)x[{t.feature[i]}] <= {float(t.threshold[i]).hex()}) {{');node(t.children_left[i],indent+' ');lines.append(indent+'} else {');node(t.children_right[i],indent+' ');lines.append(indent+'}')
        node(0)
    lines+=['return sum / '+str(len(model.estimators_))+'.0;','}','static inline int mqttguard_predict(const float *x) { return mqttguard_probability(x) > 0.5 ? 1 : 0; }']
    path.write_text('\n'.join(lines)+'\n')

def verify_export(model, imp, captures, out):
    cpp=out/'verify.cpp'; lib=out/'verify.so'
    cpp.write_text('#include "'+str(ROOT/'firmware/mqttguard/mqttguard_model.h')+'"\nextern "C" double probability(const float *x) { return mqttguard_probability(x); }\n')
    subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(lib)],check=True)
    dll=ctypes.CDLL(str(lib)); fn=dll.probability; fn.argtypes=[ctypes.POINTER(ctypes.c_float)];fn.restype=ctypes.c_double
    X=np.array([w['x'] for cap in captures.values() for w in cap['windows'] if w['valid']])
    X=imp.transform(X).astype(np.float32)
    rng=np.random.default_rng(42); extra=[]
    for e in model.estimators_:
        for feature,t in zip(e.tree_.feature,e.tree_.threshold):
            if feature<0: continue
            for v in [np.float32(t),np.nextafter(np.float32(t),np.float32(-np.inf)),np.nextafter(np.float32(t),np.float32(np.inf))]:
                row=X[rng.integers(len(X))].copy();row[feature]=v;extra.append(row)
    X=np.concatenate([X,np.array(extra)])
    expected=model.predict_proba(X)[:,1]; actual=np.array([fn(row.ctypes.data_as(ctypes.POINTER(ctypes.c_float))) for row in X])
    disagreement=int(np.sum((actual>.5)!=(expected>.5))); error=float(np.max(np.abs(actual-expected)))
    assert disagreement==0 and error<=1e-6,(disagreement,error)
    return {'inputs':len(X),'threshold_boundary_inputs':len(extra),'label_disagreements':disagreement,'max_probability_error':error}

def main():
    out=ROOT/'reports/experiment'; out.mkdir(parents=True,exist_ok=True)
    fw=ROOT/'firmware/mqttguard';fw.mkdir(parents=True,exist_ok=True)
    results_dir=ROOT/'docs/results';results_dir.mkdir(parents=True,exist_ok=True)
    captures={i:make_capture(ROOT/f'data/raw/MQTTEEB-D_dataset_loop_{i}.csv',i) for i in range(1,5)}
    for cap in captures.values():
        with (out/f'capture_{cap["id"]}_windows.csv').open('w',newline='') as stream:
            writer=csv.writer(stream)
            writer.writerow(['capture','window_id','end_epoch_us','valid','scoring_label','label_composition']+FEATURES)
            for w in cap['windows']:
                writer.writerow([cap['id'],w['id'],w['end'],w['valid'],w['y'],json.dumps(w['labels'],sort_keys=True)]+w['x'])
    (out/'observed_label_runs.json').write_text(json.dumps({i:c['runs'] for i,c in captures.items()},indent=2)+'\n')
    imp,model,rate,candidates=fit(captures,[1,2],3)
    export_model(model,imp,fw/'mqttguard_model.h'); parity=verify_export(model,imp,captures,out)
    results=[]; predictions={}
    for name,baseline in [('RF',None),('rate',rate)]:
        pred,micros=predict_capture(captures[4],imp,model,baseline); results+=evaluate(captures[4],pred,name)
        if name=='RF': predictions[4]=pred; rf_micros=micros
        np.savez_compressed(out/f'primary_{name}.npz',prediction=pred,labels=[w['y'] for w in captures[4]['windows']],window_id=[w['id'] for w in captures[4]['windows']])
    folds=[]
    for test in range(1,5):
        val=test%4+1;train=[i for i in range(1,5) if i not in [test,val]]
        fi,fm,fr,_=fit(captures,train,val)
        for name,baseline in [('RF',None),('rate',fr)]:
            pred,_=predict_capture(captures[test],fi,fm,baseline)
            rows=evaluate(captures[test],pred,name)
            np.savez_compressed(out/f'fold_{test}_{name}.npz',prediction=pred,labels=[w['y'] for w in captures[test]['windows']],window_id=[w['id'] for w in captures[test]['windows']])
            for row in rows: row['train_captures']=train;row['validation_capture']=val
            folds+=rows
    # Ideal pure-label opportunity diagnostic (not trained-model performance).
    ideal=[r for cap in captures.values() for r in evaluate(cap,[w['y'] if w['y']>=0 else -1 for w in cap['windows']],'ideal_pure_labels')]
    # Source-trace clips: fixed first benign, first slowite, and first idle transition in validation capture.
    cap=captures[3];pred,_=predict_capture(cap,imp,model); clips=[]
    for name,condition in [('BENIGN TRACE',lambda w:w['y']==0),('SLOWITE TRACE',lambda w:w['y']==1),('GAP TRACE',lambda w:not w['valid'])]:
        start=next(i for i,w in enumerate(cap['windows']) if condition(w));start=max(0,start-2);selected=cap['windows'][start:start+18]
        clips.append({'name':name,'capture':3,'start_window':start,'windows':selected})
    lines=['#pragma once','struct ReplayWindow { uint32_t id; bool valid; uint8_t missing; float x[4]; };','struct ReplayClip { const char *name; const ReplayWindow *rows; uint16_t count; };']
    for c,clip in enumerate(clips):
        lines.append(f'static const ReplayWindow CLIP_{c}[] = {{')
        for w in clip['windows']:
            missing=sum(1<<j for j,v in enumerate(w['x']) if not np.isfinite(v));vals=','.join((float(v).hex()+'f') if np.isfinite(v) else '0.0f' for v in w['x'])
            lines.append('{'+f'{w["id"]},{str(w["valid"]).lower()},{missing},'+'{'+vals+'}},')
        lines.append('};')
    lines.append('static const ReplayClip CLIPS[] = {'+','.join('{"'+c['name']+'",CLIP_'+str(i)+','+str(len(c['windows']))+'}' for i,c in enumerate(clips))+'};')
    lines.append('static const uint8_t CLIP_COUNT = '+str(len(clips))+';')
    (fw/'replay_data.h').write_text('\n'.join(lines)+'\n')
    manifest={'dataset_sha256':{i:c['sha256'] for i,c in captures.items()},'features':FEATURES,'window_s':2,'seed':42,'split':{'train':[1,2],'validation':3,'test':4},'parameters':model.get_params(),'imputation':imp.statistics_.tolist(),'candidates':candidates,'rate_baseline':rate,'export_parity':parity,'python':platform.python_version(),'sklearn':sklearn.__version__,'clips':[{'name':c['name'],'capture':3,'start_window':c['start_window'],'count':len(c['windows'])} for c in clips],'batch_inference_us_per_valid_window':rf_micros,'timing_note':'Laptop batch timing, not physical ESP32 inference.'}
    for name,value in [('manifest',manifest),('primary',results),('robustness',folds),('ideal_diagnostic',ideal)]:
        (results_dir/(name+'.json')).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    joblib.dump({'imputer':imp,'model':model},out/'model.joblib')
    with (out/'validation_predictions.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['window_id','label','prediction']);writer.writerows((w['id'],w['y'],p) for w,p in zip(cap['windows'],pred))
    print(json.dumps({'selected':model.get_params(),'parity':parity,'primary_RF':results[:3]},indent=2))

if __name__=='__main__': main()
