# MQTTGuard implementation status

Updated: 2026-10-23. Core implementation, complete-clip target verification, controlled connection recovery and current-version handoff documentation complete. Follow-up experiments are listed separately.

**Live demo:** https://wokwi.com/projects/478675756306751489

- [x] Dataset downloaded, checksummed and audited.
- [x] Installed reviewed scikit-learn and scientific-critical-thinking skills.
- [x] Trained compact RF and rate baseline; primary and four held-out-capture evaluations.
- [x] Exported soft-voting C++ model; zero Python/C++ label disagreements on all valid replay inputs plus boundary checks (see results manifest for count).
- [x] Built, saved and ran ESP32 firmware/circuit in Wokwi.
- [x] Verified actual inference and k=1/2/3 confirmation in simulation.
- [x] Verified button controls, scripted isolated/sustained positives, gaps and duplicate rejection.
- [x] Received actual Wokwi MQTT status messages in Python; evidence saved.
- [x] Twelve Python/host-C++ tests passed, including the final checkpoint rerun.
- [x] Saved research summaries, diagnostic results, plot, serial evidence and screenshot.
- [x] Rewritten README/PRD/methodology for the current embedded version; added implementation, demo and teammate handoff guides.
- [x] Final reproduction/test/link checks; all six initial and 11 recovery-test MQTT model records match host predictions/counters.
- [x] Complete Wokwi passes of all three distinct validation clips; 90 observed MODEL rows agree with the host reference.
- [x] Controlled target-resolution failure/recovery; inference continues during failed connections and MQTT reception resumes.
- [x] Recorded simulator image size, heap and inference-time distribution, with measurement limits.

## Measured primary result

Train loops 1+2, validate loop 3, test loop 4. Selected RF: 16 trees, depth 3. Window F1: 0.8387; SlowITe-window recall: 0.7222.

| k | Clean false events | Observed runs detected | Mean detection delay |
| --- | ---: | ---: | ---: |
| 1 | 0 | 12/12 | 0.888 s |
| 2 | 0 | 12/12 | 3.555 s |
| 3 | 0 | 10/12 | 4.900 s |

No false-alarm reduction is demonstrated on this primary capture: k=1 already has zero, and adjacent pure-benign windows are absent. Separate robustness results expose the trade-off, e.g. capture 1 changes 66 to 3 false events at k=2 while detections change 84/84 to 83/84. These are observed label runs from one testbed/day, not independently validated attack executions.

## Handoff and current verification

Start with [HANDOFF](HANDOFF.md), then [IMPLEMENTATION](IMPLEMENTATION.md), [METHODOLOGY](METHODOLOGY.md), and [DEMO](DEMO.md). Generated model export parity covers 11,210 inputs with zero label disagreements; twelve automated tests pass. The initial six-message and later 11-message integration samples are separately verified. See [embedded verification](evidence/EMBEDDED_VERIFICATION.md) for the complete target and connection-recovery evidence.

## Boundaries and remaining limitations

Feature extraction and training run on the host. ESP32 executes the actual trained model on replayed features; it does not sniff live traffic. MQTT reporting works through a public test broker and is best-effort. Inference remains independent of network-task retries. Physical hardware timing/power, live attacks, ThingsBoard, and raw-packet feature extraction are not implemented.

The optional Wokwi PCAP download was declined by the browser permission gate; no workaround was attempted. Serial, screenshot and externally received MQTT evidence are retained instead. A controlled client target-resolution failure/recovery test is now verified; exhaustive network fault testing and 1/5-second sensitivity experiments remain future work. Simulator measurements include firmware image/heap, not a full physical or linker-section resource report.
