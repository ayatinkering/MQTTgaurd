# MQTTGuard Methodology

## Basis and Research Hypothesis

This document translates the team's current report into an implementation protocol. The report specifies MQTTEEB-D, Legitimate/SlowITe filtering, 2-second windows, four compact features, Random Forest classification, and consecutive-window confirmation for k in {1, 2, 3}.

The hypothesis is that sustained slow attacks offer repeated evidence that can improve alert reliability. Reduced false alerts, retained episode recall, bounded delay, and low processing overhead are objectives to evaluate, not established results.

Policies for missing data, splitting, transition windows, and event counting below are explicit implementation decisions where the report leaves details open.

## 1. Acquire and Validate Data

Use the public MQTTEEB-D data identified by report reference [14]. Before training, verify the actual download location and license, record the version and file checksums, and inspect the schema.

The report describes approximately 222,813 observations across six classes and selects 17,557 Legitimate plus 20,090 SlowITe observations. Treat these counts as expectations to check, not constants to enforce by dropping records.

Required inputs are timestamps, TCP length, MQTT keep-alive, and ground-truth labels. Confirm timestamp units, numeric field meanings, missing-value conventions, and capture/session identity from the source. A dataset row is called an observation unless packet-level semantics are verified.

Retain original timestamps and source identifiers. Establish continuity boundaries before class filtering: removing other attack classes must not join otherwise separated benign and SlowITe regions. Check chronological order within each capture and use stable ordering for tied timestamps. Do not remove equal timestamps or duplicate-looking rows without evidence that they are acquisition duplicates.

## 2. Define Episodes and Data Partitions

An attack episode is a contiguous SlowITe region within a source capture, respecting timestamp discontinuities and any supplied attack/session metadata. Define the discontinuity rule from the capture format and document it before evaluation. Verify that row-label runs correspond to meaningful attack episodes; a single sorted table does not by itself establish independent attack repetitions.

Prefer held-out captures when independent captures exist. Otherwise use chronological training, validation, and test blocks with published boundaries. Keep whole episodes within partitions, fit all learned preprocessing on training data, tune only on validation data, and reserve the test set for the final comparison. Reset persistence at every partition boundary.

Do not fabricate independent episodes or use random window shuffling to imply temporal generalization. If available data cannot support partitions containing both suitable benign periods and attack episodes, report that limitation before drawing performance conclusions.

## 3. Construct Windows

Use fixed, non-overlapping half-open intervals:

```text
Tw = 2 seconds
Wj = [t0 + j*Tw, t0 + (j+1)*Tw)
```

Choose t0 once per capture from its first valid timestamp and record it. A boundary observation belongs to the window beginning at that boundary. Keep window IDs, start/end times, source identity, observation count, and label composition.

Window policies:

- **Pure Legitimate:** label 0 for classifier development and evaluation.
- **Pure SlowITe:** label 1 for classifier development and evaluation.
- **Mixed transition:** exclude from classifier fitting and pure-window classification metrics, following the report. Retain in operational replay, score from traffic features, and assess alerts against the original episode timeline.
- **Empty or unscorable:** retain its position on the timeline, mark unavailable, and reset persistence. Do not compact time by removing it.
- **Other-class or capture boundary:** break continuity and reset persistence.
- **Trailing incomplete window:** omit from primary inference, log it, and retain any affected ground-truth episode in the operational denominator so omission cannot inflate recall.

Operational replay runs after acquisition/splitting policies are fixed and never uses ground-truth class purity to decide whether a nonempty eligible window produces an inference.

## 4. Extract Features

For N observations in a window:

| Feature | Definition |
| --- | --- |
| Observation count | N |
| Mean TCP length | Arithmetic mean of valid `tcp_len` values |
| Mean inter-arrival time | Sum of consecutive timestamp differences divided by N - 1, for N >= 2 |
| Mean MQTT keep-alive | Arithmetic mean of valid `mqtt_kalive` values |

For N = 1, inter-arrival time is undefined and represented as missing. Preserve source-defined zeros where they are meaningful. Invalid numeric values become missing and are counted in the validation log. For nonempty windows, impute missing feature values using training-set medians; save those medians with the model. If a required feature has no valid training values, stop with a clear validation error rather than inventing a value.

