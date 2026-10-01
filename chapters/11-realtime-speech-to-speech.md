# 11. Realtime speech-to-speech sessions

**Prerequisites:** chapters 4–10. **Goal:** understand session-level audio models without giving away application ownership.

## What changes at the model boundary

In a speech-to-speech interface, audio is part of model input and output. A typical system encodes incoming sound into learned representations and generates representations that a decoder converts to sound. It may use discrete audio tokens, continuous features, text supervision, or multiple cooperating models. The API alone cannot reveal a proprietary model's exact internals.

The application sees a session protocol: configure behavior, append input, commit or detect turns, request responses, receive audio/text events, run tools, and cancel or reconcile output. The names and ordering constraints vary by provider.

Avoid describing speech-to-speech as “no STT or TTS exists internally.” The meaningful contrast is the application contract and what information crosses it.

## Session ownership

Decide who detects completion. If the provider automatically creates a response on a detected turn, your controller should not also request a response for the same turn. Double ownership produces duplicate answers.

Likewise, determine whether provider interruption stops generation, truncates context, clears only a provider buffer, or also clears client playback. A server interrupt event is not proof that a device stopped playing.

Session setup should specify accepted audio format, output format, voice behavior, tool definitions, and lifecycle limits. Validate readiness before sending a greeting or microphone audio. A transport connection being open is not always the same as the model session being ready.

## Transcript events have limits

Realtime transcripts may be side-channel interpretations rather than the exact intermediate representation used to generate speech. They can arrive after audio, differ from what a listener heard, or omit prosodic information.

Do not assume every spoken word has an aligned text timestamp. For evaluation, distinguish generated transcript, recognized output audio, and human annotation. For history, reconcile interruption using supported session mechanisms and document remaining uncertainty.

## Tools still belong to the application

The model can propose a function name and arguments. Your server validates schemas, identity, permissions, deadlines, and idempotency. It sends a correlated result and coordinates whether another response should be requested.

A tool result arriving after an interrupted response may still need to update business state without triggering speech for the obsolete turn. Keep operation completion separate from permission to speak.

## Cascaded versus realtime comparison

| Dimension | Cascaded interface | Realtime audio interface |
| --- | --- | --- |
| Inspection | Explicit recognition and synthesis boundaries | Depends on exposed session events |
| Provider swapping | Stage adapters can be replaced separately | Session semantics can be tightly coupled |
| Nonverbal cues | Must be preserved deliberately alongside text | May be available to the model, depending on design |
| Output control | Application segments and synthesizes text | Application coordinates provider output and playback |
| Safety | Controller validates actions | Controller validates actions |

Compare actual systems rather than assuming a universal performance ranking. Use identical utterances, endpoint policies where possible, regions, and success criteria. State where the policies cannot be made equivalent.

## Source exercise

TEN's inspected realtime graph replaces separate STT, LLM, and TTS nodes with a `v2v` node backed by `openai_mllm_python`. The controller consumes session and model events while transport still handles audio. This is a concrete example of different model ownership with retained application responsibilities; it is not a recommendation for a particular current model.

## Check your understanding

1. How can two endpoint owners create duplicate output?
2. Why is a side-channel transcript not a complete record of audible delivery?
3. What stays in the application when STT/LLM/TTS are replaced?

Continue with [tools](12-tool-calling-and-workflows.md). [Lab 6](../labs/06-realtime-comparison.md) and [realtime source walkthrough](../code-reading/realtime.md).
