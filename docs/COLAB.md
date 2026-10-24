# ML notebook and model handoff

Open [MQTTGuard_ML_Colab.ipynb](../notebooks/MQTTGuard_ML_Colab.ipynb) in Colab and run cells in order. CPU is sufficient; no GPU or API key is required. It needs network access, git, curl and g++.

The notebook intentionally fetches the fixed original source revision `bd0022fd536751ce4e304db0df62f3507b11ffd6`, installs locked dependencies, verifies the data, trains the RF, exports C++, publishes metrics/plots, checks evidence and packages a downloadable outputs ZIP. The pinned checkout contains the original paths even where this current repository has consolidated its guides. Keep the pin unless deliberately updating the experiment version.

## What is preserved

- Notebook training recipe and baseline source revision.
- `scripts/train_pipeline.py`: fitting, validation selection, export and Python/C++ model parity.
- `firmware/mqttguard/mqttguard_model.h`: trained C++ model with imputation constants.
- `docs/results/`: primary/fold/ideal diagnostic JSON, metrics CSVs, provenance and figures.
- Current extended research scripts/results and evidence, documented in [methodology](METHODOLOGY.md).

Local training creates `reports/experiment/model.joblib`, predictions and window arrays; these are ignored rather than committed. From the current checkout, `scripts/package_ml_outputs.py` puts them in `reports/MQTTGuard_ML_outputs.zip` together with notebook, source, firmware, results and per-file hashes. Downloading raw data and rerunning training restores the artifacts on a fresh clone. Load only trusted joblib files.

Accuracy 90.35% and SlowITe F1 83.87% describe the same original model. A reproduced confusion matrix is not a new independent evaluation. Keep the fitted model, imputer, feature order, replay data and bundled sketch from the same run together.

The pinned notebook was checked for Python syntax and its pipeline/packaging sequence was exercised locally in a separate checkout; its original 12-test suite passed and generated firmware matched the original verified build. A new hosted Colab execution is not claimed. The current checkout's suite has 20 tests. Current extended experiments are reproduced using [methodology](METHODOLOGY.md), not by assuming the old notebook already runs them.

The original three-LED bundle is regenerated locally under ignored `firmware/wokwi/`. The current four-LED research demo is under `firmware/wokwi_research/`. A new ZIP does not update either online Wokwi project; changing the firmware fingerprint requires matching new target evidence.
