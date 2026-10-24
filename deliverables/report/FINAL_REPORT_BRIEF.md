# MQTTGuard — Final research-report generation brief

**Purpose:** Supply this entire file to a report-writing assistant together with the prescribed LaTeX template. It contains the final project scope, main research claim, methodology, measured findings, proof sources and writing constraints. It is a factual writing brief, not a new experiment or an independently peer-reviewed paper.

**Project title:** MQTTGuard: A Lightweight Persistence-Aware Intrusion Detection System for Slow MQTT Attacks in IoT Networks.

**Application:** AI-based intrusion/anomaly detection in MQTT-enabled IoT networks.

**Team:** Ayati Rauthan, Ireshi Rawat and Pranav Tawakley. Copy registration numbers, roll numbers and institutional formatting from the team’s supplied template; do not invent or correct them by guessing.

**Evidence checkpoint:** Repository commit `794547460afa7e60552307507be88b52261cf929`. The scientific evidence links below are pinned to this checkpoint. New document edits do not alter those measurements.

**Narrative priority:** Consecutive-window confirmation is the main research methodology and result. Bounded confidence accumulation is a secondary exploratory extension. Keep low-level tree settings out of the presentation narrative; say that a compact RF is selected on validation data. Exact settings remain available in the source/artifacts for reproducibility.

---

## 1. Central research question and final answer

> **Can requiring consecutive suspicious predictions reduce false alarms in SlowITe MQTT detection, while maintaining attack detection and an acceptable delay?**

The initial motivation was that an isolated suspicious classification may be an error, whereas repeated suspicious classifications provide additional evidence. We test this proposition; we do not assume all false positives are isolated or all attacks create uninterrupted positives.

**Main measured answer:** On the capture-1 evaluation, requiring two consecutive suspicious windows reduced alarm starts on labelled legitimate traffic from **66 to 3 (95.45%)** and reduced legitimate time spent in alarm from **164 to 32 seconds (80.49%)**, while covering **83 of 84 observed SlowITe runs (98.81%)**. Conditional mean coverage delay increased from **1.068 to 3.172 seconds**, an increase of approximately **2.10 seconds**. One additional run was missed.

This is a positive, dataset-specific false-alarm–coverage–delay tradeoff. Whether the added delay is operationally acceptable depends on the intended deployment; no stakeholder-approved delay budget or live-service protection criterion was tested. Use “modest measured delay cost” or “a quantified delay tradeoff,” rather than “guaranteed acceptable latency.”

The capture-1 comparison is the **headline finding** because it directly demonstrates the original research question where benign alarms occur. It remains a result from the original robustness evaluation. It was highlighted after examining the results; do not call it a preregistered primary endpoint or conceal the other captures.

## 2. Paper-ready main-results paragraph

> Using identical Random Forest predictions on the capture-1 test sequence, two-window persistence reduced alarm starts on labelled legitimate traffic from 66 under immediate alerting to 3, corresponding to a 95.45% reduction. Benign confirmed windows decreased from 82 to 16, reducing benign alarm duration from 164 to 32 seconds, or 80.49%, over 3,518 seconds of eligible benign-window exposure. Observed SlowITe-run coverage decreased from 84/84 to 83/84 (98.81%), while mean delay among covered runs increased from 1.068 to 3.172 seconds. These findings support persistence-based suppression of isolated suspicious decisions on this capture, with an explicit coverage and delay cost. Results on the remaining captures and stronger alert-policy alternatives are retained to characterize the scope of this benefit.

**Use these corrected delays throughout:** `1.068 → 3.172 seconds`, approximately `+2.10 seconds`. Older files contain the legacy immediate value `0.925 seconds`, giving `+2.25 seconds` under that older definition. Do not use the legacy value in the final main table or mix it with the current audit.

## 3. Suggested abstract

MQTT intrusion detection requires both accurate classification and an operational rule for confirming suspicious observations. This work presents MQTTGuard, a lightweight Random Forest pipeline with consecutive-window confirmation and an ESP32 implementation demonstrated in Wokwi. Timestamped MQTT traffic is aggregated into two-second windows using four compact features, with training-only preprocessing and capture-separated evaluation. The principal comparison holds classifier predictions fixed and varies the confirmation rule. On the capture-1 evaluation, two-window confirmation reduced benign alarm starts from 66 to 3 and benign alarm duration from 164 to 32 seconds, reductions of 95.45% and 80.49%, respectively. Coverage was retained for 83 of 84 observed SlowITe runs, with conditional mean delay increasing from 1.068 to 3.172 seconds. A separate reference classifier evaluation achieved 90.35% accuracy and 83.87% SlowITe F1. Stronger alert-policy alternatives, independent MQTT data, legitimate workload changes and window/feature sensitivity characterize transfer and calibration limitations. Actual simulated-target inference and independently received MQTT status verify the embedded implementation. The contribution is a reproducible, lightweight confirmation methodology and measured operational tradeoff, rather than universal detection superiority.

**Suggested keywords:** AIoT; MQTT; intrusion detection; SlowITe; Random Forest; temporal persistence; ESP32; embedded simulation.

## 4. Required report structure from the supplied course brief

Use the prescribed IEEE-style LaTeX template. The attachment sets minimum content requirements; its examples are examples, not claims about MQTTGuard.

| Section | Required treatment |
| --- | --- |
| Introduction — minimum one page | IoT, AIoT, application domain, challenges, motivation, problem, objectives and brief contribution; include the application architecture |
| Literature survey — minimum one page | At least three relevant research papers, at least one journal article; critically compare problem, AI method, architecture, data, implementation/evaluation, results, strengths and limits |
| Proposed methodology — approximately two pages | Cover all twelve components in Section 7 of this brief; include the host/ESP32/MQTT architecture |
| Experimental setup and results | Lead with the consecutive-confirmation result; separate supporting ML and embedded evidence; put extended studies in concise subsections or an appendix if space is limited |
| Discussion/conclusion | Supported improvement, delay/coverage cost, research contribution, limitations and future work |
| References | IEEE style with accurate authors, titles, venues, years and DOI/links |
| Similarity report | Team obtains the institution-required Turnitin report; do not fabricate a percentage or claim that a report was generated |

