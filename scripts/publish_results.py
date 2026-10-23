"""Generate readable tables/plot from measured experiment JSON, never invented values."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];d=ROOT/'docs/results'
primary=json.loads((d/'primary.json').read_text()); folds=json.loads((d/'robustness.json').read_text());manifest=json.loads((d/'manifest.json').read_text())
lines=['# Measured MQTTGuard results','', 'Generated from the checked-in JSON summaries. Dataset: original MQTTEEB-D v2 captures. Labels define observed run proxies, not independently timed physical attack executions.','', '## Primary test: train 1+2, validate 3, test 4','', '| Model | k | Window F1 | False clean events | Detected runs | Mean delay (s) |','| --- | ---: | ---: | ---: | ---: | ---: |']
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
