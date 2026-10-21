# MQTTGuard Product Requirements

## Purpose and Status

Build a reproducible software research pipeline for detecting SlowITe MQTT attacks using compact temporal features, Random Forest classification, and persistence-aware alert confirmation.

This specification is based on the team report, *MQTTGuard: A Lightweight Persistence-Aware Intrusion Detection System for Slow MQTT Attacks in IoT Networks*. It describes intended behaviour, not completed functionality or measured results. Operational details added below make the report implementable and must remain visible as implementation decisions.

## Research Question

Does requiring two consecutive suspicious 2-second windows reduce false alert events relative to immediate Random Forest alerting, while preserving useful attack-episode recall and acceptable time to detection?

No numerical improvement target is asserted. Compare k = 1, 2, and 3 and report any degradation alongside gains.

## Users and Deliverables

The primary users are the student research team and academic reviewers. They need to reproduce preprocessing, train and evaluate the model, inspect temporal decisions, and trace conclusions to generated evidence.

Deliverables are an ingestion and validation pipeline, window construction, feature extraction, model training, chronological replay, evaluation exports, plots, and documented execution instructions.

## Scope

The first implementation supports offline MQTTEEB-D analysis with Legitimate/SlowITe classification, fixed 2-second windows, four features, and one Random Forest model evaluated under three persistence settings.

Live capture, hardware deployment, cloud services, dashboards, recurrent models, multiclass classification, and automated mitigation are outside this initial scope.

## Functional Requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-01 | Load a user-supplied dataset and record its provenance, checksum, schema, timestamp units, and labels. | A manifest identifies input files, verified class counts, parsing decisions, and software versions. |
| FR-02 | Validate timestamps, numeric inputs, labels, and capture/session boundaries. | Invalid records are reported; processing does not silently concatenate independent captures or remove temporal gaps. |
| FR-03 | Construct fixed, non-overlapping 2-second windows. | Window boundaries, counts, mixed labels, and empty intervals are auditable. |
| FR-04 | Extract observation count, mean TCP length, mean inter-arrival time, and mean MQTT keep-alive. | Features match independently calculated examples, with documented missing-value and singleton policies. |
| FR-05 | Train a reproducible Random Forest without test leakage. | Saved configuration, seed, training-only preprocessing, split boundaries, model, and held-out predictions are available. |
| FR-06 | Replay identical held-out predictions using k = 1, 2, and 3. | A timeline exposes predictions, consecutive-positive state, confirmation status, and alert events for each setting. |
| FR-07 | Reset confirmation when continuity is broken. | A negative prediction, empty/unscorable interval, capture boundary, or replay start prevents evidence from bridging that boundary. |
| FR-08 | Evaluate classification and operational detection separately. | Exports include confusion counts, classification metrics, event counts, episode recall, missed episodes, and latency distributions. |
| FR-09 | Measure processing overhead. | Runtime evidence identifies hardware, dataset size, model size/configuration, and measurement scope. |
| FR-10 | Support reproduction from documented commands. | A new run can regenerate results from the recorded dataset and configuration. |

## Evaluation Requirements

1. Use chronological splits within captures, or held-out captures when supported by the source data. Avoid splitting attack episodes across partitions. Publish actual split boundaries and class/episode counts.
2. Keep model selection and decision thresholds independent of the final test set. Apply the same trained model and predictions to every persistence setting.
3. Exclude mixed transition windows from classifier fitting and pure-window classification metrics. Retain them in operational replay under the explicit policy in the methodology.
4. Count both confirmed-positive windows and distinct alert events. Do not present window counts as independent alerts.
5. Report the denominator and definition for every metric. Undefined values remain explicit rather than being silently converted to zero.
6. If the dataset lacks enough independent attack episodes or benign periods for credible evaluation, disclose the limitation and narrow conclusions.

## Reproducibility and Quality

- Keep raw inputs unchanged and generated data separate from source code.
- Fix and record random seeds; save configuration and dependency versions.
- Keep labels, ground-truth episode IDs, and future observations out of model features.
- Test behaviour that can change conclusions: boundary assignment, state resets, mixed windows, alert transitions, episode matching, and latency calculations.
- Record anomalous inputs and exclusions with counts and reasons.
- Distinguish proposed features, implemented functionality, and validated findings in documentation.

## Implementation Sequence

1. Acquire and inspect the dataset; verify provenance, schema, and usable temporal structure.
2. Implement validation, windowing, features, and boundary policies.
3. Establish leakage-resistant train/validation/test partitions and train the baseline.
4. Implement persistence replay and alert-event generation.
5. Evaluate all configurations and export traceable metrics and plots.
6. Document reproducible commands, findings, limitations, and any departures from the report.

## Completion Criteria

The initial implementation is complete when the pipeline runs end to end on the documented dataset, produces reproducible held-out comparisons for all three persistence settings, passes the relevant behavioural checks, and includes commands and evidence sufficient for review. A negative or inconclusive research result is valid and must be reported accurately.
