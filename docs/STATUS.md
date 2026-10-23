# MQTTGuard implementation status

Updated: 2026-10-23. Working implementation; final documentation pass in progress.

**Live demo:** https://wokwi.com/projects/478675756306751489

- [x] Dataset downloaded, checksummed and audited.
- [x] Installed reviewed scikit-learn and scientific-critical-thinking skills.
- [x] Trained compact RF and rate baseline; primary and four held-out-capture evaluations.
- [x] Exported soft-voting C++ model; zero Python/C++ label disagreements on all valid replay inputs plus boundary checks (see results manifest for count).
- [x] Built, saved and ran ESP32 firmware/circuit in Wokwi.
- [x] Verified actual inference and k=1/2/3 confirmation in simulation.
- [x] Verified button controls, scripted isolated/sustained positives, gaps and duplicate rejection.
- [x] Received actual Wokwi MQTT status messages in Python; evidence saved.
- [x] Seven Python/host-C++ tests passed, including the final checkpoint rerun.
- [x] Saved research summaries, diagnostic results, plot, serial evidence and screenshot.
- [ ] Finish README/PRD/methodology integration and concise demo guide.
- [ ] Final consistency checks and firmware/output agreement evidence.

## Measured primary result

Train loops 1+2, validate loop 3, test loop 4. Selected RF: 16 trees, depth 3. Window F1: 0.8387; SlowITe-window recall: 0.7222.

| k | Clean false events | Observed runs detected | Mean detection delay |
| --- | ---: | ---: | ---: |
| 1 | 0 | 12/12 | 0.888 s |
| 2 | 0 | 12/12 | 3.555 s |
| 3 | 0 | 10/12 | 4.900 s |

No false-alarm reduction is demonstrated on this primary capture: k=1 already has zero, and adjacent pure-benign windows are absent. Separate robustness results expose the trade-off, e.g. capture 1 changes 66 to 3 false events at k=2 while detections change 84/84 to 83/84. These are observed label runs from one testbed/day, not independently validated attack executions.

## Boundaries and remaining limitations

Feature extraction and training run on the host. ESP32 executes the actual trained model on replayed features; it does not sniff live traffic. MQTT reporting works through a public test broker and is best-effort. Inference remains independent of network-task retries. Physical hardware timing/power, live attacks, ThingsBoard, and raw-packet feature extraction are not implemented.

The optional Wokwi PCAP download was declined by the browser permission gate; no workaround was attempted. Serial, screenshot and externally received MQTT evidence are retained instead. Extended broker-outage/recovery verification and 1/5-second sensitivity experiments are not yet performed.
