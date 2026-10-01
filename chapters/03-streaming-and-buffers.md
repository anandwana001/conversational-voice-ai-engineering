# 3. Streaming, buffering, clocks, and backpressure

**Prerequisites:** chapter 2. **Goal:** explain why individually fast stages can accumulate seconds of delay.

<!-- chapter-navigation:start -->
**In this chapter**

- [A stream is a sequence with a contract](#a-stream-is-a-sequence-with-a-contract)
- [Buffers solve one problem and create another](#buffers-solve-one-problem-and-create-another)
- [Backpressure internally](#backpressure-internally)
- [Chunk boundaries are not semantic boundaries](#chunk-boundaries-are-not-semantic-boundaries)
- [Cancellation has a race](#cancellation-has-a-race)
- [Worked trace](#worked-trace)
- [Derive queue growth from producer and consumer rates](#derive-queue-growth-from-producer-and-consumer-rates)
- [What a bounded queue does and does not solve](#what-a-bounded-queue-does-and-does-not-solve)
- [Build a media-time jitter buffer on paper](#build-a-media-time-jitter-buffer-on-paper)
- [Track the age of content, not just connection health](#track-the-age-of-content-not-just-connection-health)
- [Clock drift and buffer drift](#clock-drift-and-buffer-drift)
- [Debugging drill](#debugging-drill)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Derive queue growth from producer and consumer rates

Let `λ` be the number of incoming frames per second and `μ` the number processed per second. If `λ > μ` for a sustained interval, a simplified backlog model grows at `λ − μ` frames per second. With 20 ms frames, arrival at 50 frames/s and processing at 40 frames/s adds 200 ms of backlog per second.

After five seconds, about 50 frames are waiting. Even if the network adds only 30 ms, a newly arriving frame can wait more than a second before processing. This explains a common symptom: a service starts responsive, then becomes slower during a long call without any single request showing an extraordinary execution time.

The equation is a fluid approximation. Real systems have bursts, variable processing duration, scheduling, and shared workers. It still tells you what to measure: arrival rate, service rate, queue age, and queued media duration.

## What a bounded queue does and does not solve

Here is an executable bounded-producer/consumer example for Python 3.9+. It represents work items, not a real microphone or playback device:

```python
import asyncio

async def producer(queue):
    for sequence in range(5):
        await queue.put(sequence)
        print("accepted", sequence, "queued", queue.qsize())
    await queue.put(None)

async def consumer(queue):
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            await asyncio.sleep(0.02)  # simulated work
            print("processed", item)
        finally:
            queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=2)
    await asyncio.gather(producer(queue), consumer(queue))
    await queue.join()

asyncio.run(main())
```

Once two items are waiting, the producer's next `put` waits until capacity is freed. This bounds this queue, but a real capture callback cannot necessarily await it. If capture keeps adding to a different unbounded queue, the system merely moves the backlog upstream. Document the overflow policy at the earliest producer that cannot pause.

Calling `task_done` completes the queue's bookkeeping; it does not mean a user heard sound. Likewise, `queue.join` waits for processing acknowledgements, not necessarily a device's audio completion. Use distinct signals for work processing and media delivery. The [Python queue documentation](https://docs.python.org/3/library/asyncio-queue.html) defines the API behavior.

## Build a media-time jitter buffer on paper

Consider three 20 ms audio packets with media timestamps 0, 20, and 40 ms. They arrive at local times 30, 75, and 68 ms: packet 2 arrives before packet 1. A receiver must reorder by media sequence/timestamp rather than play arrival order.

Suppose first playout begins at 70 ms. Packet 0 plays during 70–90 ms, packet 1 during 90–110 ms, and packet 2 during 110–130 ms. All are available in time. With first playout at 40 ms, packet 1 is needed at 60 ms but does not arrive until 75 ms; the receiver must conceal, pause, or change scheduling. This is the basic tradeoff between buffering delay and underflow.

A production receiver also needs wraparound-aware timestamps, clock drift handling, packet loss rules, and codec-specific dependencies. The paper example deliberately uses one small timeline to make the decision understandable before adding protocol complexity.

## Track the age of content, not just connection health

Define `queue_age = now_monotonic − enqueue_monotonic` for local scheduling. Define `queued_audio_ms` from sample counts and rate. These measurements tell you whether content is still useful even when every socket is connected.

For an assistant response, a five-second queued answer may already be socially obsolete. For a transcription archive, delayed processing may still be acceptable. Overload policy depends on whether the workload is interactive or archival; the same drop rule does not serve both.

Control events deserve bounded service. If cancellation enters the same FIFO behind 250 audio frames, it waits behind five seconds of content. Use a priority lane, a separate control queue, or direct state invalidation, and then clear dependent media. Priority alone is insufficient if the consumer is blocked in one long noninterruptible operation.

## Clock drift and buffer drift

Capture and playback devices can disagree slightly about how fast one second passes. If one side effectively supplies 48,005 samples while the other consumes 48,000 per nominal second, backlog grows slowly even without network problems. Long calls make that drift visible.

Avoid repairing drift by periodically throwing away arbitrary samples without considering audible artifacts. Real media systems can use timestamp-based scheduling and adaptive conversion. For your application, first determine which layer already handles drift, and do not apply a second incompatible correction.

## Debugging drill

Make a table with capture cadence, receive cadence, consumer completion cadence, queue duration, and playback cadence for a slow turn. If receive cadence is bursty but average service exceeds arrival, inspect jitter handling. If service persistently falls below arrival, inspect capacity. If only obsolete generations appear, inspect fencing. These hypotheses require different fixes despite a shared complaint of “lag.”

## Check your understanding

1. What is the duration of 75 queued 20 ms frames?
2. Why can a cancel request leave late audio callbacks?
3. What must happen if input audio is dropped during overload?

Continue with [LLM internals](04-llm-internals.md). [Lab 2](../labs/02-streaming-transcripts.md) and [lab 5](../labs/05-interruption.md).
