# MQTTGuard implementation — host training, ESP32 inference, MQTT reporting

This is the current implementation, not the earlier host-only proposal. Working project: https://wokwi.com/projects/478675756306751489 . See [HANDOFF](HANDOFF.md) for setup and [METHODOLOGY](METHODOLOGY.md) for experimental definitions.

## 1. Code map and build products

| Source | Responsibility |
| --- | --- |
| `scripts/download_dataset.py`, `scripts/inspect_dataset.py` | Acquire/checksum original data; inspect schema, labels and timing |
| `scripts/train_pipeline.py` | Windowing, capture splits, training, rate baseline, temporal scoring, C++ export and parity verification |
| `scripts/publish_results.py` | Render measured JSON into a readable results table and static plot |
| `firmware/mqttguard/mqttguard_model.h` | Generated classifier and training medians; do not hand-edit |
| `firmware/mqttguard/replay_data.h` | Generated validation input clips; no ground-truth label field |
| `firmware/mqttguard/confirmation.h` | Shared, independently host-testable C++ confirmation logic |
| `firmware/mqttguard/sketch.ino` | Arduino application: scheduling, inputs/outputs and network task |
| `scripts/bundle_firmware.py` | Inline headers into `firmware/wokwi/sketch.ino` and generate circuit/library files |
| `scripts/mqtt_status.py` | Receive exact-topic messages and write JSONL evidence |
| `scripts/verify_demo_evidence.py` | Check recorded actual-model MQTT outputs against the host model and counter reference |

Generated files are checked in so Wokwi can run without retraining. `data/`, `reports/` and `.venv/` are ignored. The fitted joblib model, complete-window feature CSVs, observed-run JSON and replay prediction arrays are regenerated under `reports/experiment/`. Raw data is not embedded in Git.

Changes to training require regeneration of model/replay headers, results and the standalone sketch. Changes to application/counter source require rebundling. Neither command updates the saved website automatically.

## 2. Host experiment and model selection

`make_capture()` reads each original CSV in source order with integer-microsecond timestamps. It creates the full two-second grid and observed SlowITe label runs. Complete nonempty windows contain four features and a separate scoring label; empty intervals contain no valid classifier input.

`fit()` fits an imputer/float32/RF pipeline on training captures only. Four candidates are selected by validation F1, then smaller node count/tree count/depth. The saved primary RF is 16 trees/depth 3; seed 42, minimum leaf size 2, balanced class weights. The rate baseline tests thresholds derived from training count quantiles and selects direction/threshold on validation. All k settings reuse a model's same predictions.

Primary split is train 1+2, validate 3, test 4. Additional test=i folds use validation=i%4+1 and the other two captures for training. Each fold has separately fitted preprocessing/model. This is within-testbed evidence, not cross-site/day testing.

`confirm()` counts false-to-true confirmation transitions as events. `evaluate()` reports pure-window classification, coverage, clean benign events and observed-run detection/latency. Other-class and uncertain evidence is never silently relabelled benign. The JSON includes detected/missed run IDs and run delays.

## 3. Embedded numerical contract

The generated header exposes:

```cpp
static const float MQTTGUARD_MEDIANS[4];
static inline double mqttguard_probability(const float *x);
static inline int mqttguard_predict(const float *x);
```

Inputs are four float32 values in this order: count, mean TCP length, mean intra-window gap in seconds, mean recorded MQTT keepalive. Missing features are replaced by the exported training median before inference. Empty windows bypass inference entirely.

Each tree uses its original double threshold and leaf class proportions. The forest averages positive-class probabilities; strictly greater than 0.5 means class 1, with ties assigned class 0. There is no feature/leaf quantization or hard-vote substitution.

Host verification compiles the same header into a shared library with `g++`, compares against scikit-learn on every complete valid recorded window plus boundary inputs, and requires zero label disagreements and maximum probability error <=1e-6. The current run checks 11,210 inputs, including 321 boundary cases, with zero disagreement/error. This verifies the host-compiled export; actual ESP32 outputs also need separately identified observation evidence.

## 4. Replay input and temporal state

```cpp
struct ReplayWindow {
  uint32_t id;       // original capture-relative window index
  bool valid;       // false for empty intervals
  uint8_t missing;  // bit j: replace feature j with training median
  float x[4];
};
```

All stored clips come from validation capture 3. They preserve consecutive source IDs, including empty windows. Default startup plays the SlowITe clip. Labels are not present in this structure. The baseline BENIGN TRACE and GAP TRACE currently select the same first 18 windows: one illustrates the normal data and its sparse availability. Distinct presentation clips are a small follow-up improvement, not a different research dataset.

`Confirmation.accept(id,prediction)` returns false for duplicate/older IDs without updating counters. A nonconsecutive increasing ID resets streaks before accepting fresh evidence. Prediction -1 represents unavailable data and clears confirmation. Each policy has a capped streak, active flag and cumulative event counter. `reset()` clears temporal state while retaining totals; scenario restart assigns a fresh instance and resets totals as well.

