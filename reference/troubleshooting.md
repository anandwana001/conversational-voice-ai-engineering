# Troubleshooting by boundary

Find the earliest incorrect boundary in the trace. Changing a prompt will not repair corrupted audio or duplicated controller transitions.

| Symptom | Inspect first | Useful experiment |
| --- | --- | --- |
| Audio pitch/speed is wrong | Capture/output rate versus declared rate | Count samples and play a known tone |
| Clicks at frame boundaries | Resampler/decoder state and byte alignment | Compare continuous processing with per-frame resets |
| First syllable is missing | VAD prefix buffer and onset delay | Record onset with and without prefix padding |
| Agent responds to itself | Echo path, playback reference, microphone settings | Compare headphones and speakerphone |
| Repeated transcript prefixes | Snapshot versus delta contract | Replay synthetic revisions from lab 2 |
| User gets cut off during pauses | Endpoint ownership and threshold | Replay hesitation utterances with annotations |
| Long delay before answer | Endpoint, retrieval, segmentation, synthesis, queues | Trace end-of-speech through device playback |
| Two answers to one utterance | Duplicate turn commitment or response ownership | Correlate ASR final, endpoint, and provider auto-response |
| Audio continues after cancel | Downstream/device buffers and late callbacks | Clear queue then inject an obsolete-generation chunk |
| Wrong speech order | Concurrent TTS completion order | Tag and reorder segments by generation/sequence |
| Booking duplicated | Retry operation key and durable atomicity | Lose the reply after a successful commit |
| Tool says timeout but action happened | Unknown outcome reconciliation | Query the authoritative operation ledger |
| Reconnect repeats old speech | Replay policy and event IDs | Interrupt transport and inspect resumed input |
| Phone call connects silently | RTP/media routing, negotiated codec, bridge | Inspect signal and media paths independently |
| Preferences attach to wrong person | Speaker alignment, overlap, summary provenance | Compare an attributed timeline with one-user summary |
| Retrieval leaks another tenant | Filters, cache keys, memory/tool scope | Test two synthetic tenants with identical queries |
| Good transcript score, bad UX | Playback, prosody, timing, tool ledger | Listen and compare actual actions |
| Memory grows under load | Unbounded buffers/tasks and session cleanup | Track queue duration and per-session allocations |
| Negative network duration | Mixed clocks or wall-clock changes | Use local monotonic spans and explicit clock assumptions |

## A useful bug report

Include the environment, source/configuration versions, channel, synthetic reproduction steps, expected/actual behavior, named timing boundaries, redacted event IDs, and the earliest broken contract. Avoid raw caller data and credentials.

Mark simulations and inferred behavior explicitly. If actual playback is not instrumented, report provider audio readiness and state that audible timing remains unverified.

[Contribution guide](../CONTRIBUTING.md) · [Labs](../labs/README.md)
