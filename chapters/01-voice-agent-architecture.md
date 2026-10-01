# 1. What a conversational voice agent is

**Prerequisites:** basic programming. **Goal:** distinguish a model, an agent controller, and a realtime communication system.

<!-- chapter-navigation:start -->
**In this chapter**

- [The problem starts with time](#the-problem-starts-with-time)
- [Separate the responsibilities](#separate-the-responsibilities)
- [Two major architectures](#two-major-architectures)
- [Follow a request internally](#follow-a-request-internally)
- [Data plane and control plane](#data-plane-and-control-plane)
- [Failure exercise](#failure-exercise)
- [Worked design: a receptionist from input to verified outcome](#worked-design-a-receptionist-from-input-to-verified-outcome)
- [Implementation boundaries you should be able to draw](#implementation-boundaries-you-should-be-able-to-draw)
- [Debugging exercise with expected reasoning](#debugging-exercise-with-expected-reasoning)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Worked design: a receptionist from input to verified outcome

We will use one running application throughout the course: a receptionist for a fictional repair shop. The shop has a catalog, an appointment calendar, and customer records. The caller says, “Can you book a repair tomorrow at two?” The assistant must identify the service, interpret the date in the shop's timezone, find an available slot, confirm the proposed booking, execute it, and communicate the result.

Start by identifying what counts as success. A pleasant response is insufficient. Success means exactly one authorized booking with the intended service, date, and customer, plus a truthful confirmation. This definition tells us what state and evidence the architecture needs.

### Step 1: distinguish observations from decisions

An observation is something an adapter reports: an audio frame arrived, a transcript changed, a provider returned text, or a booking endpoint timed out. A decision changes application state: commit a turn, authorize a booking, accept output for playback, or close a session.

The same observation can lead to different decisions. A transcript update containing “two” may be displayed immediately, but the booking workflow waits for clarification about AM/PM. A tool timeout can lead to reconciliation rather than a second write. Keeping observations separate from decisions is what allows the application to recover without guessing.

### Step 2: define boundary records

Here is a **conceptual application schema**, not a TEN or provider API:

```json
{
  "session_id": "session-A",
  "user_turn_id": 7,
  "response_generation": 12,
  "event_id": "event-183",
  "type": "transcript_segment_final",
  "media_start_ms": 10200,
  "media_end_ms": 11900,
  "payload": {
    "segment_id": "segment-9",
    "text": "Can you book a repair tomorrow at two?"
  }
}
```

`session_id` chooses the conversation. `user_turn_id` correlates intent and workflow. `response_generation` determines whether generated content is still valid. `event_id` can deduplicate delivery. Media times place words in the signal. None of these fields proves identity; authenticated account scope must come from the trusted session context.

Do not require every event to have every field. Input audio may precede assignment to a user turn. The point is to define which identifiers are required for each event type, and who supplies them.

### Step 3: trace one turn, including a correction

| Event | Controller state | Permitted effect |
| --- | --- | --- |
| Speech begins | Listening → collecting input | Start/continue recognition; stop obsolete assistant output |
| Interim “tomorrow at…” | Collecting input | Update displayed hypothesis; optionally prefetch read-only context |
| Final segment “tomorrow at two” | Awaiting completion | Store stable text; do not yet assume the whole turn is complete |
| User adds “actually three” | Collecting input again | Cancel pending endpoint; revise intended time |
| Turn policy commits | Intent ready | Ask which repair service or resolve missing fields |
| Availability result | Proposal ready | Offer the specific slot, including timezone |
| User confirms | Authorized operation ready | Execute one keyed booking |
| Booking commits | Business state updated | Produce truthful confirmation |
| Caller interrupts confirmation | Business state stays booked | Clear obsolete speech; preserve the booking outcome |

This table reveals why one variable named `conversation_done` cannot represent the system. Input collection, workflow completion, response generation, and delivery have independent states.

### Step 4: choose the architecture deliberately

For this teaching application, a cascade makes boundary inspection easy: we can examine recognized text, the constructed LLM context, generated clauses, and synthesized frames. A realtime audio session may improve conversational cues or reduce some delays in a particular implementation, but it can expose different observability and cancellation semantics.

Compare architectures using the same success definition. Ask whether each can preserve the correction, produce one booking, and reconcile interrupted delivery. Only then compare turn gap and voice quality. This avoids choosing an architecture because one provider demo sounds impressive on a single uncomplicated utterance.

## Implementation boundaries you should be able to draw

Use a separate adapter for capture/transport, recognition, generation, synthesis, and tools. An adapter converts an external contract into your application contract. It should not quietly decide business policy. For example, the ASR adapter normalizes a provider finalization event; the session controller decides whether that is enough to commit a user turn.

The controller needs a dependency on an abstract booking interface, not the browser's audio implementation. The playback component needs response IDs and clear controls, not customer database access. This reduces the number of places where a provider change can alter business correctness.

Not every adapter needs its own process. In a small application they can be objects within one worker. Process boundaries are a deployment choice; responsibility boundaries should be understandable even inside a single process.

## Debugging exercise with expected reasoning

Suppose logs show a correct final transcript and the assistant says “Booked for three,” but the calendar contains two appointments, at two and three. Do not begin by improving TTS or asking the LLM to be more careful. Inspect when the two booking calls were authorized, their operation keys, and whether an interim interpretation triggered the first call.

Suppose instead there is one correct appointment, but the caller hears the old time after interrupting. Inspect output generation IDs and playback queues. The business workflow is correct while the delivery path is wrong. Architecture becomes useful when it helps distinguish these two failures with evidence.

## Check your understanding

1. Why can a final transcript be correct while a booking is wrong?
2. Which component should authorize a tool call?
3. Why does generated speech differ from heard speech?

Continue with [digital audio](02-digital-audio.md). Use [lab 1](../labs/01-audio-contracts.md) and the [TEN map](../code-reading/README.md). [Answer guide](../reference/answers.md).