Do not create slides. The requested output is report content/LaTeX. If asked later for speaking notes, each team member has approximately five minutes under the assignment brief.

## 5. Introduction: facts and argument to develop

1. IoT connects sensing, actuation and services using communication protocols. MQTT is a broker-based publish–subscribe protocol used in IoT systems.
2. AIoT adds learned classification or decision-making. Here, the AI task is distinguishing legitimate and SlowITe-related traffic windows.
3. Slow-rate MQTT attacks motivate scrutiny beyond large traffic-volume spikes. This is the motivation, not proof that our four features identify every slow attack.
4. A model’s positive prediction and a confirmed operational alarm are different decisions. Isolated errors may trigger nuisance alerts; stricter confirmation can delay or miss attacks.
5. The selected problem is this post-classification tradeoff, using a compact detector that can execute on an embedded target.
6. The original methodology is temporal persistence: compare immediate alerts with two/three consecutive positives on the same prediction sequence.
7. The implementation exports the learned model to C++ and executes it on a simulated ESP32 with GPIO and MQTT status reporting.
8. The completed findings are measured, not merely expected. The main result is the 66-to-3 benign-onset reduction with retained 83/84 run coverage and a measured delay cost.

**Problem statement:** A lightweight MQTT classifier can produce isolated suspicious predictions, but conventional window metrics do not specify when those predictions should become a confirmed alarm. MQTTGuard evaluates whether consecutive temporal evidence can reduce benign alarms while preserving observed SlowITe-run coverage at a measured delay cost.

**Objectives:** Construct a reproducible traffic representation; train and validate a compact RF; compare k=1/2/3 on frozen score streams; audit benign alarm starts and duration together with coverage/misses/delay; execute inference and confirmation on Wokwi ESP32; and evaluate stronger alternatives, independent-data compatibility and sensitivity as supporting analyses.

## 6. Literature survey and defensible research gap

If the team supplies its existing literature survey, preserve its useful comparison and structure. Check its bibliography before reproducing author names or numerical claims. The entries below provide a verified, relevant source set; they need not replace an approved survey wholesale. Avoid comparing headline accuracies across incompatible datasets as if they were a shared benchmark.

| Source | Problem, architecture and method | Evidence relevant to our project | Strength | Scope of comparison / remaining issue |
| --- | --- | --- | --- | --- |
| Vaccari, Aiello and Cambiaso, SlowITe, Sensors, 2020 [1] | Investigates a low-rate MQTT availability threat against broker services using a real network testbed | Establishes the threat motivation | Direct MQTT relevance | Attack characterization is different from evaluating a post-classification confirmation policy |
| Vaccari et al., MQTTset, Sensors, 2020 [2] | Publishes MQTT testbed traffic and attack recordings for ML evaluation | Supplies independent raw captures used in our compatibility and transfer study | Raw timestamped data | Scenario files and shuffled ML tables do not automatically establish valid sequential attack labels |
| Aqachtoul et al., MQTTEEB-D, Data in Brief, 2025 [3] | Describes an MQTT testbed dataset containing legitimate traffic and several attack categories | Source of our four original primary-study captures | Relevant MQTT/SlowITe data | The inspected release still requires timestamp, duplicate-file, sparse-window and label-run audits |
| Gavric, Bhandari and Shalaginov, Journal of Network and Systems Management, 2024 [4] | Uses periodically generated system/network metrics for time-driven ML detection | Motivates compact interval processing | Resource-aware design | Its features/testbed differ from ours; its headline accuracy is not our baseline |
| Page, Biometrika, 1954 [5] | Establishes sequential inspection/evidence methods | Context for the secondary accumulation extension | Foundational sequential reasoning | Does not make our RF-confidence rule a new general sequential algorithm or an optimal CUSUM |

For each paper in the actual survey, address the assignment’s nine items: problem, IoT architecture, AI technique, data, methodology, evaluation/results, advantages, limitations and the specific gap relevant to this project. Describe actual source limitations; do not claim a paper “never studies time” unless the paper has been checked.

**Gap wording suitable for the report:** The reviewed sources motivate MQTT security, compact ML and temporal evaluation. This project focuses on an operational question not answered by a classifier confusion matrix: how a lightweight detector should turn successive suspicious classifications into confirmed alarms, with valid time, explicit missing-evidence handling and joint reporting of false starts, benign alarm duration, coverage and delay.

**Contribution wording:** A reproducible persistence-aware MQTT alarm methodology, a full operational-metric audit and a verified trace-driven embedded implementation, with an additional bounded confidence extension. Do not claim first-ever use of persistence, globally novel Random Forest architecture, universal false-alarm reduction, or state-of-the-art performance.

## 7. Proposed methodology — all twelve course components

### 7.1 Problem statement

Translate suspicious MQTT-window classifications into operational alerts without treating every isolated positive as a confirmed incident. Evaluate the tradeoff rather than assuming more confirmation is always better.

### 7.2 Research objectives

Use the objectives in Section 5. Keep the original consecutive-confirmation question central. Confidence accumulation is an exploratory secondary objective, not the original motivation rewritten after seeing results.

### 7.3 Existing-system limitations

