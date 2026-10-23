# Embedded verification extension — 2026-10-23

Project: https://wokwi.com/projects/478675756306751489 . Tested source build fingerprint: `de9898239e6ee3a8`, also printed by the saved firmware. See `firmware/wokwi/build.json` for the standalone source hash. This fingerprint identifies source, not compiler/runtime versions.

## Actual target execution

The observed serial log contains **90 MODEL rows**, covering complete passes of all three 18-record validation clips plus repeated SlowITe passes. Fifty-three rows performed actual model inference; the others were empty/unavailable inputs. The verifier compares predictions, six-decimal probabilities, duplicate acceptance, streaks, active flags and event totals with the frozen host model/counter reference. There were **zero discrepancies**.

The BENIGN, SLOWITE and GAP clips now use distinct source starts (0, 712 and 716). Fast `verify` mode runs all clips at a 200-ms display cadence; this is firmware verification only. It does not change source window duration or research latency results.

## Controlled broken-connection experiment

The `selftest` serial command replays the SlowITe clip at its normal two-second cadence. At record offset 4, the network task disconnects and switches its target to `mqttguard-offline.invalid`; at offset 10 it restores the original broker.

Observed sequence:

- Fault requested at simulated time 130866 ms.
- Failed MQTT connection attempts were logged with state -2 while the model continued processing.
- Six model/replay rows were processed between the fault-begin and fault-end markers.
- Recovery requested at 142866 ms; the outstanding failing attempt completed, then the network target changed back.
- MQTT reconnected at 145449 ms and publishing resumed.
- The independent subscriber received source windows 712-715 before the fault and 723-729 after recovery. All 11 received actual-model records matched host predictions and confirmation states.

This is a controlled client-side target-resolution fault, **not an outage induced at the public MQTT broker**. It verifies one failure/recovery path and continued inference, not exhaustive network reliability. The mailbox deliberately supersedes stale telemetry; missed statuses are not reconstructed as reliably delivered events.

## Simulator measurements

| Measurement | Observed value |
| --- | ---: |
| Full firmware image reported by ESP API | 928,112 bytes |
| Minimum free heap reported during this session | 214,952 bytes |
| Latest free heap after recovery | 220,608 bytes |
| Status snapshot size | 36 bytes |
| Three replay arrays | 1,296 bytes |
| Valid inference timing samples | 53 |
| Median simulated inference duration | 140 microseconds |
| p95 / maximum simulated inference duration | 147 / 147 microseconds |

These are measurements of the instrumented Wokwi configuration. They are not physical-chip latency/power measurements. Image size includes Arduino, networking and the application; it is not RF-only model size. Heap values do not replace a linker's complete static-RAM/section report. Timing wraps the model probability call, excluding preprocessing, GPIO update, serial and networking; it does not measure full end-to-end detection latency.

## Reproduce and verify

In Wokwi's serial input, send `verify`, then wait for END_OF_SCENARIO/METRICS. Send `selftest` to demonstrate failure/recovery. Other commands are `fault`, `recover` and `metrics`. Normal circuit button actions restore the two-second cadence and cancel automatic diagnostics.

The complete observed UI serial text was captured without invoking a browser download. No PCAP download was retried after its earlier denial.

From the repository after training:

```bash
.venv/bin/python scripts/verify_wokwi_serial.py docs/evidence/wokwi-serial-full.txt
.venv/bin/python scripts/verify_demo_evidence.py --file docs/evidence/mqtt_recovery.jsonl --output docs/evidence/mqtt_recovery_verification.json
.venv/bin/python -m pytest scripts -q
```

Evidence: `wokwi-serial-full.txt`, `target_verification.json`, `mqtt_recovery.jsonl`, `mqtt_recovery_verification.json`, and `wokwi-recovery.png`. Twelve automated tests pass, including checks that the evidence verifier rejects a wrong build, prediction, probability, or confirmation state.
