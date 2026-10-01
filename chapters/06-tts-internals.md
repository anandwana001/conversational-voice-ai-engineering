# 6. Speech synthesis, text segmentation, and playback

**Prerequisites:** chapters 2–5. **Goal:** trace text to sound and distinguish synthesis progress from audible progress.

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

## Check your understanding

1. Why does one-token synthesis often hurt prosody?
2. What can reorder concurrently synthesized segments?
3. How should history represent interrupted speech without word alignment?

Continue with [VAD](07-vad-and-audio-front-end.md). [Lab 3](../labs/03-first-cascade.md). Further reading: [neural Transformer TTS](https://arxiv.org/abs/1809.08895).