The feature vector is `[count, mean_tcp_length, mean_interarrival, mean_keepalive]`. Labels, episode IDs, source row indices, and absolute timestamps are not predictor features. Scaling is not required for the proposed Random Forest pipeline.

## 5. Train the Classifier

Train a scikit-learn Random Forest on pure training windows. Save feature order, imputation parameters, random seed, hyperparameters, class mapping, partition manifest, and dependency versions.

Use a single fixed model and decision rule to generate held-out binary predictions. Any tuning or probability-threshold choice uses validation data only. Do not retune the classifier separately for each persistence setting.

## 6. Apply Persistence

For prediction y_hat[t] in {0, 1}, confirm an attack only when the previous k consecutive eligible windows, including the current window, are suspicious:

```text
confirmed[t, k] = AND(y_hat[t-j] for j in 0..k-1)
k = 1: immediate Random Forest baseline
k = 2: proposed MQTTGuard configuration
k = 3: strict persistence comparison
```

Equivalent state update:

```text
on boundary, missing interval, or unscorable window:
    streak = 0
    confirmed = false
on a valid prediction:
    streak = min(streak + 1, k) if prediction == 1 else 0
    confirmed = (streak >= k)
```

An alert event starts when confirmation changes from false to true. Continued confirmation is one event with an ongoing status, not a new event every window. A negative prediction or continuity break ends that event.

This layer uses constant additional state for a fixed k. Total system cost still includes aggregation, feature extraction, preprocessing, and Random Forest inference and must be measured.

## 7. Evaluate Classification and Alerts

### Classification

