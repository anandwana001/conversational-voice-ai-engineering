# Understanding-check answer guide

These concise answers describe the reasoning expected after each chapter. Explain them in your own words and apply them to a new failure case.

## 1. Architecture

1. An interim interpretation can trigger a side effect before a later correction appears.
2. The application/controller enforces authorization and workflow policy.
3. Generated output may be buffered, delayed, interrupted, or never played.

## 2. Audio

1. `24,000 × 0.1 × 1 × 2 = 4,800` payload bytes.
2. Frequencies above the new band limit can alias unless filtered before downsampling.
3. A container header describes bytes; it does not decode or transform their signal encoding.

## 3. Streaming

1. Seventy-five 20 ms frames contain 1,500 ms of audio.
2. Cancellation can race with already scheduled/in-flight callbacks.
3. Report discontinuity and explicitly reset or reconcile affected processing; do not silently merge gaps.

## 4. LLMs

1. Prefill processes existing context; decode creates new tokens incrementally.
2. Syntax validity does not establish intended date, availability, access, or confirmation.
3. External evidence cannot become authority to change application policy.

## 5. Recognition

1. Snapshot hypotheses repeat the current prefix; concatenation duplicates it.
2. Stable recognized segments can precede a pause, continuation, or correction.
3. Critical entity/negation errors and timing can dominate task success despite low average WER.

## 6. Synthesis

1. Prosody needs linguistic context and future structure, not just the current token.
2. Concurrent requests can return out of order; sequence IDs or serialization preserve playback order.
3. Store an interrupted marker and conservative delivery state rather than inventing exact heard words.

## 7. VAD

1. Playback leakage is speech-like microphone input unless the echo path is controlled.
2. Prefix padding retains onset audio that precedes the detector's decision.
3. Muting prevents simultaneous user input, so real barge-in cannot be observed.

## 8. Turn detection

1. Recognition stability and conversational floor transfer answer different questions.
2. An old timer can commit after speech resumes unless state/turn guards reject it.
3. Speculative reads can be invalidated; consequential writes should wait for committed, authorized intent.

## 9. Interruption

1. Clearing removes present output; fencing rejects later obsolete output.
2. A committed external action survives local cancellation and may require reconciliation/compensation.
3. Provider context may retain generated content the user never heard.

## 10. Runtime

1. Controller code and imported helpers issue events/commands beyond static graph connections.
2. Serialize state changes while running I/O tasks concurrently with IDs and guarded result application.
3. Durable operation outcomes and business state must survive; ephemeral audio may not.

## 11. Realtime

1. Automatic and manual response creation can both react to the same turn.
2. Transcript events need not align exactly with emitted or played audio.
3. Tools, authorization, transport, playback, lifecycle, tracing, and durable state remain application work.

## 12. Tools

1. A stable key identifies one logical operation; a fresh key makes each retry a potential new write.
2. The model's arguments do not prove the caller's identity or account access.
3. A timeout proves no timely reply; the server may already have committed.

## 13. MCP

1. A runtime client translates protocol capabilities into the model's tool interface.
2. Request IDs correlate protocol exchanges; operation keys deduplicate business effects.
3. Discovery describes capabilities, while authorization is separately enforced.

## 14. Retrieval and memory

1. Organizational evidence and personal information have different provenance, scope, and retention needs.
2. Filter before model context, and enforce scope in indexes, caches, memory, and tools.
3. Summaries can lose negation, uncertainty, speaker identity, and interrupted delivery.

## 15. Transport

1. Ordered TCP delivery can hold later data while earlier lost bytes are retransmitted.
2. The application must exchange connection/session information through a signaling mechanism.
3. A reopened connection does not recreate model state, operation ownership, or playback progress.

## 16. Telephony

1. Session signaling and media delivery use separate paths and can fail independently.
2. Decode companding, resample statefully, assemble PCM frames, and declare the true format.
3. Caller number metadata can be insufficient or spoofed; use explicit account authorization.

## 17. Diarization

1. Speaker clusters are acoustic labels, not authenticated account credentials.
2. Multiple speakers can be active in one interval; one exclusive label loses information.
3. Collars, overlap handling, and reference rules change the error calculation.

## 18. Co-pilots

1. Help must arrive at an appropriate time and through an acceptable channel.
2. Use evidence captured near the utterance and track freshness, not merely the latest inference-time frame.
3. Stop obsolete audio, motion, and any associated queued output.

## 19. Latency

1. The endpoint can already include a long silence wait before the reported interval begins.
2. Percentiles are not additive and spans may overlap or peak on different turns.
3. Removing failures selects an artificially favorable subset of sessions.

## 20. Evaluation

1. Echo, clipped audio, prosody, audible delay, and hidden tool effects can be absent from transcripts.
2. Synthetic speech/behavior differs from actual users and can share model blind spots.
3. The authoritative operation/result and intended workflow state confirm the task.

## 21. Security

1. Model arguments are proposals derived from untrusted content, not proof of permission.
2. Shared caches, tools, logs, memory, storage, and derived summaries can also leak scope.
3. Include summaries, embeddings, caches, and exports under the explicit deletion policy.

## 22. Operations

1. Capacity or dependency limits can prevent safely admitting new sessions despite a live process.
2. Reconcile durable external actions and their operation keys before retrying.
3. Returning to earlier code does not reverse already committed external side effects.

[Chapters](../chapters/README.md) · [Labs](../labs/README.md)