Firmware advances one record per two simulated seconds, with a brief startup delay. Record 0's replay start is the local origin, not a claim about its absolute original epoch. Because inputs are already completed windows, their features are available at the replay tick; offline research latency still uses the original window-end timestamps. Pausing freezes replay progression; it does not change reported dataset event-time metrics.

## 5. Circuit and controls

| Function | ESP32 GPIO | DevKit v1 diagram pin |
| --- | ---: | --- |
| k=1 LED | 16 | RX2 |
| k=2 LED | 17 | TX2 |
| k=3 LED | 18 | D18 |
| Buzzer | 19 | D19 |
| NEXT TRACE button | 25 | D25 |
| PAUSE / PLAY button | 26 | D26 |
| AI / TEST button | 27 | D27 |
| Inference marker | 23 | Not wired to a logic analyzer in the current diagram |

LEDs use 220-ohm resistors. Buttons use input pull-ups and connect to ground when pressed. The sketch debounces inputs; the saved diagram disables simulated switch bounce. Serial baud is 115200. Buzzer sounds briefly on a new k=2 event, while the three LEDs show active confirmation, not latched attack history.

NEXT cycles clips and restarts counters. PAUSE/PLAY pauses or resumes, or restarts an ended scenario. AI/TEST switches between actual model replay and scripted predictions. TEST mode is visibly identified in serial/MQTT output and deliberately bypasses inference.

## 6. Network task and message interface

The Arduino loop handles replay and GPIO. A separate FreeRTOS task owns WiFi and PubSubClient. A one-entry overwrite queue transfers the newest status without blocking inference; old telemetry may be superseded during disconnection. Cumulative counters allow inspection of event totals, but this is not reliable event delivery.

- WiFi: `Wokwi-GUEST`, channel 6, no password.
- Broker: `test.mosquitto.org:1883`, ordinary public test messages.
- Topic: `mqttguard/<random-per-boot-run-id>/status`.
- Publication: QoS 0, not retained; retries approximately every five seconds while connected to WiFi.
- Library: PubSubClient 2.8 in the repository configuration.
- No incoming model commands, tokens, private data or attack traffic are required.

A representative payload shape is:

```json
{"run":"mqg-example","mode":"ACTUAL_MODEL","clip":1,"capture":3,"window":725,"prediction":1,"streak":[1,1,1],"confirmed":[1,0,0],"events":[3,1,1],"inference_us_simulated":56}
```

`prediction=-1` means unavailable. TEST messages use source-test IDs; their `capture` field remains the fixed value 3 for compatibility with this first firmware version, so consumers must use `mode` to distinguish tests from dataset observations. A future schema should make test-source identity explicit. This first interface is a demo format, not a production telemetry contract.

The subscriber receives only the exact generated topic by default. It appends JSON messages with host receive time to `reports/mqtt_received.jsonl`. Simulator time, host arrival time and dataset event time are different clocks.

Wokwi's public gateway cannot directly reach a laptop-local broker. Public test-broker availability is not guaranteed, and no performance/security claims are based on it. Extended disconnection/recovery testing remains open; observed inference before initial broker connection and task separation support operation without an initial connection.

## 7. Verification and measurement boundaries

Seven automated tests cover audit edge cases, temporal window boundaries, gaps/events, and the actual C++ confirmation header. Export parity is a separate training-stage gate. Checked-in MQTT messages provide independent reception evidence; the evidence verifier compares their actual-model outputs with the host reference.

The observed Wokwi model calls took approximately 45-56 simulated microseconds in the sampled trace, and the startup log showed 289,548 free heap bytes before network-task creation. These are observations of the simulator configuration, not physical-device benchmarks or a full memory budget. Build flash/static-RAM usage has not yet been recorded. The inference marker exists for a future logic-analyzer check.

The optional PCAP download was declined by the browser gate. Do not describe a PCAP as delivered or bypass that gate. Screenshots and received MQTT messages remain available.

## 8. Development guidance and attribution

Installed user-level guidance skills: `scikit-learn` and `scientific-critical-thinking`, from K-Dense's Scientific Agent Skills repository. These are not dependencies of the firmware or training program. To install them for Codex on another machine:

```bash
npx skills add https://github.com/k-dense-ai/scientific-agent-skills --skill scikit-learn -a codex -g -y
npx skills add https://github.com/k-dense-ai/scientific-agent-skills --skill scientific-critical-thinking -a codex -g -y
```

Source instructions were reviewed; broad skill packs and the flagged embedded-systems skill were not installed. Keep project-specific capture/time rules above generic example workflows.

Software-development guidance reference: T. Kassis, V. Agarwal, Y. He, D. Patel and A. M. Brueckner, *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, arXiv:2609.00065, 2026 (record checked 2026-10-23): https://doi.org/10.48550/arXiv.2609.00065 . This is tooling attribution, not evidence of MQTTGuard's detection effectiveness.

## 9. Primary engineering references

- Wokwi ESP32 simulation: https://docs.wokwi.com/guides/esp32
- Wokwi networking and time/capture limitations: https://docs.wokwi.com/guides/esp32-wifi
- Random Forest inference semantics: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- Public broker endpoint and availability limits: https://test.mosquitto.org/