Immediate positive-to-alarm mapping is sensitive to classification errors. Window accuracy does not describe alarm duration, redundant transitions, missed runs or time to confirmation. Conversely, suppressing alerts indiscriminately can lower alarm counts while failing to detect attacks. These considerations motivate a multi-endpoint evaluation; they are not a claim that every published IDS lacks temporal logic.

### 7.4 Identified research gap

Evaluate a small causal decision layer on common frozen predictions, with explicit window/gap rules and auditable alarm endpoints, and demonstrate that the resulting classifier and confirmation state execute on a simulated microcontroller.

### 7.5 Proposed AI technique

A compact Random Forest binary classifier maps traffic features to a suspicious score. RF combines learned tree leaf probabilities through soft voting. A score above 0.5 is positive. These scores are not asserted to be calibrated real-world attack probabilities. Training is host-side; the learned inference function is exported to C++.

### 7.6 IoT architecture

| Layer | Implemented location and responsibility |
| --- | --- |
| Traffic source | Public MQTT capture records; local-only legitimate workload for supplementary stress |
| Preprocessing and training | Python host software audits timestamps, forms windows, fits the imputer and trains/validates the RF |
| Detector input in the demo | Label-free prerecorded feature windows with IDs, validity and missing-feature masks |
| Embedded inference | Wokwi ESP32 executes the exported C++ RF |
| Embedded decision | k=1/2/3 confirmation; current research demo additionally computes bounded evidence |
| Embedded outputs | LEDs, buzzer, buttons, serial monitor and state/resource observations |
| IoT communication | ESP32 network task publishes computed status through an MQTT broker |
| Independent verification | Python subscriber receives messages and compares them with the expected host reference |

Architecture figure content: **Recorded MQTT traffic → host temporal aggregation/features/training → verified model export → Wokwi ESP32 inference → persistence confirmation → GPIO and MQTT status → independent subscriber/application.** Clearly draw the host and ESP32 boundaries. Do not draw live sensors feeding a live ESP32 sniffer as an implemented component.

### 7.7 Data collection and provenance

Use the original four MQTTEEB-D v2 capture CSVs. Their union has 222,813 records:

| Source label | Observations |
| --- | ---: |
| Legitimate | 17,557 |
| SlowITe | 20,090 |
| DoS | 41,802 |
| Malformed | 105,528 |
| Brute force | 27,377 |
| Flood | 10,213 |
| Missing label | 246 |

The cleaned CSV has the same row multiset as the combined originals and is not added as extra training data. Keep data hashes, publisher version, source URLs and attribution. Original data are under CC BY 4.0. MQTTset licensing is recorded separately in its external manifest; raw public datasets are not redistributed in Git.

The inspected primary captures lack client identity and independently logged attack execution boundaries. Consecutive SlowITe labels define observed run proxies. The four files originate from one testbed/day, not four independent sites.

### 7.8 Data preprocessing

Parse source timestamps as exact integer microseconds. Each capture is independently anchored at its first timestamp. Use complete half-open windows `[start, start + Δ)` with `Δ = 2 seconds`; discard the trailing incomplete interval.

Keep every time bin, including empty intervals. Do not remove other attack rows before constructing the timeline. Pure legitimate and pure SlowITe windows enter binary fitting/scoring; mixed, unknown and other-class windows are separately audited at runtime. They are not relabelled benign.

The supplied `tcp_time_delta` repeats absolute timestamps, so recompute timing from `timestamp`. A singleton has no measurable interarrival interval; represent that feature as missing and impute with a median fitted only on training windows. Empty windows are not classified and clear confirmation. Separate capture boundaries are never treated as adjacent valid evidence.

### 7.9 AI/ML model and experimental splits

The four features, in fixed order, are:

1. observation count;
2. mean TCP payload length;
3. mean within-window interarrival;
4. mean recorded MQTT keepalive metadata.

For more than one observation, mean interarrival is `(last_timestamp - first_timestamp) / (count - 1)`. Keepalive values outside CONNECT are default metadata in this representation, not proof of a continuously negotiated per-client state.

RF candidates are selected by validation F1; smaller models break ties. Training-only median imputation, balanced class weights and fixed seed 42 are used. The export preserves float32 inputs, learned split thresholds, imputation constants and soft voting. No recurrent model or extra learned classifier is required for persistence.

| Evaluation | Training captures | Validation capture | Test capture | Role in final report |
| --- | --- | --- | --- | --- |
| Capture-1 / `fold_1` | 3 and 4 | 2 | 1 | Main persistence finding |
| Original reference / `primary` | 1 and 2 | 3 | 4 | Supporting classifier and deployed-model evaluation |
| Other cyclic folds | Other two captures | Next capture cyclically after test | 2, 3 or 4 | Robustness/context; keep all outcomes |

These use the same learning pipeline but are separately fitted evaluations. Do not present the reference model’s 90.35% accuracy as the classifier accuracy belonging to the capture-1 alarm-reduction table. The main k comparison holds its own fitted model and predictions fixed; only the confirmation rule changes. “Main finding” is narrative emphasis, not a renamed training split.

The Colab notebook deliberately pins an original source revision. It reproduces the reference workflow; current extended scripts reproduce the extended study. The fitted Python model and per-window predictions are generated locally; the trained C++ export is tracked in the repository.

### 7.10 Decision-making process

Let `p_t` be the suspicious score for a valid window and `yhat_t = 1` when `p_t > 0.5`, otherwise zero.

- k=1: confirm immediately on one positive window.
- k=2: require two consecutive positive valid windows.
- k=3: require three consecutive positive valid windows.

For each k, keep a bounded streak count. A negative score clears the streak. Empty input or an ID gap clears previous evidence; duplicate/older IDs do not advance state. An alarm start is an inactive-to-active transition, not every active window. Labels are used for fitting/evaluation, never for the embedded prediction or confirmation decision.

