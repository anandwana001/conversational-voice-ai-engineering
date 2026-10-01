# Lab 6. Compare cascade and realtime audio sessions

**Read:** [chapter 11](../chapters/11-realtime-speech-to-speech.md) and [the realtime walkthrough](../code-reading/realtime.md). **Mode:** live. **Time:** 2–3 hours.

## Build

1. Start the pinned TEN realtime example or another documented audio-session runtime. Confirm format, readiness, and endpoint ownership.
2. Repeat the same five utterances used in lab 3, with equivalent microphone, output device, transport, and region where possible.
3. Interrupt a long response and trace provider cancellation, local playback clear, and history reconciliation.
4. Identify the events for input transcript, output transcript, audio, tool call, session readiness, and interruption.
5. Document policies that cannot be made equivalent between the architectures.

## Deliver

Submit a comparison of task success, perceived quality, turn gap, interruption behavior, and event visibility. Distinguish audio models from provider session APIs.

## Acceptance

- There is one response owner per committed turn.
- The controller still validates tools and owns business state.
- Transcript timing is not misreported as word-aligned playback.
- Every latency claim states its measurement boundary and sample count.

**Failure experiment:** enable both automatic and manual response creation in a controlled test, if supported. Detect duplicated responses; restore single ownership.

**Transfer:** list the application responsibilities that survive a model architecture change.

[Next lab](07-tools-and-mcp.md) · [All labs](README.md)
