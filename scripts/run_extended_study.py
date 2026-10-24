"""Execute the fixed extended protocol; archive all results including failures."""
import csv
import hashlib
import json
from pathlib import Path
import argparse
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from train_pipeline import ROOT, FEATURES, make_capture
from research_core import as_arrays, apply_policy, audit, select_policies, key
from mqttset_data import download, capture_from_packets, slice_capture

OUT=ROOT/'docs/research'
CACHE=ROOT/'reports/research'


def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def fit_model(caps,training,validation,features,tag):
    path=CACHE/(tag+'.joblib')
    fingerprint=hashlib.sha256(json.dumps({'features':features,'grid':[[8,16],[3,5]],'seed':42}).encode())
    for cap in training+validation:
        fingerprint.update(cap['name'].encode());fingerprint.update(cap['X'][:,features].tobytes());fingerprint.update(cap['y'].tobytes())
    signature=fingerprint.hexdigest()
    if path.exists():
        cached=joblib.load(path)
        if cached.get('input_signature')==signature:return cached
    X=np.concatenate([c['X'][c['y']>=0][:,features] for c in training])
    y=np.concatenate([c['y'][c['y']>=0] for c in training])
    V=np.concatenate([c['X'][c['y']>=0][:,features] for c in validation])
    vy=np.concatenate([c['y'][c['y']>=0] for c in validation])
    imputer=SimpleImputer(strategy='median',keep_empty_features=True).fit(X)
    X=imputer.transform(X).astype(np.float32);V=imputer.transform(V).astype(np.float32)
    candidates=[]
    for trees in [8,16]:
        for depth in [3,5]:
            m=RandomForestClassifier(n_estimators=trees,max_depth=depth,min_samples_leaf=2,
                                     class_weight='balanced',random_state=42,n_jobs=1).fit(X,y)
            score=float(f1_score(vy,m.predict(V),zero_division=0));nodes=sum(e.tree_.node_count for e in m.estimators_)
            candidates.append((score,-nodes,-trees,-depth,m))
    best=max(candidates,key=lambda r:r[:4])
    model={'imputer':imputer,'model':best[-1],'features':features,'tag':tag,'input_signature':signature,
           'training_names':[c['name'] for c in training],'validation_names':[c['name'] for c in validation],
           'candidates':[{'f1':a,'nodes':-b,'trees':-c,'depth':-d} for a,b,c,d,_ in candidates]}
    joblib.dump(model,path);return model


def scores_for(cap,model):
    valid=cap['valid'];scores=np.full(len(valid),np.nan)
    if valid.any():
        X=model['imputer'].transform(cap['X'][valid][:,model['features']]).astype(np.float32)
        scores[valid]=model['model'].predict_proba(X)[:,1]
    return scores


def classifier(cap,scores):
    mask=cap['y']>=0;y=cap['y'][mask];p=(scores[mask]>.5).astype(int)
    return {'confusion_matrix':confusion_matrix(y,p,labels=[0,1]).tolist(),
            'accuracy':float(accuracy_score(y,p)),
            'precision':float(precision_score(y,p,zero_division=0)),
            'recall':float(recall_score(y,p,zero_division=0)),
            'f1':float(f1_score(y,p,zero_division=0)),'scored_windows':int(mask.sum())}


def save_scores(cap,scores,tag):
    np.savez_compressed(CACHE/(tag+'.npz'),ids=cap['ids'],end_us=cap['end_us'],
                        labels=cap['y'],scores=scores,valid=cap['valid'])


def evaluate_policies(cap,scores,selection,model_tag):
    chosen=[({'family':'consecutive','k':k},None) for k in [1,2,3]]
    chosen += [(r['policy'],r) for r in selection]
    chosen += [({'family':'always_positive'},None)]
    results=[]
    for policy,selected in chosen:
        result=audit(cap,apply_policy(scores,cap['ids'],policy),policy)
        result.update({'policy':policy,'model_tag':model_tag})
        if selected:
            result.update({'selection_validation_capture':selected['validation']['capture'],
                           'selection_validation_coverage_floor':selected['validation_coverage_floor'],
                           'selection_constraint_met':selected['validation_constraint_met']})
        results.append(result)
    ideal=np.where(cap['y']==1,1.,np.where(cap['y']==0,0.,np.nan))
    result=audit(cap,apply_policy(ideal,cap['ids'],{'family':'threshold','threshold':.5}))
    result.update({'policy':{'family':'ideal_pure_labels'},'model_tag':'diagnostic_not_a_trained_model'})
    return results+[result]