Example: `positive, negative, positive, positive` produces two separated immediate alarm starts; k=2 only confirms at the final window. A continuous legitimate misclassification can still pass k=2, and a short attack may be missed. The experiment measures these costs explicitly.

The secondary bounded extension maintains `e_t = min(h, max(0, d*e_(t-1) + p_t - 0.5))` and confirms at `e_t >= h`, with the same unavailable-input/gap resets. It adds confidence strength and decay to the original binary-streak idea. It is not the main headline result.

### 7.11 IoT/edge/cloud interaction and embedded behaviour

ESP32 inference does not depend on a cloud model. The network task owns WiFi and PubSubClient and receives snapshots through a one-record overwrite queue. This keeps connection retries from blocking replay/inference. Ordinary computed status is published using QoS 0 to a boot-specific topic; the independent Python subscriber listens to that exact topic.

Reporting is best-effort latest-state telemetry, not guaranteed delivery of every event. MQTT topic messages are not the TCP features being classified. Training and packet-window extraction run on the host. No live packet-sniffing, automated blocking, real attack generation, physical energy measurement or broker-protection guarantee is implemented.

Three LEDs indicate k=1/2/3; the current demo’s fourth green LED indicates bounded evidence. The buzzer marks a new k=2 event. Buttons select trace, pause/play and switch AI versus scripted TEST mode. TEST mode bypasses the classifier and verifies state logic only. Serial `verify` runs the demonstration clips; `metrics` prints resource observations.

### 7.12 Performance evaluation methodology

Report both classifier and operational endpoints:

| Endpoint | Exact interpretation |
| --- | --- |
| Accuracy/precision/recall/F1 | Window classification on pure legitimate/SlowITe windows |
| Benign alarm starts | Inactive-to-active transitions whose current window is pure legitimate |
| Benign confirmed windows/seconds | Labelled legitimate windows spent in confirmed state; seconds = windows × window duration |
| Benign occupancy | Confirmed legitimate windows / eligible legitimate windows |
| Legacy clean false starts | For fixed k, starts for which all k supporting windows are pure benign; not interchangeable with current-window starts |
| Excluded starts | Starts on mixed, unknown or other-class windows; neither silently correct nor silently benign |
| Observed-run coverage | At least one confirmed pure-SlowITe window ending within that label run’s observed start/end |
| New-onset coverage | A new alarm transition during that interval, distinct from an already-active alarm |
| Misses | Observed runs without qualifying coverage |
| Delay | First qualifying window end minus observed run start; conditional on covered runs |
| Median/p95 delay | Delay distribution, reported with misses and exposure, not just the mean |

Use audit version 2 from `research_core.py`. “Detected attack” in the paper should be qualified as observed SlowITe-run coverage because independent attack start/stop logs are unavailable. Sample timing is from dataset timestamps, not animation speed or accelerated Wokwi verification playback.

No statistical significance test or independent-session confidence interval was established. Do not invent p-values, confidence intervals or claims that the new rule is optimal. Mean differences are descriptive; covered-run sets can differ between policies.

## 8. Experiments and results — ordered for the final report

### E1. Main experiment: consecutive persistence versus immediate alarms

**Question:** Does waiting for two consecutive suspicious predictions reduce benign alarms at a measured coverage/delay cost?

**Design:** Evaluate k=1 and k=2 on the same capture-1 frozen RF predictions. Use train captures 3+4, validate capture 2 and test capture 1. There are 15,173 complete windows: 8,563 empty, 1,759 pure legitimate, 1,117 pure SlowITe and 3,734 mixed/unknown/other. Pure-class window scoring therefore uses 2,876 windows. Eligible benign exposure is `1,759 × 2 = 3,518 seconds`; it is summed labelled-window exposure, not a separately recorded continuous benign session. There are 84 observed SlowITe label runs.

| Measure | Immediate k=1 | Two-window k=2 |
| --- | ---: | ---: |
| Benign alarm starts | 66 | 3 |
| Benign confirmed windows | 82 | 16 |
| Benign alarm duration (s) | 164 | 32 |
| Observed-run coverage | 84/84 | 83/84 |
| Missed runs | 0 | 1 |
| Mean delay, covered runs (s) | 1.068 | 3.172 |
| Median delay, covered runs (s) | 1.022 | 3.063 |
| 95th-percentile delay, covered runs (s) | 2.146 | 6.118 |
| Excluded mixed/unknown/other starts | 484 | 327 |

**Derivations:**

- Benign-onset reduction: `(66 - 3) / 66 × 100 = 95.45%`.
- Benign-duration reduction: `(164 - 32) / 164 × 100 = 80.49%`.
- Retained run coverage: `83 / 84 × 100 = 98.81%`.
- Conditional mean-delay increase: `3.1717221205 - 1.0679048452 = 2.1038172752 seconds`, approximately `2.10 seconds`.
- Benign occupancy: `82/1759 = 4.66%` for k=1 versus `16/1759 = 0.91%` for k=2.

**Interpretation:** The same model’s predictions lead to substantially fewer benign alarms after temporal confirmation. The result is not an accuracy improvement, not proof of better classification and not a universal effect size. The decrease in covered runs and increase in p95 delay must remain visible. The missed k=2 run has saved zero-based run ID 48.

The capture-1 classifier’s own confusion is `[[1677,82],[185,932]]`, corresponding to accuracy 90.72%, precision 91.91%, recall 83.44% and F1 87.47%. These values are optional setup detail; do not substitute the separate reference classifier’s figures into E1.

**Proof:** [All selected-policy results](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/comparisons.json), select `split=fold_1` and consecutive policies k=1/2; [alarm audit CSV](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/alarm_audit.csv), select `study=fold_1`; local saved predictions `reports/experiment/fold_1_RF.npz` and source `data/raw/MQTTEEB-D_dataset_loop_1.csv`. The source window IDs and labels were checked against the saved predictions during recomputation.

