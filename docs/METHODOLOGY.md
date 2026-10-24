# MQTTGuard: Current Research and Embedded Simulation Methodology

## Completed research extension — 24 October 2026

The stronger-policy comparisons, audit version 2, continuous legitimate workload, independent MQTTset compatibility/direct-transfer/adaptation tests, and all 18 feature/window sensitivity configurations are complete. Read the [editable report content](../deliverables/report/REPORT_CONTENT.md) for the full paper narrative and [measured extended results](research/RESULTS.md) for tables. The original results below remain a historical baseline; legacy delays and clean false-event counts must not be mixed with audit-v2 endpoints.

The new contribution is bounded gap-aware confidence accumulation with validation-only coverage-constrained calibration, implemented in C++. It is a modest application-specific extension to established sequential evidence methods. At matched 83/84 coverage in capture 1 it reduces benign occupancy 43.75% and mean delay 15.19% relative to k=2, while increasing benign starts from 3 to 5. It underperforms k=2 on the primary split; no universal advantage is claimed.

The [research Wokwi demo](https://wokwi.com/projects/478737844363875329) uses `firmware/wokwi_research/`, build `3f718dc4c8d9ea81`, and adds a fourth evidence LED. Actual verification covers 62 paired model/evidence rows and 53 independently received MQTT records, with zero discrepancies. Original firmware and its demo remain available as the fixed baseline.

MQTTset supplies substantial independent benign exposure and a supplementary DoS scenario. Its SlowITe file spans only 0.696832 seconds and cannot validate two-second temporal detection. Separate adaptation has perfect scenario-window test classification but false alarms under changed benign scope; it is not general 100% SlowITe detection. All these outcomes are retained.

Only editable report content is requested now. Slides and synopsis production are stopped; the original course PDFs are unchanged.


## 1. What We Are Testing

The detector first classifies a traffic window using a Random Forest, then optionally waits for repeated positive predictions before confirming an attack. We ask whether that extra wait reduces false alarms enough to justify the delay and any missed attacks.

**Fixed primary configuration:** 2-second, non-overlapping windows; four features; Random Forest; k = 1, 2, and 3. The same trained model and held-out predictions serve all k values.

The original report supplies the core research question. The current implementation extends it with actual C++ Random Forest inference and confirmation on a Wokwi ESP32, plus working MQTT status reporting. Training and feature extraction remain on the host. Primary and capture-held-out results have been measured; see [RESULTS](results/RESULTS.md), [IMPLEMENTATION](IMPLEMENTATION.md), and [HANDOFF](HANDOFF.md).

This is trace-driven embedded simulation, not a live network sniffer or a live attack against a broker. The repository methodology supersedes software-only assumptions in the original PDF.

## 2. Acquire the Correct Files

Official release: https://data.mendeley.com/datasets/jfttfjn6tr/2

Run from the repository root:

```bash
python3 scripts/download_dataset.py
python3 scripts/inspect_dataset.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

These scripts require Python 3.10+ and `curl`, with no Python package installation. The downloader requires network access; inspection works offline after download. The downloader reviews only publisher version 2 and stops if the current version changes.

The inspector writes `reports/dataset_audit.json`, `reports/dataset_preview.html`, and per-file nonempty-window CSVs. Its bins are exploratory: they include each capture's trailing incomplete window and do not constitute a trained detector or final experimental cohort.

The primary modelling inputs are the four original `MQTTEEB-D_dataset_loop_*.csv` files. The cleaned CSV serves as a cross-check because the audit found the same rows in the combined raw files. Do not train on both copies. Do not use publisher SMOTE, normalized, or standardized versions for chronological replay.

Preserve the original files. Record SHA-256 hashes, release version, license, and retrieval date. The compact manifest and [dataset review](DATASET_REVIEW.md) provide traceability. Attribution must cite the dataset creators and the associated Data in Brief article, not only a later benchmark study.

## 3. Validate Before Modelling

The downloaded files use `label`, not the `target` field described in part of the paper. Original string labels include `legitimate` and `slowite`.

For this binary task, map `legitimate` to 0 and `slowite` to 1 **only for training targets and evaluation**. The publisher's metadata uses legitimate = 3 and slowite = 5 in encoded variants; that multiclass mapping is not the binary mapping.

Audit outcomes to account for:

- 246 rows have missing labels. Keep them visible; never label them normal by default.
- All timestamps parse as Unix seconds and are non-decreasing in source order. Preserve equal timestamps; they can represent different observations.
- `tcp_time_delta` equals the absolute timestamp in every row. Exclude that field and calculate time differences yourself.
- No exact duplicate rows were found. Do not remove observations merely because their timestamps coincide.
- Labels identify observations. The files do not provide source/destination IPs, client IDs, or separate attack start/stop logs in their 13-column schema. Initial analysis is at capture level, not per-device attribution.

Preserve capture and row identifiers for auditing; never use them as predictive features. Source timezone is not supplied in the files: render epoch timestamps in UTC and label them as UTC.

## 4. Freeze the Data Split

Use whole captures rather than a random shuffle of nearby windows:

| Role | Capture files | Legitimate rows | SlowITe rows |
| --- | --- | ---: | ---: |
| Training | Loops 1 and 2 | 14,366 | 16,428 |
| Validation | Loop 3 | 2,815 | 1,801 |
| Primary test | Loop 4 | 376 | 1,861 |

This split is selected before fitting any model. Fit imputation and model parameters on training data only. Choose any hyperparameters or probability threshold using validation data only. Keep the primary test unchanged and report it even if the result is poor.

Capture 4's benign windows are unusually sparse. Add an explicitly separate leave-one-capture-out robustness study: each fold holds out one capture for testing, uses a predetermined different capture for validation, and trains on the remaining two. Freeze all fold assignments before tuning and publish each result; do not replace an inconvenient primary result with a favourable fold.

All four captures are from one day and one testbed. State that restriction on generalization.

## 5. Create Windows Without Losing Time

For each capture, take the first valid timestamp as `t0`. Use integer microseconds so a timestamp exactly on a boundary is assigned consistently.

```text
window j = [t0 + j * 2 seconds, t0 + (j + 1) * 2 seconds)
```

Keep one grid across the original capture. Do not select only target-class rows and then concatenate or re-index them. That would distort clock time and could make separated observations appear consecutive.

For every window, save its capture ID, index, start/end times, observation count, feature values, and separate label composition. Missing label rows remain observations and contribute traffic features; their uncertainty affects scoring rather than changing runtime behaviour.

### Window handling

| Situation | Prediction behaviour | Ground-truth use |
| --- | --- | --- |
| Nonempty, valid features | Predict at window end, without reading labels. | Use label composition only for fitting/scoring rules below. |
| Empty interval | No inference; reset confirmation. | Record unavailable exposure. Never silently remove the interval. |
| Invalid required inputs | Mark unscorable and reset. | Record reason and exposure lost. |
| New capture/replay | Reset all temporal state. | Prevent evidence crossing partitions. |
| Last incomplete interval | Omit from primary inference. | Retain affected episode proxies in recall denominators. |

An empty two-second interval is common in this dataset and is not automatically a sensor failure. The reset is a chosen conservative confirmation policy; its effect must be measured.

## 6. Extract the Four Features

Use observations inside the current window only:

| Feature | Calculation | Interpretation |
| --- | --- | --- |
| Count | Number of observations, N | Traffic intensity over a fixed period |
| Mean TCP length | Mean of valid `tcp_len` values | Typical recorded TCP segment length |
| Mean inter-arrival time | Mean of differences between consecutive in-window timestamps | Spacing of observed traffic |
| Mean MQTT keep-alive | Mean of recorded `mqtt_kalive` values | Dataset's recorded keep-alive pattern |

For N >= 2, mean inter-arrival time is `(last_timestamp - first_timestamp) / (N - 1)`. For N = 1, it is missing. Do not divide by zero or invent an observed gap.

Fit a median imputer on training windows and save its values. A feature with no valid training measurements must trigger an explicit design review instead of being silently invented. Keep source zeros in `mqtt_kalive`; the file does not establish that a zero on every non-CONNECT observation is a negotiated client keep-alive of zero.

The primary feature set remains four values. A missingness-indicator extension may be evaluated as a separately labelled ablation. Random Forest does not require feature normalization for this experiment.

Do not feed absolute timestamps, `tcp_time_delta`, labels, row numbers, capture IDs, or episode proxies into the model.

## 7. Define Training and Classification Cohorts

Fit the binary classifier using windows containing exclusively Legitimate or exclusively SlowITe labelled observations. Exclude mixed-class and unknown-label windows from fitting and pure-window classification metrics. Log exclusions by capture and reason.

Mixed Legitimate/SlowITe transition windows still receive predictions during full-capture replay, using all their traffic observations. Their labels do not enter runtime state. Other attack types and unknown labels are outside the primary binary scoring domain, but are not secretly removed to improve model behaviour.

This distinction matters: **training labels choose fitting examples; replay labels measure results. Neither controls the deployed decision path.**

## 8. Train the Model and Baselines

Implemented selection: evaluate 8/16 trees crossed with maximum depth 3/5; seed 42, minimum leaf size 2, balanced class weights. Fit the median-imputation/float32/RF pipeline on training captures only. Choose maximum validation F1, then fewer total nodes, fewer trees, and smaller depth. The selected primary model has 16 trees/depth 3. Save feature order, medians, class mapping, parameters, versions and dataset hashes. Do not refit on validation/test after selection.

Before interpreting the AI result, compare against a simple count/rate threshold, fitted and selected on training/validation data under the same split. That asks whether AI adds value beyond traffic intensity in this dataset. Apply the same k comparisons to this baseline where feasible.

Export exactly one held-out prediction sequence per model. Every persistence setting consumes that saved sequence. Do not independently tune the RF for k = 2 to make its comparison favourable.

## 9. Confirm Suspicion Across Consecutive Windows

```text
At replay/capture start: streak = 0

For each complete two-second interval:
    if empty or unscorable:
        streak = 0
        confirmed = false
    else:
        prediction = model(current_window_features)
        streak = min(streak + 1, k) if prediction == 1 else 0
        confirmed = (streak >= k)

Start an alert event when confirmed changes from false to true.
```

- k = 1: immediate Random Forest baseline.
- k = 2: proposed MQTTGuard confirmation.
- k = 3: stricter comparison.

Example: `positive, empty, positive` cannot confirm k = 2. `positive, positive` can. A long confirmed sequence is one event, with a duration, rather than a separate alert every interval.

**Do not reset the streak because a ground-truth label is another attack or unknown.** A live detector does not know those labels. Offline evaluation can mark outputs outside the binary scoring domain without altering the detection state.

The confirmation layer needs only a bounded counter and prior confirmation flag. This does not establish that the entire Random Forest pipeline is lightweight on embedded hardware.

## 10. Define Episode Proxies Carefully

The audit found 132 contiguous SlowITe label runs across the four files: 84, 24, 12, and 12. These are **observed label-run proxies**, not independently confirmed attack executions.

For the primary proxy definition, each contiguous run of SlowITe-labelled observations within a capture starts at its first timestamp and ends at its last timestamp. Do not bridge over another label or capture boundary. Record internal gaps and run durations. Without controller logs, no algorithm can recover exact physical attack start/stop times from labels alone.

Use these names in outputs: `label_run_recall` and `label_run_detection_latency`. Call them actual attack-episode metrics only when external timing metadata validates the boundaries.

A confirmed event detects a proxy if the event starts inside that proxy's observed interval. For k > 1, require its contributing windows to be attributable to that proxy (no observations labelled as another attack or unknown in the confirming sequence); report any ambiguous confirmation separately. This is an evaluation attribution rule and never changes the prediction stream.

An alert already active before a proxy begins does not create a fresh detection. A first confirmation after the final SlowITe timestamp is a late confirmation, not an on-time detection. Report late cases separately because last-packet time may precede the actual attack stop time.

## 11. Measure the Outcomes

### Classifier metrics on pure held-out windows

Report TP, FP, TN, FN, precision, recall, F1, and FPR. These describe the RF predictions and do not change with k.

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2TP / (2TP + FP + FN)
FPR       = FP / (FP + TN)
```

Use undefined/NA when a denominator is zero. Report counts alongside percentages.

### Confirmation metrics

- **False alert events:** confirmed-event starts whose complete k-window evidence consists of pure Legitimate windows. This is a clean benign-window measure; it does not measure every possible false alarm during unknown or mixed traffic.
- **Benign confirmed windows:** pure Legitimate windows with confirmation active, reported separately from new event starts. Flag events that started outside benign traffic.
- **Proxy recall:** detected SlowITe label runs / all held-out SlowITe label runs, including misses caused by short duration or unavailable windows.
- **Missed and late proxies:** identifiers, duration, window availability, and first confirmation if any.
- **Latency:** first attributed event time minus proxy start, for detected proxies. Report mean, median, distribution, and misses separately.
- **Coverage:** valid benign and SlowITe windows, mixed/unknown/out-of-scope windows, empty time, incomplete time, and capture duration.
- **False events per eligible benign hour:** use the summed duration of pure-benign complete windows as denominator and label it explicitly. It is not the full benign wall-clock exposure.

Emit predictions at the **end** of a complete window. State whether measured computation delay is added. Do not assign an alert the start time of the window that produced it. k = 2 does not guarantee a fixed four-second latency from physical attack onset.

## 12. Check Whether the Apparent Gain Is an Artifact

Capture 4 has no adjacent pure-benign 2-second windows under the inspected alignment. Under the clean benign-event definition, k >= 2 cannot produce a false event there, regardless of model quality. Reporting that zero alone as a powerful AI improvement would be misleading.

Diagnostics and execution status:

1. Show adjacent benign-window opportunities and empty-window frequency for each capture.
2. Run a clearly labelled ideal-label diagnostic: use perfect pure-window labels as predictions, retain gaps, and measure the maximum proxy coverage allowed by windowing and persistence. Mixed/unknown windows remain uncertain in this diagnostic. It is not trained-model performance.
3. Compare with the rate/count baseline and inspect which feature drives separation.
4. Current results use the frozen 2-second protocol only. A 1/5-second sensitivity study is deferred and must be labelled exploratory because primary test outcomes have already been inspected. Do not retroactively describe alternative settings as pre-registered.
5. Report every held-out capture separately and explain loop 4's sparse benign traffic.
6. Preserve zero-effect results: if k = 1 already produces no false alerts, k = 2 cannot demonstrate a further reduction on that test.

## 13. Runtime and Reproducibility

Current instrumentation records laptop batch prediction time, the distribution of 53 observed Wokwi inference calls, firmware image size and heap usage; the manifest labels laptop timing, and telemetry labels simulated timing. It does not yet provide a complete end-to-end timing distribution, linker/static-RAM section report, or physical power measurement. These are follow-up measurements, not established lightweight-deployment claims. Keep feature extraction, inference, confirmation, display and networking costs separate when extending instrumentation.

Save a run manifest, split assignment, fitted preprocessing, model, windows, predictions, confirmation states, event starts/ends, proxy outcomes, metric tables, and failure-case plots. Record exclusions and boundary policies. Relevant tests must cover exact boundary assignment, empty resets, capture resets, mixed-window handling, singleton features, event counting, and latency.

## 14. How to Present the Result

Use a final table with one row per model/k/capture and columns for false events, eligible benign exposure, proxy recall, misses, late confirmations, median/mean delay, and processing time. Include a timeline explaining at least one successful detection and one failure.

The defensible contribution is an empirical evaluation of lightweight temporal confirmation for this dataset and threat setting. Consecutive confirmation is not itself a new general algorithm. Actual effectiveness, embedded suitability, and broader novelty must be supported by experiments and literature rather than asserted.

## 15. Sources

- Official dataset and license: https://data.mendeley.com/datasets/jfttfjn6tr/2
- A. Aqachtoul et al., *MQTTEEB-D: A Real-World IoT Cybersecurity Dataset for AI-Powered Threat Detection in MQTT Networks*, Data in Brief, 2025: https://doi.org/10.1016/j.dib.2025.111897
- Dataset creators' associated application study, listed in the release README: https://doi.org/10.1038/s41598-025-28516-2
- Detection-latency evaluation background: https://doi.org/10.1007/s10664-025-10766-3
- Original project-report bibliography, preserved with verification notes: [REPORT_REFERENCES.md](REPORT_REFERENCES.md).

## 16. Embedded Implementation and Validation

### What changed from the original proposal

The earlier report put microcontroller deployment in future scope. The current implementation trains in Python, exports its classifier to C++, and executes both inference and confirmation on a simulated ESP32. Host-precomputed feature windows are the device input. An independent network task publishes already computed status through MQTT. No temperature/sensor reading substitutes for network traffic features.

### Model export

Export original tree thresholds and leaf class proportions, average probabilities as in scikit-learn, use float32 feature inputs, and predict suspicious only for probability >0.5. Export the training medians and missing mask convention. No hard-vote substitution or quantization is used.

The host-compiled generated header was compared against Python on 11,210 inputs: all complete valid recorded windows and 321 threshold-boundary cases. Labels and probabilities matched exactly. This host verification does not alone establish target execution; actual Wokwi outputs and independently received MQTT messages provide separate evidence.

### Firmware replay

Stored clips contain original window IDs, valid/missing flags and feature values, with no ground-truth label field. Replay all intervals, including empty ones, at two simulated seconds per record. Start each excerpt with fresh counters and identify it as a validation excerpt rather than an independent experiment. Buttons control scenario, playback and labelled scripted-test mode.

The C++ counter module rejects repeated/older IDs. Missing IDs reset streaks before fresh evidence. Empty input bypasses the RF and clears confirmation. Event totals increment only on an inactive-to-active transition. Each k has separate state; all consume the same predictions. The three LEDs expose active states and the buzzer signals new k=2 events.

The default stored excerpt uses validation capture 3, windows 712-729. BENIGN TRACE uses windows 0-17 and the distinct GAP TRACE uses windows 716-733. Full-capture evaluation uses complete held-out captures, not these selected excerpts.

### Connected demonstration

A separate task owns WiFi and PubSubClient; a one-record latest-status queue prevents network retries from blocking inference. MQTT messages use a unique per-boot topic and carry mode, window, prediction, confirmation states and event totals. Delivery is best-effort, not a reliable event transport.

Actual status was received by the Python subscriber. Six checked-in received messages were compared with the frozen host model/counters with zero prediction or confirmation differences. Twelve automated tests also pass. Complete observed target verification additionally covers 90 MODEL rows across all three clips, with zero prediction/probability/state discrepancies. A controlled client target-resolution fault demonstrated six replay rows processed while the connection was broken, followed by reconnection and independently received status. See [evidence](evidence/README.md) for scope and reproduction.

Two evidence categories must remain distinct: ACTUAL_MODEL inputs execute the classifier; SCRIPTED_TEST directly injects predictions to verify counter behaviour. Never include scripted outcomes in classifier accuracy or attack-detection metrics.

### Current findings

Primary accuracy is 90.35% and SlowITe F1 is 83.87% for the same classifier on 570 pure-class windows, with confusion matrix `[[372,0],[55,143]]`. The Colab reproduction matches the existing fitted model and does not constitute independent-dataset validation. [Research findings](RESEARCH_FINDINGS.md) links the completed baseline and extended comparison/metric audits. In particular, report clean false-event starts separately from confirmed-state occupancy on benign windows; a zero count of the former does not imply zero of the latter.

Primary test RF F1 is 0.8387 and SlowITe-window recall is 0.7222. Observed-run detection is 12/12 for k=1 and k=2, and 10/12 for k=3. Mean detected-run delay is 0.888, 3.555 and 4.900 seconds respectively. Primary clean false events are zero for every k; no primary false-alarm reduction is established.

The separate held-out-capture study reveals suppression/recall/delay trade-offs. Its full tables and rate baseline are checked in; do not pool its outcomes as independent replications across environments.

### Remaining work and claim limits

Physical target timing/power, live packet capture, raw-record aggregation on ESP32, complete linker/static-RAM profiling, exhaustive network-failure testing are not completed. Simulator image/heap/timing measurements and a controlled target-resolution failure/recovery test are documented in [embedded verification](evidence/EMBEDDED_VERIFICATION.md). The optional PCAP download was declined by the browser gate. The delivered contribution is an implemented, traceable embedded simulation and dataset-specific trade-off study, not proven operational protection of a live MQTT deployment.

### Colab and report artifacts

[COLAB](COLAB.md) describes the fixed-source notebook and versioned handoff archive. `publish_results.py` regenerates the classification/persistence CSVs and both figures from measured JSON, checking classifier scores against confusion counts. It labels base-classifier FPR explicitly and exposes ambiguous/out-of-scope event counts. `package_ml_outputs.py` includes source scripts, locked requirements, source commit and artifact hashes. Newly regenerated firmware requires new target evidence if its source build changes. The original pinned notebook remains the baseline reproduction. Extended filters and independent-data experiments are reproduced by the scripts and protocol linked above.
