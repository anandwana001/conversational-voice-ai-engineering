# 7. VAD, noise suppression, and echo cancellation

**Prerequisites:** chapters 2–3 and 5. **Goal:** detect speech presence without confusing it with turn completion or speaker identity.

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

## Check your understanding

1. Why can a speech detector interrupt on assistant echo?
2. What does prefix padding protect?
3. Why is microphone muting incompatible with natural full-duplex interruption?

Continue with [turn detection](08-endpointing-and-turn-detection.md). [Lab 4](../labs/04-turn-policy.md). Reference implementation: [TEN VAD](https://github.com/ten-framework/ten-vad).
