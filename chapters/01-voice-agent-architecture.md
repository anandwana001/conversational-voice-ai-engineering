# 1. What a conversational voice agent is

**Prerequisites:** basic programming. **Goal:** distinguish a model, an agent controller, and a realtime communication system.

## The problem starts with time

A text chatbot receives a mostly complete message and returns text. A voice agent receives a changing stream while the user may pause, correct themselves, overlap another speaker, or interrupt output. The system must decide when to listen, when to act, what to say, and whether the user has actually heard it.

Consider: “Book a room for Friday—actually Saturday.” A correct transcript at the end is not enough. If the controller already booked Friday during an interim recognition result, the application failed despite accurate final recognition. Voice correctness includes timing and side effects.

## Separate the responsibilities

| Component | Responsibility | Does not automatically provide |
| --- | --- | --- |
| STT / ASR | Infer words from audio | User intent, safe execution, authoritative identity |
| LLM | Generate or interpret token sequences | Guaranteed truth or authorization |
| TTS | Turn text into playable speech | Confirmation that a listener heard it |
| Controller | Own turn state, history, actions, cancellation | A network or audio device |
| Transport | Move media and events between endpoints | Business workflow correctness |

An agent is a system in which model output can influence actions under application control. The controller decides which proposed actions are permitted and how their results become conversational context.

## Two major architectures

In a cascade, audio becomes text through STT, text and history go to an LLM, and response text goes to TTS. Each boundary is inspectable. You can separately change recognition and voice generation. But emotional tone, timing, laughter, and overlap can be lost when audio is reduced to plain text.

A speech-to-speech session consumes audio and emits audio through a model-oriented session interface. It may preserve cues a text cascade discards. Do not assume the underlying system is a single indivisible neural network: providers may combine models, encoders, decoders, and orchestration internally. The application still needs tool policy, playback control, tracing, and session lifecycle management.

Neither architecture guarantees better latency. Compare measured systems on the same microphone input, transport, turn policy, region, and workload. A fast model behind a long endpoint timeout still feels slow.

## Follow a request internally

1. The client captures samples and labels their format.
2. Transport delivers frames with timing information.
3. Recognition and turn policy collect evidence that the user has finished.
4. The controller commits the user turn and constructs model context.
5. A model emits text, audio, or a proposed tool call.
6. The controller validates actions; synthesis and playback deliver permitted output.
7. Playback progress and interruption events update conversation state.

These steps can overlap. STT may process frames while the user is still speaking. TTS can synthesize a finished clause while the LLM continues generating. The controller must correlate every result with its session and response generation.

## Data plane and control plane

The data plane carries audio, transcript updates, and generated content. The control plane carries start, cancel, clear-buffer, commit-turn, tool-result, and disconnect events. A cancellation control event must not wait behind several seconds of queued audio. Give urgent controls a path with bounded delay.

An audio chunk can be structurally valid and still be semantically invalid because it belongs to an interrupted response. Format validation and state validation are separate checks.

## Failure exercise

Draw a cascade for a receptionist. Mark where a wrong sample rate, late transcript revision, duplicate tool execution, and uncleared speaker buffer would occur. Then replace STT/LLM/TTS with a realtime session and identify which responsibilities remain.

## Check your understanding

1. Why can a final transcript be correct while a booking is wrong?
2. Which component should authorize a tool call?
3. Why does generated speech differ from heard speech?

Continue with [digital audio](02-digital-audio.md). Use [lab 1](../labs/01-audio-contracts.md) and the [TEN map](../code-reading/README.md). [Answer guide](../reference/answers.md).
