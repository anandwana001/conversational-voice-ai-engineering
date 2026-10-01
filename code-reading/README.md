# Read TEN as a reference implementation

This course uses TEN to make abstract concepts inspectable. You should finish each exercise with a provider-neutral explanation. The repository is not bundled here, and running TEN is not required for the offline experiments.

## Reference revision

The inspected upstream commit is [`1b78cb725910d6f63389ef4ae69b182854d5b9d9`](https://github.com/ten-framework/ten-framework/tree/1b78cb725910d6f63389ef4ae69b182854d5b9d9). Paths in this guide were verified against that commit's Git tree, not inferred from current marketing descriptions. This is a course reference snapshot, not a claim that it is the newest upstream revision.

Clone a separate checkout outside this course repository:

```bash
git clone https://github.com/ten-framework/ten-framework.git ten-reference
cd ten-reference
git checkout --detach 1b78cb725910d6f63389ef4ae69b182854d5b9d9
git rev-parse HEAD
```

Read the pinned [root README](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/README.md) and your selected example's README before setup. Use upstream prerequisites, environment template, Docker configuration, and task commands for that revision. Installation can download dependencies and consume model/transport usage when run; it is separate from the offline course setup.

## Reading order

1. [Cascade walkthrough](cascade.md): graph, ingress, transcript, controller, sentence segmentation, output.
2. [Turn-control walkthrough](turn-control.md): transcript-driven interruption, VAD onset, semantic turn detection, flushing.
3. [Realtime walkthrough](realtime.md): audio-session node and remaining controller responsibilities.

## Concept-to-source map

All paths below are relative to the upstream checkout. The [machine-readable manifest](../resources/sources.json) records them with pinned links.

| Concept | Start at | Inspect next |
| --- | --- | --- |
| Cascade | `ai_agents/agents/examples/voice-assistant/tenapp/property.json` | `tenapp/ten_packages/extension/main_python/extension.py` under the same example |
| Streaming ASR | `ai_agents/agents/ten_packages/extension/deepgram_asr_python/extension.py` | Result/finalize callbacks and reconnect manager in that package |
| LLM adapter | `ai_agents/agents/ten_packages/extension/openai_llm2_python/extension.py` | `openai.py` and imported base-class contract |
| TTS adapter | `ai_agents/agents/ten_packages/extension/elevenlabs_tts2_python/extension.py` | Input/output and flush handling in that package |
| VAD | `ai_agents/agents/examples/voice-assistant-with-ten-vad/tenapp/property.json` | `ten_vad_python/extension.py` in shared extensions |
| Turn detection | `ai_agents/agents/examples/voice-assistant-with-turn-detection/tenapp/property.json` | `ten_turn_detection/extension.py` and controller handlers |
| Realtime audio | `ai_agents/agents/examples/voice-assistant-realtime/tenapp/property.json` | Shared `openai_mllm_python/extension.py` |
| Tools | `ai_agents/agents/ten_packages/extension/weatherapi_tool_python/extension.py` | Tool registration and execution in the example agent controller |
| WebSocket | `ai_agents/agents/examples/websocket-example/README.md` | Shared `websocket_server/extension.py` |
| SIP | `ai_agents/agents/examples/voice-assistant-sip-twilio/README.md` | Example graph and server README |
| Diarization | `ai_agents/agents/examples/speaker-diarization/README.md` | Example controller and graph |
| Memory | `ai_agents/agents/examples/voice-assistant-with-memU/README.md` | Example graph/controller and external memory integration contract |
| Video | `ai_agents/agents/examples/voice-assistant-video/README.md` | Example controller, graph, and visual event timing |

These are reading entry points, not promises that every course production feature is already implemented there. The course labs deliberately add requirements such as durable idempotency, tenant isolation, and failure evidence. Inspect the source before claiming that an example provides them.

## Read imported behavior, not just subclass methods

An adapter often delegates to a base class or another package. Find definitions rather than assuming the subclass contains all streaming and cancellation logic:

```bash
rg -n 'class AsyncASRBaseExtension|class AsyncLLM2BaseExtension' ai_agents
rg -n 'flush_llm|queue_llm_input|register_llm_tool' ai_agents/agents/examples/voice-assistant
rg -n 'tts_flush|tts_text_input|pcm_frame' ai_agents/agents
```

Search scope is intentionally limited to agent code. Follow imports if a definition comes from an installed dependency and record that dependency version.

## Upgrade exercise

When changing reference commits, save the new SHA, verify paths, compare graph node names and event contracts, and rerun the relevant live labs. Update the manifest and prose together. A working link alone does not establish that the same behavior remains.

[Course](../README.md) · [Chapter index](../chapters/README.md)