### E2. Supporting classifier evaluation and reference confirmation

**Design:** Train captures 1+2, validate 3, test 4. This is separate from E1 and is the reference model used for the verified C++/Wokwi implementation.

| Classifier metric | Measured value |
| --- | ---: |
| Accuracy | 90.35% |
| SlowITe precision | 100.00% |
| SlowITe recall | 72.22% |
| SlowITe F1 | 83.87% |
| Macro F1 | 88.49% |
| Weighted F1 | 89.90% |
| Scored pure-class windows | 570 |

Confusion matrix, true rows/predicted columns:

| Actual class | Predicted legitimate | Predicted suspicious |
| --- | ---: | ---: |
| Legitimate | 372 | 0 |
| SlowITe | 55 | 143 |

The traffic-count baseline achieves F1 71.84% in this reference experiment. The RF misses 55 of 198 SlowITe windows, despite covering all 12 observed runs with k=1/2. Coverage of a run does not require every window to be classified correctly.

| Policy | Benign starts | Benign occupancy | Run coverage | Mean delay (s) |
| --- | ---: | ---: | ---: | ---: |
| k=1 | 0 | 0.00% | 12/12 | 1.055 |
| k=2 | 0 | 0.00% | 12/12 | 3.555 |
| k=3 | 0 | 0.00% | 10/12 | 4.900 |

The primary capture has zero adjacent pure-benign windows and zero benign alarm occupancy under these selected policies. It therefore cannot demonstrate additional false-alarm suppression over immediate alerting. Do not claim the main 95.45% reduction was obtained here.

The full reference capture has 3,727 complete windows: 570 pure-class, 2,575 empty and 582 mixed/unknown/other. The latter categories are excluded from binary classification scores, not erased from runtime.

**Proof:** [Classification CSV](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/results/classification_metrics.csv), [confusion-matrix figure](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/results/classification_metrics.png), [reference manifest](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/results/manifest.json), and `split=primary` in [audit-v2 comparisons](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/comparisons.json). Legacy `docs/results/persistence_metrics.csv` uses older run-delay semantics; the final narrative uses v2.

### E3. All original robustness folds

Each fold tests one capture, validates on the next cyclic capture and trains on the other two. Each fold has a separately selected/fitted model. This table uses current-window benign starts and audit-v2 delay, not legacy clean-only counts.

| Test capture | k | Benign starts | Benign confirmed windows | Covered runs | Mean delay (s) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 66 | 82 | 84/84 | 1.068 |
| 1 | 2 | 3 | 16 | 83/84 | 3.172 |
| 1 | 3 | 4 | 13 | 81/84 | 5.091 |
| 2 | 1 | 16 | 18 | 24/24 | 1.165 |
| 2 | 2 | 1 | 2 | 24/24 | 3.332 |
| 2 | 3 | 0 | 1 | 23/24 | 5.184 |
| 3 | 1 | 10 | 14 | 12/12 | 0.841 |
| 3 | 2 | 3 | 4 | 12/12 | 3.175 |
| 3 | 3 | 1 | 1 | 12/12 | 5.675 |
| 4 | 1 | 0 | 0 | 12/12 | 1.055 |
| 4 | 2 | 0 | 0 | 12/12 | 3.555 |
| 4 | 3 | 0 | 0 | 10/12 | 4.947 |

The original-question benefit is supported by nonzero benign-alarm reductions on captures 1–3; capture 4 provides no immediate benign alarms to reduce. The magnitude and coverage/delay tradeoff vary. Do not average fold percentages or pool the temporally dependent captures as independent deployments. Report the headline E1 result with this wider context.

### E4. Stronger alternatives and confidence-accumulation extension

**Question:** Is consecutive confirmation preferable to simply changing a score threshold or using a small temporal filter?

Compare the same causal RF score streams using raised thresholds, majority vote, moving mean, EWMA and bounded confidence accumulation. Parameters are selected on validation data under a coverage constraint: at least fixed-k2 validation coverage minus 0.02. Among feasible candidates minimize benign occupancy, then benign starts, then mean delay. Infeasible constraints are recorded. Test frontiers are descriptive and not used to choose parameters.

| Reference policy | Selected parameters | Run coverage | Mean delay (s) | Excluded starts |
| --- | --- | ---: | ---: | ---: |
| Consecutive | k=1 | 12/12 | 1.055 | 65 |
| Consecutive | k=2 | 12/12 | 3.555 | 30 |
| Consecutive | k=3 | 10/12 | 4.900 | 22 |
| Raised threshold | threshold=0.95 | 12/12 | 4.055 | 19 |
| Majority | width=3 | 12/12 | 4.555 | 28 |
| Moving mean | width=3, threshold=0.8 | 10/12 | 4.900 | 22 |
| EWMA | alpha=0.5, threshold=0.9 | 11/12 | 2.171 | 29 |
| Bounded extension | h=0.75, decay=0.5 | 11/12 | 5.251 | 16 |

All selected policies in this reference table have zero benign occupancy. The primary-validation bounded setting is `h=0.75, decay=0.5`; it covers 11/12 and is slower than k=2. Preserve this negative result.

At matched observed capture-1 coverage:

| Policy | Benign starts | Benign confirmed windows | Run coverage | Mean delay (s) |
| --- | ---: | ---: | ---: | ---: |
| k=2 | 3 | 16 | 83/84 | 3.172 |
| Threshold 0.99 | 5 | 5 | 83/84 | 3.001 |
| Bounded evidence, h=0.5 and decay=0.5 | 5 | 9 | 83/84 | 2.690 |

