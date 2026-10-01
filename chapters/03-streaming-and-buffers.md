# 3. Streaming, buffering, clocks, and backpressure

**Prerequisites:** chapter 2. **Goal:** explain why individually fast stages can accumulate seconds of delay.

## A stream is a sequence with a contract

“Streaming” means results can be processed incrementally; it does not mean every stage starts immediately or that latency is bounded. A transport may stream 20 ms frames while a recognizer batches 500 ms and synthesis waits for a complete paragraph.

Give each audio event a session identifier, stream identifier, sequence number, sample timestamp, format, and response generation where appropriate. A sequence detects loss or duplicates; a media timestamp places the event on the signal timeline; an arrival timestamp measures delivery. These identifiers answer different questions.

Use a monotonic clock for local duration measurements. Wall-clock corrections can make elapsed times negative. Separate clock domains across client and server. Without synchronization, subtracting a client timestamp from a server timestamp does not produce a reliable one-way network delay.

## Buffers solve one problem and create another

A jitter buffer smooths irregular delivery so playback can continue. A model-input buffer groups samples into the context required by inference. A TTS queue absorbs variation in synthesis speed. A device buffer keeps the sound hardware fed.

Each buffer stores time, not just memory. If 50 queued frames each contain 20 ms, the queue contains one second of audio. A 100-item limit is meaningless unless item duration is controlled. Prefer reporting queue duration and oldest-item age alongside item count.

Small buffers reduce waiting but risk underflow. Large buffers tolerate variability but increase response and interruption delay. Adaptive playback buffering must be bounded so sustained network instability does not turn a conversational stream into delayed narration.

## Backpressure internally

Suppose frames arrive at 50 per second but a stage processes 40. The backlog grows by 10 frames per second, or 200 ms of audio per second with 20 ms frames. After ten seconds, that stage has introduced two seconds of delay even if each individual call appears quick.

Backpressure makes overload visible to producers. Options include reducing generated output, limiting concurrent sessions, pausing a non-media producer, or explicitly failing a session. Live microphone capture cannot always pause without losing speech. If frames must be dropped, record the discontinuity and reset or notify affected recognizers; do not silently concatenate unrelated samples.

For assistant output, prefer cancelling an obsolete generation over playing stale queued content. If the user interrupted, the old answer's bytes are no longer useful regardless of how expensive they were to generate.

## Chunk boundaries are not semantic boundaries

A network read may split a JSON event, a UTF-8 character, a tool argument, or an audio packet. Let the relevant parser assemble its complete unit. Do not treat arbitrary socket chunks as complete sentences.

LLM token chunks can end in the middle of a word. Text sent to TTS needs a segmentation policy. Audio chunks sent to playback need the decoder's frame constraints. One shared `chunk_size` setting cannot specify all of these contracts.

## Cancellation has a race

Cancellation is a request; an in-flight callback can still arrive. Label output with a generation number, and reject output whose generation is no longer active. This is a fencing rule. A queue clear removes existing content; generation fencing rejects future late content. You need both for reliable interruption.

The [runtime experiment](../examples/turn_runtime.py) demonstrates this with deliberately late chunks. It models state and queue logic, not threads, real audio devices, or provider sockets.

## Worked trace

```text
0 ms     microphone emits frame 0
20 ms    frame 1 emitted
35 ms    server receives frame 0
38 ms    server receives frame 1
60 ms    consumer completes frame 0
80 ms    consumer completes frame 1
```

Irregular arrival did not change capture cadence. Compute network and processing behavior separately. For production tracing, use correlation IDs plus local span durations, and document any clock synchronization assumptions.

## Check your understanding

1. What is the duration of 75 queued 20 ms frames?
2. Why can a cancel request leave late audio callbacks?
3. What must happen if input audio is dropped during overload?

Continue with [LLM internals](04-llm-internals.md). [Lab 2](../labs/02-streaming-transcripts.md) and [lab 5](../labs/05-interruption.md).
