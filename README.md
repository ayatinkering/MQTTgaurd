# MQTTGuard

An Embedded Systems + AIoT course project: a compact Random Forest detects suspicious MQTT traffic, and an ESP32 simulated in Wokwi confirms alarms using consecutive predictions and bounded confidence evidence. The ESP32 runs actual C++ inference on prerecorded feature windows, drives LEDs/a buzzer and publishes computed status through MQTT.

**[Open the current Wokwi demo](https://wokwi.com/projects/478737844363875329)** · **[Report content](deliverables/report/REPORT_CONTENT.md)** · **[Results](docs/research/RESULTS.md)**

## Start here

| Task | Read or open |
| --- | --- |
| Run the simulation | [Demo guide](docs/DEMO.md); upload the three files in `firmware/wokwi_research/` together |
| Understand/reproduce the ML and experiments | [Methodology and commands](docs/METHODOLOGY.md) |
| Train in Colab | [Notebook](notebooks/MQTTGuard_ML_Colab.ipynb) and [version notes](docs/COLAB.md) |
| Write the report | [Editable content](deliverables/report/REPORT_CONTENT.md) and [LaTeX](deliverables/report/main.tex) |
| Inspect the data | [Dataset audit](docs/DATASET_REVIEW.md) and [hash manifest](docs/DATASET_MANIFEST.json) |
| Check measured evidence | [Alarm audit CSV](docs/research/alarm_audit.csv) and [target verification](docs/evidence/README.md) |

## What is implemented

- **AI:** training-only preprocessing, validation-selected RF (16 trees, depth 3), rate baseline, exact C++ export and feature/window sensitivity.
- **Embedded systems:** simulated ESP32 inference, timed replay, confirmation state, GPIO, debounced buttons and an independent FreeRTOS network task.
- **IoT:** MQTT intrusion-detection application plus actual status exchange with an independent subscriber.
- **Research:** stronger thresholds/temporal filters, full alarm audit, independent MQTTset checks, recorded benign traffic profiles and 18 sensitivity configurations.

Feature extraction and training run on the host. This is a trace-driven simulation; live packet sniffing, live attack protection and physical power measurements are outside its claims.

## Quick local setup and training

Python 3.12, `uv`, `git`, `curl` and `g++` are needed. Run from the repository root:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.lock
.venv/bin/python scripts/download_dataset.py
.venv/bin/python scripts/train_pipeline.py
.venv/bin/python scripts/publish_results.py
.venv/bin/python scripts/bundle_research_firmware.py
.venv/bin/python -m pytest scripts -q
```

Training creates `reports/experiment/model.joblib`, predictions and model/replay headers. The research bundler produces the current Wokwi sketch using the shared baseline source plus the evidence policy. Regeneration does not update the online project automatically. See [methodology](docs/METHODOLOGY.md) for extended experiments, report generation and ML ZIP packaging.

## Main findings

The primary classifier achieves **90.35% accuracy, 72.22% SlowITe recall and 83.87% F1** on 570 pure-class windows. These are different metrics of the same model.

At matched 83/84 run coverage in capture 1, bounded evidence reduces benign alarm occupancy **43.75%** and mean delay **15.19%** relative to k=2, while increasing benign starts from 3 to 5. It underperforms k=2 on the primary split. This is a measured tradeoff, not a universal improvement.

Independent MQTTset provides substantial benign exposure and a supplementary DoS scenario. Its SlowITe file spans only 0.696832 seconds and cannot support the chosen temporal windows. Separate adaptation results and their benign-stress failures remain explicit in the [full results](docs/research/RESULTS.md).

Current demo build `3f718dc4c8d9ea81`: 62 observed paired model/evidence rows and 53 independently received MQTT records, with zero discrepancies. The verification suite has 20 tests. Simulator measurements are distinct from physical measurements.

## Repository layout

```text
notebooks/                 Fixed-source Colab ML notebook
scripts/                   Dataset, training, evaluation, export and verification tools
firmware/mqttguard/        Shared RF/replay headers and original application source
firmware/research/         Bounded-evidence C++ policy
firmware/wokwi_research/   Current paste-ready Wokwi sketch, circuit, libraries and build ID
docs/                      Reproduction guides, data audit, protocols, results and evidence
deliverables/report/       Editable report content and LaTeX
```

Raw datasets, fitted Python models and intermediate predictions remain local under ignored `data/` and `reports/`. They can be downloaded/regenerated; the trained C++ model and all ML source are tracked. The original three-LED browser bundle is generated under ignored `firmware/wokwi/` when needed for baseline verification. Superseded documents and snapshots remain recoverable in Git history.

Ayati Rauthan · Ireshi Rawat · Pranav Tawakley.
