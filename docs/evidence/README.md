# Verification evidence

Wokwi project: https://wokwi.com/projects/478675756306751489

- `wokwi-scripted-test.png`: browser screenshot from the saved running project.
- `wokwi-serial-excerpt.txt`: explicitly transcribed excerpt of actual UI serial observations; not a full automatically exported log.
- `wokwi-ui-state.txt`: the final accessibility-state diff, supporting project identity only; it is not the complete serial transcript.
- `mqtt_received.jsonl`: actual messages received independently by Python from Wokwi through the public test broker. Contains ordinary demo status only.
- `verification.json`: reproducible comparison of those received actual-model messages with the host model and counter reference. Generate using `scripts/verify_demo_evidence.py` after training.

Simulation timing is not physical ESP32 timing. Scripted TEST mode bypasses AI deliberately to verify confirmation, not classifier quality. PCAP download was declined by the browser permission gate and is not included. Browser access later recovered. A full observed serial transcript, complete-clip validation, connection-recovery experiment and resource measurements were then captured without invoking downloads. See [EMBEDDED_VERIFICATION](EMBEDDED_VERIFICATION.md).

Extended evidence: `wokwi-serial-full.txt` is automatically extracted observed UI serial text; `target_verification.json` validates 90 MODEL rows; `mqtt_recovery.jsonl` contains actual independently received messages, checked by `mqtt_recovery_verification.json`; `wokwi-recovery.png` shows the tested project. Earlier source/UI snapshots are retained as historical evidence and may identify the preceding build.

## Completed research build

Project: https://wokwi.com/projects/478737844363875329 , fingerprint `3f718dc4c8d9ea81`.

- `research_wokwi_serial.txt` and `research_wokwi_ui.txt`: observed browser serial/UI evidence.
- `research_wokwi.png`: actual running demo screenshot.
- `research_mqtt.jsonl`: 53 independently received model-status records, not a delivery-rate estimate.
- `research_target_verification.json`: checks 62 paired MODEL/EVIDENCE rows and all received MQTT records; zero discrepancies. Full three-clip passes plus a partial repeated SlowITe pass; 34 actual inference calls.
- Policy object 40 bytes, full image 928,912 bytes, minimum observed heap 211,168 bytes. Median/p95 simulated model-call time 140/147 microseconds. This build did not repeat the original controlled fault diagnostic; its false/zero fault fields mean not exercised.
- `benign_workloads.pcap.gz` and session manifest: actual local-only 120-second, 24-client legitimate workload, compressed for exact reproducibility. No public attack traffic was generated.

Verify: `.venv/bin/python scripts/verify_research_target.py docs/evidence/research_wokwi_serial.txt`.
