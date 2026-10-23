"""Small fixtures verify audit conclusions that affect the experiment."""
import csv
from pathlib import Path
import tempfile
import unittest
from inspect_dataset import audit


class AuditTests(unittest.TestCase):
    def inspect(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.csv'
            with path.open('w', newline='') as output:
                writer = csv.writer(output)
                writer.writerow(['timestamp','label','tcp_len','mqtt_kalive','tcp_time_delta'])
                writer.writerows(rows)
            return audit(path)[0]

    def test_exact_boundary_and_empty_interval_break_adjacency(self):
        result = self.inspect([['100.000001','slowite',40,60,100],
                               ['102.000001','slowite',40,60,102],
                               ['106.000001','slowite',40,60,106]])
        windows = result['two_second_windows']
        self.assertEqual(windows['empty_within_observed_span'], 1)
        self.assertEqual(windows['adjacent_same_label_pairs']['slowite'], 1)
        self.assertEqual(windows['longest_same_label_window_streak']['slowite'], 2)

    def test_mixed_windows_and_unknown_labels_are_visible(self):
        result = self.inspect([[100,'slowite',40,60,100], [101,'legitimate',40,0,101],
                               [102,'',40,0,102]])
        self.assertEqual(result['missing_tokens_by_column']['label'], 1)
        self.assertEqual(result['two_second_windows']['nonempty_by_label']['mixed_target'], 1)

    def test_source_order_and_duplicate_rows_are_not_repaired(self):
        result = self.inspect([[102,'legitimate',40,0,102], [100,'slowite',40,60,100],
                               [100,'slowite',40,60,100]])
        self.assertEqual(result['negative_timestamp_steps'], 1)
        self.assertEqual(result['exact_duplicate_rows'], 1)
        self.assertEqual(result['equal_timestamp_steps'], 1)

    def test_timestamp_delta_artifact_is_reported(self):
        result = self.inspect([[100,'legitimate',40,0,100], [101,'slowite',40,60,101]])
        self.assertEqual(result['tcp_time_delta_equal_timestamp_rows'], 2)
        self.assertEqual(result['interarrival_seconds']['median'], 1)


if __name__ == '__main__':
    unittest.main()
