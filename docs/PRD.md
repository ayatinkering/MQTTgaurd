# MQTTGuard: Product Requirements and Build Plan

## 1. The Project in Plain Words

Build a program that reads recorded MQTT network traffic, learns to recognize SlowITe attack patterns, and checks whether suspicious predictions repeat before raising an alert.

There are two separate decisions:

1. **Classifier:** Does this two-second traffic summary look suspicious?
2. **Confirmation rule:** Has suspicion lasted long enough to raise an alert?

The Random Forest is the AI component. MQTT traffic from an IoT testbed is the IoT component. The first version runs offline on a laptop; a physical edge deployment is future work.

## 2. Current Status

Dataset acquisition and inspection are complete. The repository includes runnable download and inspection scripts, local downloaded data, an HTML preview, and an audit report. Model training, persistence replay, and performance evaluation remain to be implemented.

This document supersedes the initial planning document. It incorporates actual dataset inspection rather than assuming the report's proposed experiment is already valid.

## 3. Research Question and Success

**Question:** Does requiring two consecutive suspicious windows reduce false alert events while retaining attack detection and acceptable latency, compared with immediate alerting?

Compare k = 1, 2, and 3 using the same model and held-out predictions. Success means a correct, reproducible answer with transparent limitations; a negative result is acceptable. Do not promise a particular accuracy, recall, or false-alarm reduction.

The result is more convincing if improvements also survive a comparison with a simple traffic-rate baseline, reasonable window-duration sensitivity checks, and explicit examination of sparse benign traffic.

## 4. Verified Dataset Foundation

- Dataset: MQTTEEB-D, official Mendeley release **version 2**, CC BY 4.0.
- Download: https://data.mendeley.com/datasets/jfttfjn6tr/2
- Four original capture loops and one combined cleaned file are downloaded locally.
- The cleaned file has **222,813 rows and 13 columns**: 12 input columns including timestamp, plus the `label` column.
- Legitimate: **17,557** rows. SlowITe: **20,090** rows. Binary selection: **37,647** rows before windowing.
- There are **246 missing labels**; do not turn these into normal traffic.
- `tcp_time_delta` equals `timestamp` in all rows. Recalculate inter-arrival time from actual timestamps.
- Raw and cleaned files contain the same row multiset; do not combine them as extra training examples.
- Capture 4 contains only **376 Legitimate rows**, and its pure-benign two-second windows are all isolated under the inspected alignment. A false-alarm result on this capture alone cannot establish general usefulness.

See [the dataset review](DATASET_REVIEW.md) for evidence, per-capture counts, download links, and limitations.

## 5. Scope

### Included

- Local dataset validation and human-readable inspection.
- Capture-aware temporal windowing and four numerical features.
- Reproducible Random Forest training on Legitimate versus SlowITe.
- Chronological held-out replay and k = 1/2/3 confirmation.
- Classification, alert-event, episode-proxy, latency, and runtime evaluation.
- Documentation explaining what was measured and what remains uncertain.

### Deferred

Live capture, physical sensors, embedded deployment, cloud services, multiclass training, automatic blocking, and a production dashboard. Do not describe these as implemented features.

## 6. Inputs and Outputs

**Inputs:** Original loop CSVs, dataset manifest, configuration, split assignment, window duration, Random Forest parameters, and fixed seed.

**Outputs:** Validation log, windows/features, trained model and preprocessing state, held-out predictions, confirmation timeline, distinct alert events, episode outcomes, metrics, plots, and a run manifest identifying versions and inputs.

Downloaded raw CSVs and regenerated previews stay out of Git. Commit scripts, documentation, a compact dataset manifest, and a summary of verified inspection findings.

## 7. Functional Requirements

