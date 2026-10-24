# Completed extended MQTTGuard study

All results are measured outputs of the saved protocol and metadata-driven external amendment. Original-data additions are exploratory because the original test outcomes were already inspected. The course report uses these definitions rather than silently mixing legacy and version-2 metrics.

## Main report finding: consecutive confirmation

The main research question is whether consecutive suspicious predictions reduce benign alarms while retaining observed SlowITe-run coverage at a measured delay cost. Confidence accumulation is a secondary extension. See the [final report-generation brief](../../deliverables/report/FINAL_REPORT_BRIEF.md) for the authoritative narrative, complete methodology and proof sources.

| Capture-1 measure | Immediate k=1 | Two-window k=2 |
| --- | ---: | ---: |
| Benign alarm starts | 66 | 3 |
| Benign confirmed windows | 82 | 16 |
| Benign alarm seconds | 164 | 32 |
| Observed-run coverage | 84/84 | 83/84 |
| Mean covered-run delay s, audit v2 | 1.068 | 3.172 |

Two-window confirmation reduces benign starts by 95.45% and benign alarm duration by 80.49%, with 98.81% observed-run coverage and approximately 2.10 seconds more conditional mean delay. This is the highlighted capture-1 result, not an overall effect across deployments or the separate 90.35%-accuracy reference classifier test. Excluded mixed/unknown/other starts remain separately recorded (484 versus 327). The older 0.925-second immediate delay is a legacy definition and is not used in this main comparison.

## Proposed extension and contribution

The bounded gap-aware evidence policy accumulates classifier confidence with a fixed scalar state and validation-only coverage-constrained calibration. This adapts established sequential evidence accumulation to the MQTT replay pipeline. Its contribution is the implemented decision-layer variant and complete evaluation; it does not establish a new general-purpose sequential detection principle.

## Primary alert comparison under audit version 2

| Policy | Benign onsets | Benign occupancy | Covered runs | Mean delay s | Excluded onsets |
| --- | ---: | ---: | ---: | ---: | ---: |
| k=1 | 0 | 0.00% | 12/12 | 1.055 | 65 |
| k=2 | 0 | 0.00% | 12/12 | 3.555 | 30 |
| k=3 | 0 | 0.00% | 10/12 | 4.900 | 22 |
| Raised threshold | 0 | 0.00% | 12/12 | 4.055 | 19 |
| Majority vote | 0 | 0.00% | 12/12 | 4.555 | 28 |
| Moving mean | 0 | 0.00% | 10/12 | 4.900 | 22 |
| EWMA | 0 | 0.00% | 11/12 | 2.171 | 29 |
| Bounded evidence | 0 | 0.00% | 11/12 | 5.251 | 16 |
| Always positive diagnostic | 372 | 100.00% | 12/12 | 1.055 | 211 |
| Ideal labels diagnostic | 0 | 0.00% | 12/12 | 1.055 | 0 |

Audit v2 requires a pure-positive window for run coverage and reports coverage separately from a new onset. Legacy immediate-run mean delay is 0.888 s; version2 is 1.055 s because the earliest mixed legitimate/SlowITe window is no longer credited. This is a definition change, not a changed classifier. Base primary confusion remains [[372,0],[55,143]], accuracy 90.35%, precision 100%, recall 72.22%, F1 83.87%.

The proposed primary-validation-selected setting is h=0.75, decay=0.5. It covers 11/12 primary runs and is slower than k2; therefore it is not claimed to dominate k2. The original fixed k2 remains the default reference.

## Matched coverage comparison on capture 1

| Policy | Benign onsets | Benign confirmed windows | Covered runs | Mean delay s |
| --- | ---: | ---: | ---: | ---: |
| k=2 | 3 | 16 | 83/84 | 3.172 |
| Raised threshold | 5 | 5 | 83/84 | 3.001 |
| Bounded evidence | 5 | 9 | 83/84 | 2.690 |

At 83/84 covered runs, bounded evidence reduces benign occupancy by 43.75% and mean delay by 15.19% relative to k2, but increases benign onsets from 3 to 5. Raising the threshold yields fewer benign confirmed windows than either, with a longer delay than bounded evidence. These are different operating tradeoffs, not uniform superiority.

## Independent MQTTset evaluation

The original full benign capture supplies 11,915,716 TCP records and 302,551 complete two-second windows over approximately one week. The frozen primary model produces zero benign alarms on this capture. This provides independent benign exposure evidence, not proof of detecting all external attacks.

The SlowITe file is excluded from temporal scoring because its 9,202 records span only 0.696832 seconds. Parser validation against its author-provided CSV has zero differences for all 9,202 timestamps, TCP lengths and recorded keepalive values, including fragmented CONNECT attribution.

