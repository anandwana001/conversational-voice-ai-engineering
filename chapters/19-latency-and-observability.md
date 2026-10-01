# 19. Latency engineering and observability

**Prerequisites:** chapters 3 and 8–16. **Goal:** explain a slow conversation using measured stage boundaries.

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

## Check your understanding

1. Why can endpoint-to-audio hide real delay?
2. Why is the sum of stage p95s misleading?
3. How can failed-turn omission distort a benchmark?

Continue with [evaluation](20-evaluation.md). [Lab 11](../labs/11-latency-and-evaluation.md).
