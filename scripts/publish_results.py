"""Generate readable tables/plot from measured experiment JSON, never invented values."""
import csv
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];d=ROOT/'docs/results'
primary=json.loads((d/'primary.json').read_text()); folds=json.loads((d/'robustness.json').read_text());manifest=json.loads((d/'manifest.json').read_text())
rf=[r for r in primary if r['model']=='RF']
if len(rf)!=3 or [r['k'] for r in rf]!=[1,2,3]:
    raise ValueError('Expected one RF primary result per k=1,2,3')
cm=np.asarray(rf[0]['classification']['confusion_matrix'],dtype=int)
if cm.shape!=(2,2) or (cm<0).any():
    raise ValueError('Expected a nonnegative 2x2 confusion matrix')
truth=np.concatenate([np.full(int(cm[i,j]),i) for i in range(2) for j in range(2)])
predicted=np.concatenate([np.full(int(cm[i,j]),j) for i in range(2) for j in range(2)])
metrics={
    'Accuracy':float(accuracy_score(truth,predicted)),
    'Precision (SlowITe)':float(precision_score(truth,predicted,zero_division=0)),
    'Recall (SlowITe)':float(recall_score(truth,predicted,zero_division=0)),
    'F1-score (SlowITe)':float(f1_score(truth,predicted,zero_division=0)),
    'Macro F1':float(f1_score(truth,predicted,average='macro',zero_division=0)),
    'Weighted F1':float(f1_score(truth,predicted,average='weighted',zero_division=0)),
    'Test windows':len(truth),
}
for r in rf:
    if not np.array_equal(cm,r['classification']['confusion_matrix']):
        raise ValueError('Confirmation policies must share the same base classifier')
    for key,column in [('precision','Precision (SlowITe)'),('recall','Recall (SlowITe)'),('f1','F1-score (SlowITe)')]:
        if abs(r['classification'][key]-metrics[column])>1e-12:
            raise ValueError('Stored classification scores disagree with confusion counts')
