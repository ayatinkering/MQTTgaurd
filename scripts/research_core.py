"""Causal alert policies and version-2 event/occupancy audit for MQTTGuard."""
from collections import deque
import json
import math
import numpy as np


def policies():
    result = [{'family': 'consecutive', 'k': k} for k in [1, 2, 3]]
    result += [{'family': 'threshold', 'threshold': float(round(t, 3))}
               for t in list(np.arange(.5, .951, .05)) + [.975, .99]]
    result += [{'family': 'majority', 'width': w} for w in [3, 5]]
    result += [{'family': 'mean', 'width': w, 'threshold': t}
               for w in [3, 5] for t in [.5, .6, .7, .8, .9]]
    result += [{'family': 'ewma', 'alpha': a, 'threshold': t}
               for a in [.25, .5, .75] for t in [.5, .6, .7, .8, .9]]
    result += [{'family': 'bounded_evidence', 'h': h, 'decay': decay}
               for h in [.1, .25, .5, .75, 1.] for decay in [.5, .8, 1.]]
    return result


def key(policy):
    return json.dumps(policy, sort_keys=True, separators=(',', ':'))


def apply_policy(scores, ids, policy):
    active = np.zeros(len(scores), dtype=bool)
    family = policy['family']
    history = deque(maxlen=policy.get('width', 1))
    evidence = 0.; streak = 0; ewma = None; last = None
    for i, (raw_score, window) in enumerate(zip(scores, ids)):
        p = float(raw_score)
        if last is not None and window <= last:
            # Duplicates/older inputs do not produce a second accepted state.
            continue
        gap = last is not None and window != last + 1
        last = window
        if gap or not math.isfinite(p):
            history.clear(); evidence = 0.; streak = 0; ewma = None
        if not math.isfinite(p):
            continue
        if family == 'consecutive':
            streak = min(streak + 1, policy['k']) if p > .5 else 0
            active[i] = streak >= policy['k']
        elif family == 'threshold':
            active[i] = p > policy['threshold']
        elif family in ['mean', 'majority']:
            history.append(p)
            if len(history) == policy['width']:
                active[i] = (sum(v > .5 for v in history) > len(history)//2
                             if family == 'majority'
                             else sum(history)/len(history) > policy['threshold'])
        elif family == 'ewma':
            ewma = p if ewma is None else policy['alpha']*p+(1-policy['alpha'])*ewma
            active[i] = ewma > policy['threshold']
        elif family == 'bounded_evidence':
            evidence = min(policy['h'], max(0., policy['decay']*evidence+p-.5))
            active[i] = evidence >= policy['h']
        elif family == 'always_positive':
            active[i] = True
        else:
            raise ValueError(f'Unknown policy {family}')
    return active


def as_arrays(cap, seconds=2):
    ws = cap['windows']
    return {
        'name': str(cap['id']), 'seconds': seconds,
        'ids': np.array([w['id'] for w in ws], dtype=np.int64),
        'end_us': np.array([w['end'] for w in ws], dtype=np.int64),
        'X': np.array([w['x'] for w in ws], dtype=float),
        'y': np.array([w['y'] for w in ws], dtype=np.int8),
        'valid': np.array([w['valid'] for w in ws], dtype=bool),
        'runs': cap['runs'],
    }


def audit(cap, active, policy=None):
    y = cap['y']; duration = cap['seconds']
    boundary = np.r_[True, cap['ids'][1:] != cap['ids'][:-1] + 1]
    starts = active & (~np.r_[False, active[:-1]] | boundary)
    benign = y == 0; positive = y == 1; other = y < 0
    delays = []; onset_delays = []; missed = []
    for run in cap['runs']:
        eligible = positive & (cap['end_us'] >= run['start']) & (cap['end_us'] <= run['end'])
        covered = np.flatnonzero(eligible & active)
        onsets = np.flatnonzero(eligible & starts)
        if covered.size:
            delays.append(float((cap['end_us'][covered[0]]-run['start'])/1e6))
        else:
            missed.append(run['id'])
        if onsets.size:
            onset_delays.append(float((cap['end_us'][onsets[0]]-run['start'])/1e6))
    longest = current = 0
    for v in benign:
        current = current+1 if v else 0
        longest = max(longest, current)
    exposure = int(benign.sum())*duration
    legacy = None
    if policy and policy['family'] == 'consecutive':
        k = policy['k']
        legacy = sum(int(i >= k-1 and benign[i-k+1:i+1].all())
                     for i in np.flatnonzero(starts))
    return {
        'capture': cap['name'], 'windows': len(y),
        'pure_benign_windows': int(benign.sum()), 'pure_positive_windows': int(positive.sum()),
        'empty_windows': int((~cap['valid']).sum()),
        'mixed_unknown_other_windows': int((other & cap['valid']).sum()),
        'benign_alarm_onsets': int((starts & benign).sum()),
        'positive_alarm_onsets': int((starts & positive).sum()),
        'excluded_alarm_onsets': int((starts & other).sum()),
        'total_alarm_onsets': int(starts.sum()),
        'legacy_clean_false_onsets': legacy,
        'benign_confirmed_windows': int((active & benign).sum()),
        'benign_alarm_seconds': int((active & benign).sum())*duration,
        'benign_exposure_seconds': exposure,
        'benign_alarm_fraction': float((active & benign).sum()/benign.sum()) if benign.any() else None,
        'benign_onsets_per_exposure_hour': float((starts & benign).sum()*3600/exposure) if exposure else None,
        'excluded_confirmed_windows': int((active & other).sum()),
        'run_count': len(cap['runs']), 'covered_runs': len(delays),
        'run_coverage_recall': len(delays)/len(cap['runs']) if cap['runs'] else None,
        'runs_with_new_onset': len(onset_delays),
        'run_onset_recall': len(onset_delays)/len(cap['runs']) if cap['runs'] else None,
        'missed_run_ids': missed,
        'coverage_delay_mean_s': float(np.mean(delays)) if delays else None,
        'coverage_delay_median_s': float(np.median(delays)) if delays else None,
        'coverage_delay_p95_s': float(np.percentile(delays, 95)) if delays else None,
        'coverage_delays_s': delays,
        'adjacent_benign_pairs': int((benign[1:] & benign[:-1]).sum()),
        'longest_benign_streak': longest,
    }


def select_policies(validation, scores):
    candidates = []
    reference = audit(validation, apply_policy(scores, validation['ids'], {'family': 'consecutive', 'k': 2}))
    floor = max(0., (reference['run_coverage_recall'] or 0.)-.02)
    for policy in policies():
        metric = audit(validation, apply_policy(scores, validation['ids'], policy), policy)
        candidates.append({'policy': policy, 'validation': metric})
    selected = []
    for family in ['threshold', 'majority', 'mean', 'ewma', 'bounded_evidence']:
        options = [r for r in candidates if r['policy']['family'] == family]
        feasible = [r for r in options if (r['validation']['run_coverage_recall'] or 0.) >= floor]
        pool = feasible or options
        def objective(r):
            m = r['validation']
            return (0 if feasible else -(m['run_coverage_recall'] or 0.),
                    m['benign_alarm_fraction'] if m['benign_alarm_fraction'] is not None else 1.,
                    m['benign_alarm_onsets'],
                    m['coverage_delay_mean_s'] if m['coverage_delay_mean_s'] is not None else math.inf,
                    key(r['policy']))
        winner = min(pool, key=objective)
        selected.append({**winner, 'validation_coverage_floor': floor,
                         'validation_constraint_met': bool(feasible)})
    return selected, candidates
