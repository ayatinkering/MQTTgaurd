# Research findings and completed evidence

## Completed research extension — 24 October 2026

The stronger-policy comparisons, audit version 2, continuous legitimate workload, independent MQTTset compatibility/direct-transfer/adaptation tests, and all 18 feature/window sensitivity configurations are complete. Read the [editable report content](../deliverables/report/REPORT_CONTENT.md) for the full paper narrative and [measured extended results](research/RESULTS.md) for tables. The original results below remain a historical baseline; legacy delays and clean false-event counts must not be mixed with audit-v2 endpoints.

The new contribution is bounded gap-aware confidence accumulation with validation-only coverage-constrained calibration, implemented in C++. It is a modest application-specific extension to established sequential evidence methods. At matched 83/84 coverage in capture 1 it reduces benign occupancy 43.75% and mean delay 15.19% relative to k=2, while increasing benign starts from 3 to 5. It underperforms k=2 on the primary split; no universal advantage is claimed.

The [research Wokwi demo](https://wokwi.com/projects/478737844363875329) uses `firmware/wokwi_research/`, build `3f718dc4c8d9ea81`, and adds a fourth evidence LED. Actual verification covers 62 paired model/evidence rows and 53 independently received MQTT records, with zero discrepancies. Original firmware and its demo remain available as the fixed baseline.

MQTTset supplies substantial independent benign exposure and a supplementary DoS scenario. Its SlowITe file spans only 0.696832 seconds and cannot validate two-second temporal detection. Separate adaptation has perfect scenario-window test classification but false alarms under changed benign scope; it is not general 100% SlowITe detection. All these outcomes are retained.

Only editable report content is requested now. Slides and synopsis production are stopped; the original course PDFs are unchanged.


Updated 24 October 2026. This document distinguishes measured findings, their interpretation, and experiments still needed. Numerical sources are [primary results](results/primary.json), [capture-held-out results](results/robustness.json), [dataset audit](DATASET_REVIEW.md), and [embedded evidence](evidence/EMBEDDED_VERIFICATION.md).

## 1. Research question and supported contribution

**Question:** What happens to false alert events, observed SlowITe-run coverage and detection delay when a compact MQTT classifier requires consecutive suspicious windows, and can the resulting pipeline execute on a simulated ESP32?

The supported contribution is a reproducible capture-separated evaluation, exact C++ model export, and verified trace-driven embedded implementation. Consecutive confirmation, Random Forests and Wokwi are established techniques; their use alone is not algorithmic novelty. A claim of superiority over existing IDS research has not been established.

## 2. Dataset findings

MQTTEEB-D v2 contains 222,813 observations across four original captures: 17,557 legitimate, 20,090 SlowITe, 41,802 DoS, 105,528 malformed, 27,377 brute-force, 10,213 flood, and 246 missing labels. The cleaned file equals the raw captures' combined row multiset and is not additional training data.

We found that `tcp_time_delta` repeats absolute timestamps, so timing is recomputed. Most pure windows contain only one record; interarrival is then missing and receives a training-only median. Recorded keepalive is only 0/60. These findings weaken assumptions that this release provides a rich continuous SlowITe timing signature.

All four captures originate from one testbed/day. IP/client identity and independent attack execution logs are absent from the inspected schema. The 132 SlowITe label runs (84/24/12/12) are episode proxies, not 132 independently verified attack executions.

## 3. Primary classifier result

Train captures 1+2, validate 3, test 4. Four features, two-second complete windows, train-only imputation, 16 RF trees, maximum depth 3. Validation chooses among four tree/depth candidates; test is not used for that selection.

| Metric | Measured value |
| --- | ---: |
| Accuracy | 90.3509% |
| SlowITe precision | 100% |
| SlowITe recall | 72.2222% |
| SlowITe F1 | 83.8710% |
| Macro F1 | 88.4937% |
| Weighted F1 | 89.9048% |
| Correct legitimate / false positive windows | 372 / 0 |
| Correct SlowITe / missed SlowITe windows | 143 / 55 |

Accuracy and F1 describe the same model. The friend's Colab reproduction is not a separate 90.35%-versus-83.87% model comparison.

These scores cover 570 pure legitimate/SlowITe windows. Capture 4 has 3,727 complete windows in total, including 2,575 empty and 582 mixed/unknown/other windows. Runtime predicts valid windows without reading their labels; classification scoring excludes uncertain/out-of-scope classes. The current experiment does not validate all-attack detection.

The traffic-count baseline's primary F1 is 71.84%, compared with RF's 83.87% (12.03 percentage points higher on this split). This comparison is measured, but no independent-dataset superiority or statistical significance is established.

## 4. Primary persistence result

All policies receive the same base predictions; k does not retrain the forest.

| k | Clean false starts | Run proxies detected | Missed runs | Mean delay | Median delay |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 12/12 | 0 | 0.888 s | 0.770 s |
| 2 | 0 | 12/12 | 0 | 3.555 s | 3.136 s |
| 3 | 0 | 10/12 | 2 | 4.900 s | 4.668 s |

k=2 adds approximately 2.667 s mean delay while retaining detection of all 12 proxies. k=3 misses two proxies. Delays are measured only among detected runs; k=3's mean uses a different detected subset. Run detection can be 100% while window recall is 72.22% because a run contains multiple windows.

**No primary false-alarm suppression claim is supported.** Immediate alerts already have zero clean false events. Furthermore, this capture has no adjacent pure-benign windows: with resets, k>=2 clean false starts are structurally impossible under the present definition.

There are 118/42/32 total event starts for k=1/2/3, of which 64/30/22 are ambiguous or out of scope. Those excluded starts cannot be silently described as correct detections or as nonexistent false alarms. A clean false start requires its entire k-window evidence to be pure benign. A legitimate current window can still be confirmed because evidence started in another class.

## 5. Capture-held-out robustness

Each fold has a separately fitted model; the next capture cyclically is validation and the remaining two are training. These are related-data robustness checks, not independent deployments.

| Test capture | Clean false starts k=1/2/3 | Run proxies detected k=1/2/3 | Mean delay k=1/2/3 (s) |
| --- | --- | --- | --- |
| 1 | 66 / 3 / 3 | 84 / 83 / 81 of 84 | 0.925 / 3.172 / 5.091 |
| 2 | 16 / 0 / 0 | 24 / 24 / 23 of 24 | 1.165 / 3.332 / 5.184 |
| 3 | 10 / 0 / 0 | 12 / 12 / 12 of 12 | 0.841 / 3.175 / 5.675 |
| 4 | 0 / 0 / 0 | 12 / 12 / 10 of 12 | 0.888 / 3.555 / 4.947 |

Capture 1 shows 95.45% fewer clean false starts at k=2 (66 to 3), with coverage falling from 84/84 to 83/84 and mean delay rising by approximately 2.247 s. Do not present 95.45% as an overall project-wide reduction.

False-event counts and false-alarm occupancy are different. The numbers of pure-benign windows spent confirmed are:

| Test capture | Confirmed benign windows k=1/2/3 |
| --- | --- |
| 1 | 82 / 16 / 13 |
| 2 | 18 / 2 / 1 |
| 3 | 14 / 4 / 1 |
| 4 | 0 / 0 / 0 |

Thus capture 2 has zero clean false starts at k=2 but still two benign windows in confirmed state. This is why the paper must report both outcomes. Existing false-event/hour denominators sum pure-benign window duration, not continuous verified benign sessions.

Do not pool fold observations as independent trials or bootstrap individual temporally correlated windows to produce narrow confidence intervals. More seeds from these same captures do not create independent testbeds.

## 6. Embedded implementation findings

- Host-compiled exported C++ matches Python over 11,210 inputs: 10,889 valid complete windows plus 321 threshold-boundary inputs, zero label disagreements and maximum probability error 0.0.
- Actual observed Wokwi output covers 90 MODEL rows across complete passes of all three demonstration clips and repeated passes. Zero prediction/probability/confirmation discrepancies; 53 rows perform actual inference, others represent unavailable input.
- Six initial and 11 recovery-test independently received MQTT model messages match expected outputs. These are integration samples, not delivery-rate estimates.
- A controlled failed-hostname connection test processes six replay rows while the fault is active; MQTT reconnects and publication resumes after recovery. It does not prove exhaustive network fault tolerance or lossless telemetry.
- Simulator image size: 928,112 bytes for the full application/runtime. Minimum observed free heap: 214,952 bytes. Median/p95 simulated model-call time: 140/147 microseconds over 53 calls. These are not physical-chip power/latency or RF-only image measurements.
- Twelve automated Python/host-C++ tests passed at the verified firmware checkpoint. Live packet capture, feature extraction on ESP32, and automatic blocking are not implemented.

## 7. Friend's handoff and current reproduction

The supplied Colab outputs match the existing model, predictions and numerical summaries. Its old firmware has a duplicate gap/benign clip and lacks later verification/recovery diagnostics, so it is not substituted for current firmware. No experimental history-model notebook or artifact was supplied.

The adopted Colab notebook is under `notebooks/`. It uses a fixed source commit, runs the repository scripts, regenerates all report exports, bundles the current firmware, and records input/output hashes. It does not itself supply an independent evaluation dataset. See [Colab instructions](COLAB.md).

## 8. Completed stronger study and report content

All five requested numerical extensions are complete: stronger simple comparators, full alarm audit, real-time legitimate workload, independent timestamped MQTT compatibility and evaluation, and 18 feature/window sensitivity configurations. See [extended results](research/RESULTS.md), [audit CSV](research/alarm_audit.csv), [protocol](EXTENDED_PROTOCOL.md) and [external amendment](EXTERNAL_PROTOCOL_AMENDMENT.md).

The editable report contains the full introduction, critical literature comparison, proposed bounded evidence method, reproducible evaluation, measured results and threats to validity. See [report content](../deliverables/report/REPORT_CONTENT.md) or [LaTeX source](../deliverables/report/main.tex). User requested report content only; slides and synopsis production stopped.

Remaining scientific limits are independent adequately timed SlowITe execution logs, repeated sites/days, physical measurements and live packet extraction on target. These are limits of claims, not unfinished steps hidden behind the completed study. The independent SlowITe download is temporally incompatible; the external DoS and benign experiments are explicitly labelled substitutes for their respective questions, not fabricated SlowITe validation.
