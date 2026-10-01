# Walkthrough: realtime audio without losing controller ownership

**Read first:** [chapter 11](../chapters/11-realtime-speech-to-speech.md). **Revision:** `1b78cb725910d6f63389ef4ae69b182854d5b9d9`.

## Compare graph boundaries

Open the [realtime graph](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant-realtime/tenapp/property.json). The selected graph includes a `v2v` node using `openai_mllm_python` rather than separate STT/LLM/TTS nodes. Transport sends input through `streamid_adapter` to `v2v`; output audio returns from `v2v` to transport.

Transport, controller, message collector, and tool registration remain. Removing explicit stage nodes did not remove lifecycle management or tool execution policy.

## Follow the session event interface

Read [the controller](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant-realtime/tenapp/ten_packages/extension/main_python/extension.py) and [the model adapter](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/ten_packages/extension/openai_mllm_python/extension.py).

The graph declares server events for input/output transcripts, session readiness, interruption, and function calls. In the controller, follow the event-consumer task, greeting readiness, context/message methods, response creation, and `_interrupt`.

The inspected realtime controller's `_interrupt` sends a transport flush. To explain provider-side response cancellation and history semantics, continue into the adapter and its client implementation. Do not assume the cascade's `flush_llm` and `tts_flush` calls apply unchanged.

## Ask ownership questions

- Who decides that input audio constitutes a completed turn?
- Who initiates the next response, automatically or manually?
- What identifies the current provider response?
- What happens to provider context after local playback is cleared?
- How does a function result trigger continuation?
- What prevents a late result from speaking during a new turn?

Answer with the pinned code and, when behavior depends on the live provider, a trace of that actual provider session. Current model availability and session limits must be checked in the provider's own documentation before running the lab.

## Deliverable

Draw the cascade and realtime interfaces side by side. Annotate which responsibilities moved behind the model-session adapter and which remain in the application. Include a cancellation experiment and mark any unobserved playback or history behavior as unverified.

[Source map](README.md) · [Lab 6](../labs/06-realtime-comparison.md) · [Course](../README.md)
