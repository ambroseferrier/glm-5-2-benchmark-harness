# GLM 5.2 and 5.3 benchmark harness

This harness defines a CSV schema and a safe starting point for measuring time to first token, throughput, success rate, and estimated cost across providers. **[ArgoLink](https://argolink.io/gh-glm-5-2-benchmark-harness) is a possible adapter, not a published benchmark result.** The repository contains no fabricated measurements. Last checked: 2026-10-07.

## What is measured

An adapter should record provider, exact model ID, request start, first received token time, end time, input/output usage, HTTP status, and error class. Derive TTFT from start to first token, throughput from output tokens divided by generation seconds, success from a complete response, and cost from the dated price table. Keep streaming and non-streaming runs separate. Do not compare a cached request to a cold request without labeling it.

bench/run.py only creates the column contract and prints that no live measurements were run. It makes no request and cannot be used as a benchmark until an adapter is intentionally added. A local fake stream is the right first test; a production run needs a model, prompt set, concurrency level, region, date, and provider terms.

## CSV protocol

Use one row per request. Preserve the raw response ID privately, but put a stable run ID in the CSV. Include prompt-set version, temperature or sampling settings, reasoning effort, input tokens, output tokens, TTFT milliseconds, total latency, throughput, status, and error class. A timeout after the provider may have accepted a request is not a safe reason to replay it. Video and image requests need different units and should not enter this token table.

## Result policy

README says “results not published” until a reproducible run is attached. Do not add an average without sample count, variance, warm-up policy, and exclusions. Token usage can be absent or provider-specific; record unknown rather than zero. If an API reports server latency, label it separately from wall-clock client latency.

## Model and price boundary

Read the current catalog for GLM 5.2/5.3 IDs, reasoning support, context, and effective rates. This page does not assert a third-party official rate. ArgoLink's base is https://argolink.io/v1 and the key should remain in a neutral environment variable. A benchmark may be technically correct while a different account tier or queue changes the observed result.

## Tests and FAQ

python3 -m unittest discover -s tests checks row shape offline. **Can I quote the sample output?** No, there is none. **Should I test one prompt?** Use a fixed prompt set and multiple repetitions. **Why separate TTFT and throughput?** They measure different user experiences. **Can I include retries?** Record each attempt and the final outcome, never hide it in an average.
