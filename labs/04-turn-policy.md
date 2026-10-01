# Lab 4. Compare silence endpoints and turn policies

**Read:** [chapters 7–8](../chapters/07-vad-and-audio-front-end.md). **Mode:** offline control simulation plus optional live speech. **Time:** 90 minutes.

## Build

1. Run `python3 examples/turn_runtime.py`. Read `EndpointPolicy` and distinguish it from a real VAD model.
2. Replay synthetic speech probabilities at a known frame cadence with 200, 500, and 900 ms silence limits.
3. Add a brief low-probability gap inside speech and a second speech onset before the endpoint timer expires.
4. For a live comparison, use “yes,” “I need a booking for… Saturday,” and “cancel—actually don't cancel.” Annotate actual conversational completion.
5. Compare the basic TEN, TEN VAD, and turn-detection event ownership using [the source walkthrough](../code-reading/turn-control.md).

## Deliver

Submit a table of decision times, premature endpoints, and delayed endpoints. Document threshold semantics and whether timestamps refer to samples or event receipt.

## Acceptance

- A short pause below the configured limit does not finish a turn.
- Renewed speech invalidates the pending silence endpoint.
- One committed turn causes at most one response.
- You can explain why a shorter threshold is faster and sometimes worse.

**Failure experiment:** let an old endpoint timer fire after renewed speech. Describe a turn-ID or state guard that prevents it.

**Transfer:** map speech presence, segment finalization, and turn commitment to distinct events.

[Next lab](05-interruption.md) · [All labs](README.md)