| Evaluation | Scenario | Policy | Covered scenario | Mean proxy delay s | Benign occupancy |
| --- | --- | --- | ---: | ---: | ---: |
| direct_transfer | capture_1w.pcap | k=1 | 0/0 | NA | 0.000 |
| direct_transfer | capture_1w.pcap | k=2 | 0/0 | NA | 0.000 |
| direct_transfer | capture_1w.pcap | k=3 | 0/0 | NA | 0.000 |
| direct_transfer | capture_1w.pcap | Bounded evidence | 0/0 | NA | 0.000 |
| direct_transfer | capture_malariaDoS.pcap | k=1 | 1/1 | 28.000 | NA |
| direct_transfer | capture_malariaDoS.pcap | k=2 | 0/1 | NA | NA |
| direct_transfer | capture_malariaDoS.pcap | k=3 | 0/1 | NA | NA |
| direct_transfer | capture_malariaDoS.pcap | Bounded evidence | 0/1 | NA | NA |
| within_external_dataset_adaptation | capture_1w.pcap_test | k=1 | 0/0 | NA | 0.000 |
| within_external_dataset_adaptation | capture_1w.pcap_test | k=2 | 0/0 | NA | 0.000 |
| within_external_dataset_adaptation | capture_1w.pcap_test | k=3 | 0/0 | NA | 0.000 |
| within_external_dataset_adaptation | capture_1w.pcap_test | Bounded evidence | 0/0 | NA | 0.000 |
| within_external_dataset_adaptation | capture_malariaDoS.pcap_test | k=1 | 1/1 | 3.400 | NA |
| within_external_dataset_adaptation | capture_malariaDoS.pcap_test | k=2 | 1/1 | 5.400 | NA |
| within_external_dataset_adaptation | capture_malariaDoS.pcap_test | k=3 | 1/1 | 7.400 | NA |
| within_external_dataset_adaptation | capture_malariaDoS.pcap_test | Bounded evidence | 1/1 | 3.400 | NA |

The supplementary external attack is an MQTT DoS scenario, not SlowITe packet-level validation. Direct transfer detects the scenario with immediate alerts but stricter confirmation can miss it. Separate chronological adaptation is measured on first 40% train / next 20% validation / last 40% test with five-second guards. Its perfect scenario-window confusion counts must be interpreted with the strong benign/DoS file separation and only one attack recording; this is not evidence of universal 100% attack detection.

## Real time legitimate workload

Twenty-four Paho clients run six profiles with four seeded repetitions for 120 real seconds concurrently against a local MQTT broker: steady, bursts, reconnects, rate changes, idle and combined. They are controlled benign sessions, not independent physical devices/days. Aggregate observation and per-client diagnostics are kept separate.

| Model | Policy | Aggregate benign alarm windows | Aggregate benign onsets |
| --- | --- | ---: | ---: |
| original_frozen | k=1 | 0/60 | 0 |
| original_frozen | k=2 | 0/60 | 0 |
| original_frozen | k=3 | 0/60 | 0 |
| original_frozen | Bounded evidence | 0/60 | 0 |
| external_adapted | k=1 | 1/60 | 1 |
| external_adapted | k=2 | 0/60 | 0 |
| external_adapted | k=3 | 0/60 | 0 |
| external_adapted | Bounded evidence | 1/60 | 1 |

Per-client profile diagnostics and seeds are retained in benign_stress_results.json and alarm_audit.csv. They use narrower traffic scopes than the global detector, so they are stress diagnostics rather than equivalent deployment replications.

## Window and feature sensitivity

| Window s | Features | Window F1 | k2 runs | Bounded evidence runs |
| ---: | --- | ---: | ---: | ---: |
| 1 | all4 | 0.8830 | 12/12 | 12/12 |
| 1 | no_keepalive | 0.8893 | 12/12 | 12/12 |
| 1 | count_length | 0.8851 | 12/12 | 12/12 |
| 1 | no_count | 0.8830 | 12/12 | 12/12 |
| 1 | no_length | 0.7943 | 12/12 | 12/12 |
| 1 | no_interarrival | 0.8851 | 12/12 | 12/12 |
| 2 | all4 | 0.8387 | 12/12 | 11/12 |
| 2 | no_keepalive | 0.8455 | 12/12 | 12/12 |
| 2 | count_length | 0.5118 | 12/12 | 12/12 |
| 2 | no_count | 0.8421 | 12/12 | 11/12 |
| 2 | no_length | 0.7143 | 12/12 | 12/12 |
| 2 | no_interarrival | 0.8387 | 12/12 | 12/12 |
| 5 | all4 | 0.4026 | 12/12 | 12/12 |
| 5 | no_keepalive | 0.4054 | 12/12 | 12/12 |
| 5 | count_length | 0.3993 | 12/12 | 12/12 |
| 5 | no_count | 0.8357 | 12/12 | 12/12 |
| 5 | no_length | 0.7216 | 12/12 | 12/12 |
| 5 | no_interarrival | 0.8357 | 12/12 | 12/12 |

All 18 prespecified sensitivity configurations are retained. Results do not justify choosing a new official model from the best inspected test score. Different durations change the evaluated window cohort, so F1 changes are not paired predictions on identical rows.

## Embedded evidence

The actual C++ bounded-evidence module matches Python on 2,721,252 saved score/policy transitions with zero state/event disagreements. Host sizeof is 40 bytes, including configuration and counters; ESP32 size and timings are separate target observations. Current firmware is under firmware/wokwi_research; the original baseline bundle is regenerated under ignored firmware/wokwi. Actual target verification is recorded in docs/evidence/research_target_verification.json.

## Files and reproduction

Numerical sources: comparisons.json, validation_frontiers.json, test_frontiers.json, external_results.json, sensitivity.json, benign_stress_results.json, external_manifest.json, parser_validation.json and evidence_cpp_parity.json. Raw captures and per-window scores remain under ignored data/ and reports/ paths.

```bash
.venv/bin/python scripts/mqttset_data.py
.venv/bin/python scripts/benign_stress.py
.venv/bin/python scripts/run_extended_study.py
.venv/bin/python scripts/bundle_research_firmware.py
.venv/bin/python scripts/verify_evidence_policy.py
.venv/bin/python scripts/publish_extended_results.py
```
