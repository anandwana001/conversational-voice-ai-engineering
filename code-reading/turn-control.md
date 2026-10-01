# Walkthrough: turn ownership and flush propagation

**Read first:** [chapters 7–10](../chapters/README.md). **Revision:** `1b78cb725910d6f63389ef4ae69b182854d5b9d9`.

## Compare three policies

| Example controller | Observed policy |
| --- | --- |
| [Basic assistant](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant/tenapp/ten_packages/extension/main_python/extension.py) | `_on_asr_result` can interrupt on final or text length greater than two; final text queues generation |
| [VAD assistant](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant-with-ten-vad/tenapp/ten_packages/extension/main_python/extension.py) | `_on_vad_start_of_sentence` interrupts; final recognition queues generation |
| [Turn-detection assistant](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/examples/voice-assistant-with-turn-detection/tenapp/ten_packages/extension/main_python/extension.py) | ASR events are sent to turn detection; detected-result and interruption handlers drive the controller |

These are facts about inspected controller code, not performance claims. Timing depends on detectors, settings, adapters, transport, and device buffering.

## Read the detector path

Open the turn-detection example's graph and the shared [turn detector](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/ten_packages/extension/ten_turn_detection/extension.py). Trace input text/audio, completion logic, timeout settings, and outbound events. Identify whether the inspected path uses textual, acoustic, or combined evidence instead of deducing that from the product name.

Likewise inspect [the VAD adapter](https://github.com/ten-framework/ten-framework/blob/1b78cb725910d6f63389ef4ae69b182854d5b9d9/ai_agents/agents/ten_packages/extension/ten_vad_python/extension.py). Record frame requirements and event emission. A controller handler named “start of sentence” does not by itself prove linguistic sentence detection.

## Read cancellation destinations

In the basic controller, `_interrupt` clears its text fragment, calls `agent.flush_llm()`, emits `tts_flush`, and sends `flush` to `agora_rtc`. The turn-detection controller also flushes turn detection.

This shows cancellation propagating through several layers. To claim complete barge-in, follow each destination's implementation and observe client playback. A function named `flush` is not evidence of which queues were cleared or whether late callbacks are fenced.

## Design a race

Queue synthesis for generation A. Trigger interruption. Deliver an old synthesis callback after the clear. Ask whether that callback is discarded, tagged, or accepted in the inspected implementation. Then use the course's [offline runtime](../examples/turn_runtime.py) to explain a generation-fencing design.

Do not attribute the teaching simulator's behavior to TEN. If the upstream implementation handles the race differently, document that difference with code and a live trace.

## Deliverable

Submit an event-ownership table, cancellation sequence, and one actual or simulated late-result trace. Translate the controller-specific names into speech onset, transcript stability, conversational completion, invalidate response, cancel producer, and clear playback.

[Next walkthrough](realtime.md) · [Source map](README.md) · [Labs 4–5](../labs/README.md)