def join_caps(caps,name):
    # Preserve boundaries as a missing input, preventing filters from joining separate files.
    arrays={k:[] for k in ['ids','end_us','X','y','valid']};runs=[];offset=0;time_offset=0
    for cap in caps:
        shifted=cap['end_us']-cap['end_us'][0]+time_offset
        for k in arrays:
            if k=='ids':values=np.arange(len(cap['ids']))+offset
            elif k=='end_us':values=shifted
            else:values=cap[k]
            arrays[k].append(values)
        for run in cap['runs']:
            runs.append({'id':len(runs),'start':int(run['start']-cap['end_us'][0]+time_offset),
                         'end':int(run['end']-cap['end_us'][0]+time_offset)})
        # Gap is encoded in IDs; no synthetic legitimate/attack samples are added.
        offset+=len(cap['ids'])+2;time_offset=int(shifted[-1]+10e6)
    return {'name':name,'seconds':caps[0]['seconds'],'runs':runs,
            **{k:np.concatenate(v) for k,v in arrays.items()}}


def original_study():
    caps={i:as_arrays(make_capture(ROOT/f'data/raw/MQTTEEB-D_dataset_loop_{i}.csv',i),2) for i in range(1,5)}
    definitions=[('primary',[1,2],3,4)]+[(f'fold_{i}',[j for j in range(1,5) if j not in [i,i%4+1]],i%4+1,i) for i in range(1,5)]
    results=[];frontiers=[];test_frontiers=[];primary=None
    for tag,train,val,test in definitions:
        model=fit_model(caps,[caps[i] for i in train],[caps[val]],[0,1,2,3],tag)
        validation_scores=scores_for(caps[val],model)
        selected,grid=select_policies(caps[val],validation_scores)
        test_scores=scores_for(caps[test],model);save_scores(caps[test],test_scores,tag+'_test')
        metrics=evaluate_policies(caps[test],test_scores,selected,tag)
        for row in metrics:row.update({'split':tag,'train_captures':train,'validation_capture':val,
                                       'test_capture':test,'base_classifier':classifier(caps[test],test_scores)})
        results+=metrics;frontiers.append({'split':tag,'selected':selected,'validation_grid':grid})
        test_frontiers.append({'split':tag,'scope':'Descriptive test frontier; never used for parameter selection',
            'candidates':[{'policy':g['policy'],'test':audit(caps[test],apply_policy(test_scores,caps[test]['ids'],g['policy']),g['policy'])} for g in grid]})
        if tag=='primary':primary=(model,selected)
        print('Original comparison:',tag,flush=True)
    dump(OUT/'comparisons.json',results);dump(OUT/'validation_frontiers.json',frontiers)
    dump(OUT/'test_frontiers.json',test_frontiers)
    return primary


def sensitivity():
    featuresets={'all4':[0,1,2,3],'no_keepalive':[0,1,2],'count_length':[0,1],
                 'no_count':[1,2,3],'no_length':[0,2,3],'no_interarrival':[0,1,3]}
    rows=[]
    for seconds in [1,2,5]:
        caps={i:as_arrays(make_capture(ROOT/f'data/raw/MQTTEEB-D_dataset_loop_{i}.csv',i,seconds),seconds) for i in range(1,5)}
        for label,indices in featuresets.items():
            tag=f'sensitivity_{seconds}s_{label}'
            model=fit_model(caps,[caps[1],caps[2]],[caps[3]],indices,tag)
            selected,_=select_policies(caps[3],scores_for(caps[3],model))
            proposed=next(s for s in selected if s['policy']['family']=='bounded_evidence')
            scores=scores_for(caps[4],model)
            k2={'family':'consecutive','k':2}
            rows.append({'seconds':seconds,'feature_set':label,'features':[FEATURES[i] for i in indices],
                         'base_classifier':classifier(caps[4],scores),
                         'trees':model['model'].n_estimators,'depth':model['model'].max_depth,
                         'k2':audit(caps[4],apply_policy(scores,caps[4]['ids'],k2),k2),
                         'proposed':audit(caps[4],apply_policy(scores,caps[4]['ids'],proposed['policy'])),
                         'proposed_parameters':proposed['policy'],
                         'status':'Exploratory on previously inspected captures; no best-test selection'})
            print('Sensitivity:',tag,flush=True)
    dump(OUT/'sensitivity.json',rows)


