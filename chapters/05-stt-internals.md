# 5. Speech recognition: from waveform to evolving words

**Prerequisites:** chapters 2–4. **Goal:** understand alignment, interim hypotheses, finalization, and recognition errors.

## What ASR must infer

Automatic speech recognition, also called speech-to-text, estimates a word or token sequence from audio. It must cope with accent, noise, reverberation, speaking speed, disfluency, and multiple possible interpretations. There are no reliable spaces between spoken words in the waveform.

Many recognizers first transform short overlapping windows into frequency-domain features, such as log-mel spectrograms. A window trades time resolution against frequency resolution. An encoder maps acoustic features into learned representations. A decoder or alignment mechanism maps those representations to text.

Different architectures make different choices. CTC introduces a blank symbol and collapses repeated labels to marginalize over alignments. Transducers combine acoustic and label history while emitting aligned token steps. Encoder-decoder models attend to acoustic context while predicting text. A model designed for complete recordings is not automatically a low-latency streaming recognizer.

## Why recognition changes mid-sentence

The acoustic prefix “book a flight to…” permits many continuations. More audio changes the most likely hypothesis. A streaming recognizer can send:

```text
revision 1: book a flight to new
revision 2: book a flight to Newark
revision 3: book a flight to New York
final:      book a flight to New York tomorrow
```

Interim results are snapshots or deltas according to the provider contract. Appending every snapshot creates duplicated nonsense. Define segment IDs and replace the active hypothesis when the contract supplies snapshots. Do not assume `final` always means the entire user turn has ended: it may mean only that one recognized segment is stable.

The [transcript lab](../labs/02-streaming-transcripts.md) asks you to model revisions separately from committed user turns.

## Finalization and endpointing

A recognizer may finalize after silence, an explicit flush request, a segment limit, or a provider-specific endpoint event. A dialogue controller may still wait because the user has not finished their thought. STT segment stability and conversational completion are different states.

Streaming finalization can require buffered audio and a final server event. Closing the connection immediately on detected silence can discard the last syllable. During graceful shutdown, allow bounded finalization and mark any incomplete transcript instead of presenting it as complete.

## Accuracy needs task-specific measurement

Word error rate is `(substitutions + deletions + insertions) / reference_words`. It needs a normalization policy for punctuation, case, numbers, and contractions. It can exceed 100% with many insertions. Good average WER may still hide disastrous errors in names, account identifiers, negation, or appointment dates.

Track entity accuracy and task success alongside WER. “Do not cancel” becoming “cancel” is more consequential than a missing article. Recognition confidence, where available, is not a universally calibrated probability of semantic correctness.

For uncertain names or numbers, ask for repetition, spelling, or a keypad entry. Do not silently “correct” an account number using language-model plausibility. Domain vocabulary hints can help when supported, but benchmark them on held-out examples.

## Silence, hallucination, and reconnects

Noise or silence can produce plausible text in some recognizers. Detect speech presence, reject malformed segments, and investigate repeated outputs. VAD helps but cannot certify transcript truth.

On reconnect, decide whether buffered frames are replayed, discarded, or marked as a gap. Replaying can duplicate transcripts; discarding can lose a correction. Carry offsets and segment IDs across the boundary, and avoid processing replayed text as a new action.

## Source exercise

In TEN's pinned `deepgram_asr_python` adapter, inspect `_handle_asr_result`, `finalize`, and the reconnect manager. Identify where provider results become framework events. Then follow the controller to find where those events become a committed dialogue turn. See [the source map](../code-reading/README.md).

## Check your understanding

1. Why should interim snapshots replace rather than append?
2. How can stable STT text coexist with an unfinished user turn?
3. Why does WER alone fail to measure booking reliability?

Continue with [TTS](06-tts-internals.md). Primary reading: [CTC](https://www.cs.toronto.edu/~graves/icml_2006.pdf) and [Whisper research](https://arxiv.org/abs/2212.04356).
