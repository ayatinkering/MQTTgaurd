# Colab adoption: local reproduction check

Date: 24 October 2026. Implementation source commit: `bd0022fd536751ce4e304db0df62f3507b11ffd6`. The notebook deliberately pins this source checkpoint, which contains the updated publishers, packaging script and current firmware.

The new notebook's Python cells were compiled for syntax. Its computation/check/packaging sequence was then run in a separate local Git checkout of the pinned source, using the existing locked Python 3.12 environment and copied cached raw dataset files. The downloader was invoked and verified its required files. This was not a new hosted Colab execution or a fresh dependency installation.

All commands completed successfully:

1. `scripts/download_dataset.py`
2. `scripts/inspect_dataset.py`
3. `scripts/train_pipeline.py`
4. `scripts/publish_results.py`
5. `scripts/bundle_firmware.py`
6. `python -m pytest scripts -q` — 12 passed.
7. `scripts/verify_demo_evidence.py`
8. `scripts/verify_wokwi_serial.py docs/evidence/wokwi-serial-full.txt`
9. `scripts/verify_demo_evidence.py --file docs/evidence/mqtt_recovery.jsonl --output reports/colab_mqtt_recovery_verification.json`
10. `scripts/package_ml_outputs.py --output <temporary archive>`

The pinned-source archive contained 55 hashed artifacts plus its manifest; every archive member's hash matched. The regenerated standalone firmware was byte-identical to the existing verified sketch, with build fingerprint `de9898239e6ee3a8`. No online Wokwi replacement was required. Packaging the later repository checkout additionally includes the notebook itself.

The classification figure was visually inspected. Its confusion counts and percentages agree with the primary saved predictions. The adopted publisher regenerates the classification CSV/figure, persistence CSV, existing delay figure and RESULTS.md together, avoiding the older notebook's potential stale Markdown/plot problem.

This verifies the local pipeline and packaging recipe. It does not establish new classification performance, independent-dataset validity, hosted-runtime compatibility, or new online target execution. Previous Wokwi evidence remains associated with its unchanged source build.