The bounded extension reduces benign occupancy 43.75% and mean delay 15.19% relative to k=2 but increases benign starts. The threshold rule has lower occupancy than bounded evidence but greater mean delay. Describe alternative operating tradeoffs, not universal superiority. Parameters differ across validation splits; observed equal test coverage is not a guarantee from validation calibration.

**Proof:** [Validation grids and selected parameters](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/validation_frontiers.json), [descriptive test frontiers](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/test_frontiers.json), and [selected-policy results](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/comparisons.json).

### E5. Alarm-metric audit and diagnostics

Always-positive and ideal-pure-label controls expose misleading metrics and are not deployable-model competitors. On the reference capture, the always-positive diagnostic has 100% benign occupancy, while the legacy clean k>=2 false-start count is structurally constrained by isolated benign windows.

Distinguish persistent false state from new false starts: on capture 2, k=2 has one current-window benign onset and two benign confirmed windows, despite zero legacy all-supporting-windows-benign starts. This is why the final report uses the broader current audit.

**Proof:** [Complete audit](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/alarm_audit.csv) and [audit implementation](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/scripts/research_core.py).

### E6. Independent timestamped MQTTset data

**Question:** Does the representation and detector transfer beyond the original source testbed?

| Capture/check | Measured finding | Valid interpretation |
| --- | --- | --- |
| Full benign capture | 11,915,716 TCP records; 302,551 complete two-second windows; 605,102 seconds of benign exposure; frozen model produces zero benign alarms for evaluated policies | Independent benign exposure evidence |
| SlowITe PCAP | 9,202 records spanning 0.696832 seconds; no complete 1/2/5-second window | Excluded from temporal scoring; no independent temporal SlowITe detection claim |
| SlowITe parser check | All 9,202 author-CSV records match independent extraction for timestamps, TCP payload lengths and keepalive | Measurement/parser validation, not attack detection |
| Supplementary MQTT DoS capture | 130,223 records over 126.849502 seconds; 63 complete two-second windows | Temporally usable broader DoS scenario, not SlowITe validation |
| Frozen-model DoS transfer | Immediate covers 1/1 scenario after 28 s; k2/k3 and primary bounded rule cover 0/1 | Stricter confirmation can miss external suspicious activity |

A separate adapted model uses chronological first40%/next20%/last40% per source with five-second boundary guards. Its test scenario-window confusion is `[[121017,0],[0,22]]`. Immediate/bounded coverage delay is 3.4 s from the retained test-segment boundary; k2/k3 are 5.4/7.4 s. This perfect scenario-window classification has strong file separation and only one attack recording. It is not 22 independent attacks, independent-site validation or universal 100% accuracy.

No timestamps were expanded or attack sessions fabricated. The metadata-driven exclusion/amendment was recorded before external scores were examined. The benign PCAP has 23 timestamp inversions that are aggregated using their true timestamps; CONNECT-fragment metadata are assigned to the completing segment after parser validation.

**Proof:** [External manifest](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/external_manifest.json), [results](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/external_results.json), [parser validation](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/parser_validation.json) and [protocol amendment](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/EXTERNAL_PROTOCOL_AMENDMENT.md).

### E7. Recorded legitimate workload changes

**Design:** 24 concurrent Paho software clients run six legitimate profiles, four fixed seeds each, for 120 real seconds against a local-only broker: steady, bursts, reconnects, rate changes, idle and combined. Actual packet capture contains 2,335 legitimate publishes. It yields 60 complete aggregate windows.

| Model | Policy | Aggregate benign alarm windows | Aggregate starts |
| --- | --- | ---: | ---: |
| Original frozen | k1/k2/k3/bounded | 0/60 for each | 0 for each |
| Separately adapted | Immediate | 1/60 | 1 |
| Separately adapted | k2 or k3 | 0/60 | 0 |
| Separately adapted | Bounded | 1/60 | 1 |

Narrower per-client diagnostics comprise 1,219 eligible benign windows. Adapted k2 has 74 confirmed windows and 57 starts; adapted bounded evidence has 264 confirmed windows and 190 starts. The original frozen model remains quiet on the retained per-client diagnostics. Do not treat the 24 concurrent clients as 24 independently captured physical devices/days or compare per-client and global scopes as identical deployments.

**Finding:** Perfect adapted scenario-window classification does not guarantee low alarms under changing legitimate behaviour and scope. This supports the need to evaluate operational alarm behaviour beyond a confusion matrix.

**Proof:** [Workload manifest](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/evidence/benign_workload_sessions.json), [stress results](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/benign_stress_results.json) and the checked-in compressed packet fixture `docs/evidence/benign_workloads.pcap.gz`.

### E8. Window and feature sensitivity

| Feature set | F1, 1 s | F1, 2 s | F1, 5 s |
| --- | ---: | ---: | ---: |
| All four | 0.8830 | 0.8387 | 0.4026 |
| No keepalive | 0.8893 | 0.8455 | 0.4054 |
| Count and length | 0.8851 | 0.5118 | 0.3993 |
| No count | 0.8830 | 0.8421 | 0.8357 |
| No length | 0.7943 | 0.7143 | 0.7216 |
| No interarrival | 0.8851 | 0.8387 | 0.8357 |

The full grid is three durations × six feature sets = 18 configurations. All configurations’ k2 policies cover 12/12 primary run proxies despite substantial differences in window F1. Removing count at five seconds gives F1 0.8357 versus 0.4026 with all four features. At two seconds, count+length alone gives F1 0.5118.

These findings show feature–duration interaction. Durations change the pure/mixed/complete window cohort, so F1 values are not paired predictions on identical examples. The original captures had already been inspected; sensitivity and other added original-data analyses are exploratory. The best observed test configuration was not promoted to a newly validated final model.

**Proof:** [All sensitivity results](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/sensitivity.json) and [figure](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/sensitivity.png).

