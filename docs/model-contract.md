# GLM-5.2 model contract

This table is intentionally short. Update it only after checking the live [Argolink model page](https://argolink.io/gh-glm-5-2-benchmark-harness).

- Model ID: `glm-5.2`
- Argolink model page: `https://argolink.io/gh-glm-5-2-benchmark-harness` (tracked shortlink; destination is the model page)
- Endpoint family: `/v1/chat/completions`
- Context: `1,000,000` tokens; max output: `128000` tokens.
- Reasoning efforts: `high, max`; default: `max`.
- Listed token rates: input `$1.4` / output `$4.4` per million tokens; cached input `$0.26` when listed.

## Request boundary

- Authentication: `Authorization: Bearer $ARGOLINK_API_KEY`.
- Base URL: `https://api.argolink.io`.
- Model ID: `glm-5.2`.
- Endpoint: `/v1/chat/completions`.
- For media jobs, save the returned task identifier, poll the documented task endpoint, and download the final URL before its retention window ends.

Do not copy prices or limits from third-party lists into this file; the model page and catalog are the current source of truth.
