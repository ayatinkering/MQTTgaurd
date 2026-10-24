# Run the current Wokwi demo

Open [MQTTGuard Research on ESP32](https://wokwi.com/projects/478737844363875329) and press Start. To make your own copy, upload `sketch.ino`, `diagram.json` and `libraries.txt` from `firmware/wokwi_research/` together. The verified fingerprint is `3f718dc4c8d9ea81`.

The ESP32 runs the exported Random Forest on prerecorded feature windows and updates k=1/2/3 plus bounded evidence (h=0.75, decay=0.5). Orange/red/purple LEDs indicate k=1/2/3; green indicates bounded evidence. A buzzer signals a new k=2 event. Feature extraction and training occur on the host; MQTT status is an output, not incoming raw detector traffic.

## Controls and serial output

- **NEXT TRACE:** change between BENIGN, SLOWITE and GAP clips.
- **PAUSE / PLAY:** pause or resume timed replay.
- **AI / TEST:** switch actual model inference to explicitly scripted state tests.
- Serial command `verify`: run complete clips automatically. `MODEL` lines report predictions/counters; paired `EVIDENCE` lines report evidence/state/events. `METRICS` reports simulator measurements.
- `metrics`: print resource observations. The original firmware also supports controlled connection diagnostics with `selftest`, `fault` and `recover`; the saved fault evidence belongs to that original build.

TEST mode bypasses the model and cannot demonstrate classification accuracy. Source labels never enter runtime decisions. Empty windows skip inference and clear confirmation; duplicates do not advance state. Short demo excerpts demonstrate execution; full captures supply research metrics.

## Receive actual MQTT status

Read the exact `TOPIC=` value from the serial monitor, then run:

```bash
.venv/bin/python scripts/mqtt_status.py --topic 'PASTE_TOPIC_HERE' --seconds 120 --output reports/demo_mqtt.jsonl
```

The firmware uses WiFi and a public broker via Wokwi's gateway. A separate FreeRTOS task owns the MQTT client; a one-record overwrite queue keeps retries from blocking inference. QoS-0/latest-state reporting is best-effort and does not guarantee every event is logged. Wokwi's public gateway cannot directly reach a broker running only on the laptop.

If communication fails, inspect serial connection messages, wait for retry and check the current topic rather than reusing an earlier boot's topic. Network availability does not determine the classifier's output. No live attack is generated against the public broker.

## Verify the saved demonstration

After training and bundling, run:

```bash
.venv/bin/python scripts/verify_research_target.py docs/evidence/research_wokwi_serial.txt
```

The saved research observations have 62 paired rows and 53 independently received MQTT model-status records with zero prediction/state discrepancies. The minimum observed heap is 211,168 bytes; full image 928,912 bytes; evidence object 40 bytes. Median/p95 model-call timing is 140/147 simulated microseconds over 34 actual inference calls. Timing excludes preprocessing/network delivery and is not a physical ESP32 benchmark.

See [evidence](evidence/README.md), [results](research/RESULTS.md) and [reproduction commands](METHODOLOGY.md). Regenerating a bundle does not upload it to Wokwi or produce new target evidence.
