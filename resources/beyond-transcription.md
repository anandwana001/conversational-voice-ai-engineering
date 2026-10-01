# Study guide: Beyond Transcription

**Resource:** [Beyond Transcription: Building Voice AI That Understands Conversations — Hervé Bredin, pyannoteAI](https://www.youtube.com/watch?v=mFLlVpnGpds), published on the AI Engineer channel.

Title/channel metadata was verified via YouTube oEmbed on 2026-10-01. The talk was not transcribed or viewed during authoring. The following is an original course study guide, not an account of what the speaker said.

## Prepare

Read [STT internals](../chapters/05-stt-internals.md) and [diarization](../chapters/17-diarization-and-conversation-understanding.md). Write your own definitions of transcription, diarization, overlap detection, speech separation, identification, and authentication.

## Questions to investigate while watching

1. What information about a conversation cannot be preserved by a single plain transcript?
2. Which speaker/timing signals are discussed, and how are they represented?
3. How are overlapping speech and short turns handled, if discussed?
4. What is available online with limited context versus retrospectively?
5. Which demonstrations establish capability, and which evaluation evidence is provided?

Record timestamps and paraphrase only what you actually observe. If a question is not addressed in the talk, mark it unanswered rather than guessing the speaker's position.

## Apply it

Create the two-speaker preference example from [lab 10](../labs/10-speakers-and-copilot.md). Compare a plain transcript summary with a speaker-attributed timeline. Explain how inaccurate attribution can corrupt memory even when recognized words are right.

## Notes template

For each observation record: timestamp, observed claim or demonstration, evidence, limitation, and generic engineering implication. Keep your own architectural conclusions labeled separately from the speaker's claims.

## Discussion

What additional permission or identity mechanism is needed before using a diarized utterance to perform an account action? Why should diarization confidence not substitute for authorization?

[Resource index](README.md) · [Chapter 17](../chapters/17-diarization-and-conversation-understanding.md)
