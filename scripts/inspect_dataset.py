"""Audit MQTTEEB-D CSVs without changing rows or training a model (Python stdlib only)."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import json
import math
from pathlib import Path
import statistics

TARGETS = {'legitimate', 'slowite'}


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def quantiles(values):
    values = sorted(values)
    if not values:
        return None
    return {'min': values[0], 'median': statistics.median(values),
            'p95': values[min(len(values)-1, math.ceil(.95*len(values))-1)],
            'max': values[-1]}


def utc(microseconds):
    return datetime.fromtimestamp(microseconds / 1e6, timezone.utc).isoformat()


def audit(path):
    with path.open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames
        rows = list(reader)
    required = {'timestamp', 'label', 'tcp_len', 'mqtt_kalive'}
    if not required.issubset(columns or []):
        raise ValueError(f'{path.name}: missing required columns: {required-set(columns or [])}')
    labels, missing, malformed = Counter(), Counter(), 0
    previous = None
    times, deltas, class_values, runs = [], [], defaultdict(lambda: defaultdict(list)), []
    bins = defaultdict(lambda: {'labels': Counter(), 'count': 0})
    hashes = Counter()
    preview = []
    seen_preview = Counter()
    timestamp_equal_delta = 0
    invalid_timestamps = 0
    origin = None
    run = None
    for index, row in enumerate(rows):
        if None in row or any(value is None for value in row.values()):
            malformed += 1
        label = (row.get('label') or '').strip().lower()
        labels[label] += 1
        for column in columns:
            if str(row.get(column, '')).strip().lower() in {'', 'none', 'nan', 'null', 'n/a'}:
                missing[column] += 1
        canonical = json.dumps([row.get(c) for c in columns], separators=(',', ':'))
        hashes[hashlib.sha256(canonical.encode()).hexdigest()] += 1
        if seen_preview[label] < 8:
            preview.append(row)
            seen_preview[label] += 1
        try:
            ts = int(Decimal(row['timestamp']) * 1_000_000)
        except (InvalidOperation, ValueError, TypeError, OverflowError):
            invalid_timestamps += 1
            run = None
            continue
        if origin is None:
            origin = ts
        times.append(ts)
        delta = None if previous is None else (ts-previous)/1e6
        if delta is not None:
            deltas.append(delta)
        previous = ts
        bucket = bins[(ts-origin)//2_000_000]
        bucket['labels'][label] += 1
        bucket['count'] += 1
        if run is None or run['label'] != label:
            run = {'label': label, 'first_row': index+2, 'last_row': index+2,
                   'start_us': ts, 'end_us': ts, 'count': 1, 'max_internal_gap_s': 0}
            runs.append(run)
        else:
            run['last_row'], run['end_us'] = index+2, ts
            run['count'] += 1
            run['max_internal_gap_s'] = max(run['max_internal_gap_s'], delta or 0)
        for feature in ('tcp_len', 'mqtt_kalive'):
            value = number(row.get(feature))
            if value is not None:
                class_values[label][feature].append(value)
        if number(row.get('tcp_time_delta')) == number(row.get('timestamp')):
            timestamp_equal_delta += 1
    window_counts, adjacent_pairs = Counter(), Counter()
    class_window_sizes = defaultdict(list)
    previous_bin, previous_status = None, None
    longest, streak = Counter(), 0
    for bin_id, bucket in sorted(bins.items()):
        label_set = set(bucket['labels'])
        if len(label_set) == 1:
            status = next(iter(label_set))
        elif label_set <= TARGETS:
            status = 'mixed_target'
        else:
            status = 'contains_other_class'
        window_counts[status] += 1
        class_window_sizes[status].append(bucket['count'])
        if previous_bin is not None and bin_id == previous_bin+1 and status == previous_status:
            adjacent_pairs[status] += 1
            streak += 1
        else:
            streak = 1
        longest[status] = max(longest[status], streak)
        previous_bin, previous_status = bin_id, status
    complete_bin_limit = (max(times)-origin)//2_000_000 if times else 0
    window_rows = []
    for bin_id, bucket in sorted(bins.items()):
        window_rows.append({'window_id': bin_id, 'start_utc': utc(origin+bin_id*2_000_000),
                            'observation_count': bucket['count'],
                            'labels': json.dumps(dict(bucket['labels']), sort_keys=True),
                            'complete_at_last_observation': bin_id < complete_bin_limit})
    stats = {}
    for label, features in class_values.items():
        stats[label] = {feature: {'distribution': quantiles(values),
                                 'most_common': Counter(values).most_common(8)}
                        for feature, values in features.items()}
    result = {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'bytes': path.stat().st_size, 'rows': len(rows), 'columns': columns,
              'labels': dict(labels), 'missing_tokens_by_column': dict(missing),
              'malformed_rows': malformed, 'invalid_timestamps': invalid_timestamps,
              'exact_duplicate_rows': sum(count-1 for count in hashes.values()),
              'start_utc': utc(min(times)) if times else None,
              'end_utc': utc(max(times)) if times else None,
              'duration_seconds': (max(times)-min(times))/1e6 if times else None,
              'negative_timestamp_steps': sum(value < 0 for value in deltas),
              'equal_timestamp_steps': sum(value == 0 for value in deltas),
              'interarrival_seconds': quantiles(deltas),
              'gaps_over_2_seconds': sum(value > 2 for value in deltas),
              'gaps_over_60_seconds': sum(value > 60 for value in deltas),
              'tcp_time_delta_equal_timestamp_rows': timestamp_equal_delta,
              'label_runs': [dict(r, start_utc=utc(r['start_us']), end_utc=utc(r['end_us']),
                                  duration_seconds=(r['end_us']-r['start_us'])/1e6) for r in runs],
              'two_second_windows': {'origin_utc': utc(origin) if origin is not None else None,
                  'nonempty_by_label': dict(window_counts),
                  'empty_within_observed_span': (max(bins)-min(bins)+1-len(bins)) if bins else 0,
                  'adjacent_same_label_pairs': dict(adjacent_pairs),
                  'longest_same_label_window_streak': dict(longest),
                  'observations_per_nonempty_window': {k: quantiles(v) for k,v in class_window_sizes.items()},
                  'note': 'Exploratory bins include the final incomplete bin. No model is trained.'},
              'feature_stats_by_class': stats}
    return result, preview, window_rows, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--output-dir', type=Path, default=Path('reports'))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results, previews, raw_hashes, cleaned_hashes = [], [], Counter(), None
    paths = sorted(args.data_dir.glob('MQTTEEB-D*.csv'))
    if not paths:
        raise SystemExit('No CSV files found. Run scripts/download_dataset.py first.')
    for path in paths:
        result, preview, windows, hashes = audit(path)
        results.append(result)
        previews.append((path.name, preview))
        if '_loop_' in path.name:
            raw_hashes.update(hashes)
        elif path.name == 'MQTTEEB-D_cleaned_data.csv':
            cleaned_hashes = hashes
        with (args.output_dir / f'{path.stem}_windows.csv').open('w', newline='') as target:
            writer = csv.DictWriter(target, fieldnames=['window_id', 'start_utc', 'observation_count',
                                                       'labels', 'complete_at_last_observation'])
            writer.writeheader()
            writer.writerows(windows)
        print(f"{path.name}: {result['rows']:,} rows; {result['labels']}", flush=True)
    all_loops = all((args.data_dir / f'MQTTEEB-D_dataset_loop_{i}.csv').exists() for i in range(1,5))
    combined = {'files': results, 'all_four_raw_loops_present': all_loops,
                'cleaned_equals_raw_loop_row_multiset':
                (cleaned_hashes == raw_hashes) if cleaned_hashes is not None and all_loops else None,
                'notes': ['Timestamps rendered in UTC; source timezone is not inferred.',
                          'Label runs are observed runs, not independently verified attack episodes.',
                          'Empty bins stay empty; class filtering is not used to construct these bins.']}
    (args.output_dir / 'dataset_audit.json').write_text(json.dumps(combined, indent=2)+'\n')
    content = ['<!doctype html><html lang="en"><meta charset="utf-8">',
               '<meta name="viewport" content="width=device-width,initial-scale=1">',
               '<title>MQTTGuard dataset inspection</title><style>',
               'body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 24px;color:#182435}',
               'table{border-collapse:collapse;font-size:13px}td,th{padding:8px;border:1px solid #d7dfe8;text-align:left}',
               'th{background:#eaf1fa}pre{background:#f3f6fa;padding:16px;overflow:auto}.scroll{overflow:auto}',
               '</style><h1>MQTTGuard dataset inspection</h1>',
               '<p>Read-only audit of official unscaled CSVs. No classifier has been trained. ',
               'Times are UTC. The sample tables show the first eight rows of each class, not a continuous replay.</p>',
               '<p><a href="dataset_audit.json">Full machine-readable audit</a></p>']
    for result, (name, preview) in zip(results, previews):
        content.append('<h2>'+html.escape(name)+'</h2>')
        brief = {k: result[k] for k in ('rows','labels','start_utc','end_utc','negative_timestamp_steps',
                                       'missing_tokens_by_column','exact_duplicate_rows','two_second_windows')}
        content.append('<pre>'+html.escape(json.dumps(brief,indent=2))+'</pre>')
        columns = result['columns']
        content.append('<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(c)+'</th>' for c in columns)+'</tr>')
        for row in preview:
            content.append('<tr>'+''.join('<td>'+html.escape(str(row.get(c,'')))+'</td>' for c in columns)+'</tr>')
        content.append('</table></div>')
    content.append('</html>')
    (args.output_dir / 'dataset_preview.html').write_text('\n'.join(content))
    print('Cleaned equals raw loop row multiset:', combined['cleaned_equals_raw_loop_row_multiset'])
    print('Wrote', args.output_dir / 'dataset_preview.html')


if __name__ == '__main__':
    main()
