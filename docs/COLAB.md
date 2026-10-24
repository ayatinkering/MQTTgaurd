# Reproduce the current ML pipeline in Colab

Open [`notebooks/MQTTGuard_ML_Colab.ipynb`](../notebooks/MQTTGuard_ML_Colab.ipynb) in Google Colab and run its cells in order. CPU is sufficient; no GPU, API key, cleaned CSV upload or model service is required.

The notebook checks out an exact repository source commit, installs locked dependencies, verifies the original dataset, trains/exports the model, regenerates the result tables/CSVs/plots, runs the automated checks, and creates a downloadable outputs ZIP with source revision and SHA-256 manifests. Use a fresh Colab runtime. Training/export needs `g++`, `git`, `curl` and network access.

This replaces the friend's upload-an-unspecified-repository-ZIP workflow. Her reproduction matched our existing classifier; 90.35% accuracy and 83.87% SlowITe F1 describe the same model. We retain the current firmware, distinct gap clip and diagnostics.

## Outputs and their meaning

- `docs/results/classification_metrics.csv`: accuracy, SlowITe precision/recall/F1, macro and weighted F1, and scored window count, derived from the primary confusion matrix.
- `docs/results/classification_metrics.png`: primary confusion matrix and classifier metrics.
- `docs/results/persistence_metrics.csv`: k=1/2/3 clean false events, run proxies detected/missed, delay, confirmed benign windows, exposure and excluded/ambiguous event starts.
- `docs/results/RESULTS.md`, `primary_delay.png` and result JSONs: regenerated summaries and evidence sources.
- `firmware/wokwi/`: freshly bundled source, diagram, library list and source-build manifest.
- `reports/experiment/`: fitted model, numerical predictions and windows, generated in the same run.
- `handoff_manifest.json`: source Git commit, dataset hashes, and hashes of every other file in the handoff archive.

`base_classifier_window_FPR` in the persistence CSV is the classifier's FPR before confirmation; it repeats across k. It is not the fraction of benign windows in confirmed state. Clean false starts and time spent falsely confirmed are separate metrics. Excluded event starts must not be counted as correct detections without additional attribution.

## Version rules

Keep the model, imputation constants, feature order, replay inputs and bundled sketch from one run together. A new ZIP does not update the online Wokwi project. Compare `firmware/wokwi/build.json` with the verified project before replacing anything. If the build differs, use a copy of the project and collect new target evidence; old screenshots/timing/recovery evidence cannot verify a changed build.

The archive includes source scripts and locked requirements so the training recipe travels with the generated artifacts. Joblib is a pickle-based format; load only the artifact from a trusted run. The notebook's fixed source commit is deliberately reproducible; change it only as an explicit version update and record the new revision.

Colab hosting and Python/runtime availability may change. The notebook syntax and the same pipeline/packaging flow are checked locally; a fresh hosted Colab execution is not claimed until observed. The friend's older notebook had a saved successful Colab run using Python 3.13; our original local environment is Python 3.12.14.

See the [local reproduction check](evidence/COLAB_LOCAL_CHECK.md) for the exact commands and verification scope. The newly generated firmware matched the already verified build byte for byte.

See [research findings](RESEARCH_FINDINGS.md) for results suitable for the paper and pending experiments.
