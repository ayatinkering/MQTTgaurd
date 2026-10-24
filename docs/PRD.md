# MQTTGuard PRD — Current ESP32/Wokwi Version

Updated 2026-10-23. This replaces the earlier host-only scope. Read [STATUS](STATUS.md) for verification and [HANDOFF](HANDOFF.md) to continue development.

## 1. Purpose and audience

Deliver a demonstrable Embedded Systems + AIoT course project investigating lightweight confirmation of SlowITe MQTT intrusion predictions. Students and examiners must be able to see a trained classifier execute on a simulated ESP32, understand the alert state, and independently receive its MQTT status. A teammate must be able to reproduce the research and modify the firmware without relying on chat history.

**Success is a working, reproducible system and an honest answer to the research question. A positive performance gain is not required.**

## 2. Fixed current scope

| Layer | Current implementation |
| --- | --- |
| Dataset | Original MQTTEEB-D v2 captures; Legitimate/SlowITe binary fitting |
| Host processing | Timestamp validation, full capture time grid, feature extraction and training |
| Features | Count, mean TCP length, mean intra-window interarrival, mean recorded MQTT keepalive |
| Model | Validation-selected RF, currently 16 trees/depth 3, exported to C++ |
| Embedded target | ESP32 DevKit simulated in Wokwi, Arduino C++ |
| Input to firmware | Precomputed chronological feature windows stored with firmware |
| Decision | On-device RF inference plus parallel k=1,2,3 state machines |
| Outputs | Three LEDs, buzzer, serial logs and MQTT status |
| Networking | Public broker, independent Python subscriber, separate network task |
| Research | Primary test, rate baseline, capture-held-out robustness and ideal-label diagnostic |

Live packet capture, actual broker exhaustion, physical hardware, on-device raw feature extraction, automatic blocking, ThingsBoard and cloud dashboards are outside this version. Do not describe replayed features as live traffic observations. Sensors are not required by this IDS architecture.

## 3. User flows

**Examiner:** open saved Wokwi project → start → observe actual-model trace → compare confirmation indicators → use buttons for another trace or labelled TEST mode → optionally view MQTT subscriber → inspect measured results.

**Researcher:** download audited captures → reproduce windows and train-only preprocessing → select RF on validation → freeze → evaluate full held-out timelines → inspect trade-offs and coverage → verify export → regenerate firmware assets.

**Teammate:** read HANDOFF → install locked dependencies → run tests/reproduction → inspect relevant source → make a scoped change → regenerate affected artifacts → revalidate → update online Wokwi manually and record evidence.

## 4. Requirements and acceptance status

| ID | Requirement | Current acceptance evidence |
| --- | --- | --- |
| R1 | Obtain original dataset files and verify provenance/checksums | Downloader, audit and checked-in manifest |
| R2 | Preserve capture boundaries and empty intervals | Window construction and automated boundary/empty tests |
| R3 | Keep labels/timestamps/IDs out of learned features | Four-feature schema; labels absent from firmware replay records |
| R4 | Fit imputation and RF on training data only | Explicit split and per-fit training pipeline; manifest |
| R5 | Compare one model with k=1,2,3 | Common prediction sequence and parallel firmware counters |
| R6 | Measure operational detection separately from classification | Primary/robustness JSON with exposure, misses, latency and coverage |
| R7 | Expose dataset sparsity and simple-baseline performance | Rate baseline, ideal diagnostic and adjacency counts |
| R8 | Execute actual exported model on simulated ESP32 | Running Wokwi serial outputs and received MQTT messages |
| R9 | Preserve model semantics through export | 11,210 host-C++ parity inputs, zero disagreements |
| R10 | Handle gaps, duplicate IDs, resets and distinct event starts | Shared C++ module test and labelled Wokwi TEST mode |
| R11 | Allow replay controls and readable local outputs | Working NEXT, PAUSE/PLAY and AI/TEST buttons; LEDs/serial |
| R12 | Send computed MQTT status without blocking inference | Separate network task and nonblocking latest-status mailbox; actual subscriber evidence |
| R13 | Expose connectivity limitations | Best-effort delivery and controlled target-resolution failure/recovery verified; exhaustive network fault testing remains open |
| R14 | Provide reproducible source and handoff | Locked Python dependencies, generation commands, circuit and guides |

No physical power, physical inference-latency or broad deployment claim is an acceptance requirement. Simulated timing must be labelled as simulated.

## 5. Experimental contract

- Primary: training loops 1+2; validation loop 3; test loop 4. No test-set tuning.
- Four RF candidates: 8/16 trees by depth 3/5; seed 42; minimum leaf size 2; balanced class weights. Select validation F1, break ties by fewer nodes, then trees, then depth.
- Train-only median imputation; no normalization or quantization.
- Two-second half-open windows on each capture's original grid; omit trailing incomplete interval.
- Pure target windows for fitting/classification metrics; all valid nonempty complete windows receive runtime predictions without labels.
- Gaps/empty intervals break persistence; mixed/unknown labels never drive runtime reset.
- The separately labelled robustness folds use test=i, validation=next capture cyclically, training=remaining two.
- Episode metrics refer to observed label-run proxies. Exact physical attack boundaries are unavailable.
- Full-capture metrics support research claims; short validation clips only demonstrate execution.

Details and operational metric definitions are in [METHODOLOGY](METHODOLOGY.md).

## 6. Current result and supported claim

Primary window F1 is 0.8387. k=2 detects 12/12 observed runs with mean delay 3.555 s; k=1 also detects 12/12 with 0.888 s delay and already has zero clean false events. k=3 detects 10/12. This primary result demonstrates the cost of waiting, not a false-alarm benefit.

Separate capture-held-out results show suppression with a recall/latency trade-off, e.g. capture 1 goes from 66 to 3 clean false events at k=2 while run detection goes from 84/84 to 83/84. Generalization remains limited to this testbed/day.

## 7. Deliverables and remaining extensions

Delivered core: data inspection, training/evaluation, generated embedded model, Wokwi circuit/firmware, MQTT subscriber, checked-in summaries/evidence and current-version guides.

The ML handoff additionally includes a fixed-version [Colab workflow](COLAB.md), classification/persistence CSVs, classification figure and a source/artifact-hashed outputs ZIP generator. The [research findings ledger](RESEARCH_FINDINGS.md) defines the report-ready results and pending evidence: matched-threshold/filter baselines, a full alarm-metric audit, continuous benign traces and independent-dataset validation. These are research extensions, not newly completed experiments.

Remaining extensions are prioritized in HANDOFF: remaining broader target inputs, exhaustive network failure modes, complete linker/static-RAM report, optional 1/5-second exploratory sensitivity, raw-record aggregation and optional dashboard. Complete-clip checks, controlled connection recovery and simulator image/heap/timing evidence are delivered. The main classifier and primary test must not be retuned simply to improve final numbers.

The course PDF/slides still need their proposed-software-only paragraphs replaced with the current embedded simulation description. Repository documentation supplies the correct content; it does not modify the original submitted PDF.
