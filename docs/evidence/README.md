# Verification evidence

Wokwi project: https://wokwi.com/projects/478675756306751489

- `wokwi-scripted-test.png`: browser screenshot from the saved running project.
- `wokwi-serial-excerpt.txt`: explicitly transcribed excerpt of actual UI serial observations; not a full automatically exported log.
- `wokwi-ui-state.txt`: the final accessibility-state diff, supporting project identity only; it is not the complete serial transcript.
- `mqtt_received.jsonl`: actual messages received independently by Python from Wokwi through the public test broker. Contains ordinary demo status only.
- `verification.json`: reproducible comparison of those received actual-model messages with the host model and counter reference. Generate using `scripts/verify_demo_evidence.py` after training.

Simulation timing is not physical ESP32 timing. Scripted TEST mode bypasses AI deliberately to verify confirmation, not classifier quality. PCAP download was declined by the browser permission gate and is not included. Browser attachment became unavailable after that rejected download, so subsequent evidence work used the already received messages rather than claiming new browser observations.
