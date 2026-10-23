# MQTTGuard demonstration guide

## Before presenting

Open https://wokwi.com/projects/478675756306751489 . Keep the Wokwi tab visible while it runs. Open [RESULTS](results/RESULTS.md) alongside it. The saved project already contains the trained model and replay features; no local Python server or model API is required.

For independent MQTT reception, prepare the Python environment using the README. Start Wokwi, copy its printed `TOPIC=` value, then run:

```bash
.venv/bin/python scripts/mqtt_status.py --topic 'mqttguard/PASTE_RUN_ID/status' --seconds 180
```

Only normal demonstration status is published to a public test broker. If the broker is unavailable, show the still-running firmware/serial output and state that the connected portion needs retrying; do not claim successful reception without a received message.

## A three-to-five-minute presentation

1. **Explain the question:** a single suspicious classification may become a false alarm. Does waiting for repeated evidence improve alert reliability enough to justify delay?
2. **Start in ACTUAL_MODEL mode:** the default SlowITe clip sends stored network-feature windows into the model executing on ESP32. Show serial prediction and probability. LEDs light for k=1, then k=2, then k=3 when consecutive positives occur.
3. **Show an empty interval:** prediction -1 means unavailable, not normal; it resets the streak. The saved SlowITe clip contains both consecutive positives and empty gaps.
4. **Show MQTT:** the independent subscriber displays the same run/window and confirmation states. Explain that MQTT carries computed results; broker messages do not supply the model's answers.
5. **Press AI / TEST:** explicitly announce scripted verification mode. Isolated positives confirm only k=1; two/three consecutive positives activate the appropriate policies. Later tests include a missing source ID and duplicate ID; the duplicate is printed `accepted=0`.
6. **Show research results:** primary k=2 preserves 12/12 observed-run detections but adds delay; primary k=1 already has zero clean false events. Use the separately labelled robustness table to show suppression/recall trade-offs elsewhere.
7. **State limitations:** recorded-feature replay, one testbed/day, no live packet capture, no physical timing/power claims.

## Buttons and indicators

- NEXT TRACE: select the next validation excerpt, restart its counters.
- PAUSE / PLAY: pause/resume; replay if the excerpt ended.
- AI / TEST: toggle actual inference and scripted module verification.
- Orange/red/purple LEDs: active confirmation at k=1/2/3.
- Buzzer: short notification at a new k=2 event.

Each clip has 18 records, normally about 36 simulated seconds. They start at validation window IDs 0, 712 and 716; the SlowITe and gap clips overlap, so these are not independent evaluation sequences.

For verification, enter `verify` in serial input to run every clip at 200-ms cadence. Enter `selftest` to show controlled connection failure/recovery at the normal cadence. `metrics` prints resource/timing observations. These diagnostic timings do not replace dataset event-time latency metrics. See [verified results](evidence/EMBEDDED_VERIFICATION.md).

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Build waits in queue | Wait for the free build slot; do not buy a plan for this demo |
| No messages in subscriber | Check `MQTT_CONNECTED`, exact topic, per-boot run ID, internet access and TCP port 1883 |
| Topic changed after restart | Copy the new TOPIC line and restart the subscriber |
| Browser controls appear to do nothing | Check simulation is running, then inspect the SCENARIO line; source pin names are DevKit-v1 specific |
| Scenario ended | PAUSE / PLAY restarts it; NEXT chooses another |
| Local source changed but website did not | Regenerate bundle, replace Wokwi files and save; there is no automatic sync |
| Cannot edit someone else's saved project | Use a copy/fork under your account; record the new URL in status/docs |

Do not replace recorded features with hardcoded attack labels to create a convenient AI demonstration. Scripted tests already provide a clearly labelled way to explain confirmation logic.
