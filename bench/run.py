"""Offline benchmark result schema and summary; never sends a provider request."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

FIELDNAMES = [
    "run_id", "provider", "model", "prompt_set", "attempt", "concurrency",
    "reasoning_effort", "cache_state", "started_at", "first_token_at", "ended_at",
    "input_tokens", "cached_input_tokens", "output_tokens", "ttft_ms", "total_ms",
    "throughput_tokens_per_sec", "estimated_usd", "http_status", "status", "error_class",
]
STATUSES = {"success", "error", "timeout", "cancelled"}


def _nonnegative(value: int, name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def record(*, run_id: str, provider: str, model: str, prompt_set: str, attempt: int, concurrency: int, reasoning_effort: str, cache_state: str, started_at: float, first_token_at: float | None, ended_at: float, input_tokens: int, cached_input_tokens: int, output_tokens: int, http_status: int | None, status: str, error_class: str = "", estimated_usd: float | None = None) -> dict[str, Any]:
    """Build one validated row from monotonic timestamps and provider usage."""
    if not all(isinstance(value, str) and value.strip() for value in (run_id, provider, model, prompt_set, reasoning_effort, cache_state)):
        raise ValueError("run_id, provider, model, prompt_set, effort, and cache_state are required")
    if status not in STATUSES or ended_at < started_at or (first_token_at is not None and not started_at <= first_token_at <= ended_at):
        raise ValueError("invalid status or timestamp ordering")
    if attempt < 1 or concurrency < 1:
        raise ValueError("attempt and concurrency must be positive")
    input_tokens = _nonnegative(input_tokens, "input_tokens")
    cached_input_tokens = _nonnegative(cached_input_tokens, "cached_input_tokens")
    output_tokens = _nonnegative(output_tokens, "output_tokens")
    if cached_input_tokens > input_tokens:
        raise ValueError("cached_input_tokens cannot exceed input_tokens")
    total_ms = round((ended_at - started_at) * 1000, 3)
    ttft_ms = round((first_token_at - started_at) * 1000, 3) if first_token_at is not None else None
    generation_seconds = max(ended_at - (first_token_at or started_at), 0)
    throughput = round(output_tokens / generation_seconds, 3) if generation_seconds and output_tokens else None
    if status == "success" and not output_tokens:
        raise ValueError("successful sample must record output_tokens")
    return {
        "run_id": run_id, "provider": provider, "model": model, "prompt_set": prompt_set,
        "attempt": attempt, "concurrency": concurrency, "reasoning_effort": reasoning_effort,
        "cache_state": cache_state, "started_at": started_at, "first_token_at": first_token_at,
        "ended_at": ended_at, "input_tokens": input_tokens, "cached_input_tokens": cached_input_tokens,
        "output_tokens": output_tokens, "ttft_ms": ttft_ms, "total_ms": total_ms,
        "throughput_tokens_per_sec": throughput, "estimated_usd": estimated_usd,
        "http_status": http_status, "status": status, "error_class": error_class,
    }


def load_rates(path: Path = Path(__file__).with_name("models.json")) -> dict[str, dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return document["models"]


def estimate_cost(model: dict[str, Any], input_tokens: int, cached_input_tokens: int, output_tokens: int) -> float:
    if cached_input_tokens > input_tokens:
        raise ValueError("cached_input_tokens cannot exceed input_tokens")
    uncached = input_tokens - cached_input_tokens
    return round(uncached / 1_000_000 * model["input_per_million"] + cached_input_tokens / 1_000_000 * model["cached_per_million"] + output_tokens / 1_000_000 * model["output_per_million"], 8)


def summarize(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    if not rows:
        return {"count": 0, "success_rate": None, "median_ttft_ms": None, "p95_total_ms": None, "median_throughput_tokens_per_sec": None, "estimated_usd": 0.0}
    successful = [row for row in rows if row["status"] == "success"]
    ttft = [row["ttft_ms"] for row in successful if row["ttft_ms"] is not None]
    totals = [row["total_ms"] for row in rows]
    throughput = [row["throughput_tokens_per_sec"] for row in successful if row["throughput_tokens_per_sec"] is not None]
    ordered = sorted(totals)
    p95_index = min(len(ordered) - 1, math.ceil(len(ordered) * 0.95) - 1)
    return {
        "count": len(rows),
        "success_rate": round(len(successful) / len(rows), 4),
        "median_ttft_ms": round(statistics.median(ttft), 3) if ttft else None,
        "p95_total_ms": ordered[p95_index],
        "median_throughput_tokens_per_sec": round(statistics.median(throughput), 3) if throughput else None,
        "estimated_usd": round(sum(row.get("estimated_usd") or 0 for row in rows), 8),
    }


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write an offline benchmark CSV schema or summarize supplied rows")
    parser.add_argument("--output", type=Path, default=Path("results.csv"))
    parser.add_argument("--input", type=Path, help="JSON array of validated rows; no network adapter is included")
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8")) if args.input else []
    if not isinstance(rows, list):
        raise SystemExit("--input must contain a JSON array")
    write_csv(args.output, rows)
    print(json.dumps({"rows_written": len(rows), "summary": summarize(rows), "live_measurements": False}, indent=2))


if __name__ == "__main__":
    main()
