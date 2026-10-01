# 7. VAD, noise suppression, and echo cancellation

**Prerequisites:** chapters 2–3 and 5. **Goal:** detect speech presence without confusing it with turn completion or speaker identity.

<!-- chapter-navigation:start -->
**In this chapter**

- [What VAD decides](#what-vad-decides)
- [Thresholds and hysteresis](#thresholds-and-hysteresis)
- [Echo is a system feedback problem](#echo-is-a-system-feedback-problem)
- [Placement changes latency](#placement-changes-latency)
- [Source exercise](#source-exercise)
- [Implement speech-state logic before tuning a detector](#implement-speech-state-logic-before-tuning-a-detector)
- [Energy thresholds: why calibration matters](#energy-thresholds-why-calibration-matters)
- [Trace acoustic echo cancellation as a signal path](#trace-acoustic-echo-cancellation-as-a-signal-path)
- [A failure investigation](#a-failure-investigation)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## What VAD decides

Voice activity detection estimates whether an audio interval contains speech. It does not determine the words, whether the speaker is authorized, or whether a conversational turn has finished.

A basic detector compares frame energy against a threshold. A learned detector uses acoustic features and temporal context to distinguish speech from other sound. Music, breath, keyboard noise, laughter, far-field speech, and different languages can challenge both approaches.

The offline endpointing example uses synthetic probabilities. It teaches control logic; it is not a trained VAD and should not be benchmarked as one.

## Thresholds and hysteresis

A detector can oscillate near its threshold. Use a start threshold and a lower stop threshold, or require consecutive evidence before changing state. This is hysteresis. A hangover period keeps activity open for a short interval after low-confidence frames so brief consonant gaps do not split speech.

Prefix padding preserves audio immediately before detected onset. Without it, inference delay can cut the initial consonant. Maintain a bounded ring buffer and include its frames when speech begins. Do not accidentally replay prefix audio twice into a continuously fed recognizer.

An example policy might need three high-probability 20 ms frames to confirm onset and 15 low-probability frames to consider a pause. These numbers are illustrative, not recommended universal defaults. Tune them against intended microphones, languages, and conversational behavior.

## Echo is a system feedback problem

The speaker plays assistant speech; the microphone picks it up; VAD or STT interprets that audio as user speech. The agent can interrupt itself or respond to its own words.

Acoustic echo cancellation uses a playback reference and estimates the path from speaker to microphone to suppress correlated echo. It must handle delay, changing acoustics, and double-talk when the human speaks over output. Simply muting microphone input while the assistant talks prevents useful barge-in.

Headphones are a useful debugging baseline because they reduce acoustic feedback. They do not prove a speakerphone experience is correct. Test both, with echo cancellation enabled and disabled where your client permits it.

Noise suppression estimates unwanted background sound; automatic gain control adjusts levels; VAD detects speech presence. Each changes the signal seen by later stages. Excessive suppression can erase quiet speech, and aggressive gain can amplify noise. Inspect the combined front end rather than optimizing each component independently.

## Placement changes latency

Client VAD can reduce upload and provide early local interruption, but different clients may behave differently. Server VAD centralizes behavior but waits for transport. Provider VAD can coordinate with model state but may expose fewer controls. A hybrid design needs a policy for disagreement.

For immediate user experience, a client can clear local playback on strong speech onset while the server cancels generation. Record separate timestamps for local clear, server cancel, and last audible sample. Do not equate a fast server log with fast silence on the device.

## Source exercise

Compare TEN's basic assistant and `voice-assistant-with-ten-vad`. In the inspected controller, basic interruption can follow transcript evidence; the VAD variant handles `VadStartOfSentenceEvent`. This separates recognition delay from speech-onset detection. Check the graph and detector configuration to understand the actual timing.

## Implement speech-state logic before tuning a detector

A trained VAD might return a speech probability every 20 ms. That probability is an observation. The controller needs a temporal policy to turn observations into stable onset/offset events. Without it, a sequence such as `0.59, 0.61, 0.58, 0.62` can toggle repeatedly around a threshold of 0.60.

Consider this illustrative policy:

| Parameter | Example value | Purpose |
| --- | ---: | --- |
| Start threshold | 0.70 | Require stronger evidence to enter speech |
| Stop threshold | 0.40 | Do not leave speech on a small confidence decline |
| Start evidence | 3 frames | Suppress isolated transients |
| Stop evidence | 10 frames | Bridge brief low-confidence regions |
| Prefix buffer | 200 ms | Preserve sound before onset notification |

At 20 ms per frame, three consecutive start frames represent 60 ms of evidence. Ten stop frames represent 200 ms. This policy creates detection delay even before network and model costs. Treat these values as an experiment to reason about, not production defaults.

### Step through an onset

The detector first sees low probabilities. It retains the last ten frames in a ring buffer. Then it sees `0.75, 0.82, 0.79`. After the third frame it confirms onset, but the probable acoustic onset occurred earlier. The event should distinguish the estimated media onset from the time the decision was delivered.

If the recognizer was receiving all audio continuously, do not replay the ring buffer into that same stream; the buffer is already represented there. If recognition begins only after onset, prepend the buffered frames and maintain original media offsets. These two ingestion designs require different padding behavior.

### Step through an offset

During speech, probabilities briefly fall to `0.30, 0.35`, then return to `0.85`. The stop counter resets on renewed speech evidence. A longer low sequence produces a speech-offset event. The conversation controller can then start endpointing, which adds its own waiting interval.

Do not sum “VAD silence” and “endpoint silence” accidentally without understanding which time each uses. If the endpoint starts only after a 200 ms detector hangover and then waits another 500 ms, the total quiet interval can reach 700 ms. A detector event carrying original media offset may allow a different implementation.

## Energy thresholds: why calibration matters

For frame RMS `r`, an energy detector might declare speech when `r > threshold`. A quiet speaker near a low-gain microphone can fall below the threshold while a loud fan exceeds it. Adaptive noise estimates can help, but they can also drift if speech is included in the estimated noise baseline.

Separate acoustic evidence from product behavior. A coughing sound may correctly be detected as speech-like yet not warrant a new model answer. A learned VAD can be more discriminative than energy alone, but conversation policy still needs to decide what that sound means for the floor.

Measure detector performance with labeled frame activity, onset/offset timing, and the eventual conversational consequence. Counting only positive frames cannot tell you whether first consonants were lost or whether the assistant stopped on every keyboard click.

## Trace acoustic echo cancellation as a signal path

Let the microphone signal be `m[n] = u[n] + e[n] + noise[n]`, where `u[n]` is user speech and `e[n]` is assistant playback after traveling through the room. An echo canceller receives a playback reference and estimates the echo path. Conceptually it subtracts an estimated echo signal, leaving a residual closer to user speech.

The echo path includes delay and filtering from the speaker, room, and microphone. If the reference is misaligned or excludes part of the actual output, subtraction is poor. During double-talk, the canceller must avoid treating independent user speech as evidence that the echo path should adapt incorrectly.

You generally should not implement your own acoustic echo canceller in a beginner voice project. Understand the interface well enough to configure the client/media stack and debug it. Determine whether processing happens on capture, in the SDK, or on a server. Applying multiple incompatible gain/noise processors can degrade the signal.

## A failure investigation

The assistant stops after saying three words, even when the caller is silent. Inspect the microphone waveform while playback runs. Compare headphones and speakers. Check whether detected text resembles the assistant's own output. If so, investigate echo handling before changing the VAD threshold.

Raising the threshold may hide echo but also suppress quiet users. This is a tradeoff, not a repair of the underlying reference path. Record false stops and missed user onsets after every adjustment.

## Check your understanding

1. Why can a speech detector interrupt on assistant echo?
2. What does prefix padding protect?
3. Why is microphone muting incompatible with natural full-duplex interruption?

Continue with [turn detection](08-endpointing-and-turn-detection.md). [Lab 4](../labs/04-turn-policy.md). Reference implementation: [TEN VAD](https://github.com/ten-framework/ten-vad).
