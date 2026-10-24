# Extended MQTTGuard evaluation protocol

Protocol fixed 24 October 2026 before scoring new external captures or new confirmation variants. Original MQTTEEB-D outcomes have already been inspected; all added analyses on those captures are explicitly exploratory. Existing primary and firmware evidence will remain preserved.

## Scope and proposed extension

We compare alert-decision layers on identical causal Random Forest probability streams. The proposed bounded gap-aware evidence policy updates `e = min(h, max(0, decay * e + p - 0.5))` for a valid window, raises confirmation at `e >= h`, and resets on empty/missing windows. State consists of one bounded scalar and the last ID. This is an application-specific variant of established evidence accumulation, not a claim to have invented sequential detection. Its contribution will be evaluated through matched validation coverage, explicit gap handling and embedded implementation.

The original four-feature, two-second RF and k=1/2/3 experiment remains the reference. New results use an explicitly versioned alarm audit and are not substituted into old tables.

## Compared policies and selection

- Immediate probability threshold: 0.50, 0.55, ..., 0.95, plus 0.975 and 0.99.
- Consecutive positives: k=1/2/3 at probability strictly greater than 0.5.
- Causal majority: last 3 or 5 contiguous valid windows, positive vote strictly above 0.5, majority floor(n/2)+1; require a full history.
- Causal mean: last 3 or 5 contiguous valid scores, full history, thresholds 0.50, 0.60, 0.70, 0.80, 0.90.
- EWMA: alpha 0.25/0.5/0.75, initialized at the first valid score; thresholds 0.50/0.60/0.70/0.80/0.90.
- Proposed bounded evidence: h=0.1/0.25/0.5/0.75/1.0 and decay=0.5/0.8/1.0.
- Diagnostic always-positive and ideal-pure-label policies, excluded from deployable model rankings.

Each family selects parameters on its validation capture only. The recall constraint is validation run-coverage recall at least `max(0, k2_validation_recall - 0.02)`. Among feasible candidates minimize benign confirmed-window fraction, then benign false-start count, mean detection delay, and a deterministic parameter serialization. If none is feasible, select maximum validation coverage first and mark the constraint unmet. No selection uses test outcomes. Fixed k=1/2/3 and all candidate frontiers are retained even when a selected policy performs poorly.

## Alarm audit version 2

Preserve chronological empty windows. Runtime filters never read labels. Onsets are inactive-to-active transitions. Report all of:

1. Base window confusion matrix, accuracy, precision, recall, F1, with the scored denominator.
2. Alarm onsets on current pure-benign windows, on pure-SlowITe windows, and on mixed/unknown/other windows separately.
3. The legacy clean-false-event count for fixed k (all supporting windows benign), kept under its original name.
4. Confirmed benign windows, seconds and fraction of pure-benign exposure. Also count confirmed empty/unknown/other intervals. A small onset count alone is not sufficient.
5. Run coverage: any confirmed pure-SlowITe window ending within that label run, with mean/median/p95 delay among covered runs, misses and denominators. Separately report runs receiving a new onset during their interval. An already-active alarm may cover a run without generating a new onset.
6. Number of adjacent benign pairs and longest benign streak, and always-positive/ideal opportunity diagnostics.

Complete half-open windows use exact integer microseconds. Delays are observed label-run proxies unless independent attack start/stop logs exist. Benign exposure is summed eligible window duration, not wall-clock deployment time. All counts and per-window scores are archived.

## Experiments

### A Original dataset comparisons

Primary train1+2/validate3/test4, plus the same four cyclic-validation robustness folds. Train-only imputation, current fixed candidate RF grid, seed42. Fit each model once and reuse its scores for every policy. All new analyses here are exploratory because these captures have been inspected.

### B Independent MQTTset captures

Use the original authors' Kaggle release cnrieiit/mqttset version5, preferably its chronological PCAPs. Record source URLs, hashes, link types, TCP/MQTT extraction rules and measured schema compatibility before scoring. Full benign-week capture and complete SlowITe capture are the primary external pair. Other attack captures may be included as explicitly out-of-target stress cases. Do not treat a shuffled reduced CSV as continuous traffic.

First evaluate direct transfer using the frozen original model and the primary-validation-selected decision parameters, without external fitting. File-level attack scenarios are not packet-level ground truth: use known benign capture for false alarms and label attack-file outcomes as scenario-level suspicious coverage/detection. Do not claim verified SlowITe packet recall from a whole-file label.

For separately reported within-MQTTset adaptation, divide each source file's observed duration into first40% training, next20% validation and last40% testing, discarding a five-second boundary guard. Keep source identity and time order. This provides a controlled adaptation test, not a second independent site-level replication. No cross-file artificial adjacency. Report lack of multiple independent attack executions and any missing/unsupported feature rather than fabricate it. Retain poor transfer results.

### C Continuous legitimate stress

Use real independent benign MQTTset traffic and categorize non-overlapping complete chronological sessions before inspecting model scores. Also generate a separate seeded legitimate workload through a local-only MQTT broker: steady publishing, bursts, reconnects, rate changes and idle periods. Preserve actual observed times and label it as controlled benign stress, not independent recorded attacks. If accelerated timestamps are used, disclose them and keep them separate from real-time observations. No public broker attack traffic.

### D Window and feature sensitivity

Window durations1/2/5 seconds with complete empty grids. Feature sets: all4; count+length+interarrival; count+length; length+interarrival+keepalive; count+interarrival+keepalive; count+length+keepalive. Train/select on train/validation with the same RF grid and seed for each configuration. Retain all configurations; do not select the best test outcome as the official model. Report base F1 and k2/proposed-policy coverage, benign occupancy and delay. All runs on existing data are exploratory.

### E Embedded and report

Implement the proposed scalar policy as a shared C++ module and check parity/state against Python on full score streams and edge cases. Keep original firmware intact until a versioned extended sketch is tested in a copy of Wokwi. Capture actual MODEL/policy serial evidence and status reception if the new policy is demonstrated online. Clearly separate host parity, actual target coverage, simulated timings and physical claims.

Generate the report, synopsis and slides from saved measured result files. Include external-transfer failures, occupancy versus onset distinctions, temporal dependence and scenario-label limits. Literature comparison must distinguish established techniques from the modest implementation/calibration extension. No result or novelty claim is guaranteed in advance.
