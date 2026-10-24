# Methodology and reproduction

This is the implementation guide for the current project. For the paper narrative use [report content](../deliverables/report/REPORT_CONTENT.md); for measured tables use [extended results](research/RESULTS.md). Run all commands from the repository root after the setup in [README](../README.md).

## Data and model

The primary source is [MQTTEEB-D v2](https://data.mendeley.com/datasets/jfttfjn6tr/2), attributed to Aqachtoul et al., [Data in Brief](https://doi.org/10.1016/j.dib.2025.111897), under CC BY 4.0. Four original captures provide 222,813 rows. The cleaned CSV duplicates their union and is not an additional training source. Read the [dataset audit](DATASET_REVIEW.md) for field semantics, hashes and class counts.

Windows are complete half-open two-second intervals anchored to each capture's first timestamp. Integer microseconds avoid floating-point boundary changes. Empty windows and original capture boundaries remain present; missing intervals reset confirmation. Only pure legitimate and pure SlowITe windows enter binary fitting/scoring. Mixed/other windows are separately audited rather than silently labelled benign.

Features, in order, are observation count, mean TCP payload length, mean within-window interarrival and mean recorded MQTT keepalive. Singleton interarrival is missing and receives a training-only median. Recorded keepalive is metadata, not a continuously measured connection setting. The supplied `tcp_time_delta` duplicates absolute time; timing is recomputed.

Train captures 1+2, validate 3, test 4. RF candidates have 8/16 trees, depth 3/5, minimum leaf size 2, balanced class weights and seed 42. Validation F1 selects the model, preferring fewer nodes/trees/depth on ties. The selected RF has 16 trees/depth 3. The export uses float32 inputs and preserves learned thresholds, leaf probabilities and soft voting. Original robustness folds rotate test capture, next cyclic validation capture and two training captures; they share a testbed/day.

```bash
.venv/bin/python scripts/download_dataset.py
.venv/bin/python scripts/inspect_dataset.py
.venv/bin/python scripts/train_pipeline.py
.venv/bin/python scripts/publish_results.py
```

The fitted imputer/model, predictions and parity inputs are generated in `reports/experiment/`. CSVs, plots and numerical JSONs are published in `docs/results/`; model and replay headers are generated in `firmware/mqttguard/`. Load only trusted joblib artifacts.

## Confirmation and research evaluation

The fixed references require k=1/2/3 consecutive positive predictions. The extension updates `e = min(h, max(0, decay * e + p - 0.5))` and confirms at `e >= h`. Empty/nonfinite input or an ID gap resets prior evidence; the current valid score may start accumulating again. Duplicate/older IDs do not advance the C++ state. A new event is an inactive-to-active transition.

Comparators include raised thresholds, majority, moving mean and EWMA. Each family's parameters are chosen on validation data to satisfy k=2 validation coverage minus 0.02, then minimize benign occupancy, starts and delay. All test results are retained, including failures. [Protocol](EXTENDED_PROTOCOL.md) records the grid and metric definitions; the [external amendment](EXTERNAL_PROTOCOL_AMENDMENT.md) records metadata-driven exclusions before scoring.

Audit v2 distinguishes current-window benign starts, legacy all-benign-evidence starts, benign time in alarm, excluded starts, run coverage, new-onset coverage, misses and conditional mean/median/p95 delay. Runs are label proxies, not independently logged attacks. Primary immediate delay is 1.055 s under v2 versus 0.888 s in legacy scoring; the model is unchanged. Never merge these definitions.

```bash
.venv/bin/python scripts/mqttset_data.py
.venv/bin/python scripts/run_extended_study.py
.venv/bin/python scripts/verify_evidence_policy.py
.venv/bin/python scripts/publish_extended_results.py
```

The external download is large. [MQTTset](https://www.kaggle.com/datasets/cnrieiit/mqttset) uses raw PCAP timestamps, not shuffled classification CSVs. Dataset versions/hashes/license caveat are in [external manifest](research/external_manifest.json). Frozen-model transfer is separate from 40/20/40 chronological adaptation with five-second guards. The independent SlowITe file spans 0.696832 s and is excluded from temporal scoring. The supplementary external attack is DoS, with scenario-level labels.

The recorded benign fixture contains 120 seconds of actual local MQTT traffic, 24 concurrent clients, six profiles and 2,335 publishes. `run_extended_study.py` restores it from `docs/evidence/benign_workloads.pcap.gz` if no local capture exists. Exact replay needs no privileged packet collection. `benign_stress.py` collects a new local-only workload if deliberately requested; this needs dumpcap capture permission. Aggregate and per-client diagnostics use different traffic scopes.

All 18 window/feature configurations are evaluated. Original-data additions remain exploratory because the original test outcomes were already inspected. Do not choose a new official model using the highest observed test F1. Current source-capture run proxies, one external attack recording and simulation measurements do not establish universal deployment reliability.

## Firmware, target evidence and checks

```bash
.venv/bin/python scripts/bundle_research_firmware.py
.venv/bin/python -m pytest scripts -q
.venv/bin/python scripts/verify_research_target.py docs/evidence/research_wokwi_serial.txt
```

`firmware/mqttguard/` contains shared baseline source. `firmware/research/evidence_policy.h` is the decision extension. The research bundler derives the current standalone Wokwi sketch without keeping duplicate intermediate headers. It also rebuilds the ignored original bundle for baseline verification. The checked-in current bundle is the convenient browser upload, not a separate hand-maintained model.

Only a matching source fingerprint can be verified by existing target logs. Retraining or changing firmware may require a new Wokwi run and new evidence. [Demo](DEMO.md) explains GPIO, buttons, FreeRTOS networking and serial commands. [Evidence](evidence/README.md) separates original-build recovery observations from research-build observations.

Optional original baseline verification after bundling:

```bash
.venv/bin/python scripts/verify_wokwi_serial.py docs/evidence/wokwi-serial-full.txt
.venv/bin/python scripts/verify_demo_evidence.py
```

## Report and ML handoff

```bash
.venv/bin/python scripts/build_research_report.py
.venv/bin/python scripts/export_report_content.py
.venv/bin/python scripts/package_ml_outputs.py
```

Report tables read canonical result JSONs; figures link to `docs/research/` without duplicate image copies. Compile `deliverables/report/main.tex` from its own directory so those relative figure paths resolve. The ZIP under `reports/` includes the fitted model, predictions, notebook, locked requirements, source, firmware, result/evidence files and SHA-256 provenance. Keep model, imputation, replay and firmware from one run together. The [Colab notebook](COLAB.md) deliberately pins the original baseline source; extended work uses the current checkout commands above.

Development used K-Dense scikit-learn and scientific-critical-thinking guidance, with attribution in the report. Skills are optional tooling, not runtime dependencies. The research claim is the implemented decision-layer variant and complete evaluation, not invention of Random Forests or sequential evidence accumulation.
