# 10. Runtime architecture, events, and orchestration

**Prerequisites:** chapters 1–9. **Goal:** build a session controller whose state remains coherent under concurrency.

## The runtime joins incompatible interfaces

Transport delivers audio frames. ASR delivers changing text. LLMs deliver text deltas and tool proposals. TTS delivers audio. A runtime adapts these into explicit events and coordinates their lifecycle.

A graph declares which components exist and how messages flow. An extension or adapter implements a component's behavior. The graph is not the whole application: controller code can send commands directly, assemble context, validate actions, or initiate requests outside a static audio connection.

In TEN, graph properties, extension lifecycle methods, and controller events together determine behavior. [The cascade walkthrough](../code-reading/cascade.md) shows how to read them in that order.

## Define your event vocabulary

Separate `audio_frame`, `transcript_interim`, `transcript_segment_final`, `turn_committed`, `response_started`, `response_delta`, `tool_proposed`, `tool_completed`, `playback_progress`, `interrupted`, and `session_closed`. Provider-specific messages should become application events at an adapter boundary.

Every event needs an owner and correlation identifiers. Include enough information to reject stale data. Do not emit a generic `done` without identifying whether recognition, text generation, synthesis, or playback completed.

An event schema is an API. Evolve it with versioning or compatibility rules. Treat missing fields as explicit validation failures when they are required for safe routing.

## Own state centrally, process work concurrently

A session controller can serialize state transitions while asynchronous tasks perform recognition, generation, retrieval, and synthesis. This reduces race conditions without forcing all network calls to run one at a time.

Do not hold a state lock while waiting on a slow provider call. Update state, launch a task with the current identifiers, and apply its result only if the state still permits it. This combines concurrency with deterministic transitions.

Maintain a registry of tasks so shutdown can cancel and await them. Untracked background tasks can emit events after the session closes. Cleanup must close sockets, stop audio producers, release model sessions, and clear queues with bounded timeouts.

## State is more than conversation history

Track active user turn, active response generation, tool operation state, playback cursor, authentication context, pending endpoint timer, and transport health. Conversation messages alone cannot tell you whether an external action is still running or audio is stale.

Separate ephemeral runtime state from durable business state. A process restart should not reset a booking that already committed. Durable tool records need operation IDs, outcomes, and a reconciliation strategy.

## Errors belong to the protocol

Adapters should produce typed failures: invalid input, authentication failure, quota exhaustion, timeout, transient disconnect, and internal error. Retry policy depends on the category. Blind retry on invalid credentials adds delay and cost without improving success.

The user needs a truthful, concise recovery message; engineers need a redacted diagnostic event. Avoid speaking provider exception text, secrets, or raw stack traces.

## Workflows and multiple agents

A deterministic workflow is often appropriate for booking: collect fields, validate, confirm, execute, report. An LLM can interpret user input within those stages. Letting an unconstrained model choose every transition makes the workflow harder to audit.

Multiple agents can separate expertise, but they also add context handoffs, latency, duplicated actions, and ownership ambiguity. A router plus tools may solve the task more simply. If you introduce specialists, explicitly define who speaks, who owns the tool operation, and how cancellation propagates.

## Worked failure

An ASR final and an endpoint timer both arrive. Each starts a response. Two TTS streams play and two tool calls execute. Prevent this with a single `commit_turn` transition that is idempotent for the turn ID. A prompt cannot reliably repair this concurrency bug.

## Check your understanding

1. Why do graph connections not describe all controller behavior?
2. How do serialized transitions coexist with concurrent network work?
3. Which state should survive a worker restart?

Continue with [realtime models](11-realtime-speech-to-speech.md). [Lab 5](../labs/05-interruption.md) and [TEN map](../code-reading/README.md).
