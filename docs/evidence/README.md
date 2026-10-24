# Verification evidence

The minimal retained evidence supports the reported results. Repeated browser accessibility snapshots, partial transcripts and superseded screenshots were removed; Git history retains them.

## Current research build

[Wokwi project](https://wokwi.com/projects/478737844363875329), fingerprint `3f718dc4c8d9ea81`.

- `research_wokwi_serial.txt`: observed serial text, 62 paired MODEL/EVIDENCE rows and complete passes of all three clips; 34 actual inference calls.
- `research_mqtt.jsonl`: 53 independently received model-status messages.
- `research_target_verification.json`: zero model, state and MQTT discrepancies, resource observations and input hashes.
- `research_wokwi.png`: actual running demo screenshot.

Full image 928,912 bytes; minimum observed free heap 211,168 bytes; evidence object 40 bytes; median/p95 simulated model-call time 140/147 microseconds. These are simulator observations, not physical power or end-to-end timing. The false/zero controlled-failure fields mean that diagnostic was not exercised on this build.

## Original baseline evidence retained for report claims

Original fingerprint `de9898239e6ee3a8`.

- `wokwi-serial-full.txt` and `target_verification.json`: 90 observed MODEL rows with zero discrepancies, 53 actual inference calls, full three-clip coverage and the controlled failed-hostname recovery test. Six replay rows were processed during the fault and status resumed after recovery.
- `mqtt_recovery.jsonl` and `mqtt_recovery_verification.json`: 11 independently received, checked model-status messages after recovery.

Original full image 928,112 bytes, minimum observed heap 214,952 bytes and median/p95 model-call time 140/147 simulated microseconds. These figures belong to the original build. The older six-message initial sample is superseded by the retained recovery sample and remains in Git history; report claims are limited to the retained samples.

## Recorded legitimate traffic fixture

`benign_workloads.pcap.gz` and `benign_workload_sessions.json` preserve a real-time local-only 120-second workload: 24 concurrent clients, six profiles, 2,335 legitimate publishes. Hashes are recorded in the manifest. Replay is automatic in `run_extended_study.py`; capture privilege is not needed for reproduction. Concurrent clients are not independent devices or days. No public attack traffic was generated.

## Reproduce checks

After the training/bundling steps in [methodology](../METHODOLOGY.md):

```bash
.venv/bin/python scripts/verify_research_target.py docs/evidence/research_wokwi_serial.txt
.venv/bin/python scripts/verify_wokwi_serial.py docs/evidence/wokwi-serial-full.txt
.venv/bin/python scripts/verify_demo_evidence.py
```

Independent reception samples are integration checks, not delivery-rate estimates. New firmware needs matching new observations. [Host C++ evidence parity](../research/evidence_cpp_parity.json) and [parser validation](../research/parser_validation.json) are separate from target execution.
