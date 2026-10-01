# 9. Barge-in and cancellation across the whole pipeline

**Prerequisites:** chapters 3 and 6–8. **Goal:** stop obsolete output and preserve the difference between action completion and audible completion.

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

## Check your understanding

1. Why are both queue clearing and generation fencing needed?
2. Can coroutine cancellation reverse a completed booking?
3. What might a provider's history believe after local playback is cleared?

Continue with [orchestration](10-runtime-and-orchestration.md). [Lab 5](../labs/05-interruption.md) and [TEN interruption walkthrough](../code-reading/turn-control.md).
