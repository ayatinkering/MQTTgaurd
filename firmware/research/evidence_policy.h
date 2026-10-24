#pragma once
#include <stdint.h>
#include <math.h>

// Bounded causal score accumulation. Constants are selected on validation only.
struct BoundedEvidence {
  double threshold, decay, value = 0.0;
  bool active = false, seen = false;
  uint32_t last = 0, events = 0;
  BoundedEvidence(double h, double d): threshold(h), decay(d) {}
  void clearEvidence() { value = 0.0; active = false; }
  bool accept(uint32_t id, double probability) {
    if(seen && id <= last) return false;
    if(seen && id != last + 1) clearEvidence();
    seen = true; last = id;
    if(!isfinite(probability)) { clearEvidence(); return true; }
    double next = decay * value + probability - 0.5;
    value = next < 0.0 ? 0.0 : next > threshold ? threshold : next;
    bool confirmed = value >= threshold;
    if(confirmed && !active) events++;
    active = confirmed;
    return true;
  }
};
