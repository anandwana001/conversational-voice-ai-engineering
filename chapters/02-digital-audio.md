# 2. Digital audio, PCM, codecs, and resampling

**Prerequisites:** chapter 1. **Goal:** account for every audio byte and avoid silent format mistakes.

## From air pressure to numbers

A microphone converts changing air pressure into an electrical signal. An analog-to-digital converter samples that signal at intervals. A sample is an amplitude measurement, not a word or an audio packet. The sample rate says how many measurements are taken per second per channel.

PCM stores quantized amplitudes directly. Signed 16-bit PCM commonly represents amplitudes as integers from −32,768 to 32,767. Floating-point audio commonly uses a nominal range near −1 to 1, although a processing graph can temporarily exceed that range before clipping. Converting float to integer requires scaling, clipping, and an agreed byte order.

For interleaved stereo, samples are typically arranged left, right, left, right. A mono recognizer cannot safely treat those bytes as one continuous mono waveform. Downmix intentionally and consider phase cancellation when averaging channels.

## Compute the frame size

For uncompressed PCM:

```text
samples per channel = sample_rate × frame_duration_seconds
frame_bytes = samples_per_channel × channels × bytes_per_sample
byte_rate = sample_rate × channels × bytes_per_sample
```

At 16 kHz, mono, 16-bit, a 20 ms frame contains 320 samples and 640 bytes. One second contains 32,000 bytes. At 48 kHz stereo with the same integer format, a 20 ms frame is 3,840 bytes. Mixing these contracts produces six times the expected payload.

The [offline experiment](../examples/audio_frames.py) calculates these sizes and writes a WAV tone. A WAV file has a container header and data chunks; raw PCM does not. Sending a whole WAV file to a raw-PCM socket can make header bytes become apparent noise.

## Sample rate is not metadata you can rewrite

If 48,000 samples captured over one second are played at 16,000 samples per second, playback takes three seconds and pitch falls. Changing a label does not create a 16 kHz signal.

Resampling reconstructs a band-limited approximation and evaluates it at a new time grid. Downsampling needs a low-pass filter before reducing the sampling density to prevent higher frequencies folding into lower ones, called aliasing. The Nyquist limit is half the sample rate; practical filters need a transition band. Merely keeping every third sample is a poor general-purpose speech resampler.

A streaming resampler retains filter state across frames. Restarting it at each packet boundary can create clicks and change timing. Noninteger ratios also need fractional position state, so per-frame rounding cannot be your only accounting mechanism.

## Codecs and containers

A codec compresses a signal into a bitstream. A container or packet format describes how encoded data is arranged. Opus is a codec; WAV is commonly a container; RTP is a media packet protocol. PCM and compressed codec packets are not interchangeable.

Decode before resampling. If the model accepts PCM, the bridge owns codec decoding and conversion. Telephony may use G.711 μ-law or A-law: each encoded byte is a companded sample, not a signed 16-bit PCM sample. WebRTC commonly negotiates compressed media such as Opus; the application's decoded capture format is a separate contract.

## Timing and clipping

Maintain sequence and sample counts. A frame's media timestamp should describe its position in the signal, while its arrival timestamp describes network delivery. Arrival gaps do not necessarily mean the speaker paused.

Clipping happens when amplitude exceeds the representable range. It creates distortion rather than making speech uniformly clearer. A quiet signal can also impair recognition. Examine RMS, peak, silence, and clipping percentage before blaming STT accuracy. Loudness normalization, noise suppression, and echo cancellation solve different problems.

## Debugging checklist

Record encoding, sample rate, channels, endianness, duration, and expected payload bytes at each boundary. Save a tiny development clip and play it with the declared format. A pitch or speed shift points toward rate mismatch; alternating-channel artifacts point toward channel interpretation.

## Check your understanding

1. How many bytes are in 100 ms of 24 kHz mono signed 16-bit PCM?
2. Why does dropping samples require filtering?
3. Why does adding a WAV header not convert a codec?

Continue with [streaming](03-streaming-and-buffers.md). [Lab 1](../labs/01-audio-contracts.md). Codec reference: [Opus specification](https://www.rfc-editor.org/rfc/rfc6716).
