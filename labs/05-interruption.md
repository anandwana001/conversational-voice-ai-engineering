# Lab 5. Implement barge-in with stale-output rejection

**Read:** [chapters 9–10](../chapters/09-interruption-and-cancellation.md). **Mode:** offline, then live if available. **Time:** 90–120 minutes.

## Build

1. Run `python3 examples/turn_runtime.py` and inspect response generations.
2. Queue two chunks for an active response. Interrupt before playback finishes.
3. Deliver an intentionally late old-generation chunk after interruption.
4. Start a new response and deliver a valid chunk. Verify the new output is accepted.
5. In a live system, cancel generation, clear synthesis/transport/playback buffers, and trace acknowledgements. Use headphones first, then test a speakerphone route for echo-triggered interruption.

## Deliver

Submit a before/after queue trace and a cancellation diagram. For live testing, distinguish speech onset, detector notification, server cancellation, and last obsolete sound heard.

## Acceptance

- Old queued output is cleared.
- Late output from the old generation is rejected.
- New output remains valid after the interruption.
- Completed external tool effects are preserved independently of cancelled speech.

**Failure experiment:** remove generation validation while retaining queue clearing. Demonstrate how a late chunk reintroduces obsolete audio.

**Transfer:** explain why the same fencing pattern applies to search results, avatar motion, and UI suggestions.

[Next lab](06-realtime-comparison.md) · [All labs](README.md)
