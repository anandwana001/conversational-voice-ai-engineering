# Lab 3. Build the first live STT → LLM → TTS cascade

**Read:** [chapters 4–6](../chapters/README.md) and [the cascade walkthrough](../code-reading/cascade.md). **Mode:** live; provider usage may be paid. **Time:** 2–3 hours after setup.

## Build

1. Follow [TEN setup and source mapping](../code-reading/README.md), or implement the same boundaries in your chosen runtime.
2. Start with microphone audio, one recognizer, one LLM, one TTS, and playback. Keep tools and durable memory disabled for this experiment.
3. Say “What is a sample rate?” Trace audio ingress, final transcript, model request, first text, first speakable segment, first generated audio, and playback start.
4. Test a name, a decimal amount, and an ambiguous date. Observe recognition and synthesis separately.
5. Change response length or segment policy and repeat the same utterances.

## Deliver

Submit a boundary diagram, redacted event trace, configuration versions, and a comparison of at least five successful turns. Label unobserved client playback timing honestly; provider first-audio timing is not a substitute.

## Acceptance

- The spoken answer matches the recognized query and generated speakable text.
- Every boundary has a documented audio or event format.
- Interim recognition does not create duplicate model requests.
- A missing provider key produces an actionable diagnostic rather than a fabricated answer.

**Failure experiment:** intentionally configure a wrong output rate in a development branch and diagnose it from byte/sample accounting. Restore the correct format.

**Transfer:** describe which adapters you would replace to swap STT or TTS providers.

[Next lab](04-turn-policy.md) · [All labs](README.md)
