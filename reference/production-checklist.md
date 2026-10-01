# Production evidence checklist

Use this as an evidence index. Check an item only when configuration, tests, and observed behavior support it under your stated workload. An offline course simulation cannot validate a deployed audio path.

## Audio and turn handling

- [ ] Every audio boundary has explicit encoding, rate, channels, duration, and conversion ownership.
- [ ] Resampling and codec paths preserve timing across frames.
- [ ] Endpointing is tested with pauses, corrections, noise, and intended languages/speaking styles.
- [ ] Interrupted output clears generation, queues, transport, device playback, and related animation.
- [ ] Late results are rejected by generation/state guards.
- [ ] Spoken-history limitations and provider context reconciliation are documented.
- [ ] Echo and speakerphone behavior are tested separately from headphone behavior.

## Actions, knowledge, and identity

- [ ] Tool arguments are schema-validated and business-validated before execution.
- [ ] Account identity and permissions are bound outside model-supplied arguments.
- [ ] Consequential actions have required confirmation and stable operation keys.
- [ ] Ambiguous write timeouts and process crashes reconcile authoritative outcomes.
- [ ] Retrieval, memory, caches, tools, and logs enforce tenant/access scope.
- [ ] Missing/conflicting evidence yields uncertainty or escalation.
- [ ] Memory has provenance, correction, deletion, and retention handling.
- [ ] MCP capabilities, authentication, versions, deadlines, and result-size limits are explicit.

## Lifecycle and observability

- [ ] Startup readiness is separate from transport connectedness.
- [ ] Session duration, resource budgets, quotas, and admission concurrency are bounded.
- [ ] Reconnect behavior states what resumes, replays, or is discarded.
- [ ] Hangup/shutdown releases tasks, sockets, media streams, and model sessions.
- [ ] Trace IDs and semantic IDs correlate turns, responses, segments, and operations.
- [ ] Latency boundaries, clocks, p50/p95 method, sample counts, and failure policy are recorded.
- [ ] Queue age, provider failure, interruption delay, and task success are observable.
- [ ] Cost accounting uses actual billing units and includes failed/cancelled work.

## Security and delivery

- [ ] Provider secrets stay server-side; client credentials are scoped and expiring where supported.
- [ ] Logs, fixtures, screenshots, and published traces are reviewed for sensitive information.
- [ ] Recording/retention permissions and actual deployment obligations are addressed.
- [ ] Webhooks and callbacks are authenticated and replay-protected as appropriate.
- [ ] Injected failures cover provider outage, disconnect, delayed tool, and worker termination.
- [ ] Code, prompts, graph configuration, dependencies, and datasets are versioned.
- [ ] Rollout, draining, alert ownership, and rollback are demonstrated.
- [ ] Evaluation includes deterministic action checks, listening, and relevant human review.

## Evidence record

For each item record: environment, version, workload, test or trace, observed outcome, owner, date, and known limitations. Revalidate affected items after changing model/session contracts, codecs, turn policy, transport, or authorization logic.

[Capstone](../capstone/README.md) · [Lab 12](../labs/12-production-failure-drills.md)
