# Lab 1. Account for audio samples and bytes

**Read:** [chapter 2](../chapters/02-digital-audio.md). **Mode:** offline. **Time:** approximately 45–60 minutes.

## Build

1. Run `python3 examples/audio_frames.py` from the repository root.
2. Inspect the generated `artifacts/tone.wav` header with Python's `wave` module. Verify mono, signed 16-bit PCM, 16 kHz, and one second of samples.
3. Before editing the script, calculate the expected bytes for 24 kHz mono, 16-bit, 100 ms. Then call `PCMFormat(24000, 1, 2).frame_bytes(100)` and compare.
4. Write a table for capture, transport decoder, STT input, TTS output, and playback. Fill in format, rate, channels, frame duration, and conversion owner.
5. Explain what would happen if the 16 kHz samples were played at 48 kHz. Optionally write a second WAV with only the header rate changed and listen at a comfortable volume.

## Deliver

Submit your calculations, format table, and a paragraph explaining why relabeling is not resampling. The tone is deliberately synthetic and contains no recognition task.

## Acceptance

- The 20 ms default frame contains 320 samples and 640 PCM payload bytes.
- The one-second file contains 16,000 samples; the container is larger than its 32,000-byte payload.
- Your 24 kHz calculation yields 4,800 bytes for 100 ms.
- Every format conversion in your table has an explicit owner.

**Failure experiment:** request a frame duration that produces a fractional sample count. The example rejects it rather than rounding silently. Explain how a production stream could maintain fractional timing state.

**Transfer:** describe the contract without using any framework type names.

[Next lab](02-streaming-transcripts.md) · [All labs](README.md)
