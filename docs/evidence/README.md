# Verification evidence

Wokwi project: https://wokwi.com/projects/478675756306751489

- `wokwi-scripted-test.png`: browser screenshot from the saved running project.
- `wokwi-serial-excerpt.txt`: explicitly transcribed excerpt of actual UI serial observations; not a full automatically exported log.
- `wokwi-ui-state.txt`: the final accessibility-state diff, supporting project identity only; it is not the complete serial transcript.
- `mqtt_received.jsonl`: actual messages received independently by Python from Wokwi through the public test broker. Contains ordinary demo status only.
- `verification.json`: reproducible comparison of those received actual-model messages with the host model and counter reference. Generate using `scripts/verify_demo_evidence.py` after training.

Simulation timing is not physical ESP32 timing. Scripted TEST mode bypasses AI deliberately to verify confirmation, not classifier quality. PCAP download was declined by the browser permission gate and is not included. Browser access later recovered. A full observed serial transcript, complete-clip validation, connection-recovery experiment and resource measurements were then captured without invoking downloads. See [EMBEDDED_VERIFICATION](EMBEDDED_VERIFICATION.md).

Extended evidence: `wokwi-serial-full.txt` is automatically extracted observed UI serial text; `target_verification.json` validates 90 MODEL rows; `mqtt_recovery.jsonl` contains actual independently received messages, checked by `mqtt_recovery_verification.json`; `wokwi-recovery.png` shows the tested project. Earlier source/UI snapshots are retained as historical evidence and may identify the preceding build.
