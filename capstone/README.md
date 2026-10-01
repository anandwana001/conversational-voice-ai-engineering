# Capstone: a measured, recoverable voice service

Build a receptionist or customer-support agent using synthetic business data. The goal is a coherent system whose behavior can be explained and verified, rather than a polished greeting demo.

## Required behavior

- Conduct a live voice conversation over browser RTC, a documented WebSocket media interface, or a phone route.
- Recognize self-corrections and handle interruption across generation and playback.
- Offer three tools: a scoped record lookup, availability search, and a confirmed mock booking or update.
- Execute one tool path through MCP and keep application authorization outside the model.
- Retrieve answers from a small versioned knowledge base with access scope and abstention for missing evidence.
- Maintain session state and one explicitly scoped, correctable user preference.
- Record named latency boundaries, tool outcomes, cancellations, failures, and per-session resource usage.
- Evaluate normal, noisy, ambiguous, interrupted, unauthorized, and disconnected scenarios.
- Recover from an ambiguous write timeout without duplicating the operation.
- Deploy in a development environment with secrets, admission limits, bounded session duration, and cleanup.

Use mock consequential writes and synthetic accounts. A publicly accessible demo is optional; a development deployment with reproducible evidence satisfies the hosting requirement.

## Submission

Submit your source repository, setup instructions, architecture diagram, event schema, redacted sample traces, evaluation report, failure-drill report, and a short demonstration. Include pinned versions and explicit unverified limits.

Use [the production checklist](../reference/production-checklist.md) as an evidence index. A checked box should link to a trace, assertion, configuration, or observed behavior rather than just an intention.

## Rubric: 100 points

| Area | Points | Evidence |
| --- | ---: | --- |
| Audio and streaming contracts | 10 | Correct formats, conversion owners, bounded queues |
| Turn taking and interruption | 15 | Pause/self-correction cases, late-output rejection, measured playback clear |
| Tool and workflow correctness | 15 | Schemas, confirmation, authoritative state, retry-safe write |
| MCP integration | 5 | Initialization/discovery/call trace and scoped execution |
| Retrieval and memory | 10 | Grounded answers, access filtering, provenance, correction/deletion |
| Channel engineering | 10 | Connection lifecycle, codec path, reconnect/hangup behavior |
| Observability and latency | 10 | Defined boundaries, p50/p95 with count, failures and clock assumptions |
| Evaluation | 10 | Scenario matrix, deterministic outcomes, listening checks |
| Security and reliability | 10 | Tenant tests, credentials, failure recovery, resource controls |
| Explanation and transfer | 5 | Provider-neutral account of internals and limitations |

Within each area award full points for reproducible evidence, partial points for working behavior with incomplete evidence, and zero for absent or contradicted behavior. Do not give points for a spoken success claim contradicted by tool state.

## Gates before calling it production-ready

Regardless of total score, cross-tenant access, unconfirmed consequential writes, duplicate writes under retry, or uncontrolled stale output require remediation. Passing this learning rubric does not establish compliance or readiness for every real-world domain; readiness depends on the actual task and deployment evidence.

## Stretch work

Compare cascaded and realtime models, add a second channel, or add diarization/co-pilot assistance. Publish measured differences and preserve the no-assistance baseline. Add these after the required flow works reliably.

[Labs](../labs/README.md) · [Course](../README.md)
