# 22. Reliability, deployment, and session scaling

**Prerequisites:** chapters 10 and 19–21. **Goal:** operate long-lived conversations through failure, deploy safely, and plan capacity using evidence.

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

## Check your understanding

1. Why can a live worker be unready for new sessions?
2. Which state must be reconciled after a crash?
3. Why is rollback not reversal of external actions?

[Production checklist](../reference/production-checklist.md) · [Lab 12](../labs/12-production-failure-drills.md) · [Capstone](../capstone/README.md) · [Course](../README.md).
