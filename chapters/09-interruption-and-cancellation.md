# 9. Barge-in and cancellation across the whole pipeline

**Prerequisites:** chapters 3 and 6–8. **Goal:** stop obsolete output and preserve the difference between action completion and audible completion.

<!-- chapter-navigation:start -->
**In this chapter**

- [Why “cancel the LLM” is insufficient](#why-cancel-the-llm-is-insufficient)
- [A complete interruption sequence](#a-complete-interruption-sequence)
- [Fencing late output](#fencing-late-output)
- [Tool cancellation is different](#tool-cancellation-is-different)
- [History and delivery](#history-and-delivery)
- [Measure the right thing](#measure-the-right-thing)
- [Walk through the race that queue clearing alone misses](#walk-through-the-race-that-queue-clearing-alone-misses)
- [Separate the acknowledgements](#separate-the-acknowledgements)
- [Implementation pattern for asynchronous producers](#implementation-pattern-for-asynchronous-producers)
- [What task cancellation really means](#what-task-cancellation-really-means)
- [Reconcile a consequential operation separately](#reconcile-a-consequential-operation-separately)
- [Delivery history under partial playback](#delivery-history-under-partial-playback)
- [Failure drill](#failure-drill)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## Why “cancel the LLM” is insufficient

When a user interrupts, the LLM may already have emitted text, synthesis may have produced audio, the server may have queued packets, and the device may have buffered sound. Cancelling one producer does not remove downstream material.

Reliable barge-in is a distributed state transition. The assistant yields the floor, obsolete generation becomes invalid, pending output is cleared, and the application reconciles what happened during the interrupted turn.

## A complete interruption sequence

1. Detect and classify speech onset under the product's policy.
2. Advance the active response generation or mark the response invalid.
3. Clear local playback quickly where supported.
4. Cancel LLM and TTS work using their actual interfaces.
5. Clear runtime and transport queues for the invalid generation.
6. Reject late callbacks carrying obsolete generation IDs.
7. Mark the spoken response interrupted and preserve completed tool effects.

The exact sequence depends on interfaces; local clear and server cancellation may run concurrently. Advancing invalidation before awaiting a slow provider cancel prevents late output from being accepted during that await.

## Fencing late output

```text
active generation = 8
chunk(generation=8) -> accept
user interrupts -> active generation = 9
late chunk(generation=8) -> reject
chunk(generation=9) -> accept
```

A generation ID fences content. Session IDs alone do not distinguish several responses within one session. Turn IDs describe user/assistant interaction; tool call IDs and provider response IDs have their own roles. Preserve a mapping rather than reusing one identifier for every purpose.

The [offline runtime](../examples/turn_runtime.py) demonstrates queue clearing and stale-chunk rejection. It also includes a simple silence endpoint to show how one controller owns both turn transitions and output validity.

## Tool cancellation is different

A read-only search can often be abandoned. A booking request may have reached a server and committed even if your request task was cancelled. Cancellation cannot undo an external side effect. Query authoritative state or use an idempotency key before retrying.

If the user interrupts with “don't book it” during a booking, stop further actions, determine whether the first action committed, and explain the actual state. If already committed, use the application's cancellation workflow with appropriate authorization. Do not pretend local coroutine cancellation reversed the booking.

## History and delivery

Keep tool state, generated text, and playback progress independently. Store “assistant response interrupted” if accurate alignment is unavailable. A later model should not assume the user heard an unplayed instruction or confirmation code.

If a realtime provider maintains its own conversation history, use its supported truncation or reconciliation mechanism. Local playback clearing alone may leave the provider reasoning from content the user never heard. The application must understand that session contract; generic “flush” naming is not enough.

## Measure the right thing

Interruption latency is the interval from the chosen speech-onset definition to last obsolete audio heard. You can separately measure VAD detection delay, control-event transit, server queue clear, and local playback clear. For a device-level result, record loopback audio or use a verified client playback signal with documented limits.

Count false interruptions from echo, background speech, and backchannels. A low interruption delay with frequent false triggers makes a poor conversation.

## Walk through the race that queue clearing alone misses

At 0 ms, response generation 20 is active. At 100 ms, text segment 0 begins synthesis. At 200 ms, its first audio reaches the server output queue. At 250 ms, the user starts speaking. At 290 ms, onset is confirmed and the controller interrupts. At 310 ms, an already in-flight synthesis callback returns another chunk for generation 20.

If the interrupt handler merely empties the queue at 290 ms, the callback at 310 ms can enqueue fresh obsolete audio. The queue was successfully cleared; the design still fails. The correct acceptance condition is both “this output belongs to the active generation” and “the session state permits output.”

Advance invalidation before awaiting cancellation. Otherwise the provider's cancel call can take 100 ms while callbacks continue to pass an unchanged generation check. Generation fencing is the immediate local transition; provider cancellation reduces wasted work and prevents further external generation when supported.

## Separate the acknowledgements

| Signal | What it establishes | What it does not establish |
| --- | --- | --- |
| Controller invalidated response | New local acceptance should reject old output | Existing device audio is gone |
| Provider accepted cancellation | Provider received/processed a control request under its contract | Every late callback has disappeared |
| Server queue cleared | That queue no longer holds old chunks | Transport/client/device queues are empty |
| Client clear acknowledged | Client processed a clear command under its contract | Sound already sent to hardware stopped instantaneously |
| Last obsolete sample observed | Device-level output stopped at the measured point | External tool side effects were reversed |

Design traces around these meanings. A log line saying “interrupt success” is too coarse to identify which guarantee you have.

## Implementation pattern for asynchronous producers

This is **pseudocode for lifecycle ordering**; the provider and output interfaces must be implemented against the chosen stack:

```text
interrupt(session):
    old_generation = session.active_generation
    session.active_generation += 1
    session.output_allowed = false
    clear_local_server_queue(old_generation)
    request_client_clear(old_generation)
    request_provider_cancel(old_generation)
    mark_delivery_interrupted(old_generation)

accept_output(event):
    if session.closed: discard
    if event.generation != session.active_generation: discard
    if not session.output_allowed: discard
    enqueue_for_playback(event)
```

Starting a new response sets output permission deliberately. Merely incrementing a number should not automatically allow a response while the user is still speaking. Where producers cannot carry your generation ID, bind their provider response ID to a generation when they are created and resolve callbacks through that mapping.

## What task cancellation really means

In asynchronous Python, a cancellation request is delivered at a suspension opportunity; a coroutine may run cleanup and propagate cancellation. Blocking work outside that cooperative path may not stop promptly. Cancelling the task waiting for a network operation also does not prove the remote service stopped processing it. The [task documentation](https://docs.python.org/3/library/asyncio-task.html) explains the local mechanism.

Use `try/finally` for local resource cleanup, bounded waiting for shutdown, and provider-specific cancel semantics. Do not swallow cancellation as an ordinary provider failure and automatically start a fallback response; that can make the assistant restart talking while the caller is interrupting.

For threaded or native processing, investigate how cancellation crosses that boundary. A cancelled await can leave a background computation using CPU or memory. Register ownership and completion so late work cannot publish into a closed session.

## Reconcile a consequential operation separately

Imagine a booking commits at 260 ms, but its reply is delayed until 400 ms. The interruption at 290 ms cannot undo the commit. The operation ledger should still receive the authoritative result at 400 ms, while the old response generation remains invalid for speech.

The next interaction can truthfully say that the booking completed, then offer a cancellation workflow if the caller wants to reverse it. If the outcome remains unknown, state uncertainty and reconcile by operation key. Do not use the state of the response coroutine as the state of the business operation.

## Delivery history under partial playback

Keep a response record containing generated text, synthesized segments, playback progress where observable, interruption reason, and known business outcomes. If the first sentence was heard and the second was not, the next turn should avoid assuming the user has the second sentence's instructions.

Without word alignment, retain conservative segment-level delivery or an interruption marker. If a provider offers a truncation interface, verify which timeline and response item it expects. Truncating based on bytes received rather than samples played can retain unheard content or remove heard content.

## Failure drill

Inject a late text delta, a late audio chunk, a late tool result, and a late avatar update after one interruption. Predict which should be discarded and which should update durable state without speaking. The audio and avatar belong to obsolete delivery; a completed booking belongs to business state. This is the distinction that a single “cancel everything” boolean cannot express.

## Check your understanding

1. Why are both queue clearing and generation fencing needed?
2. Can coroutine cancellation reverse a completed booking?
3. What might a provider's history believe after local playback is cleared?

Continue with [orchestration](10-runtime-and-orchestration.md). [Lab 5](../labs/05-interruption.md) and [TEN interruption walkthrough](../code-reading/turn-control.md).
