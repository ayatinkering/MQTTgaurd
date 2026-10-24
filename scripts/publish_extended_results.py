"""Publish measured extended-study tables, plots and machine-readable report data."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from train_pipeline import ROOT

D=ROOT/'docs/research'


def load(name):return json.loads((D/name).read_text())


def label(policy):
    family=policy['family']
    if family=='consecutive':return f"k={policy['k']}"
    if family=='bounded_evidence':return 'Bounded evidence'
    if family=='threshold':return 'Raised threshold'
    if family=='ideal_pure_labels':return 'Ideal labels diagnostic'
    if family=='always_positive':return 'Always positive diagnostic'
    return {'mean':'Moving mean','majority':'Majority vote','ewma':'EWMA'}[family]


def n(value,digits=3):return 'NA' if value is None else f'{value:.{digits}f}'


def main():
    comparisons=load('comparisons.json');sensitivity=load('sensitivity.json')
    external=load('external_results.json');stress=load('benign_stress_results.json')
    parity=load('evidence_cpp_parity.json')
    for r in comparisons+external['results']+stress['results']:
        assert r['total_alarm_onsets']==r['benign_alarm_onsets']+r['positive_alarm_onsets']+r['excluded_alarm_onsets']
        assert r['covered_runs']+len(r['missed_run_ids'])==r['run_count']
        assert r['benign_alarm_seconds']<=r['benign_exposure_seconds']
    primary=[r for r in comparisons if r['split']=='primary']
    f1=[r for r in comparisons if r['split']=='fold_1']
    a=next(r for r in f1 if r['policy']=={'family':'consecutive','k':2})
    b=next(r for r in f1 if r['policy']['family']=='bounded_evidence')
    summary={'metric_version':2,'primary':primary,'matched_fold1':{
        'reference_k2':a,'proposed':b,
        'benign_occupancy_reduction_fraction':1-b['benign_alarm_fraction']/a['benign_alarm_fraction'],
        'mean_delay_reduction_fraction':1-b['coverage_delay_mean_s']/a['coverage_delay_mean_s']},
        'external':external,'stress':stress,'sensitivity':sensitivity,'cpp_parity':parity}
    columns=['study','capture','model_tag','policy','base_f1','benign_alarm_onsets','legacy_clean_false_onsets',
             'benign_alarm_seconds','benign_exposure_seconds','benign_alarm_fraction','excluded_alarm_onsets',
             'covered_runs','run_count','runs_with_new_onset','coverage_delay_mean_s','coverage_delay_median_s',
             'coverage_delay_p95_s','adjacent_benign_pairs','longest_benign_streak']
    with (D/'alarm_audit.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');writer.writeheader()
        for study,rows in [('original',comparisons),('external',external['results']),('benign_stress',stress['results'])]:
            for row in rows:
                writer.writerow({**{c:row.get(c) for c in columns if c not in ['study','policy','base_f1']},
                    'study':row.get('split',row.get('evaluation',study)),
                    'policy':json.dumps(row['policy'],sort_keys=True),'base_f1':row.get('base_classifier',{}).get('f1')})
    lines=['# Completed extended MQTTGuard study','','All results are measured outputs of the saved protocol and metadata-driven external amendment. Original-data additions are exploratory because the original test outcomes were already inspected. The course report uses these definitions rather than silently mixing legacy and version-2 metrics.','',
        '## Proposed extension and contribution','',
        'The bounded gap-aware evidence policy accumulates classifier confidence with a fixed scalar state and validation-only coverage-constrained calibration. This adapts established sequential evidence accumulation to the MQTT replay pipeline. Its contribution is the implemented decision-layer variant and complete evaluation; it does not establish a new general-purpose sequential detection principle.','',
        '## Primary alert comparison under audit version 2','',
        '| Policy | Benign onsets | Benign occupancy | Covered runs | Mean delay s | Excluded onsets |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for r in primary:
        lines.append(f"| {label(r['policy'])} | {r['benign_alarm_onsets']} | {n(100*r['benign_alarm_fraction'],2)}% | {r['covered_runs']}/{r['run_count']} | {n(r['coverage_delay_mean_s'])} | {r['excluded_alarm_onsets']} |")
    lines += ['', 'Audit v2 requires a pure-positive window for run coverage and reports coverage separately from a new onset. Legacy immediate-run mean delay is 0.888 s; version2 is 1.055 s because the earliest mixed legitimate/SlowITe window is no longer credited. This is a definition change, not a changed classifier. Base primary confusion remains [[372,0],[55,143]], accuracy 90.35%, precision 100%, recall 72.22%, F1 83.87%.',
              '', 'The proposed primary-validation-selected setting is h=0.75, decay=0.5. It covers 11/12 primary runs and is slower than k2; therefore it is not claimed to dominate k2. The original fixed k2 remains the default reference.','',
              '## Matched coverage comparison on capture 1','',
              '| Policy | Benign onsets | Benign confirmed windows | Covered runs | Mean delay s |',
              '| --- | ---: | ---: | ---: | ---: |']
    matched=[r for r in f1 if (r['policy']=={'family':'consecutive','k':2} or r['policy']['family'] in ['threshold','bounded_evidence'])]
    for r in matched:lines.append(f"| {label(r['policy'])} | {r['benign_alarm_onsets']} | {r['benign_confirmed_windows']} | {r['covered_runs']}/{r['run_count']} | {n(r['coverage_delay_mean_s'])} |")
    lines += ['',f"At 83/84 covered runs, bounded evidence reduces benign occupancy by {100*summary['matched_fold1']['benign_occupancy_reduction_fraction']:.2f}% and mean delay by {100*summary['matched_fold1']['mean_delay_reduction_fraction']:.2f}% relative to k2, but increases benign onsets from 3 to 5. Raising the threshold yields fewer benign confirmed windows than either, with a longer delay than bounded evidence. These are different operating tradeoffs, not uniform superiority.",
              '', '## Independent MQTTset evaluation','',
              'The original full benign capture supplies 11,915,716 TCP records and 302,551 complete two-second windows over approximately one week. The frozen primary model produces zero benign alarms on this capture. This provides independent benign exposure evidence, not proof of detecting all external attacks.',
              '', 'The SlowITe file is excluded from temporal scoring because its 9,202 records span only 0.696832 seconds. Parser validation against its author-provided CSV has zero differences for all 9,202 timestamps, TCP lengths and recorded keepalive values, including fragmented CONNECT attribution.',
              '', '| Evaluation | Scenario | Policy | Covered scenario | Mean proxy delay s | Benign occupancy |',
              '| --- | --- | --- | ---: | ---: | ---: |']
    for r in external['results']:
        if r['policy']['family']=='consecutive' or r['policy']['family']=='bounded_evidence':
            lines.append(f"| {r['evaluation']} | {r['capture']} | {label(r['policy'])} | {r['covered_runs']}/{r['run_count']} | {n(r['coverage_delay_mean_s'])} | {n(r['benign_alarm_fraction'])} |")
    lines += ['', 'The supplementary external attack is an MQTT DoS scenario, not SlowITe packet-level validation. Direct transfer detects the scenario with immediate alerts but stricter confirmation can miss it. Separate chronological adaptation is measured on first 40% train / next 20% validation / last 40% test with five-second guards. Its perfect scenario-window confusion counts must be interpreted with the strong benign/DoS file separation and only one attack recording; this is not evidence of universal 100% attack detection.','',
              '## Real time legitimate workload','',
              'Twenty-four Paho clients run six profiles with four seeded repetitions for 120 real seconds concurrently against a local MQTT broker: steady, bursts, reconnects, rate changes, idle and combined. They are controlled benign sessions, not independent physical devices/days. Aggregate observation and per-client diagnostics are kept separate.','',
              '| Model | Policy | Aggregate benign alarm windows | Aggregate benign onsets |',
              '| --- | --- | ---: | ---: |']
    for r in stress['results']:
        if r['profile']=='aggregate' and (r['policy']['family']=='consecutive' or r['policy']['family']=='bounded_evidence'):
            lines.append(f"| {r['model_tag']} | {label(r['policy'])} | {r['benign_confirmed_windows']}/{r['pure_benign_windows']} | {r['benign_alarm_onsets']} |")
    lines += ['', 'Per-client profile diagnostics and seeds are retained in benign_stress_results.json and alarm_audit.csv. They use narrower traffic scopes than the global detector, so they are stress diagnostics rather than equivalent deployment replications.','',
              '## Window and feature sensitivity','',
              '| Window s | Features | Window F1 | k2 runs | Bounded evidence runs |',
              '| ---: | --- | ---: | ---: | ---: |']
    for r in sensitivity:lines.append(f"| {r['seconds']} | {r['feature_set']} | {r['base_classifier']['f1']:.4f} | {r['k2']['covered_runs']}/{r['k2']['run_count']} | {r['proposed']['covered_runs']}/{r['proposed']['run_count']} |")
    lines += ['', 'All 18 prespecified sensitivity configurations are retained. Results do not justify choosing a new official model from the best inspected test score. Different durations change the evaluated window cohort, so F1 changes are not paired predictions on identical rows.','',
              '## Embedded evidence','',
              f"The actual C++ bounded-evidence module matches Python on {parity['score_policy_transitions']:,} saved score/policy transitions with zero state/event disagreements. Host sizeof is {parity['host_state_bytes']} bytes, including configuration and counters; ESP32 size and timings are separate target observations. Current firmware is under firmware/wokwi_research; the original baseline bundle is regenerated under ignored firmware/wokwi. Actual target verification is recorded in docs/evidence/research_target_verification.json.",
              '', '## Files and reproduction','',
              'Numerical sources: comparisons.json, validation_frontiers.json, test_frontiers.json, external_results.json, sensitivity.json, benign_stress_results.json, external_manifest.json, parser_validation.json and evidence_cpp_parity.json. Raw captures and per-window scores remain under ignored data/ and reports/ paths.','',
              '```bash','.venv/bin/python scripts/mqttset_data.py','.venv/bin/python scripts/benign_stress.py','.venv/bin/python scripts/run_extended_study.py','.venv/bin/python scripts/bundle_research_firmware.py','.venv/bin/python scripts/verify_evidence_policy.py','.venv/bin/python scripts/publish_extended_results.py','```','']
    text='\n'.join(lines)
    (D/'RESULTS.md').write_text(text)
    fig,ax=plt.subplots(figsize=(7,4))
    for r,color in zip(matched,['#2563eb','#d97706','#059669']):
        x=100*r['benign_alarm_fraction'];y=r['coverage_delay_mean_s']
        ax.scatter(x,y,s=100,color=color,label=label(r['policy']))
        ax.annotate(label(r['policy']),(x,y),xytext=(8,8),textcoords='offset points',fontsize=9)
    ax.set_xlabel('Benign time in alarm (%)');ax.set_ylabel('Mean covered-run delay (s)')
    ax.set_title('Capture 1: matched 83/84 run coverage');ax.grid(alpha=.2)
    ax.margins(.3);fig.tight_layout();fig.savefig(D/'matched_tradeoff.png',dpi=180);plt.close(fig)
    names=list(dict.fromkeys(r['feature_set'] for r in sensitivity))
    values=np.array([[next(r['base_classifier']['f1'] for r in sensitivity if r['seconds']==seconds and r['feature_set']==name) for name in names] for seconds in [1,2,5]])
    fig,ax=plt.subplots(figsize=(9,3.5));im=ax.imshow(values,vmin=0,vmax=1,cmap='Blues',aspect='auto')
    ax.set_xticks(range(len(names)),[x.replace('_',' ') for x in names],rotation=18,ha='right')
    ax.set_yticks(range(3),['1 s','2 s','5 s'])
    for i in range(3):
        for j in range(len(names)):ax.text(j,i,f'{values[i,j]:.3f}',ha='center',va='center',color='white' if values[i,j]>.6 else 'black')
    ax.set_title('Exploratory primary-test F1 across all 18 configurations')
    fig.colorbar(im,ax=ax,label='SlowITe F1');fig.tight_layout();fig.savefig(D/'sensitivity.png',dpi=180);plt.close(fig)
    print('Published extended tables, audit CSV and figures.')


if __name__=='__main__':main()
