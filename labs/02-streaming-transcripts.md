# Lab 2. Model transcript revisions and commitment

**Read:** [chapters 3](../chapters/03-streaming-and-buffers.md) and [5](../chapters/05-stt-internals.md). **Mode:** offline first; optional live ASR. **Time:** 60–90 minutes.

## Build

Use this synthetic snapshot sequence for one segment:

```text
interim: book a flight to new
interim: book a flight to Newark
interim: book a flight to New York
final:   book a flight to New York tomorrow
```

1. Write a small accumulator keyed by segment ID. Replace interim snapshots rather than concatenating them.
2. Separate the displayed live hypothesis, finalized segment list, and committed user-turn list.
3. Add a second finalized segment, “Actually, make that next week,” before conversational commitment.
4. Send a duplicate finalized event. Ensure it does not create a duplicate committed turn.
5. If using live ASR, record the provider's snapshot/delta and finalization contract and adapt your accumulator explicitly.

## Deliver

Submit the event sequence, state after each event, and assertions for duplicates and revisions. Include a note explaining when the controller—not the ASR adapter—decides to trigger the LLM.

## Acceptance

- The UI hypothesis is current and has no repeated prefix.
- A segment-level final does not automatically execute a booking.
- Duplicates are correlated by segment/event identity.
- The eventual user intent includes the correction.

**Failure experiment:** concatenate every snapshot. Explain why the result fails even though the recognizer supplied reasonable updates.

**Transfer:** identify equivalent fields in another ASR API or propose a provider-neutral schema.

[Next lab](03-first-cascade.md) · [All labs](README.md)
