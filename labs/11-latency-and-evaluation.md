# Lab 11. Measure latency and evaluate actual outcomes

**Read:** [chapters 19–20](../chapters/19-latency-and-observability.md). **Mode:** offline report, then live traces. **Time:** 2–3 hours.

## Build

1. Run `python3 examples/latency_report.py fixtures/turns.jsonl`.
2. Explain the nearest-rank percentile rule and why the small synthetic sample cannot establish production performance.
3. Instrument your live pipeline with the same named boundaries. Collect at least 20 controlled turns, preserving failures separately.
4. Write deterministic checks for task success, tool arguments, operation count, access scope, and stale-output rejection.
5. Add a listening rubric and optionally a model judge. Compare judge results with human checks on a subset.

## Deliver

Submit a redacted JSONL trace, p50/p95 report with sample count and failure rate, scenario matrix, and one diagnosed slow turn. State where spans overlap and which clocks produced timestamps.

## Acceptance

- Failed turns are counted, not silently excluded from the headline.
- First audible response is distinguished from provider audio readiness.
- Stage p95s are not summed to invent an end-to-end p95.
- Success is checked against tool/business state, not only spoken claims.

**Failure experiment:** include a transcript claiming successful cancellation while the ledger shows an unauthorized write. Verify the deterministic check catches it.

**Transfer:** explain how to compare two systems with different endpoint definitions fairly.

[Next lab](12-production-failure-drills.md) · [All labs](README.md)
