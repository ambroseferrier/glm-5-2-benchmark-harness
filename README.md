# GLM 5.2 / 5.3 benchmark harness

An offline-first result contract for measuring GLM requests across providers. It records time to first token (TTFT), total latency, generation throughput, success rate, and an estimated request cost in a CSV that can be reviewed or plotted later. The repository is an independent community project and is not affiliated with Zhipu, Vercel, or any provider.

## What is included

- `bench/models.json` — the model IDs, endpoint family, reasoning options, effective ArgoLink rates, and dated source links checked on 2026-10-07.
- `bench/run.py` — validation, derived metrics, cost estimation, CSV writing, and summary statistics. It never sends a request.
- `tests/test_bench.py` — deterministic fixtures for the schema, percentile calculation, cached-input pricing, and validation failures.

The catalog facts used here are the live ArgoLink catalog at [GET /v1/models](https://argolink.io/v1/models) and the [GLM-5.2](https://argolink.io/en/models/glm-5-2) and [GLM-5.3](https://argolink.io/en/models/glm-5-3) model pages. Recheck those pages before publishing a new run; IDs, prices, limits, and reasoning options can change.

## Current model boundary

| Model | API family | Context / max output | Reasoning options | Effective rates per 1M tokens |
| --- | --- | ---: | --- | ---: |
| `glm-5.2` | Chat Completions (`/v1/chat/completions`) | 1,000,000 / 128,000 | `high`, `max`; `reasoning_effort: none` disables reasoning | $1.12 input / $3.52 output / $0.208 cached input |
| `glm-5.3` | Chat Completions (`/v1/chat/completions`) | 1,000,000 / 128,000 | `low`, `high`, `max`; default `max`; `medium` aliases to `high`, `xhigh` to `max` | $1.12 input / $3.52 output / $0.208 cached input |

Rates are estimates for accounting, not a promise of a provider invoice. Keep the catalog date beside every report. Do not claim a latency, throughput, success rate, or ranking until it has been measured and the prompt set, region, concurrency, warm-up policy, and exclusions are published with it.

## CSV contract

There is one row per request attempt. `run_id`, provider, exact model ID, prompt-set version, attempt number, concurrency, reasoning effort, and `cache_state` make samples comparable. Timestamps are monotonic seconds captured by the adapter. `ttft_ms` is start to first received token; `total_ms` is start to end; `throughput_tokens_per_sec` is output tokens divided by the time after the first token. Unknown usage is blank, never silently changed to zero. A timeout is an outcome, not permission to replay a request without recording the new attempt.

Required columns are:

```text
run_id, provider, model, prompt_set, attempt, concurrency,
reasoning_effort, cache_state, started_at, first_token_at, ended_at,
input_tokens, cached_input_tokens, output_tokens, ttft_ms, total_ms,
throughput_tokens_per_sec, estimated_usd, http_status, status, error_class
```

`status` is one of `success`, `error`, `timeout`, or `cancelled`. Streaming and non-streaming runs should use separate prompt-set labels. Image and video jobs use different units and do not belong in this token benchmark.

## Offline usage

The default command writes an empty, explicitly non-live CSV:

```bash
python3 -m bench.run --output /tmp/glm-results.csv
```

To summarize validated rows produced by your own adapter, pass a JSON array. The adapter is intentionally outside this repository so credentials and billable traffic cannot be triggered accidentally:

```bash
python3 -m bench.run --input /path/to/validated-rows.json --output /tmp/glm-results.csv
```

Use the ArgoLink base URL `https://argolink.io/v1` and a secret environment variable in a separate adapter. Never commit a key. A production adapter must set a descriptive `User-Agent`, enforce timeouts, record each retry as a separate attempt, and stop before a request can exceed the selected budget.

## Development

```bash
python3 -m unittest discover -s tests -v
```

No live measurements are published in this repository yet. The first report should include the exact commit, catalog date, prompt-set file, model settings, concurrency, region, raw sample count, and the generated CSV checksum.
