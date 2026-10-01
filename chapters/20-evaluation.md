# 20. Evaluating voice quality, behavior, and task success

**Prerequisites:** chapters 5–19. **Goal:** build an evaluation suite that can detect failures a transcript-only judge misses.

## Evaluate the system at several layers

Audio tests cover capture format, clipping, loss, resampling, and intelligibility. Recognition tests cover WER, entities, language variation, and revisions. Conversation tests cover premature endpoints, false interruptions, response gaps, and recovery. Agent tests cover tools, permissions, grounded answers, and completed tasks.

A transcript judge cannot hear delayed playback, echo, clipped syllables, or awkward prosody. An audio-quality score cannot verify that a booking used the right account. Combine signals instead of claiming one overall score establishes reliability.

## Deterministic checks first

Assert what the application can know: tool name, validated arguments, operation count, account scope, result status, stale-audio drops, cancellation propagation, and final workflow state.

For “book Saturday at two,” the pass condition is not merely that the assistant said “booked.” Check the authoritative record and confirmation workflow. Add a retry with a lost response and verify exactly one business mutation.

## Scenario design

Build a matrix across task, language, speaker style, environment, channel, and failure mode. Include silence, noise, self-correction, overlapping speech, delayed tools, duplicate events, disconnects, and unauthorized requests.

Keep a small fast regression set and a broader scheduled suite. Hold out examples for meaningful evaluation rather than tuning prompts against every known test. Record prompt, adapter, model configuration, dataset version, and source commit for reproducibility.

Synthetic callers can exercise flows at scale, but their speech and behavior may be easier for the system than real users. Include consented human evaluation or carefully designed recordings. An agent that succeeds with another model as caller has not automatically proven human usability.

## Model-as-judge

A judge can score tone, helpfulness, groundedness, or policy adherence using a specific rubric and evidence. Supply tool traces and allowed evidence when the criterion requires them. Keep judge reasoning separate from executable policy.

Validate a subset with human reviewers. Judges can prefer verbosity, share a model's blind spots, or score unsupported confident claims favorably. Report agreement and disagreements instead of treating a judge score as ground truth.

Avoid letting the evaluated transcript inject judge instructions. Put transcript content in a clearly bounded evidence field, restrict judge capabilities, and compare deterministic outcomes independently.

## Listening evaluation

Ask listeners to rate intelligibility, naturalness, turn timing, interruption responsiveness, and fatigue. Use randomized order where feasible, comparable loudness, and consistent devices. Disclose population and sample count.

For co-pilots, score whether intervention was wanted and timely. Include episodes where the correct output is silence. More spoken assistance is not necessarily better performance.

## Release gates

Choose explicit gates for your task: no cross-tenant access in the tested cases, no duplicate writes under retry, bounded stale output after cancellation, acceptable task success, and latency within stated workload targets. Do not invent universal thresholds for every application.

Regressions should link to traces and reproducible inputs. Track trend and uncertainty; one noisy measurement should trigger investigation rather than automatic claims of improvement or failure.

## Worked counterexample

The assistant correctly says “I cannot cancel without confirmation,” but has already called the cancellation tool. A transcript judge may approve the response. The tool ledger fails the test. Evaluate both words and actions.

## Check your understanding

1. Which failures are invisible to a transcript-only judge?
2. Why are simulated callers insufficient by themselves?
3. What evidence confirms a completed business task?

Continue with [security](21-security-and-privacy.md). [Lab 11](../labs/11-latency-and-evaluation.md) and [capstone rubric](../capstone/README.md).