with (d/'classification_metrics.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(metrics),lineterminator='\n');writer.writeheader();writer.writerow(metrics)
persist=[]
for r in rf:
    persist.append({
        'k':r['k'],'false_events':r['false_events'],
        'detected_runs':r['detected_runs'],'total_runs':r['label_runs'],
        'run_recall':r['label_run_recall'],'missed_runs':r['missed_runs'],
        'mean_latency_s':r['mean_latency_s'],'median_latency_s':r['median_latency_s'],
        'base_classifier_window_FPR':r['classification']['fpr'],
        'benign_confirmed_windows':r['benign_confirmed_windows'],
        'pure_benign_windows':r['coverage']['pure_benign'],
        'benign_window_exposure_hours':r['benign_hours'],
        'false_events_per_benign_window_exposure_hour':r['false_events_per_benign_hour'],
        'total_event_starts':r['total_events'],
        'ambiguous_or_out_of_scope_event_starts':r['ambiguous_or_out_of_scope_events'],
    })
with (d/'persistence_metrics.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(persist[0]),lineterminator='\n');writer.writeheader();writer.writerows(persist)
lines=['# Measured MQTTGuard results','', 'Generated from the checked-in JSON summaries. Dataset: original MQTTEEB-D v2 captures. Labels define observed run proxies, not independently timed physical attack executions.','', '## Primary test: train 1+2, validate 3, test 4','', '| Model | k | Window F1 | False clean events | Detected runs | Mean delay (s) |','| --- | ---: | ---: | ---: | ---: | ---: |']
lines[4:4]=[
    'Primary RF accuracy is **'+f"{metrics['Accuracy']:.4%}"+'**, SlowITe precision **'+f"{metrics['Precision (SlowITe)']:.2%}"+'**, recall **'+f"{metrics['Recall (SlowITe)']:.2%}"+'**, and F1 **'+f"{metrics['F1-score (SlowITe)']:.2%}"+'**. These are different metrics of the same model.',
    '',f'Confusion matrix (true rows / predicted columns; legitimate, SlowITe): `{cm.tolist()}`. Scored subset: {len(truth)} pure-class windows; empty and mixed/unknown/other windows are excluded from these classification scores.',
    '', 'Exports: [classification CSV](classification_metrics.csv), [persistence CSV](persistence_metrics.csv), and [classification figure](classification_metrics.png). `base_classifier_window_FPR` repeats the pre-confirmation classifier FPR; it is not post-confirmation FPR. Benign-window exposure sums eligible two-second windows, not independently observed continuous benign sessions. Clean false-event starts and time spent confirmed on benign windows are distinct outcomes.',
    '', 'For the completed study and metric caveats, see [extended results](../research/RESULTS.md) and [methodology](../METHODOLOGY.md).','',
]
for r in primary:lines.append(f"| {r['model']} | {r['k']} | {r['classification']['f1']:.4f} | {r['false_events']} | {r['detected_runs']}/{r['label_runs']} | {r['mean_latency_s']:.3f} |")
lines+=['','**Interpretation:** RF immediate alerting already has zero clean benign false events on capture 4. k=2 preserves 12/12 observed run detections but increases mean delay; k=3 misses two runs. Capture 4 has no adjacent pure-benign windows, so its zero k>=2 false events cannot establish general suppression effectiveness. Other-class/unknown/mixed event starts are reported separately in JSON.','', '## Separately defined capture-held-out robustness','', 'Each fold uses the next capture cyclically for validation and the remaining two for training. These are different fitted models, not independent sites or days.','', '| Held-out | k | RF false clean events | Runs detected | Mean delay (s) |','| --- | ---: | ---: | ---: | ---: |']
for r in folds:
 if r['model']=='RF':lines.append(f"| {r['capture']} | {r['k']} | {r['false_events']} | {r['detected_runs']}/{r['label_runs']} | {r['mean_latency_s']:.3f} |")
lines+=['','In held-out capture 1, k=2 changes false clean events from 66 to 3 and run detection from 84/84 to 83/84. This is evidence of a trade-off within this dataset; it is not proof of generalization to new brokers or real attacks. Full rate-baseline and ideal-pure-label diagnostic results are supplied alongside this file.','', '## Embedded model verification','',f"Selected RF: {manifest['parameters']['n_estimators']} trees, maximum depth {manifest['parameters']['max_depth']}. Export uses original floating-point thresholds and soft voting, without quantization.",'',f"Host-compiled C++ versus Python: {manifest['export_parity']['inputs']} inputs including {manifest['export_parity']['threshold_boundary_inputs']} boundary cases; {manifest['export_parity']['label_disagreements']} label disagreements; maximum probability difference {manifest['export_parity']['max_probability_error']}.",'', 'Wokwi timing is simulated execution time; laptop batch timings are not ESP32 hardware benchmarks. The classifier operates on host-extracted feature windows. Live capture, physical power measurements and automatic mitigation are not implemented.','', '![Primary confirmation delay](primary_delay.png)','']
(d/'RESULTS.md').write_text('\n'.join(lines))
rf=[r for r in primary if r['model']=='RF'];fig,ax=plt.subplots(figsize=(6,3.4));ax.bar([f"k={r['k']}" for r in rf],[r['mean_latency_s'] for r in rf],color=['#f0a329','#3185b9','#7b56b3']);ax.set_ylabel('Mean observed-run detection delay (s)');ax.set_title('Primary test: delay among detected runs')
for i,r in enumerate(rf):ax.text(i,r['mean_latency_s']+.08,f"{r['detected_runs']}/{r['label_runs']} runs",ha='center')
ax.set_ylim(0,6);fig.tight_layout();fig.savefig(d/'primary_delay.png',dpi=160);plt.close(fig)
print('Generated docs/results/RESULTS.md and plot')
fig,axes=plt.subplots(1,2,figsize=(11,4))
axes[0].imshow(cm,cmap='Blues')
for i in range(2):
    for j in range(2):axes[0].text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()/2 else 'black')
axes[0].set_xticks([0,1],['Legitimate','SlowITe']);axes[0].set_yticks([0,1],['Legitimate','SlowITe'])
axes[0].set_xlabel('Predicted');axes[0].set_ylabel('True');axes[0].set_title(f"Capture {rf[0]['capture']}: {len(truth)} pure-class windows")
values=[metrics[k] for k in ['Accuracy','Precision (SlowITe)','Recall (SlowITe)','F1-score (SlowITe)']]
bars=axes[1].bar(['Accuracy','Precision','Recall','F1'],values,color=['#2563eb','#059669','#d97706','#7c3aed'])
axes[1].bar_label(bars,labels=[f'{v:.2%}' for v in values]);axes[1].set_ylim(0,1.15)
axes[1].set_title('SlowITe class metrics; overall accuracy')
fig.tight_layout();fig.savefig(d/'classification_metrics.png',dpi=180);plt.close(fig)
print('Generated classification_metrics.csv/.png and persistence_metrics.csv')