### E9. Embedded execution and numerical consistency

| Check | Observed result | What it supports |
| --- | --- | --- |
| RF Python/C++ export parity | 11,210 inputs, including 321 threshold-boundary cases; zero label disagreements | Numerical consistency of the exported model on tested inputs |
| Actual C++ evidence-policy parity | 2,721,252 score-policy transitions; zero state/event discrepancies | Decision-layer arithmetic and state semantics |
| Observed target model/evidence rows | 62 paired rows; zero discrepancies | Actual simulated-target execution |
| Independently received MQTT records | 53; zero prediction/state discrepancies | Actual status exchange and output consistency |
| Automated checks | 20 passing tests | Window, parser, policy and evidence-verifier checks |
| Evidence-policy object | 40 bytes including configuration, state and counters | Small decision-layer state, not total model size |
| Full research firmware image | 928,912 bytes | Full application/runtime image, not RF-only footprint |
| Minimum observed free heap | 211,168 bytes | Observed simulated runtime availability |
| Median/p95 model-call timing | 140/147 simulated microseconds over 34 inference calls | Model-call observation, not physical or end-to-end latency |

The complete current research project is [Wokwi project 478737844363875329](https://wokwi.com/projects/478737844363875329), fingerprint `3f718dc4c8d9ea81`. It executes the reference exported classifier plus k1/k2/k3 and bounded confirmation. Its demonstration clips are from validation capture 3. It does not replay the complete capture-1 robustness experiment on target; offline scoring and target integration are distinct evidence categories.

Sixty-two paired rows include 34 actual classifier calls and unavailable-input rows. Fifty-three received MQTT records verify actual status integration, not the percentage of all statuses delivered. Complete BENIGN, SLOWITE and GAP clips are observed. Short clips are not the dataset used to estimate research accuracy.

Original-build recovery evidence is retained separately: fingerprint `de9898239e6ee3a8`, 90 observed MODEL rows, 53 inference calls, six replay rows processed during a controlled failed-hostname interval, and 11 independently received recovery messages. That fault diagnostic was not repeated for the current research build. The current JSON’s false/zero fault fields mean not exercised, not failure.

**Proof:** [Current verification](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/evidence/research_target_verification.json), [observed serial text](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/evidence/research_wokwi_serial.txt), [actual received MQTT](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/evidence/research_mqtt.jsonl), [screenshot](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/evidence/research_wokwi.png), [C++ policy parity](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/research/evidence_cpp_parity.json), and [original target verification](https://github.com/ayatinkering/MQTTguard/blob/794547460afa7e60552307507be88b52261cf929/docs/evidence/target_verification.json).

## 9. Final contribution, limitations and claim boundaries

**Supported contribution:** A lightweight persistence-aware MQTT alarm decision methodology with reproducible capture-separated experiments and verified embedded execution, showing a substantial reduction in labelled benign alarm starts and duration on the headline capture at a quantified coverage/delay cost. The confidence-based decision variant and full alarm audit add modest methodological depth.

**Limitations that must remain in the report:**

- The headline result is one source-capture robustness outcome, highlighted after results were known. It is not an independently replicated population effect or a preregistered new primary endpoint.
- Original captures share one testbed/day; runs are label proxies without independent attack execution logs.
- Different train/validation/test partitions use separately fitted models. Reference classifier metrics, capture-1 policy outcomes and target observations have distinct roles.
- Delays are conditional on coverage; a mean can look better if difficult runs are missed. The mean difference compares covered sets of different sizes.
- Eligible benign exposure excludes other/mixed/unknown intervals; excluded events remain visible.
- A primary test with zero immediate benign alarms cannot demonstrate suppression, and sparse benign adjacency can constrain clean false-start counts.
- Independent MQTTset SlowITe timing is incompatible. The independent DoS test is supplementary, not a replacement SlowITe claim.
- Separate external adaptation and concurrent software stress are not independent physical deployment replications.
- Additional original-data tuning is exploratory; the best inspected test score is not a newly validated model.
- Simulated ESP32 inference is verified; physical power/latency, live packet extraction and protection of an attacked service are not established.
- No general optimality, statistical significance or state-of-the-art superiority is claimed.

These limitations qualify generalization; they do not erase the measured E1 result or the implemented course demonstration.

## 10. Paper-ready conclusion

> MQTTGuard investigated whether consecutive suspicious predictions can improve alarm behaviour in a lightweight MQTT intrusion detector. On the capture-1 evaluation, two-window confirmation reduced benign alarm starts by 95.45% and benign alarm duration by 80.49%, while retaining coverage of 83/84 observed SlowITe runs. Conditional mean delay increased by approximately 2.10 seconds and one additional run was missed. The result supports persistence-aware alarm suppression under the evaluated conditions, rather than universal superiority. A separate reference evaluation and actual Wokwi ESP32 execution establish the classifier and embedded implementation, while stronger alternatives, independent-data checks, legitimate workloads and sensitivity analyses characterize important limits. Future work should test independently timed SlowITe sessions, additional sites/days and live or physical deployment measurements.

## 11. Future work and completion status

Completed: model pipeline, k1/k2/k3 comparisons, main alarm audit, stronger simple alternatives, bounded extension, independent timestamp checks/direct transfer/adaptation, real-time legitimate stress, all 18 sensitivity configurations, C++ parity and current Wokwi/MQTT verification.

Future work: independently timed SlowITe executions with attack logs; multiple days/sites; matched deployment observation scopes; physical timing/power; live packet-window extraction; broader fault testing; multiclass detection and evaluated broker mitigation.

Report preparation still requires the team to apply its approved LaTeX template, verify author/institution details, review wording/citations, obtain the required institutional similarity report and rehearse the presentation. Do not imply these administrative steps have already been completed.

## 12. Reproduction and proof package

From a fresh checkout with Python 3.12, uv, git, curl and g++:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.lock
.venv/bin/python scripts/download_dataset.py
.venv/bin/python scripts/inspect_dataset.py
.venv/bin/python scripts/train_pipeline.py
.venv/bin/python scripts/publish_results.py
.venv/bin/python scripts/mqttset_data.py
.venv/bin/python scripts/run_extended_study.py
.venv/bin/python scripts/verify_evidence_policy.py
.venv/bin/python scripts/publish_extended_results.py
.venv/bin/python scripts/bundle_research_firmware.py
.venv/bin/python -m pytest scripts -q
.venv/bin/python scripts/verify_research_target.py docs/evidence/research_wokwi_serial.txt
.venv/bin/python scripts/package_ml_outputs.py
```

The external PCAP download is large. The exact local benign fixture is restored automatically; rerunning `benign_stress.py` is not required for reproducing the saved study and would create a new capture. No new Wokwi observations are produced by running Python verification: the verifier checks recorded target evidence against matching source/model state.

The original Colab notebook remains under `notebooks/`. Raw data and Python models are local under ignored `data/` and `reports/`; the output ZIP includes the fitted model, predictions, notebook, source, firmware, result/evidence files and hashes. Generated source changes require new target evidence if their fingerprint changes.

**Proof chain:** original data/version hashes → complete window grid → fitted imputer/RF and saved per-window predictions → identical-score policy replay → saved audit counts/delays → reported table. Separately: exported C++ → host parity checks → actual ESP32 serial observations → independent MQTT reception → matching verifier output.

For sir, open the E1 table and its audit rows, the reference confusion matrix, and the working Wokwi demo. The serial monitor proves execution; it does not by itself prove the full-capture 95.45% reduction.

## 13. IEEE-style source references

[1] I. Vaccari, M. Aiello, and E. Cambiaso, “SlowITe, a novel denial of service attack affecting MQTT,” *Sensors*, vol. 20, no. 10, Art. no. 2932, 2020, doi: [10.3390/s20102932](https://doi.org/10.3390/s20102932).

[2] I. Vaccari, G. Chiola, M. Aiello, M. Mongelli, and E. Cambiaso, “MQTTset, a new dataset for machine learning techniques on MQTT,” *Sensors*, vol. 20, no. 22, Art. no. 6578, 2020, doi: [10.3390/s20226578](https://doi.org/10.3390/s20226578).

[3] A. Aqachtoul, K. Karam, A. Elamrani, M. Najib, N. Rafalia, and M. Bakhouya, “MQTTEEB-D: A real-world IoT cybersecurity dataset for AI-powered threat detection in MQTT networks,” *Data in Brief*, vol. 62, Art. no. 111897, 2025, doi: [10.1016/j.dib.2025.111897](https://doi.org/10.1016/j.dib.2025.111897). Dataset release: [Mendeley v2, 10.17632/jfttfjn6tr.2](https://data.mendeley.com/datasets/jfttfjn6tr/2).

[4] N. Gavric, G. P. Bhandari, and A. Shalaginov, “Towards resource-efficient DDoS detection in IoT: Leveraging feature engineering of system and network usage metrics,” *Journal of Network and Systems Management*, vol. 32, Art. no. 69, 2024, doi: [10.1007/s10922-024-09848-2](https://doi.org/10.1007/s10922-024-09848-2).

[5] E. S. Page, “Continuous inspection schemes,” *Biometrika*, vol. 41, nos. 1–2, pp. 100–115, 1954, doi: [10.1093/biomet/41.1-2.100](https://doi.org/10.1093/biomet/41.1-2.100).

[6] T. Kassis, V. Agarwal, Y. He, D. Patel, and A. M. Brueckner, “Scientific Agent Skills: A library of procedural knowledge for research agents,” arXiv:2609.00065, 2026, doi: [10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065). Software/research-workflow attribution, not an MQTT detection baseline. AI-assisted development/drafting was used; the measurements come from executable scripts and retained observations. Apply the institution’s disclosure rules.

Keep any additional approved survey papers only with accurately checked metadata and source-supported claims. In particular, attribute the dataset to Aqachtoul et al.; a separate later MQTTEEB-D benchmark article is not the original dataset publication. Gavric’s coauthors are G. P. Bhandari and A. Shalaginov.

## 14. Copy-paste instruction for the report-writing GPT

> Write a complete research report in the supplied prescribed IEEE LaTeX template using this brief as the authoritative project record. Keep the original question about consecutive suspicious predictions as the central research question. Lead the abstract, results and conclusion with the E1 finding: 66-to-3 benign starts, 164-to-32 seconds benign alarm duration, 83/84 observed-run coverage and 1.068-to-3.172-second conditional mean delay. Use current audit-v2 values consistently. Present the separate reference classifier evaluation and actual ESP32/MQTT verification as supporting evidence. Keep tree-depth details out of the presentation narrative; explain validation-selected RF configuration only as needed. Do not combine different evaluation partitions into one model/test. Treat confidence accumulation, external transfer, benign stress and sensitivity as secondary studies, retaining their limitations and negative findings. Include at least one page of introduction, one page of critical literature survey with at least three papers/one journal paper, and approximately two pages of methodology covering all twelve required components with a host/ESP32/MQTT architecture figure. Preserve the supplied approved literature survey where appropriate, while correcting bibliography errors and avoiding unsupported universal novelty claims. Write in completed-study tense for measured results. Do not invent experiments, numerical improvements, statistical significance, live hardware tests, Turnitin reports or guarantees that delay is acceptable. Cite datasets, literature and evidence sources correctly. Put detailed supplementary results in an appendix if needed for length. Generate report content/LaTeX only; no slides.
