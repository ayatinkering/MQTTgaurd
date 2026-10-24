# MQTTGuard implementation status

Updated 24 October 2026. The implemented embedded simulation and extended numerical study are complete; editable report content is ready for the team to adapt.

## Completed research extension — 24 October 2026

The stronger-policy comparisons, audit version 2, continuous legitimate workload, independent MQTTset compatibility/direct-transfer/adaptation tests, and all 18 feature/window sensitivity configurations are complete. Read the [editable report content](../deliverables/report/REPORT_CONTENT.md) for the full paper narrative and [measured extended results](research/RESULTS.md) for tables. The original results below remain a historical baseline; legacy delays and clean false-event counts must not be mixed with audit-v2 endpoints.

The new contribution is bounded gap-aware confidence accumulation with validation-only coverage-constrained calibration, implemented in C++. It is a modest application-specific extension to established sequential evidence methods. At matched 83/84 coverage in capture 1 it reduces benign occupancy 43.75% and mean delay 15.19% relative to k=2, while increasing benign starts from 3 to 5. It underperforms k=2 on the primary split; no universal advantage is claimed.

The [research Wokwi demo](https://wokwi.com/projects/478737844363875329) uses `firmware/wokwi_research/`, build `3f718dc4c8d9ea81`, and adds a fourth evidence LED. Actual verification covers 62 paired model/evidence rows and 53 independently received MQTT records, with zero discrepancies. Original firmware and its demo remain available as the fixed baseline.

MQTTset supplies substantial independent benign exposure and a supplementary DoS scenario. Its SlowITe file spans only 0.696832 seconds and cannot validate two-second temporal detection. Separate adaptation has perfect scenario-window test classification but false alarms under changed benign scope; it is not general 100% SlowITe detection. All these outcomes are retained.

Only editable report content is requested now. Slides and synopsis production are stopped; the original course PDFs are unchanged.

## Completed deliverables

- Original four-feature RF, exact C++ export and original ESP32 inference/confirmation demo.
- Seven causal policy families and fixed k=1/2/3 references, with validation-only parameter selection.
- Audit-v2 onset, occupancy, exclusion, coverage, miss and conditional-delay accounting.
- 120 seconds of actual local benign traffic: 24 clients, six profiles, 2,335 publishes; replay fixture retained.
- MQTTset raw timestamp compatibility, 11,915,716 benign TCP records, direct transfer and separate chronological adaptation; incompatible SlowITe file explicitly excluded from temporal scoring.
- All 18 prespecified window/feature sensitivity configurations, labelled exploratory.
- 2,721,252 host C++ evidence-policy transitions checked with zero state/event discrepancies.
- New Wokwi implementation and independent MQTT verification; original controlled network-recovery evidence retained separately.
- 20 automated tests pass. Original RF export parity remains 11,210 inputs with zero label disagreement.
- Editable report Markdown and LaTeX; original course files unchanged. No slides requested.

## Reproduction and scope

Start with [HANDOFF](HANDOFF.md). Original classifier accuracy 90.35%, recall 72.22%, F1 83.87% describe the same model. The proposed policy has a useful capture-1 tradeoff but does not dominate the primary k=2 rule. The model is run on prerecorded feature windows on a simulated ESP32; host extraction/training, best-effort status, no physical power measurements and no live attack/sniffer claim.
