# 10. Runtime architecture, events, and orchestration

**Prerequisites:** chapters 1–9. **Goal:** build a session controller whose state remains coherent under concurrency.

<!-- chapter-navigation:start -->
**In this chapter**

- [The runtime joins incompatible interfaces](#the-runtime-joins-incompatible-interfaces)
- [Define your event vocabulary](#define-your-event-vocabulary)
- [Own state centrally, process work concurrently](#own-state-centrally-process-work-concurrently)
- [State is more than conversation history](#state-is-more-than-conversation-history)
- [Errors belong to the protocol](#errors-belong-to-the-protocol)
- [Workflows and multiple agents](#workflows-and-multiple-agents)
- [Worked failure](#worked-failure)
- [Build a session reducer and effect runner](#build-a-session-reducer-and-effect-runner)
- [Trace a reducer sequence](#trace-a-reducer-sequence)
- [Avoid shared mutable state across sessions](#avoid-shared-mutable-state-across-sessions)
- [Concurrency and lock scope](#concurrency-and-lock-scope)
- [Define error events and recovery ownership](#define-error-events-and-recovery-ownership)
- [Debug with replayable events](#debug-with-replayable-events)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Build a session reducer and effect runner

A useful design splits pure state transitions from asynchronous effects. A reducer accepts `(state, event)` and returns `(new_state, effects)`. The effect runner performs network or media work and sends its results back as events.

For example, a committed user turn updates state immediately and produces a `request_model` effect. The reducer does not wait for the model while holding ownership of session state. Later, a model delta returns with the response generation, and the reducer either accepts or rejects it.

This separation makes replay and unit testing easier: a recorded event sequence can reproduce state transitions without opening provider connections. It does not make the whole application pure—effects still happen—but it exposes where those effects are authorized.

### Define the state you actually need

```text
SessionState:
    lifecycle: NEW | READY | DRAINING | CLOSED
    floor: LISTENING | USER_SPEAKING | POSSIBLE_END | ASSISTANT_SPEAKING
    user_turn_id
    endpoint_candidate_version
    active_response_generation
    transcript_segments
    pending_operations_by_id
    delivery_records_by_generation
    authenticated_scope
```

Treat lifecycle, conversational floor, business operation, and delivery as related but independent state machines. A booking can remain `RUNNING` while the floor changes from assistant to user. A session can enter `DRAINING` while a final confirmation is delivered.

## Trace a reducer sequence

| Input event | Transition | Effect |
| --- | --- | --- |
| `speech_started` | Invalidate endpoint candidate; take user floor | Clear/cancel obsolete delivery |
| `segment_final` | Update stable transcript | None unless turn policy separately permits commitment |
| `turn_committed` | Guard against duplicate turn; allocate response generation | Build context and request model |
| `tool_proposed` | Validate proposal and workflow state | Execute permitted operation with stable key |
| `tool_completed` | Update operation outcome regardless of speech generation | Continue speaking only if current state allows it |
| `audio_ready` | Check generation and lifecycle | Queue valid audio |
| `session_closed` | Mark closed before async cleanup | Cancel producers and release resources |

The ordering of closed/invalidation state before cleanup is important. Cleanup can take time, and external callbacks may still arrive during it.

## Avoid shared mutable state across sessions

An adapter object that stores one global `current_customer` can accidentally apply one session's tool result to another. Context, authenticated scope, generation counters, and pending operations must be session-scoped.

Model clients and connection pools can be shared if their interfaces permit it, but sharing a client is not the same as sharing conversation state. A wrapper that stores history on the client object can defeat otherwise correct per-session routing.

When an event arrives, resolve its session explicitly. Do not infer the destination from whichever browser or caller most recently connected. For multi-speaker sessions, stream IDs and speaker labels further refine attribution without replacing authentication.

## Concurrency and lock scope

Suppose the controller holds a state lock while awaiting a two-second tool request. The interruption handler cannot acquire the lock, so cancellation becomes two seconds late. Instead, record a pending operation under a short transition, release the lock, execute the request, and apply the result through another guarded transition.

A serialized event loop can replace explicit locks for session transitions, provided handlers do not block it with synchronous work. CPU-heavy decoding, resampling, or inference may need an appropriate execution path. Moving work into a thread does not automatically provide safe cancellation or state ownership.

## Define error events and recovery ownership

Every adapter failure should identify its operation, category, and recoverability. Keep a single retry owner for each class of work. If an adapter retries three times and the controller also retries three times, an apparently small policy can create many requests and a large delay.

Deadlines belong to the operation or turn, not just each individual attempt. An attempt should use the remaining budget. When a turn is obsolete, stop launching retries even if budget remains.

## Debug with replayable events

Record synthetic event sequences for duplicate commitment, late completion after close, and interruption during a tool call. Replay them through the reducer and assert final state and permitted effects. These tests are stronger than checking that a particular method was invoked, because they express the desired system invariant.

Finally translate a TEN graph and controller into this vocabulary. Nodes provide adapters; graph edges route messages; lifecycle hooks initialize and release resources; the controller/agent implementation owns transitions and effects. Identify where the actual upstream design differs rather than claiming this illustrative reducer is TEN's architecture.

## Check your understanding

1. Why do graph connections not describe all controller behavior?
2. How do serialized transitions coexist with concurrent network work?
3. Which state should survive a worker restart?

Continue with [realtime models](11-realtime-speech-to-speech.md). [Lab 5](../labs/05-interruption.md) and [TEN map](../code-reading/README.md).
