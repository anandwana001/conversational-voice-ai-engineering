# 11. Realtime speech-to-speech sessions

**Prerequisites:** chapters 4–10. **Goal:** understand session-level audio models without giving away application ownership.

<!-- chapter-navigation:start -->
**In this chapter**

- [What changes at the model boundary](#what-changes-at-the-model-boundary)
- [Session ownership](#session-ownership)
- [Transcript events have limits](#transcript-events-have-limits)
- [Tools still belong to the application](#tools-still-belong-to-the-application)
- [Cascaded versus realtime comparison](#cascaded-versus-realtime-comparison)
- [Source exercise](#source-exercise)
- [Understand the audio representation boundary](#understand-the-audio-representation-boundary)
- [Specify an adapter contract instead of copying event names](#specify-an-adapter-contract-instead-of-copying-event-names)
- [Trace startup and response creation](#trace-startup-and-response-creation)
- [Tool continuation is its own subprotocol](#tool-continuation-is-its-own-subprotocol)
- [Playback reconciliation worked example](#playback-reconciliation-worked-example)
- [Compare observability fairly](#compare-observability-fairly)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Understand the audio representation boundary

A text cascade makes recognized words an explicit intermediate product. A realtime audio model can instead receive an encoded representation of sound containing timing and nonverbal information. An audio encoder might operate on spectral features; a learned audio codec can encode short waveform regions into discrete codes. Those are architectural possibilities, not a claim about a particular proprietary provider.

If a representation emits one code group every 20 ms, one second corresponds to 50 time steps. Some codecs use several codebooks per step, so “50 steps” does not necessarily mean 50 billed model tokens. Providers can define billing and tokenization differently. Do not convert audio duration into cost using an assumed codec-token rate.

An output decoder reconstructs waveform samples from generated representations. There can be lookahead and buffered context at encoding, generation, and decoding. A speech-to-speech interface does not abolish buffering; it changes where buffering is controlled and observed.

## Specify an adapter contract instead of copying event names

Normalize your chosen provider to conceptual events:

| Event | Controller meaning |
| --- | --- |
| `session_ready` | Negotiated session configuration is active |
| `input_speech_started` | Provider detected onset under its policy |
| `input_turn_committed` | Provider/app accepted a completed input item |
| `response_started` | Bind provider response ID to application generation |
| `response_audio_delta` | Audio for a particular response/segment |
| `response_tool_call_complete` | Fully assembled proposed tool call |
| `response_finished` | Provider generation ended; playback may still continue |
| `response_cancelled` | Provider cancellation state under its contract |

These are course-defined categories, not API names. An actual provider can split or combine them. The adapter should preserve distinctions needed for state ownership rather than flatten everything into `text` and `done`.

Record the negotiated input/output formats. Read the session configuration result, not just the request you sent: a server may reject, default, or constrain settings. Do not publish a model-specific claim until it is verified against that provider version.

## Trace startup and response creation

First establish the network connection, then initialize/update the model session, wait for readiness, attach tools/context, and begin input under the session's contract. A greeting should not run twice because both “connected” and “ready” handlers initiate it.

For automatic turn responses, the provider may create a response after its own completion decision. For manual responses, the application commits input and requests generation. Decide which route owns each turn, and guard duplicate create requests with a logical turn identifier.

If the user continues speaking after a tentative provider endpoint, determine whether the provider cancels or the application must react. This is not captured by a generic statement that “the realtime model handles turns.” The exact ownership determines corrections and interruption behavior.

## Tool continuation is its own subprotocol

During a response, a function call may arrive as argument deltas. Assemble them for the specific call ID, wait for the complete signal, validate, and execute. Return the result associated with that call. Some interfaces automatically continue after the result; others require an explicit next-response request.

An adapter that unconditionally requests continuation can duplicate output in an automatic interface. An adapter that never requests it can leave a manual interface silent after a successful tool. Document the specific continuation contract in the live lab.

When a delayed tool result completes after interruption, retain business state and send any required provider result according to the session contract, but do not automatically authorize obsolete speech. You may need to update context for the next current response without resurrecting the old response.

## Playback reconciliation worked example

Assume the provider emitted one second of audio and the client played 350 ms before the caller interrupted. Bytes received correspond to one second; actual delivery corresponds to 350 ms. Truncating history at one second preserves 650 ms of unheard content. Truncating at zero removes the part already heard.

A supported reconciliation API may accept a response item and audio offset. Use the offset domain it requires and account for decoding/sample-rate differences. If exact reconciliation is unsupported or not instrumented, retain an interrupted-delivery marker and describe the uncertainty.

## Compare observability fairly

In a cascade you can log STT segment timing and TTS segment requests. In a realtime session you may only observe input commitment, audio deltas, and transcripts. Missing internal stage events are an observability limitation, not proof the stage took zero time.

Compare the user's end-to-end turn gap, actual tool outcome, interruption behavior, and audible quality. Use stage metrics only where both systems expose comparable definitions. The cascade's first token and the realtime session's first audio delta are different milestones.

## Check your understanding

1. How can two endpoint owners create duplicate output?
2. Why is a side-channel transcript not a complete record of audible delivery?
3. What stays in the application when STT/LLM/TTS are replaced?

Continue with [tools](12-tool-calling-and-workflows.md). [Lab 6](../labs/06-realtime-comparison.md) and [realtime source walkthrough](../code-reading/realtime.md).