def external_study(primary):
    dest=download();caps=[];audits=[]
    for name,label in [('capture_1w.pcap',0),('slowite.pcap',1),('capture_malariaDoS.pcap',1)]:
        cache=CACHE/(name+'.joblib')
        cap=joblib.load(cache) if cache.exists() else None
        if cap is None or cap['extraction'].get('parser_version')!=2:
            cap=capture_from_packets(dest/name,name,label)
            joblib.dump(cap,cache)
        cap['name']=name
        compatible=len(cap['ids'])>0
        audits.append({'file':name,**cap['extraction'],'complete_windows':len(cap['ids']),
                       'temporal_compatibility':compatible,
                       'exclusion_reason':None if compatible else 'Recorded span shorter than one complete two-second window'})
        if compatible:caps.append(cap)
        print('External extraction:',name,cap['extraction'],flush=True)
    model,selected=primary;results=[]
    for cap in caps:
        scores=scores_for(cap,model);save_scores(cap,scores,'external_direct_'+cap['name'])
        for row in evaluate_policies(cap,scores,selected,'MQTTEEB_primary_direct_transfer'):
            row['evaluation']='direct_transfer';results.append(row)
    training=[slice_capture(c,0,.4,c['name']+'_train') for c in caps]
    validation=[slice_capture(c,.4,.6,c['name']+'_validation') for c in caps]
    testing=[slice_capture(c,.6,1,c['name']+'_test') for c in caps]
    adapted=fit_model({},training,validation,[0,1,2,3],'mqttset_adapted')
    joined=join_caps(validation,'mqttset_validation_separate_files')
    selection,grid=select_policies(joined,scores_for(joined,adapted))
    for cap in testing:
        scores=scores_for(cap,adapted);save_scores(cap,scores,'external_adapted_'+cap['name'])
        for row in evaluate_policies(cap,scores,selection,'MQTTset_adapted_chronological'):
            row['evaluation']='within_external_dataset_adaptation';results.append(row)
    alltest=join_caps(testing,'mqttset_adapted_test_scenarios')
    dump(OUT/'external_results.json',{'schema_audit':audits,
         'results':results,'adapted_scenario_classification':classifier(alltest,scores_for(alltest,adapted)),
         'adaptation_validation_selection':selection,'adaptation_validation_grid':grid,
         'label_limit':'Supplementary DoS scenario, not independent SlowITe validation; attack-file scenario scores are not verified per-packet attack recall',
         'split':'Per original file 0-40% train, 40-60% validation, 60-100% test, five-second guards'})
    return adapted,selection


def stress_study(primary,adapted):
    dest=ROOT/'data/benign_stress'
    if not (dest/'sessions.json').exists():
        import gzip,shutil
        dest.mkdir(parents=True,exist_ok=True)
        manifest=json.loads((ROOT/'docs/evidence/benign_workload_sessions.json').read_text())
        with gzip.open(ROOT/'docs/evidence/benign_workloads.pcap.gz','rb') as source,(dest/'legitimate_workloads.pcap').open('wb') as target:
            shutil.copyfileobj(source,target)
        assert hashlib.sha256((dest/'legitimate_workloads.pcap').read_bytes()).hexdigest()==manifest['pcap_sha256']
        dump(dest/'sessions.json',manifest)
    manifest=json.loads((dest/'sessions.json').read_text())
    caps=[];allports=set()
    for session in manifest['sessions']:
        ports=set(session['source_ports']);allports|=ports
        cap=capture_from_packets(dest/'legitimate_workloads.pcap',session['name'],0,port=manifest['port'],accepted_ports=ports)
        cap['profile']=session['profile'];caps.append(cap)
    globalcap=capture_from_packets(dest/'legitimate_workloads.pcap','aggregate_concurrent_workload',0,port=manifest['port'])
    globalcap['profile']='aggregate';caps.append(globalcap)
    rows=[]
    for modeltag,(model,selected) in [('original_frozen',primary),('external_adapted',adapted)]:
        for cap in caps:
            score=scores_for(cap,model)
            for row in evaluate_policies(cap,score,selected,modeltag):
                row['profile']=cap['profile'];rows.append(row)
    dump(OUT/'benign_stress_results.json',{'scope':manifest['scope'],'sessions':manifest['sessions'],
         'results':rows,'aggregation_note':'Aggregate is the global observation unit. Per-client profile diagnostics use narrower traffic scopes and are not independent devices/days.'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-sensitivity',action='store_true');parser.add_argument('--skip-stress',action='store_true')
    args=parser.parse_args();OUT.mkdir(exist_ok=True,parents=True);CACHE.mkdir(exist_ok=True,parents=True)
    protocol=ROOT/'docs/EXTENDED_PROTOCOL.md'
    dump(OUT/'study_manifest.json',{'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),
         'protocol_commit':'5f0c1e6','metric_version':2,'original_data_status':'exploratory extension; original outcomes previously inspected',
         'source_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'scripts/research_core.py',ROOT/'scripts/mqttset_data.py']}})
    primary=original_study()
    if not args.skip_sensitivity:sensitivity()
    adapted=external_study(primary)
    if not args.skip_stress:stress_study(primary,adapted)
    dump(OUT/'complete.json',{'original_comparisons':True,'sensitivity':not args.skip_sensitivity,
         'external_validation':True,'real_time_benign_stress':not args.skip_stress})
    print('Extended numerical study complete.',flush=True)


if __name__=='__main__':main()
