# Walkthrough: trace one cascaded turn

**Read first:** [chapters 1–6](../chapters/README.md). **Revision:** `1b78cb725910d6f63389ef4ae69b182854d5b9d9`.

## 1. Read the graph as configuration

Open the pinned [voice-assistant graph](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant/tenapp/property.json). Inspect the `voice_assistant` predefined graph, not a different variant in the same file.

Its nodes include `agora_rtc`, `stt`, `llm`, `tts`, `main_control`, `message_collector`, a weather tool, and `streamid_adapter`. The addons bind these logical nodes to implementations. Names such as `stt` are local graph names; names such as `deepgram_asr_python` identify an implementation package.

Environment references supply credentials and settings. Document the format assumptions without copying secret values. A property named `model` is configuration, not an architectural guarantee that any current account supports that model.

## 2. Follow audio ingress

In the graph's `audio_frame` connections, follow `pcm_frame` from transport to the stream-ID adapter and then STT. This is data-plane routing. Identify where decoded media becomes the sample format the recognizer expects.

Read the shared [ASR adapter](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/ten_packages/extension/deepgram_asr_python/extension.py). `_handle_asr_result` builds an `ASRResult` and forwards it through the base interface. `finalize` selects a configured finalize strategy. Provider-specific details remain inside the adapter; the controller receives semantic events.

## 3. Follow the controller, not a guessed straight line

Open [MainControlExtension](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant/tenapp/ten_packages/extension/main_python/extension.py). `on_init` creates an `Agent` and registers decorated handlers. `on_data` and `on_cmd` delegate incoming messages to that agent.

In `_on_asr_result`, empty text is ignored; final or sufficiently long text can interrupt; a final result increments the turn ID and queues LLM input. This is the inspected example's policy, not a recommended universal endpointing rule. The generic responsibilities are hypothesis handling, interruption evidence, and committed model input.

Follow `queue_llm_input` into its actual implementation. Record how history and tools become a model request. The [LLM adapter](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/ten_packages/extension/openai_llm2_python/extension.py) delegates generation through its client; continue into the client and base contract to understand streaming.

## 4. Follow response segmentation and synthesis

`_on_llm_response` handles message deltas using `parse_sentences`, retains a sentence fragment, sends completed pieces to TTS, and flushes remaining text when the message ends. Read the helper implementation to learn its segmentation limits rather than assuming it handles every language or decimal.

`_send_to_tts` emits `tts_text_input` with request ID, text, end marker, and metadata. The graph routes TTS PCM to transport. `message_collector` carries transcript/UI information; it is not the audio playback device.

## 5. Draw two traces

Draw the graph's static media connections, then draw a sequence diagram of controller events and commands. Explain why a diagram saying only “STT → LLM → TTS” hides useful control behavior.

Annotate where each stage can buffer, fail, or receive a late event. Verify actual output format in the adapter configuration. Do not infer user-heard timing from controller transcript messages.

## Deliverable

Submit a provider-neutral diagram using “transport adapter,” “recognition adapter,” “session controller,” “generation adapter,” and “synthesis adapter.” Include one redacted trace and a question that requires following an imported method rather than reading only graph JSON.

[Next walkthrough](turn-control.md) · [Source map](README.md) · [Lab 3](../labs/03-first-cascade.md)
