# Verification evidence

Wokwi project: https://wokwi.com/projects/478675756306751489

- `wokwi-scripted-test.png`: browser screenshot from the saved running project.
- `wokwi-serial.txt`: actual ESP32 serial output, including real model inference and scripted module tests.
- `wokwi-ui-state.txt`: captured accessibility state supporting project identity and serial observations.
- `mqtt_received.jsonl`: actual messages received independently by the Python subscriber from Wokwi through the public test broker. Contains only ordinary demonstration status.

Simulation timing is not physical ESP32 timing. Scripted mode bypasses AI deliberately and is labelled TEST; it verifies the confirmation module, not classifier quality. PCAP download was not authorized by the browser gate and is not included.
