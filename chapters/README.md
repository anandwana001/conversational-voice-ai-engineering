# Chapter index

Read in order for the complete foundation-to-production path. Every chapter includes internal mechanisms, failure cases, and understanding checks. Pair reading with the [labs](../labs/README.md) and [answer guide](../reference/answers.md).

| Chapter | Area | Focus |
| --- | --- | --- |
| [1. What a conversational voice agent is](01-voice-agent-architecture.md) | Foundations | What an agent is and which component owns each decision |
| [2. Digital audio, PCM, codecs, and resampling](02-digital-audio.md) | Audio | Samples, PCM, containers, codecs, and real conversion |
| [3. Streaming, buffering, clocks, and backpressure](03-streaming-and-buffers.md) | Streaming | Clocks, buffering, backpressure, and stale events |
| [4. LLM internals and their effect on voice](04-llm-internals.md) | Models | Tokens, attention, prefill/decode, and context |
| [5. Speech recognition: from waveform to evolving words](05-stt-internals.md) | Models | Recognition architectures, revisions, and error measurement |
| [6. Speech synthesis, text segmentation, and playback](06-tts-internals.md) | Models | Synthesis stages, segmentation, and delivery |
| [7. VAD, noise suppression, and echo cancellation](07-vad-and-audio-front-end.md) | Conversation | Speech presence, hysteresis, and echo |
| [8. Endpointing and conversational turn detection](08-endpointing-and-turn-detection.md) | Conversation | Stable words versus floor transfer |
| [9. Barge-in and cancellation across the whole pipeline](09-interruption-and-cancellation.md) | Conversation | Distributed cancellation, history, and side effects |
| [10. Runtime architecture, events, and orchestration](10-runtime-and-orchestration.md) | Runtime | Event contracts, state ownership, and concurrency |
| [11. Realtime speech-to-speech sessions](11-realtime-speech-to-speech.md) | Models | Audio session semantics and response ownership |
| [12. Tools, confirmation, idempotency, and workflow state](12-tool-calling-and-workflows.md) | Actions | Validated proposals, confirmation, and retry-safe writes |
| [13. MCP: tool discovery and integration boundaries](13-mcp.md) | Integrations | Protocol lifecycle and policy boundaries |
| [14. RAG, conversation context, and durable memory](14-rag-and-memory.md) | Knowledge | Retrieval, grounding, provenance, and scoped memory |
| [15. WebRTC, WebSocket, and the media/control boundary](15-webrtc-and-websocket.md) | Channels | Browser media and custom streaming |
| [16. SIP, RTP, PSTN, and audio bridges](16-sip-rtp-and-telephony.md) | Channels | Signaling, media packets, transcoding, and call lifecycle |
| [17. Diarization, overlap, and conversational understanding](17-diarization-and-conversation-understanding.md) | Understanding | Speakers, overlap, attribution, and evaluation |
| [18. Multimodal agents and conversational co-pilots](18-multimodal-and-conversational-copilots.md) | Understanding | Visual freshness and intervention timing |
| [19. Latency engineering and observability](19-latency-and-observability.md) | Production | Critical paths, percentiles, failures, and cost |
| [20. Evaluating voice quality, behavior, and task success](20-evaluation.md) | Production | Deterministic checks, listening, and judge limits |
| [21. Security, privacy, and application trust boundaries](21-security-and-privacy.md) | Production | Identity, tenant scope, secrets, and data retention |
| [22. Reliability, deployment, and session scaling](22-reliability-deployment-and-scaling.md) | Production | Readiness, draining, failure recovery, and capacity |

[Course](../README.md) · [Six-week path](../SYLLABUS.md) · [Source reading](../code-reading/README.md)
