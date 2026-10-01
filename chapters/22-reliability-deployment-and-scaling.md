# 22. Reliability, deployment, and session scaling

**Prerequisites:** chapters 10 and 19–21. **Goal:** operate long-lived conversations through failure, deploy safely, and plan capacity using evidence.

<!-- chapter-navigation:start -->
**In this chapter**

- [Sessions behave differently from short HTTP requests](#sessions-behave-differently-from-short-http-requests)
- [Separate lifecycle and readiness](#separate-lifecycle-and-readiness)
- [Retry and fallback policy](#retry-and-fallback-policy)
- [Durable operations versus ephemeral sessions](#durable-operations-versus-ephemeral-sessions)
- [Capacity planning](#capacity-planning)
- [Deployment evidence](#deployment-evidence)
- [Failure drill](#failure-drill)
- [Derive a first capacity estimate](#derive-a-first-capacity-estimate)
- [Separate admission, readiness, and draining](#separate-admission-readiness-and-draining)
- [Coordinate deadlines and retry budgets](#coordinate-deadlines-and-retry-budgets)
- [Worker crash after an external write](#worker-crash-after-an-external-write)
- [Load tests must resemble conversations](#load-tests-must-resemble-conversations)
- [Version the behavioral system](#version-the-behavioral-system)
- [Operational debugging drill](#operational-debugging-drill)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## Sessions behave differently from short HTTP requests

A voice session holds media connections, provider state, buffers, and controller tasks over time. Stateless request serving alone does not describe its resource needs. Frontend hosting and runtime hosting may require different infrastructure.

Deploy the browser UI where appropriate, but place long-running media workers on infrastructure supporting their connection duration, protocols, resource requirements, and termination behavior. Check platform limits explicitly rather than assuming every frontend server can hold a phone call.

## Separate lifecycle and readiness

Liveness asks whether the process is functioning. Readiness asks whether it can accept a new session. Admission control asks whether accepting that session will violate resource or provider limits.

A worker can be alive but unavailable because all model slots are occupied. Mark it unready for new work without killing existing conversations. On shutdown, stop accepting sessions, drain within a bounded interval, then terminate remaining sessions with a clear recovery path.

## Retry and fallback policy

Categorize failures. Invalid credentials require configuration repair; transient network failures may permit bounded retry with jitter; quota exhaustion may need admission control or an authorized alternative.

Do not stack retries at every layer without coordination. Three retries in the adapter and three in the controller can multiply requests and delay. Use a shared deadline and a clear retry owner.

Fallback between providers must normalize formats and semantics. A replacement TTS may use another rate; a replacement model may have different tool behavior; a replacement recognizer may emit different finalization events. Evaluate fallback as a real architecture path, not just a configurable URL.

## Durable operations versus ephemeral sessions

Store consequential operation IDs and results durably. After a worker crash, reconcile writes before retrying. Audio buffers and model sessions may be unrecoverable; explain that to the caller and resume from verified business state when possible.

Do not promise seamless session migration unless the model and transport contracts support it and you have tested it. A new worker can recreate context while still losing timing or unheard-output information.

## Capacity planning

Measure memory per session, CPU for conversion and encoding, outbound/inbound bandwidth, provider concurrency, connection setup rate, and event-loop delay. GPU workloads also depend on model size, context, batch behavior, and scheduling.

For a stable system, Little's law relates average concurrent work to arrival rate multiplied by average time in the system. At two new sessions per second and a mean duration of five minutes, average concurrency is roughly 600. This estimates the mean, not burst capacity or p95 occupancy.

Load tests should preserve realistic session duration and audio cadence. Ten thousand instantly closed sockets do not characterize a system serving ten thousand active conversations. Track task success, tail latency, and failures under load.

## Deployment evidence

Version code, prompts, graph configuration, adapter dependencies, and evaluation datasets together. Use a development environment, run regression and failure tests, and roll out changes with an observable rollback path.

Rollback can restore application code but cannot undo bookings or messages already sent. Keep migrations compatible where practical, and coordinate durable workflow schema changes explicitly.

Expose redacted dashboards for startup failure, turn latency, interruption delay, tool outcomes, provider errors, queue age, concurrency, and cost. Alerts should indicate user impact and an actionable owner.

## Failure drill

During an active session, delay recognition, fail synthesis, interrupt while a write times out, disconnect transport, and terminate a worker. Record what the user hears, what business state survives, and how resources are released. The production checklist translates these into release evidence.

## Derive a first capacity estimate

Assume a synthetic service receives two new sessions per second and the average session lasts 300 seconds. In stable conditions, average concurrency is approximately `2 × 300 = 600` sessions. This relationship does not specify burst capacity or the concurrency distribution.

Suppose measured runtime memory averages 18 MiB per active session excluding shared model weights. Six hundred sessions consume about 10,800 MiB, or 10.55 GiB, for that component alone. Add process baseline, buffers, model/client state, caches, and reserve. Do not size the service from the optimistic average without tail and burst measurements.

For 16 kHz mono signed 16-bit PCM, one direction is 32,000 payload bytes per second. Six hundred continuously active input streams represent 19.2 MB/s of raw payload. Actual wire usage depends on codec, protocol overhead, silence behavior, and other directions. This calculation is a boundary estimate, not a transport invoice.

CPU work includes decoding, resampling, feature extraction where local, packet handling, serialization, and controller tasks. Provider concurrency can be the limiting factor before CPU or memory. An admission policy should use the narrowest relevant resource budget, not only host CPU percentage.

## Separate admission, readiness, and draining

Readiness says a worker can accept new work under its dependency and capacity state. Admission decides whether this particular session is allowed under global, tenant, and provider limits. Draining closes admission while existing sessions finish within a deadline.

A deployment sequence can be: start new workers, verify dependencies/readiness, route new sessions to them, stop new admission on old workers, wait for active sessions, then close remaining sessions with an explicit policy. Killing old workers immediately can turn a routine deployment into widespread mid-call failures.

The orchestrator must know which sessions a worker owns. Load-balancing reconnects to another worker does not automatically transfer its model socket, buffers, or workflow state. Either use a supported resume design or recreate a session from durable verified state and tell the client what changed.

## Coordinate deadlines and retry budgets

Suppose a turn has a two-second remaining response budget. A tool attempt taking 1.5 seconds leaves only 0.5 seconds for recovery and communication. Starting another two-second retry because each request independently has a two-second timeout violates the turn budget.

Define operation deadlines once and pass remaining time to adapters. Retry transient failures with bounded attempts/jitter where useful. Do not retry invalid credentials or denied authorization. Stop retries when the associated turn is obsolete unless the operation requires durable reconciliation.

Fallback also consumes budget. A second provider with different format/session behavior needs adapter normalization and evaluation. “Fallback enabled” is not evidence that users receive correct, coherent output during the primary failure.

## Worker crash after an external write

Use the ledger from chapter 12. The worker has a pending operation; the external calendar commits; the worker dies before persisting success. Recovery claims the operation safely, queries external state by the stable key where supported, stores the authoritative result, and prevents duplicate execution.

If reconciliation is unavailable, report unknown outcome and route to the defined recovery process. Do not convert unknown to failed merely because a new process has an empty in-memory dictionary. Durable identity is what connects the new worker to the previous business effect.

Separate resumed conversation from resumed audio. The service may recover the booking while being unable to reconstruct which words the caller heard. A concise verified recap can be more reliable than pretending uninterrupted continuity.

## Load tests must resemble conversations

Use realistic audio cadence, session duration, turn spacing, tool mix, and interruption/disconnect rates. A benchmark opening and immediately closing sockets tests connection churn, not sustained voice concurrency.

Increase load gradually in a controlled environment. Observe event-loop delay, queue age, per-session memory, provider errors, p95 turn gap, task success, and cleanup. At overload, a good admission policy rejects or delays new sessions predictably instead of silently adding seconds of queueing to every caller.

Test burst arrivals as well as steady state. Five minutes of average capacity does not demonstrate that all workers can initialize model connections during a sudden burst.

## Version the behavioral system

A prompt, graph property, model selection, or endpoint threshold can change behavior as much as application code. Store them with version identifiers and evaluation results. Rollbacks should select a coherent set rather than old code with new incompatible schemas.

Keep durable schemas compatible across a rolling deployment or plan migration explicitly. Old and new workers may coexist while handling operations. A code rollback cannot reverse notifications or bookings already committed; business recovery needs separate operations.

## Operational debugging drill

Run one synthetic session through provider disconnect, delayed tool result, worker termination, and deployment drain. Record user-heard behavior, surviving operation state, retry decisions, and released resources. Then run several sessions under the same conditions to expose shared-capacity problems. Document which continuity guarantees are implemented and which remain unavailable.

## Check your understanding

1. Why can a live worker be unready for new sessions?
2. Which state must be reconciled after a crash?
3. Why is rollback not reversal of external actions?

[Production checklist](../reference/production-checklist.md) · [Lab 12](../labs/12-production-failure-drills.md) · [Capstone](../capstone/README.md) · [Course](../README.md).
