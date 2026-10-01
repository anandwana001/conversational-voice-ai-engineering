# 5. Speech recognition: from waveform to evolving words

**Prerequisites:** chapters 2–4. **Goal:** understand alignment, interim hypotheses, finalization, and recognition errors.

<!-- chapter-navigation:start -->
**In this chapter**

- [What ASR must infer](#what-asr-must-infer)
- [Why recognition changes mid-sentence](#why-recognition-changes-mid-sentence)
- [Finalization and endpointing](#finalization-and-endpointing)
- [Accuracy needs task-specific measurement](#accuracy-needs-task-specific-measurement)
- [Silence, hallucination, and reconnects](#silence-hallucination-and-reconnects)
- [Source exercise](#source-exercise)
- [Work through acoustic features before discussing a model](#work-through-acoustic-features-before-discussing-a-model)
- [Alignment: why audio frames and text tokens do not match one-to-one](#alignment-why-audio-frames-and-text-tokens-do-not-match-one-to-one)
- [Forced alignment is a different task](#forced-alignment-is-a-different-task)
- [Design a streaming transcript store](#design-a-streaming-transcript-store)
- [Compute errors and interpret them](#compute-errors-and-interpret-them)
- [Diagnostic procedure](#diagnostic-procedure)
- [Compute a complete tiny CTC probability](#compute-a-complete-tiny-ctc-probability)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Work through acoustic features before discussing a model

Speech changes over time. A whole-recording Fourier transform reveals frequencies but obscures when they occurred. Short-time analysis instead takes overlapping windows, applies a window function, and computes spectra repeatedly. The result describes frequency content across time.

At 16 kHz, an illustrative 25 ms window contains 400 samples; a 10 ms hop advances by 160 samples. Adjacent windows overlap by 240 samples. The window is longer than the hop because neighboring spectral estimates share signal context. These are common teaching dimensions, not required settings for every recognizer.

Mel filter banks group spectral energy into bands on a perceptually motivated scale; logarithms compress dynamic range. A recognizer can learn from these features, from other frontend features, or from a learned waveform frontend. Do not infer a provider's exact preprocessing from the fact that its API accepts PCM.

Window size and model lookahead affect streaming delay. If a stage needs future context, it cannot genuinely emit a fully informed estimate before that context exists. Apparent immediate output may be a revisable hypothesis rather than a final result.

## Alignment: why audio frames and text tokens do not match one-to-one

One vowel can last many frames; a short consonant may occupy few. The spelling “book” has four letters but the word's acoustic duration changes with the speaker. Training cannot simply require each audio frame to equal one character without an alignment mechanism.

CTC handles this by defining paths over an alphabet plus a blank symbol. A path is collapsed by merging adjacent repeated labels, then removing blanks. The ordering matters. For example:

```text
path:     b b _ o o _ o k k
collapse: b   _ o   _ o k
remove _: b     o     o k   -> book
```

The blank between the two `o` regions makes them separate labels. A path `b o o k` collapses to `bok`, not `book`. This is why “remove all repeats” is not the right algorithm for repeated letters.

An executable collapse demonstration follows. It illustrates the decoding rule only, not an ASR model:

```python
def ctc_collapse(path, blank="_"):
    result = []
    previous = None
    for label in path:
        if label != previous and label != blank:
            result.append(label)
        previous = label
    return "".join(result)

print(ctc_collapse(["b", "b", "_", "o", "o", "_", "o", "k", "k"]))
print(ctc_collapse(["b", "o", "o", "k"]))
```

CTC assigns probability to text by summing probabilities of paths that collapse to that text. Enumerating all paths grows rapidly, so training uses dynamic programming rather than listing every alignment. Greedy frame-by-frame label selection is inexpensive but can differ from the most probable collapsed sequence.

A transducer adds a prediction component conditioned on emitted labels and a joint network combining acoustic and label information. An encoder-decoder recognizer generates text using encoded audio context. These alternatives differ in alignment, latency, and context use; no acronym alone establishes real-time performance.

## Forced alignment is a different task

Recognition estimates unknown text from audio. Forced alignment starts with audio and a supplied transcript and estimates where the transcript belongs on the timeline. Alignment can support highlighting and speaker attribution, but a plausible alignment does not independently prove the supplied transcript was correct.

If a receptionist heard “three” but the supplied transcript says “two,” alignment is not a substitute for recognition or human verification. Use the [torchaudio alignment tutorial](https://docs.pytorch.org/audio/main/tutorials/ctc_forced_alignment_api_tutorial.html) as a conceptual implementation reference; its package/version assumptions are separate from this course's standard-library setup.

## Design a streaming transcript store

A useful conceptual record includes `segment_id`, `revision`, `text`, `is_segment_final`, `media_start`, `media_end`, and language/provenance fields. The application retains finalized segments and one active hypothesis. Newer revisions replace older ones for the same segment.

If a final segment arrives twice, deduplicate it by identity. If a reconnect supplies a new segment ID for already replayed audio, identity alone may not suffice; use media offsets and the adapter's resume contract. Avoid text-only deduplication: two real consecutive “yes” answers can legitimately have identical text.

Commit a conversational turn through the turn policy, not by concatenating every final event and immediately executing tools. The user can add a correction after a recognized segment stabilizes.

## Compute errors and interpret them

Reference: “book repair for Saturday at three”. Hypothesis: “book a repair for Sunday at three”. Under a simple whitespace policy, there are six reference words, one insertion (`a`), and one substitution (`Saturday` → `Sunday`). WER is `2 / 6`, about 33.3%.

Now compare “book repair for Saturday at two”: only one of six words is wrong, but the time is wrong. A lower WER does not imply a useful booking. Report date/time entity accuracy, negation accuracy, and downstream task correctness separately.

Your normalization policy changes scores. Decide how to compare “3” and “three,” punctuation, contractions, and language-specific word boundaries before looking at results. Otherwise you can improve the reported metric without improving the recognizer.

## Diagnostic procedure

Inspect a saved synthetic clip with the declared audio contract. Establish that the waveform is intelligible before evaluating text. Then compare interim hypotheses, final segments, and committed turns. If audio is right but entities are wrong, investigate language settings and recognition. If final text is right but intent is wrong, inspect controller commitment and date resolution. If duplication appears only after reconnect, inspect replay offsets and segment identity.

## Compute a complete tiny CTC probability

Take three acoustic time steps and two labels, blank `_` and `a`:

| Step | Probability of blank | Probability of a |
| --- | ---: | ---: |
| 0 | 0.6 | 0.4 |
| 1 | 0.3 | 0.7 |
| 2 | 0.5 | 0.5 |

There are `2³ = 8` paths. A path probability is the product of its frame probabilities in this toy CTC formulation. Six paths collapse to the single label `a`. The all-blank path has probability `0.6 × 0.3 × 0.5 = 0.09`; the path `a _ a` collapses to `aa` and has probability `0.4 × 0.3 × 0.5 = 0.06`. Therefore the total probability of `a` is `1 − 0.09 − 0.06 = 0.85`.

Notice that no individual path needs probability 0.85. The text probability comes from the sum over eligible alignments. This is the mechanism hidden when someone says only “the model converts audio to words.”

You can enumerate the toy using [the executable mechanism examples](../examples/model_mechanisms.py). Enumeration is useful for understanding three frames; it is infeasible for a long utterance with a large vocabulary.

### Why dynamic programming is necessary

For a target label sequence, insert blanks between labels and at its ends to build alignment states. A forward calculation tracks probability mass reaching each state at each time. It can stay in a state, advance one state, and under the appropriate nonblank/nonrepeated-label condition skip a blank state. Each transition is weighted by the current frame's probability for the state's label.

Repeated target labels need the intervening blank; otherwise two occurrences collapse to one. The recurrence avoids enumerating exponentially many paths by reusing sums for shared prefixes. Real implementations often use log-space calculations for numerical stability.

This explanation does not make every recognizer a CTC recognizer. It gives you one concrete alignment mechanism, which you can then contrast with transducer or attention-based decoding. When reading a provider adapter, distinguish the interface's streaming events from the model architecture behind the service.

## Check your understanding

1. Why should interim snapshots replace rather than append?
2. How can stable STT text coexist with an unfinished user turn?
3. Why does WER alone fail to measure booking reliability?

Continue with [TTS](06-tts-internals.md). Primary reading: [CTC](https://www.cs.toronto.edu/~graves/icml_2006.pdf) and [Whisper research](https://arxiv.org/abs/2212.04356).