| ID | Required behaviour | How to know it works |
| --- | --- | --- |
| R1 | Download official unscaled files and verify checksums. | Every selected file matches the publisher SHA-256; provenance is saved. Implemented. |
| R2 | Inspect labels, schema, missing values, timestamps, duplicates, and temporal sparsity. | JSON audit and HTML sample tables are generated. Implemented. |
| R3 | Preserve capture identity and clock time when creating fixed windows. | Boundary examples work correctly; empty intervals remain visible; no capture concatenation. |
| R4 | Extract count, mean TCP length, mean inter-arrival time, and mean MQTT keep-alive. | Independently calculated examples agree; singleton handling is documented. |
| R5 | Train a fixed-seed Random Forest without test leakage. | Only training data fit imputation/model parameters; split and model state are saved. |
| R6 | Run k = 1, 2, and 3 on the same predictions. | Each configuration exposes state and distinct alert starts. |
| R7 | Reset persistence on empty intervals, invalid observations, capture changes, and replay starts. | Tests demonstrate that separated suspicious windows cannot become consecutive. |
| R8 | Separate ground truth from the detection path. | Labels never enter features or runtime confirmation; evaluation masks do not alter prediction state. |
| R9 | Measure classification and operational detection separately. | Metrics include denominators, event counts, misses, and latency rather than accuracy alone. |
| R10 | Expose sparsity and dataset limitations. | Per-capture metrics, availability coverage, a simple rate baseline, and an ideal-label feasibility check accompany conclusions. |
| R11 | Produce reproducible evidence. | A documented command regenerates each artifact from unchanged files and saved configuration. |

## 8. Experimental Design

Use original capture files for primary experiments. Start with loops 1 and 2 for training, loop 3 for validation, and loop 4 for testing. Freeze this assignment before tuning. Because loop 4 is unusually sparse, add a separately labelled robustness analysis using held-out captures and report its results separately from the primary test.

All captures originate on the same recorded day. This is separation by capture, not evidence of generalization across sites, days, brokers, or unseen attack types.

Use pure Legitimate and pure SlowITe windows for classifier fitting and primary classifier metrics. Run operational predictions on all valid nonempty windows of a held-out capture without consulting labels. Mixed windows and other attacks are handled by evaluation rules; ground truth must not selectively reset runtime state.

Ground-truth packet label runs are only **episode proxies** until attack execution logs establish physical attack boundaries. Name the metric accordingly. Publish any sensitivity analysis that changes episode definitions.

## 9. Ordered Build Checklist

### Stage A: Inspect and understand — complete

- [x] Find the official release, license, and download links.
- [x] Download and checksum-check the cleaned CSV, four captures, and metadata.
- [x] Run the Python inspector and generate a preview.
- [x] Record missing labels, timestamp artifact, and sparse normal windows.

### Stage B: Implement temporal data processing

- [ ] Validate schema and preserve source row/capture identifiers.
- [ ] Generate per-capture 2-second window grids without compacting gaps.
- [ ] Export feature values, missing-feature flags, and ground truth in separate fields.
- [ ] Test boundary timestamps, singletons, empty windows, and mixed labels.

**Checkpoint:** Inspect examples manually. Confirm that no timestamp, label, source ID, or future information reaches the model.

### Stage C: Establish honest baselines

- [ ] Train a Random Forest on the frozen training captures.
- [ ] Fit imputation only on training windows.
- [ ] Evaluate a count/rate threshold fitted on training/validation data.
- [ ] Save the same held-out prediction sequence for every confirmation rule.

**Checkpoint:** If a simple count threshold performs similarly, describe the limited extra value of AI instead of hiding the baseline.

### Stage D: Add confirmation and evaluation

- [ ] Implement k = 1/2/3 with consistent event counting.
- [ ] Verify reset behaviour and end-of-window alert timing.
- [ ] Run an ideal-label feasibility diagnostic to show whether windowing/persistence alone makes episodes undetectable. This diagnostic is not an ML result.
- [ ] Calculate per-capture and pooled metrics, exposure denominators, misses, and latency.
- [ ] Check window durations 1/2/5 seconds on development data as a sensitivity study; do not choose settings by test performance.

**Checkpoint:** Explain how much false-alarm suppression follows simply from isolated benign observations and state resets.

### Stage E: Produce the research evidence

- [ ] Export comparison tables and timelines, including failures.
- [ ] Measure processing time and state the hardware and timing scope.
- [ ] Write conclusions and limitations from the actual results.
- [ ] Add working training/replay commands and dependency versions to the README.

## 10. Completion Criteria

The first research implementation is complete when a new run can reproduce the split, features, model, predictions, k comparisons, and plots; meaningful temporal tests pass; all outcomes are traceable to source data; and limitations are described honestly.

No deployment or broad novelty claim follows automatically from successful offline evaluation. The contribution is an empirical study of lightweight confirmation for this MQTT setting.

## 11. How to Follow the Documents

1. Open `reports/dataset_preview.html` to see the downloaded rows and summaries.
2. Read [DATASET_REVIEW.md](DATASET_REVIEW.md) for facts established by inspection.
3. Follow the stages above to understand what to build next.
4. Use [METHODOLOGY.md](METHODOLOGY.md) for exact rules and measurement definitions.
