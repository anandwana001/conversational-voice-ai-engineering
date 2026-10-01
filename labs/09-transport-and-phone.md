# Lab 9. Trace browser and telephone media

**Read:** [chapters 15–16](../chapters/15-webrtc-and-websocket.md). **Mode:** browser live; optional paid phone route. **Time:** 2–4 hours.

## Build

1. Inspect a browser connection. Identify signaling, media, negotiated codec, decoded agent format, authentication, and local playback.
2. Test reconnect after a brief disconnect. Document whether the model session resumes or is recreated.
3. For a phone route, use a supported test number or SIP endpoint under your control. Identify signaling and media separately.
4. Record the negotiated codec and rate. Trace decoding, resampling, frame assembly, output encoding, and pacing.
5. Test keypad input, remote hangup, and transfer failure if supported. Avoid using real customer data.

## Deliver

Submit a call/media sequence diagram, format table, and failure trace. If no phone account is available, complete a written packet/codec walkthrough and mark the live phone requirement unverified; this is a partial channel lab, not a successful deployed phone test.

## Acceptance

- You can locate the first silent boundary when signaling succeeds but media fails.
- Audio conversion is real, not a metadata relabel.
- Hangup closes resources and reconciles pending operations.
- Caller ID is not used as sole authorization for account changes.

**Failure experiment:** introduce a network or format failure in a controlled environment and observe the difference between call state and audio state.

**Transfer:** explain how a provider WebSocket media bridge replaces raw RTP without changing business logic.

[Next lab](10-speakers-and-copilot.md) · [All labs](README.md)
