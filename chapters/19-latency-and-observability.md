# 19. Latency engineering and observability

**Prerequisites:** chapters 3 and 8–16. **Goal:** explain a slow conversation using measured stage boundaries.

<!-- chapter-navigation:start -->
**In this chapter**

- [Define the user's metric first](#define-the-users-metric-first)
- [Decompose a trace](#decompose-a-trace)
- [Tail latency and missing outcomes](#tail-latency-and-missing-outcomes)
- [Correlation and event schema](#correlation-and-event-schema)
- [Optimize after diagnosing](#optimize-after-diagnosing)
- [Cost and efficiency](#cost-and-efficiency)
- [Calculate an end-to-end trace instead of adding labels](#calculate-an-end-to-end-trace-instead-of-adding-labels)
- [Compute percentiles and inspect the sample](#compute-percentiles-and-inspect-the-sample)
- [Why stage percentiles cannot be added](#why-stage-percentiles-cannot-be-added)
- [Instrument spans with explicit ownership](#instrument-spans-with-explicit-ownership)
- [Budget latency against task quality](#budget-latency-against-task-quality)
- [Build actionable diagnostic views](#build-actionable-diagnostic-views)
- [Account for utilization and batching tradeoffs](#account-for-utilization-and-batching-tradeoffs)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## Define the user's metric first

End-of-speech to first audible response describes a turn gap. Speech onset to last obsolete audible output describes interruption delay. Connection request to session readiness describes startup time. These metrics answer different questions and must not share an ambiguous label such as “latency.”

Define `end_of_speech`: human annotation, last speech sample from VAD, or endpoint event receipt. Each changes the measurement. If you report only endpoint-to-audio time, you can hide a long silence timeout.

## Decompose a trace

```text
t0 user acoustic speech ends
t1 controller commits turn
t2 model request starts
t3 first speakable text segment
t4 first synthesized audio is ready
t5 first audio is played by client
```

The intervals expose endpointing, request preparation, model/segmentation, synthesis, and delivery. STT finalization or retrieval may occur before or after t1 depending on the design. Add their spans without assuming the pipeline is completely sequential.

Do not sum independent span durations if they overlap. Compute the critical path from dependency and timestamp information. Summing p95 values from different stages also does not produce the true end-to-end p95, since slow events may happen in different turns.

## Tail latency and missing outcomes

A median can look excellent while one in twenty callers waits several seconds. Report p50, p95, sample count, workload, and failure rate. For small samples, a p95 is unstable; show individual results or ranges as well.

If failed turns are omitted, the remaining latency distribution looks artificially good. Report failures and timeouts alongside successful latency. Choose whether timed-out turns are right-censored, assigned a timeout bound, or analyzed separately, and state the policy.

The [latency script](../examples/latency_report.py) uses a documented nearest-rank percentile on synthetic successful turns and counts failed turns separately. It does not claim real provider performance.

## Correlation and event schema

Trace IDs join local spans; session, turn, response generation, segment, and tool operation IDs establish causality. Carry them across adapters. Log format changes, queue duration, reconnects, cancellation reason, and stale-event drops.

Use monotonic times for local durations. Across machines, rely on synchronized clocks with known uncertainty or measure local intervals and round trips. An unsynchronized client/server subtraction can invent negative network latency.

Redact transcript and tool fields by default where sensitive. Debug logs should describe event types, timing, and outcomes without needing complete caller content. Record what instrumentation can and cannot observe, especially actual device playback.

## Optimize after diagnosing

If endpointing dominates, changing model hardware may do little. If first text is quick but first speakable segment is late, inspect segmentation or response style. If audio generation is quick but hearing is late, inspect transport and playback buffers.

Useful techniques include warm sessions, connection reuse, bounded context, independent read prefetch, and measured segmentation. Each has tradeoffs in cost, quality, privacy, or resource usage. Avoid speculative writes and do not shorten endpointing without tracking false cuts.

## Cost and efficiency

Track billable audio input/output, recognition duration, text tokens, synthesis units, transport usage, tool requests, and worker time according to actual provider billing units. Cached or cancelled work may still cost money.

Report cost per successful task as well as per session. A cheap session that fails and triggers several retries can be more expensive operationally. Keep prices in configuration or dated measurement reports, not timeless explanatory chapters.

## Calculate an end-to-end trace instead of adding labels

Use an illustrative local timeline measured in milliseconds:

| Milestone | Time |
| --- | ---: |
| Acoustic end of user speech | 1,000 |
| Final transcript available | 1,180 |
| Turn commitment | 1,500 |
| Retrieval started | 1,200 |
| Retrieval complete | 1,450 |
| Model request started | 1,510 |
| First token | 1,670 |
| First speakable clause | 1,880 |
| First audio ready | 2,030 |
| First client playback | 2,180 |

The user's turn gap is `2180 − 1000 = 1180 ms`. Endpoint/commit waiting is 500 ms. First token after request is 160 ms, but the first speakable clause takes 370 ms after the request. Synthesis adds 150 ms and delivery/playback adds another 150 ms.

Retrieval took 250 ms, but it completed before commitment, so adding 250 ms again to the post-commit sequence double-counts overlapping work. If retrieval instead completed at 1,800 ms and model context required it, it would lie on the critical path and delay request start. The dependency graph, not the stage names, determines which durations are additive.

## Compute percentiles and inspect the sample

Take successful turn gaps `[700, 950, 1300, 2400]`. The nearest-rank p50 uses rank `ceil(0.50 × 4) = 2`, yielding 950 ms. The p95 uses rank `ceil(0.95 × 4) = 4`, yielding 2,400 ms. An interpolation-based percentile can return another number. State the convention before comparison.

Four observations are too few to establish a stable production tail. Show the individual values and context. Larger samples also need representative workload: hundreds of identical short “yes” turns do not characterize a service performing slow bookings on mobile networks.

If a fifth turn timed out, the success-only report still uses four values, but the failure rate is 20%. Report both. A system that times out its slowest users can look faster on successful latency unless failures remain visible.

## Why stage percentiles cannot be added

Imagine two turns: turn A has model 900 ms and synthesis 100 ms; turn B has model 100 ms and synthesis 900 ms. Both have a 1,000 ms serial total. Adding a high model percentile of 900 and a high synthesis percentile of 900 invents 1,800 ms, which neither observed turn experienced.

Conversely, correlated slowness under shared overload can concentrate several slow stages in the same turn. Preserve per-turn linkage and compute end-to-end distributions from actual linked timelines. Stage percentiles remain useful for diagnosis, but they are not an algebraic substitute for the outcome distribution.

## Instrument spans with explicit ownership

Record a start and end in the same monotonic clock domain for each local span. Include trace/session/turn/response/operation IDs, status, and adapter configuration. Propagate IDs across requests and callbacks.

Across machines, a timeline requires a synchronization assumption with known uncertainty. If the client's clock is 120 ms ahead, an apparent server-to-client duration can be wrong by 120 ms. Local spans and round-trip measurements are useful even without precise one-way timing.

For actual audible start, determine what the client event measures. “Source scheduled” can precede hardware consumption; “first packet received” precedes decoding and buffering. Use loopback or documented device signals where necessary, and label the limit of the measurement.

## Budget latency against task quality

Assign an illustrative budget to endpointing, context work, generation, synthesis, and delivery based on the desired experience. Then compare observed distributions, not only averages. A budget is a design target, not evidence you meet it.

Shorten endpointing only while measuring premature cuts. Reduce prompt/context only while measuring task correctness. Change segmentation only while listening for prosody and mispronunciation. Use warm sessions only while accounting for idle resource cost and expiry behavior.

The smallest model is not necessarily cheapest per successful task if it needs more clarification turns or makes more tool mistakes. A voice-specific objective combines correctness, usable timing, and operational cost.

## Build actionable diagnostic views

For each slow turn, show the semantic timeline, queue duration, provider attempts, tool spans, and cancellation. Bucket by channel, region, task, language, and concurrency. An aggregate p95 rising only on phone calls points toward channel-specific investigation; one rising after context expansion points elsewhere.

Keep redacted exemplars of failures. A dashboard with a single latency number cannot explain whether waiting happened before endpoint, during a retry, or in client playback. Alert on user-impact signals and retain enough correlation to investigate without recording all content.

## Account for utilization and batching tradeoffs

In a simplified single-server queue, service capacity and arrival rate determine utilization `ρ = λ / μ`. As utilization approaches one, even small bursts can create long waits. Real multi-stage voice systems are more complicated, but the lesson holds: running every resource at its theoretical maximum leaves little room for timing variation.

Model batching can improve aggregate throughput while adding waiting for individual requests. A scheduler can collect work for efficient execution, but a voice turn cares about the oldest waiting request and first usable output. Measure aggregate tokens/audio per second and per-turn response timing together.

Separately inspect cancellation waste. A server can report high throughput by continuing to generate interrupted answers. Those tokens or samples are no longer useful to users, even if they increase a utilization graph. Report completed task output and cancelled work as separate categories.

### Worked interpretation

If doubling concurrency increases total generated audio by 40% but increases p95 turn gap from 900 ms to 2,300 ms and lowers task success, the service is not simply “40% better.” It has improved aggregate production while degrading conversational service. An admission limit, additional capacity, or a different scheduling policy may be more appropriate than maximizing throughput alone.

## Check your understanding

1. Why can endpoint-to-audio hide real delay?
2. Why is the sum of stage p95s misleading?
3. How can failed-turn omission distort a benchmark?

Continue with [evaluation](20-evaluation.md). [Lab 11](../labs/11-latency-and-evaluation.md).
