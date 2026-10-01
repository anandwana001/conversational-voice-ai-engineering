# 2. Digital audio, PCM, codecs, and resampling

**Prerequisites:** chapter 1. **Goal:** account for every audio byte and avoid silent format mistakes.

<!-- chapter-navigation:start -->
**In this chapter**

- [From air pressure to numbers](#from-air-pressure-to-numbers)
- [Compute the frame size](#compute-the-frame-size)
- [Sample rate is not metadata you can rewrite](#sample-rate-is-not-metadata-you-can-rewrite)
- [Codecs and containers](#codecs-and-containers)
- [Timing and clipping](#timing-and-clipping)
- [Debugging checklist](#debugging-checklist)
- [Work through the signal representation](#work-through-the-signal-representation)
- [Derive what a rate mismatch sounds like](#derive-what-a-rate-mismatch-sounds-like)
- [Unpack channels and frame boundaries correctly](#unpack-channels-and-frame-boundaries-correctly)
- [A worked boundary audit](#a-worked-boundary-audit)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Work through the signal representation

### Sampling a known waveform

Take a sine wave with frequency 440 Hz and sample it at 16,000 Hz. Its discrete samples can be written as:

```text
x[n] = A × sin(2π × 440 × n / 16000)
```

With `A = 0.15`, the normalized peak is 0.15. There are about `16000 / 440 = 36.36` samples per cycle. There does not need to be an integer number of samples per cycle; consecutive samples follow the time grid, not the waveform's cycle boundaries.

For signed 16-bit storage, multiply by approximately 32,767, round, and store with the agreed byte order. The sine experiment in this course uses little-endian integer samples. A sample value of 1,000 is encoded as two bytes `E8 03` in little-endian order. Reading the same bytes as big-endian interprets a different signed integer. The signal is now corrupted even though the byte count remains correct.

Quantization introduces rounding error. Increasing bit depth reduces the granularity of that error for a given full-scale range, but does not restore frequencies removed during sampling or recover speech buried in noise. Sample rate and bit depth control different properties.

### Measuring amplitude instead of guessing

For samples normalized to full scale, root-mean-square amplitude is:

```text
rms = sqrt(sum(x[n]²) / N)
dBFS_rms = 20 × log10(rms)
```

For a sufficiently long sinusoid with peak 0.15, RMS is approximately `0.15 / sqrt(2) = 0.1061`, or about −19.49 dBFS using this definition. Silence has RMS zero, so its logarithm is undefined; represent it as a designated floor or negative infinity rather than dividing by zero.

“dBFS” measurements can use different peak/RMS conventions. State your convention when comparing tools. A healthy peak reading does not establish speech intelligibility, and automatic gain does not separate desired speech from background noise.

This standard-library snippet is executable in a Python interpreter:

```python
import math

def rms_dbfs(samples):
    if not samples:
        raise ValueError("Need at least one normalized sample")
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    return float("-inf") if rms == 0 else 20 * math.log10(rms)

print(rms_dbfs([0.0, 0.5, 0.0, -0.5]))  # approximately -9.03 dBFS
```

The snippet does not decode PCM bytes. First unpack and normalize samples according to their actual format. Treating bytes as amplitudes gives a meaningless loudness estimate.

## Derive what a rate mismatch sounds like

Our tone contains 16,000 samples for one intended second. If a device consumes them at 48,000 samples per second, duration becomes `16000 / 48000 = 0.333…` seconds. The number of cycles in those samples is unchanged, so frequency becomes `440 × 3 = 1320` Hz. Both speed and pitch rise by the same factor.

If you instead properly resample to 48 kHz, there are approximately 48,000 output samples over one second, and the tone remains 440 Hz. The distinction is observable in duration and pitch. It is not a matter of which header value looks plausible.

For 48 kHz to 16 kHz conversion, the new Nyquist limit is 8 kHz. Imagine an unwanted 10 kHz component. Keeping every third sample without adequate filtering can make that component appear at a lower frequency in the new signal. Once aliased, it cannot be reliably distinguished from a genuine lower-frequency component. Filtering must occur before the sampling density is reduced.

A practical resampler has filter delay and may not emit the exact expected output count for every individual input frame. Keep a running total and inspect its streaming/flush contract. Requiring each call to emit exactly one output frame can discard valid buffered samples or add discontinuities.

## Unpack channels and frame boundaries correctly

For interleaved stereo signed 16-bit data:

```text
frame bytes = L0_low L0_high R0_low R0_high L1_low L1_high R1_low R1_high ...
```

One sample **per channel** occupies four bytes across the two channels. A network chunk may end after the low byte of a sample; retain the incomplete suffix until the next read. Once complete samples exist, convert the channel layout intentionally.

If left and right both contain the same signal, `(L + R) / 2` preserves its amplitude. If `R = -L`, averaging produces zero. That is why downmixing deserves an audible test rather than a universal assumption that two microphones are always better than one.

Distinguish network fragmentation from media framing. A 640-byte application frame can arrive in several reads, while several application frames can arrive in one read. Use the protocol's framing or declared lengths, not arbitrary read sizes, to reconstruct units.

## A worked boundary audit

Suppose capture produces float32 stereo at 48 kHz, the recognizer accepts mono signed 16-bit PCM at 16 kHz, and synthesis emits mono signed 16-bit PCM at 24 kHz. Your ingress chain needs channel conversion, real resampling, and numeric-format conversion. Your egress chain must either use a playback API that accepts 24 kHz or resample to the device's required rate.

For each conversion, verify input samples, output samples, duration, peak/RMS, channel order, and retained state. Use a tone to expose pitch errors, then speech to expose intelligibility errors. A tone is easier to reason about but cannot validate recognition quality or prosody.

## Check your understanding

1. How many bytes are in 100 ms of 24 kHz mono signed 16-bit PCM?
2. Why does dropping samples require filtering?
3. Why does adding a WAV header not convert a codec?

Continue with [streaming](03-streaming-and-buffers.md). [Lab 1](../labs/01-audio-contracts.md). Codec reference: [Opus specification](https://www.rfc-editor.org/rfc/rfc6716).
