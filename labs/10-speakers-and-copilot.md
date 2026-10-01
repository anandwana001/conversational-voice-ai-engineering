# Lab 10. Preserve speaker attribution and time assistance

**Read:** [chapters 17–18](../chapters/17-diarization-and-conversation-understanding.md) and [both talk guides](../resources/README.md). **Mode:** synthetic script or consented recording. **Time:** 2–3 hours.

## Build

1. Create a two-speaker conversation with distinct preferences, short acknowledgements, one overlapping interval, and a correction.
2. Run a diarization pipeline or manually annotate a reference timeline. Keep speaker activity separate from transcription.
3. Align words or transcript segments with speaker intervals using media time. Mark ambiguous overlap instead of forcing one label.
4. Define five opportunities where a co-pilot could help and five moments where silence is preferable.
5. Implement a suggestion policy with freshness, cooldown, deduplication, and dismissal. A text-only simulation is valid for policy logic, but not for acoustic diarization validation.

## Deliver

Submit annotations, attributed preferences, intervention decisions, and an evaluation table. State which portions were manually annotated, simulated, or inferred by an actual model.

## Acceptance

- Preferences remain attached to the intended speaker.
- Acoustic labels are not treated as authenticated identities.
- Overlap and uncertain attribution remain visible.
- Correct but late or unwanted suggestions are counted as failures.

**Failure experiment:** summarize the whole transcript as if one user spoke. Identify the corrupted memory.

**Transfer:** propose the same intervention policy for a meeting sidebar rather than spoken output.

[Next lab](11-latency-and-evaluation.md) · [All labs](README.md)
