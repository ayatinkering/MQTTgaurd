# External temporal compatibility amendment

24 October 2026. This amendment records a metadata-driven change before examining external model scores. It does not change the original protocol or its saved hash.

The MQTTset v5 SlowITe PCAP has 9,202 TCP records over only 0.696832 seconds. The author's corresponding CSV independently confirms the same minimum and maximum absolute timestamps. No complete one-, two- or five-second window is available. It is excluded from temporal performance scoring; attack-duration claims in the paper cannot supply unrecorded packet timestamps.

The full independent benign capture contains 11,915,716 TCP records over approximately one week and is retained. The separate original MQTTset `capture_malariaDoS.pcap` contains 130,223 TCP records over 126.849502 seconds and is temporally usable. It is added as a supplementary broader MQTT denial-of-service scenario, explicitly not independent SlowITe validation. Label attribution remains file-level scenario attribution, not verified packet-level labels.

The prespecified external first40%/next20%/last40% chronology and five-second guards are applied to the benign and DoS files. Direct transfer of the frozen original model remains separate from within-MQTTset adaptation. The short SlowITe file remains in the provenance/audit evidence, including its exclusion reason. No timestamps are expanded, fabricated, or spliced into new attack sessions.

The parser supports Ethernet and Linux cooked IPv4 TCP captures (link types1/113/276), using capture timestamps, TCP payload length and complete CONNECT keepalive metadata. Twenty-three timestamp inversions in the benign capture are aggregated by their actual timestamp; they are not treated as new sessions or negative interarrival values.
