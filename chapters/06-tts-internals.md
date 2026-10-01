# 6. Speech synthesis, text segmentation, and playback

**Prerequisites:** chapters 2–5. **Goal:** trace text to sound and distinguish synthesis progress from audible progress.

<!-- chapter-navigation:start -->
**In this chapter**

- [Turning a sentence into a waveform](#turning-a-sentence-into-a-waveform)
- [Prosody requires context](#prosody-requires-context)
- [Three distinct clocks](#three-distinct-clocks)
- [Streaming synthesis internally](#streaming-synthesis-internally)
- [Interruption and conversational history](#interruption-and-conversational-history)
- [Failure exercise](#failure-exercise)
- [Follow one sentence through synthesis internals](#follow-one-sentence-through-synthesis-internals)
- [Design a text-to-audio stream explicitly](#design-a-text-to-audio-stream-explicitly)
- [Ordering, underflow, and timing](#ordering-underflow-and-timing)
- [Derive playback position from samples](#derive-playback-position-from-samples)
- [Debugging exercise](#debugging-exercise)
- [Measure synthesis throughput without hiding startup delay](#measure-synthesis-throughput-without-hiding-startup-delay)
- [Compare autoregressive and duration-oriented generation](#compare-autoregressive-and-duration-oriented-generation)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## Turning a sentence into a waveform

Speech synthesis must decide how text is pronounced, how long sounds last, where emphasis belongs, and what waveform represents those sounds. A conventional neural TTS path includes text normalization, pronunciation or token encoding, acoustic generation, and waveform generation through a vocoder. Newer systems may generate codec tokens or use integrated generative architectures. Do not assume all providers expose these stages.

Normalization matters. “₹1,250”, “01/02”, and “Dr.” need language and context. An ambiguous date should be resolved in the application before synthesis. Pronunciation dictionaries can help with names when supported. Voice style and speech rate influence intelligibility and duration, not just personality.

## Prosody requires context

Prosody includes stress, pitch, timing, and rhythm. Reading “You booked Saturday?” differs from “You booked Saturday.” Synthesizing one token at a time may reduce waiting but remove context needed for natural intonation.

A text segmenter collects enough generated text to form a speakable unit. Common policies use punctuation, clause boundaries, minimum length, and maximum waiting time. Punctuation alone is insufficient: periods occur in abbreviations and decimals, and some languages use different conventions.

For example, splitting “Your total is 12.50 euros” at the decimal changes meaning. A useful segmenter retains partial numbers and known abbreviations, and has tests using the actual languages served.

## Three distinct clocks

1. **Text available:** the controller has a valid speakable segment.
2. **Audio generated:** synthesis returned bytes in the declared format.
3. **Audio played:** the receiving device consumed those samples.

First audio returned from a provider is not necessarily first audio heard by the user. Encoding, transport, browser scheduling, and playback buffering intervene. This distinction becomes critical when a user interrupts midway through a confirmation.

## Streaming synthesis internally

Some interfaces accept a complete segment and stream its audio. Others accept incremental text within a synthesis session. These have different flushing and context rules. A final text marker may be needed to make the provider generate buffered content.

Preserve response and segment IDs. If synthesis calls run concurrently, later segments may complete before earlier segments. Reorder by segment sequence before playback or intentionally serialize. Never play according to callback arrival order unless the provider guarantees it matches speech order.

Validate audio format at the adapter boundary. A TTS returning 24 kHz PCM cannot be fed into a 16 kHz playback graph by changing only a metadata field. Use a stateful converter as explained in chapter 2.

## Interruption and conversational history

Imagine the model writes: “Your appointment is booked for Saturday. The confirmation code is 9132.” The user interrupts after “Your appointment…”. The tool may have succeeded, but the caller did not hear the result. The next response should distinguish action state from communication state.

Keep generated text, queued audio, played audio, and interrupted status separately. Exact word-level heard history may require aligned timestamps that your provider does not supply. If you cannot map samples precisely to words, use a conservative interrupted marker rather than inventing a fully heard transcript.

Clearing synthesis buffers alone leaves queued transport and device audio. A complete interruption strategy cancels producers, clears downstream queues, rejects late output, and reconciles history. See [chapter 9](09-interruption-and-cancellation.md).

## Failure exercise

Run the same response with short-clause and full-sentence segmentation. Measure time to first audio, naturalness, pronunciation errors, and interruption response. Include decimals, a name, and a long URL. Avoid concluding that fastest always means best.

## Follow one sentence through synthesis internals

Use “Dr. Rao, your repair costs ₹1,250.50” as a running example. Before waveform generation, the system must resolve an abbreviation, a name, currency, and a decimal. An English-oriented expansion might render the amount as “one thousand two hundred fifty rupees and fifty paise,” but language, locale, and desired speaking style determine the exact wording.

Normalization should preserve meaning. In a business application, construct an unambiguous speakable amount from validated structured data rather than hoping a model or voice provider interprets a raw number correctly. Keep the canonical numeric amount separately so spoken wording cannot become the source of financial truth.

### Text and pronunciation representation

A frontend can map normalized text to characters, phonemes, subword tokens, or another representation. Phonemes represent speech sounds and can help pronunciation, but choosing them requires language and pronunciation context. A name can have several valid pronunciations. Ask users or use an approved pronunciation dictionary rather than treating one guessed pronunciation as authoritative.

Punctuation, word boundaries, and style controls influence prosody. Some systems infer prosody from text; others accept reference audio or explicit controls. An API offering a voice identifier does not reveal how speaker identity and prosody are represented internally.

### Duration and acoustic generation

An acoustic model must map a short text sequence to a much longer time sequence. In one family, durations estimate how many acoustic frames belong to each input unit. A duration expansion makes a time-aligned representation, from which pitch, energy, and spectral features can be produced. Other architectures learn alignment through attention or generate audio representations autoregressively.

Suppose the output acoustic hop is 10 ms. A one-second phrase needs about 100 frames. If a syllable occupies eight frames, it lasts about 80 ms. Duration mistakes can sound rushed or unnaturally stretched even when the words are correct.

### Waveform generation

A vocoder maps acoustic representations into waveform samples. If it generates at 24 kHz and the acoustic hop is 10 ms, each hop corresponds to about 240 waveform samples. The vocoder must produce locally coherent waveform structure, not repeat a fixed waveform block for each feature vector.

Codec-token systems instead represent audio using a learned codec and generate token sequences that a decoder reconstructs. Their buffering, lookahead, and text alignment differ from a conventional spectrogram/vocoder pipeline. The application must follow the exposed streaming contract rather than assuming every system provides phoneme or word timestamps.

## Design a text-to-audio stream explicitly

Separate a text segmenter from the synthesis adapter. The segmenter sees the generated text stream, maintains a partial suffix, and emits complete speakable units. The adapter converts each unit into the provider's request/session format.

Here is **algorithmic pseudocode**, not a complete multilingual sentence parser:

```text
on text delta:
    append delta to pending_text
    find a safe boundary outside numbers and protected abbreviations
    if boundary exists:
        emit prefix with segment_sequence
        retain suffix
    otherwise if waiting exceeds maximum and a clause boundary exists:
        emit clause prefix

on text final:
    emit remaining nonempty text
    send final marker to synthesis session

on interruption:
    discard pending_text for this generation
    cancel synthesis and clear downstream output
```

Why not split on every period? `Dr.` is an abbreviation, and `1,250.50` contains a decimal point. Why not wait for every full sentence? The model might produce a long sentence whose first useful phrase could have been spoken earlier. Evaluate the segmentation policy using naturalness and correctness as well as delay.

Once a segment is emitted, changing it is costly: some of it may already be audible. Avoid speculative synthesis of text that may be revised unless you can reliably keep its output private until commitment.

## Ordering, underflow, and timing

Suppose segment 0 takes 500 ms to synthesize and segment 1 takes 150 ms. Launching both concurrently means segment 1 can arrive first. Give segments sequence IDs, buffer completed audio until the preceding segment is available, and ensure the head-of-line wait is bounded. Alternatively serialize requests or use a provider session that preserves input ordering.

Faster audio generation is useful only if the device has enough audio to keep playing. If a 300 ms phrase is generated and the next phrase is unavailable for 600 ms, the listener hears a gap. Track generated duration, queued duration, and playback rate to distinguish synthesis starvation from network starvation.

Do not pad every missing segment with silence without accounting for how it affects turn taking. A long unexpected gap can make the user think the assistant has finished, causing an interruption that the controller mistakes for a new request.

## Derive playback position from samples

If the device consumed 12,000 samples from a 24 kHz mono response, its sample-based position is 500 ms. This can be more precise than “chunk 4 played,” since chunks can vary in size.

However, converting that position into “which words were heard” requires a mapping from text to audio time. Without alignment, you know sample progress but not exact word progress. Store generated text plus delivery metadata and an interrupted marker. Do not silently claim the entire text was heard.

For avatar output, attach motion to the same audio timeline. A viseme animation scheduled against synthesis arrival can lead actual playback if the network buffers audio. Clearing audio must also invalidate its animation generation.

## Debugging exercise

Test the running sentence under three segment policies: complete sentence, short clause, and naive period split. Record pronunciation, amount interpretation, first-audio time, between-segment gaps, and order. Explain each failure at the responsible stage: normalization, segmentation, acoustic generation, conversion, or playback. A voice change cannot repair a decimal split introduced earlier in the pipeline.

## Measure synthesis throughput without hiding startup delay

Real-time factor, under a stated definition, can be `synthesis_compute_seconds / generated_audio_seconds`. Generating two seconds of speech in 0.5 seconds gives an RTF of 0.25: the computation is faster than the generated playback duration. That says little about first-audio delay if the system waits for the entire request before returning bytes.

Compare two illustrative systems. System A returns two seconds of speech after 500 ms. System B returns its first 100 ms after 150 ms and the rest incrementally by 800 ms. A has better total compute/duration in this example, but B may begin audible response sooner. Whether B plays smoothly depends on subsequent audio cadence and buffering.

Measure time to first audio, generated audio duration, inter-chunk gaps, and playback underflow. For a server handling concurrent sessions, also measure throughput under load. A low single-request RTF does not guarantee stable serving when many requests share resources.

## Compare autoregressive and duration-oriented generation

An autoregressive acoustic/audio generator conditions each output step on preceding steps. It can model sequential structure but may have sequential dependencies that constrain parallelism. A duration-oriented nonautoregressive path can expand text into timed positions and generate many acoustic positions in parallel, but duration/prosody prediction still needs to be accurate.

Some systems use iterative generation or learned codecs instead of either simple description. Do not infer naturalness, speed, or control from the architecture family alone. Compare the actual voice, language, context requirements, first-chunk behavior, and cancellation contract.

### Worked timing question

If synthesis produces a 500 ms segment, playback starts 200 ms after it becomes available, and the next 500 ms segment becomes available 800 ms after the first, the device runs out at 700 ms relative to the first segment's availability and waits about 100 ms for the next segment, ignoring other buffering. Increasing initial buffering could hide that gap but delays the first sound. Faster first audio and smooth continuous audio are related but distinct goals.

## Check your understanding

1. Why does one-token synthesis often hurt prosody?
2. What can reorder concurrently synthesized segments?
3. How should history represent interrupted speech without word alignment?

Continue with [VAD](07-vad-and-audio-front-end.md). [Lab 3](../labs/03-first-cascade.md). Further reading: [neural Transformer TTS](https://arxiv.org/abs/1809.08895).
