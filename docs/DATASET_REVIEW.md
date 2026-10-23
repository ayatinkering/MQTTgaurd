# MQTTEEB-D: Verified Dataset Review

Inspection date: 21 October 2026. This document reports file inspection, not model performance.

## Download and Attribution

- Official current release inspected: [Mendeley version 2](https://data.mendeley.com/datasets/jfttfjn6tr/2).
- Original release: [Mendeley version 1](https://data.mendeley.com/datasets/jfttfjn6tr/1).
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Dataset DOI for this inspection: `10.17632/jfttfjn6tr.2`.
- Creators: Abderrahmane Aqachtoul, Khaoula Karam, Abderrahmane Elamrani, Mehdi Najib, Najat Rafalia, and Mohamed Bakhouya.
- Dataset article: [Data in Brief, DOI 10.1016/j.dib.2025.111897](https://doi.org/10.1016/j.dib.2025.111897).
- Publisher metadata reports version 2 publication on 12 August 2026. All downloaded files matched its SHA-256 hashes.
- Compact provenance: [DATASET_MANIFEST.json](DATASET_MANIFEST.json). Original CSVs are unchanged and local only.

## What Was Downloaded

The cleaned CSV, four original capture CSVs, two encoding metadata files, and all three publisher README files were downloaded. The normalized, standardized, SMOTE, and other processed CSV variants were not downloaded because this study needs original temporal observations.

| CSV | Rows | Legitimate | SlowITe | Missing labels |
| --- | ---: | ---: | ---: | ---: |
| MQTTEEB-D_cleaned_data.csv | 222,813 | 17,557 | 20,090 | 246 |
| MQTTEEB-D_dataset_loop_1.csv | 137,319 | 11,158 | 12,765 | 172 |
| MQTTEEB-D_dataset_loop_2.csv | 42,470 | 3,208 | 3,663 | 52 |
| MQTTEEB-D_dataset_loop_3.csv | 21,501 | 2,815 | 1,801 | 16 |
| MQTTEEB-D_dataset_loop_4.csv | 21,523 | 376 | 1,861 | 6 |

**Exact cross-check:** the cleaned CSV and the union of all four raw captures have identical row multisets. The duplicate-row count is zero in every file; do not treat the cleaned file as additional examples.

## Full Cleaned-File Class Distribution

| Label | Rows |
| --- | ---: |
| legitimate | 17,557 |
| dos | 41,802 |
| slowite | 20,090 |
| malformed | 105,528 |
| (missing) | 246 |
| bruteforce | 27,377 |
| flood | 10,213 |

The binary target selection contains 37,647 rows before aggregation. The missing-label rows account for the difference between the full row count and the six known-class counts.

## Schema and Timestamp Findings

Actual CSV header:

```text
timestamp, tcp_flags, tcp_time_delta, tcp_len, mqtt_conack_flags, mqtt_conflag_cleansess, mqtt_conflags, mqtt_dupflag, mqtt_hdrflags, mqtt_kalive, mqtt_msg, mqtt_qos, label
```

- There are 13 columns total: 12 input fields, including timestamp, and one string `label` field.
- Timestamps parse as Unix seconds. Rendered UTC span: 2024-09-09T03:17:53.839303+00:00 to 2024-09-09T23:34:12.429866+00:00.
- All five files have zero negative timestamp steps, zero malformed CSV rows, and zero invalid timestamps.
- The combined file has 1,089 equal successive timestamps. They are not exact duplicate observations.
- Only the `label` column contains the empty/missing tokens counted by this audit. This does not prove every recorded numeric value is semantically valid.
- In **every row**, `tcp_time_delta` numerically equals `timestamp`. It is not a usable inter-arrival feature. Compute timing from timestamp differences.
- `mqtt_kalive` is 0 or 60 in these files, including SlowITe. Do not describe a high keep-alive value as a verified separating feature of this release.
- The inspected schema has no IP addresses, MQTT client identity, or independent attack start/stop fields. Do not promise per-device attribution.
- The 132 SlowITe label runs split as 84/24/12/12 across captures. They are episode proxies until external execution logs verify them.

## Temporal Sparsity at Two Seconds

The inspector uses half-open two-second bins anchored at the first timestamp of each file. Empty bins are counted but not written as synthetic observations. Results below include the final partial bin for exploration; final modelling must apply its separate complete-window policy.

| Capture | Pure benign nonempty windows | Pure SlowITe nonempty windows | Adjacent benign pairs | Longest benign streak | Empty bins in observed span |
| --- | ---: | ---: | ---: | ---: | ---: |
| MQTTEEB-D_dataset_loop_1.csv | 1,759 | 1,117 | 62 | 13 | 8,563 |
| MQTTEEB-D_dataset_loop_2.csv | 552 | 323 | 7 | 2 | 2,624 |
| MQTTEEB-D_dataset_loop_3.csv | 327 | 155 | 12 | 4 | 1,511 |
| MQTTEEB-D_dataset_loop_4.csv | 373 | 198 | 0 | 1 | 2,575 |

**Main limitation:** capture 4 has no adjacent pure-benign windows under this alignment. With empty-window resets, a rule requiring two pure-benign windows cannot start a false event in that clean evaluation subset even if the model misclassifies every benign window. Therefore zero clean false events for k >= 2 on this capture is partly guaranteed by traffic timing; it is not sufficient evidence of an AI improvement.

The combined CSV has 3,007 pure-benign nonempty windows; their observation-count median and 95th percentile are both 1. Inter-arrival time is undefined inside a singleton window. Use a documented training-only imputer and inspect whether count/sparsity dominates the classification.

Window totals from the combined file differ from sums over raw captures because each raw capture gets its own time origin. Use per-capture grids for experiments. The combined span also includes long between-capture gaps, which must not be treated as a continuous observed deployment.

## How to View the Data Locally

From the repository root:

```bash
python3 scripts/inspect_dataset.py
python3 -m unittest discover -s scripts -p "test_*.py" -v
```

Open `reports/dataset_preview.html` in a browser. It contains per-file summaries and the first eight rows from each class. These sample tables are stratified previews, not a continuous timeline. `reports/dataset_audit.json` contains detailed findings, distributions, and label-run timestamps. The per-file `*_windows.csv` files expose nonempty temporal bins and label mixtures.

## What We Can and Cannot Conclude

The data is suitable for investigating an offline binary MQTT classifier and temporal confirmation under explicitly stated rules. Inspection alone does not establish detection performance, attack-episode timing, embedded resource use, generalization, or novelty. Preserve other attacks and missing labels in audit/replay; exclude uncertain outputs from primary scoring with reasons rather than assigning them convenient labels.

Follow [PRD.md](PRD.md) for the build sequence and [METHODOLOGY.md](METHODOLOGY.md) for fixed experimental definitions.
