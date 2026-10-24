# Start here: MQTTGuard teammate handoff

## Completed research extension — 24 October 2026

The stronger-policy comparisons, audit version 2, continuous legitimate workload, independent MQTTset compatibility/direct-transfer/adaptation tests, and all 18 feature/window sensitivity configurations are complete. Read the [editable report content](../deliverables/report/REPORT_CONTENT.md) for the full paper narrative and [measured extended results](research/RESULTS.md) for tables. The original results below remain a historical baseline; legacy delays and clean false-event counts must not be mixed with audit-v2 endpoints.

The new contribution is bounded gap-aware confidence accumulation with validation-only coverage-constrained calibration, implemented in C++. It is a modest application-specific extension to established sequential evidence methods. At matched 83/84 coverage in capture 1 it reduces benign occupancy 43.75% and mean delay 15.19% relative to k=2, while increasing benign starts from 3 to 5. It underperforms k=2 on the primary split; no universal advantage is claimed.

The [research Wokwi demo](https://wokwi.com/projects/478737844363875329) uses `firmware/wokwi_research/`, build `3f718dc4c8d9ea81`, and adds a fourth evidence LED. Actual verification covers 62 paired model/evidence rows and 53 independently received MQTT records, with zero discrepancies. Original firmware and its demo remain available as the fixed baseline.

MQTTset supplies substantial independent benign exposure and a supplementary DoS scenario. Its SlowITe file spans only 0.696832 seconds and cannot validate two-second temporal detection. Separate adaptation has perfect scenario-window test classification but false alarms under changed benign scope; it is not general 100% SlowITe detection. All these outcomes are retained.

Only editable report content is requested now. Slides and synopsis production are stopped; the original course PDFs are unchanged.


Updated 2026-10-24. This document carries the current project context so another teammate can continue without the chat.

## 1. What we are building now

**MQTTGuard is a trace-driven, persistence-aware MQTT intrusion detector implemented on a simulated ESP32 in Wokwi.** Python prepares recorded network traffic and trains a Random Forest. A generated C++ classifier runs inside ESP32 firmware. The same firmware confirms suspicion across consecutive windows, drives indicators, and publishes computed status over MQTT.

This remains the original topic: lightweight AI-based detection of SlowITe attacks in MQTT IoT networks. The main implementation changed from laptop-only processing to actual on-device inference under simulation. Physical hardware is not required for the course's implementation/simulation scope.

- AI = trained Random Forest, not hardcoded attack decisions.
- Embedded systems = ESP32 C++, GPIO, buttons, scheduling, state machine and network task.
- IoT = MQTT security application plus actual status exchange through an MQTT broker.
- Simulation = ESP32/circuit simulation and recorded-feature replay, not a newly generated live SlowITe attack.

**The original PDF is historical context. Current README, PRD, methodology and implementation guide describe the current version. Do not copy its old 'no microcontroller required / deployment is future work' text into the current submission.** Physical deployment remains future work, but simulated deployment already works.

## 2. Where everything is

- Repository: https://github.com/ayatinkering/MQTTguard , branch `main`.
- Existing local clone: `/home/ayati/Documents/SEM 5/ES/Proj/MQTTgaurd` (old spelling retained in the directory).
- Working Wokwi project: https://wokwi.com/projects/478675756306751489 . Saved under Ayati's account; another teammate may need to make a copy to edit it.
- Dataset: https://data.mendeley.com/datasets/jfttfjn6tr/2 . Original raw captures are local in `data/raw/` and ignored by Git.
- Original course/report materials: `/home/ayati/Documents/SEM 5/ES Proj/Theory/` on Ayati's laptop. They are not required to run the program and are not included in this repository.
- Read next: [PRD](PRD.md), [IMPLEMENTATION](IMPLEMENTATION.md), [METHODOLOGY](METHODOLOGY.md), [RESULTS](results/RESULTS.md), [DEMO](DEMO.md).

GitHub renamed the repository from MQTTgaurd to MQTTguard. Old URLs redirect. The project name remains MQTTGuard.

## 3. Fastest ways to continue

### Show the working system

Open Wokwi and press Start. Default is actual model inference on a SlowITe validation excerpt. Three LEDs compare k=1/2/3. Read serial output; try NEXT, PAUSE/PLAY and AI/TEST. Follow DEMO for the presentation and subscriber command.

### Reproduce the research from a fresh clone

```bash
git clone https://github.com/ayatinkering/MQTTguard.git
cd MQTTguard
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.lock
python3 scripts/download_dataset.py
python3 scripts/inspect_dataset.py
.venv/bin/python scripts/train_pipeline.py
.venv/bin/python scripts/publish_results.py
.venv/bin/python scripts/bundle_firmware.py
.venv/bin/python -m pytest scripts -q
.venv/bin/python scripts/verify_demo_evidence.py
.venv/bin/python scripts/verify_wokwi_serial.py docs/evidence/wokwi-serial-full.txt
```

Requires network for dependencies/data and a host `g++` compiler for export parity. Data acquisition uses curl. Training is small and CPU-only; no API key, GPU or model download is required. The locked environment was exercised on Linux/Python 3.12.14; other platforms need appropriate compiler/toolchain paths.

For the Colab workflow, use [COLAB](COLAB.md) and the checked-in notebook. It uses a fixed repository commit and calls these same scripts. `publish_results.py` also regenerates classification/persistence CSVs and the classification figure. `package_ml_outputs.py` creates a complete versioned outputs ZIP, including source scripts and artifact hashes. The friend's supplied model/predictions matched ours exactly; retain current firmware instead of the older sketch from her ZIP. No separate experimental history model was supplied.

`reports/experiment/model.joblib` is regenerated, not committed. Only load the joblib artifact created from this repository's trusted pipeline. Data/reports/virtual environments are intentionally ignored. Checked-in compact results and generated firmware let you inspect or demo without downloading the full dataset again.

## 4. Decisions already made — do not accidentally undo them

| Decision | Current value / reason |
| --- | --- |
| Main research question | False-event suppression versus detection delay/misses |
| Dataset | MQTTEEB-D v2, original capture loops, binary Legitimate/SlowITe fitting |
| Windowing | Fixed 2 seconds; preserve empty intervals and capture identity |
| Features | Count, mean TCP length, mean in-window gap, mean recorded keepalive |
| Missing interarrival | Singleton is missing, replaced with train-only median |
| Primary split | Train 1+2, validate 3, test 4; no test tuning |
| Model search | 8/16 trees × depth 3/5; seed 42; balanced weights; min leaf 2 |
| Current selected model | 16 trees, depth 3; exact soft-voting C++ export |
| Confirmation | Same predictions for k=1,2,3; gaps reset; duplicates do not advance |
| Runtime labels | Never used to decide prediction, reset or alert |
| Embedded input | Host-extracted features, not live packets or sensor readings |
| Networking | Status only; public broker, separate task, latest-message queue |
| First-version scope | No ThingsBoard, live attacks, physical device or automatic mitigation |

## 5. What is verified

- Original data files downloaded/audited and hashes recorded.
- Primary and four capture-held-out experiments, rate baseline and ideal-label diagnostic executed.
- Exported C++ matches Python on 11,210 inputs, including 321 threshold-boundary cases.
- Twelve automated tests pass, including actual C++ confirmation-module checks and target-evidence rejection cases.
- Wokwi built and ran the trained model; GPIO controls and scripted tests were observed.
- Actual MQTT messages reached the independent laptop subscriber.
- Six initial received messages and 11 later recovery-test messages match host predictions and confirmation states.
- Ninety observed MODEL rows cover complete target passes of all three distinct validation clips, with zero prediction/probability/state discrepancies.
- Controlled target-resolution failure/recovery is verified; six replay rows ran during the fault, and MQTT reception resumed.
- Simulator firmware image/heap and 53 inference timing samples are recorded in [embedded evidence](evidence/EMBEDDED_VERIFICATION.md).
- Screenshot, received JSONL and an explicitly transcribed serial excerpt are under `docs/evidence/`.

Do not overstate the scope: host parity covers all recorded valid windows, but the actual target-output evidence covers all demonstration clips and repeated passes, not all 11,210 parity inputs on the ESP32.

## 6. Results to explain accurately

Primary test window F1 is 0.8387; SlowITe-window recall is 0.7222. Observed SlowITe run detections are 12/12 at k=1 and k=2, versus 10/12 at k=3. Mean delay rises from 0.888 s to 3.555 s to 4.900 s among detected runs.

All primary clean false-event counts are zero. This capture cannot demonstrate suppression because immediate alerting already has zero and benign windows are isolated. Separate capture-held-out results show a trade-off: e.g. capture 1 changes 66 to 3 false events with k=2 while detecting 83 rather than 84 runs.

These are dataset-specific findings from one testbed/day. Run labels are proxies for actual attack timing. Simulated inference measurements are not hardware latency/power benchmarks.

## 7. Known issues and prioritized next work

The requested research extensions and editable report are complete. Start from [report content](../deliverables/report/REPORT_CONTENT.md) and [all measured results](research/RESULTS.md), then adapt the prose to the course template. Slides are not requested. Original and research firmware have separate build fingerprints and evidence.

To reproduce the extended study after the original training pipeline has produced `reports/experiment/model.joblib`:

```bash
.venv/bin/python scripts/mqttset_data.py
.venv/bin/python scripts/run_extended_study.py
.venv/bin/python scripts/verify_evidence_policy.py
.venv/bin/python scripts/publish_extended_results.py
.venv/bin/python scripts/build_research_report.py
.venv/bin/python scripts/export_report_content.py
.venv/bin/python -m pytest scripts -q
.venv/bin/python scripts/verify_research_target.py docs/evidence/research_wokwi_serial.txt
```

Raw external captures are large and ignored by Git. The checked-in compressed local benign capture is replayed automatically when no local stress capture exists. Do not overwrite raw timing to make SlowITe compatible. The original pinned Colab notebook reproduces the original study; the extended commands above reproduce the new experiments. New capture collection is optional for exact replay and requires local packet capture tools.

Future extensions are independent adequately timed SlowITe sessions with attack logs, multiple sites/days, physical power/timing, live target feature extraction and exhaustive network fault testing. They are outside the delivered simulation claims. All 18 sensitivity configurations are completed and exploratory; do not select a new official model by the best observed test score.

The PCAP download was declined by the browser gate and was not retried. Browser access later recovered, allowing direct capture of observed serial text, full target verification and the controlled connection-recovery test without any browser file download. The saved Wokwi project matches the source fingerprint in firmware/wokwi/build.json.

## 8. Safe development workflow

Edit application source in `firmware/mqttguard/`, not the bundled copy. Edit Python research behaviour in `scripts/train_pipeline.py`. Run tests after changes. Retraining regenerates the model and replay header; rebundling generates the browser sketch and circuit. Update Wokwi manually after regeneration, save, test, and record the matching Git commit/project URL.

The default current Wokwi circuit needs only PubSubClient; no paid gateway, local model server or custom library upload is required. Browser code may differ from local source if somebody edits only one copy. Do not claim they match until checked.

Keep data and secrets out of commits. There are no model/API credentials in this project. Update STATUS, measured results and guides whenever scope or evidence changes. Skill installation is optional; see IMPLEMENTATION for the two reviewed guidance skills and attribution.

## 9. Report replacement paragraph

> MQTTGuard uses a trace-driven embedded simulation to evaluate lightweight intrusion detection for slow MQTT attacks. Timestamped MQTTEEB-D observations are aggregated into fixed two-second windows and represented by four traffic features. A compact Random Forest is trained using capture-separated data, and its preprocessing constants and classifier are exported to C++. The exported model executes on an ESP32 simulated in Wokwi, followed by parallel one-, two- and three-window confirmation policies. GPIO indicators and serial logs expose classification and alert transitions, while MQTT telemetry reports computed status to an independent subscriber. Full held-out replay evaluates detection performance; separate firmware checks verify numerical consistency and temporal state behaviour.

The defensible contribution is a reproducible, implemented MQTT alerting pipeline and measured trade-off study. Consecutive confirmation and using Wokwi are not by themselves novel algorithms.
