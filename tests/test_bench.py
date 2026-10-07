import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from bench.run import estimate_cost, record, summarize


class BenchmarkTests(unittest.TestCase):
    def sample(self, run_id="r1", ended=1.2, first=0.4, status="success"):
        return record(run_id=run_id, provider="fixture", model="glm-5.3", prompt_set="v1", attempt=1, concurrency=2, reasoning_effort="high", cache_state="cold", started_at=0.0, first_token_at=first, ended_at=ended, input_tokens=1000, cached_input_tokens=0, output_tokens=200, http_status=200, status=status, estimated_usd=0.001)

    def test_record_derives_latency_and_throughput(self):
        row = self.sample()
        self.assertEqual(row["ttft_ms"], 400.0)
        self.assertEqual(row["total_ms"], 1200.0)
        self.assertEqual(row["throughput_tokens_per_sec"], 250.0)

    def test_summary_reports_success_rate_and_percentile(self):
        result = summarize([self.sample(), self.sample("r2", ended=2.0, first=0.5), self.sample("r3", ended=3.0, first=None, status="timeout")])
        self.assertEqual(result["count"], 3)
        self.assertAlmostEqual(result["success_rate"], 0.6667)
        self.assertEqual(result["p95_total_ms"], 3000.0)

    def test_cost_separates_cached_input(self):
        self.assertAlmostEqual(estimate_cost({"input_per_million": 1.12, "cached_per_million": .208, "output_per_million": 3.52}, 200000, 100000, 20000), .2032)

    def test_invalid_timestamps_and_counts_fail(self):
        with self.assertRaises(ValueError):
            self.sample(first=2.0)
        with self.assertRaises(ValueError):
            record(run_id="x", provider="p", model="m", prompt_set="v", attempt=1, concurrency=1, reasoning_effort="high", cache_state="cold", started_at=0, first_token_at=0, ended_at=1, input_tokens=2, cached_input_tokens=3, output_tokens=1, http_status=200, status="success")


if __name__ == "__main__":
    unittest.main()