On pure held-out windows, report TP, FP, TN, FN, precision, recall, F1-score, and FPR:

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2*TP / (2*TP + FP + FN)
FPR       = FP / (FP + TN)
```

Report undefined metrics explicitly when their denominator is zero. Classification metrics describe the underlying model and remain the same across k settings.

### Operational Detection

Use full chronological held-out replay and original ground-truth episode times. An alert event is attributed to an episode if its start occurs within that episode. An episode is detected if at least one event starts during it; an already-active event that began outside the episode does not establish a new detection. This makes onset-based attribution explicit and avoids crediting a preceding false alarm as attack detection.

For dataset timestamps without attack-stop metadata, use the last recorded SlowITe timestamp as the episode end, disclose this approximation, and separately count confirmations occurring after that boundary. Do not silently extend episodes to accommodate delayed alerts.

Report:

- False alert events: starts in eligible benign time outside attack episodes.
- Confirmed-positive benign windows: a separate measure of false-confirmation duration.
- Attack-episode recall: detected episodes divided by all held-out attack episodes, including those missed due to short duration or unavailable windows.
- Missed episodes: identifiers, durations, and relevant boundary conditions.
- Detection latency for detected episodes: first attributed alert time minus episode onset, with mean, median, and spread. Report misses separately; do not assign them zero latency.
- Exposure: evaluated benign duration, attack duration, episode count, and excluded/unavailable intervals. Normalize false events per benign hour when meaningful.

A complete-window prediction becomes available at the window's **end**, not its beginning. Use the end timestamp for replay alert time, state whether measured computation time is added, and never backdate detection to window start. An alert after episode end counts as a late confirmation rather than an on-time detection under the primary definition.

Two-window confirmation does not guarantee an exact 4-second latency from attack onset. Alignment, mixed windows, model errors, and missing observations affect delay.

## 8. Measure Cost and Export Evidence

Measure feature-processing, inference, and persistence time with a monotonic clock, and identify which stages each timing includes. Separate model training time from replay processing time. Record hardware, operating system, software versions, feature/model size, and Random Forest configuration. Report typical and tail processing times and compare them with the 2-second interval. Offline speed alone does not prove real-time hardware performance.

Save input/split manifests, configuration, validation logs, model artifact, window features, predictions, confirmation timelines, alert events, episode outcomes, metric tables, and comparison plots. All k settings must derive from the same held-out predictions.

## 9. Interpretation and Future Work

Report whether false alerts decrease and what happens to episode recall and latency. Correlated false predictions can survive persistence; short attacks can be missed; dataset-specific performance may not generalize. Do not claim overall novelty from this comparison alone or infer gateway resource suitability without measurements.

Future work from the report includes adaptive windows, two-of-three confirmation, multiclass detection, live MQTT processing, Raspberry Pi deployment, resource profiling, and automated response.

## Report References

The entries below are transcribed from the report for traceability. Their publication details, DOI/title correspondence, and dataset access links have **not been independently verified**. Incomplete entries require bibliographic completion before submission or publication.

1. M. Al-Fayoumi and Q. Abu Al-Haija, “Capturing low-rate DDoS attack based on MQTT protocol in software Defined-IoT environment,” *Array*, vol. 19, Art. 100316, 2023. DOI: 10.1016/j.array.2023.100316.
2. A. Gavric, S. Bhandari, and A. Shalaginov, “Towards resource-efficient DDoS detection in IoT: Leveraging feature engineering of system and network usage metrics,” *Journal of Network and Systems Management*, vol. 32, 2024. DOI: 10.1007/s10922-024-09848-2.
3. I. H. Putro, T. Ahmad, and R. M. Ijtihadie, “Enhancing MQTT intrusion detection in IoT using machine learning and feature engineering,” *IEEE Open Journal of the Communications Society*, vol. 6, pp. 7855–7884, 2025. DOI: 10.1109/OJCOMS.2025.3610132.
4. T. Puccetti and A. Ceccarelli, “On detection latencies of network intrusion detectors—discussion and application,” *Empirical Software Engineering*, 2026. DOI: 10.1007/s10664-025-10766-3.
5. A. Alatram, L. F. Sikos, M. Johnstone, P. Szewczyk, and J. J. Kang, “DoS/DDoS-MQTT-IoT: A dataset for evaluating intrusions in IoT networks using the MQTT protocol,” *Computer Networks*, vol. 231, Art. 109809, 2023. DOI: 10.1016/j.comnet.2023.109809.
6. H. Hindy, E. Bayne, M. Bures, R. Atkinson, C. Tachtatzis, and X. Bellekens, “Machine learning based IoT intrusion detection system: An MQTT case study (MQTT-IoT-IDS2020 dataset),” 2021. Publication details incomplete in report.
7. M. A. Khan et al., “A deep learning-based intrusion detection system for MQTT enabled IoT,” *Sensors*, vol. 21, no. 21, Art. 7016, 2021. DOI: 10.3390/s21217016.
8. F. Valeur, G. Vigna, C. Kruegel, and R. A. Kemmerer, “A comprehensive approach to intrusion detection alert correlation,” *IEEE Transactions on Dependable and Secure Computing*, 2004. Volume, issue, pages, and DOI absent from report.
9. C. Udurume et al., “Intrusion detection techniques for MQTT-enabled IoT networks,” in *Proc. International Conference on Information and Communication Technology Convergence (ICTC)*, 2024. DOI: 10.1109/ICTC62082.2024.10826657.
10. R. Alaiz-Moreton et al., “Multiclass classification procedure for detecting attacks on MQTT protocol in Internet of Things,” 2019. DOI: 10.1155/2019/6516253. Venue details incomplete in report.
11. M. A. Ahmadon et al., “Process-based intrusion detection method for IoT systems using MQTT protocol,” in *Proc. IEEE Global Conference on Consumer Electronics (GCCE)*, 2019. DOI: 10.1109/GCCE46687.2019.9015331.
12. A. P. Haripriya and K. Kulothungan, “Secure-MQTT: An efficient fuzzy logic-based approach to detect DoS attack in MQTT protocol for Internet of Things,” *EURASIP Journal on Wireless Communications and Networking*, 2019. DOI: 10.1186/s13638-019-1402-8.
13. S. A. Mirheidari, S. Arshad, and R. Jalili, “Alert correlation algorithms: A survey and taxonomy,” 2018. Publication details incomplete in report.
14. H. Allaga et al., “MQTTEEB-D: Realistic MQTT anomaly detection for IoT environments,” *Ad Hoc Networks*, 2026. DOI: 10.1016/j.adhoc.2025.104062.
15. A. Alharbi and M. Ahmed, “Machine-learning-based intrusion detection in realistic IoT networks,” 2026. Publication details incomplete in report.
