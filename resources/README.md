# Resources and evidence status

The course explains concepts independently and links primary sources for deeper study. External repositories and talks retain their own copyright and licenses; no full talk transcripts or copied upstream source are included.

## Added video resources

| Resource | Verified metadata | Course connection |
| --- | --- | --- |
| [Beyond Transcription: Building Voice AI That Understands Conversations — Hervé Bredin, pyannoteAI](https://www.youtube.com/watch?v=mFLlVpnGpds) | Title and channel verified through YouTube oEmbed on 2026-10-01; channel: AI Engineer | Chapters 5, 17; [study guide](beyond-transcription.md) |
| [The Voice-First AI Overlay: Designing Conversational Co-Pilots - Gregory Bruss](https://www.youtube.com/watch?v=y9YQc9a3gNw) | Title and channel verified through YouTube oEmbed on 2026-10-01; channel: AI Engineer | Chapters 17, 18, 20; [study guide](voice-first-overlay.md) |

The study guides contain course-authored questions and experiments. The video contents were not transcribed or viewed during repository preparation. No chapter claims to quote, summarize, or reproduce those talks. Add timestamped, verified notes through a contribution if you watch them.

## Primary-source bibliography

| Topic | Source | Reading purpose |
| --- | --- | --- |
| Transformer models | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Attention and sequence-model foundations |
| Recognition alignment | [Connectionist Temporal Classification](https://www.cs.toronto.edu/~graves/icml_2006.pdf) | Alignment without presegmented token labels |
| Speech recognition | [Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) | Whisper research and generalization |
| Speech synthesis | [Neural Speech Synthesis with Transformer Network](https://arxiv.org/abs/1809.08895) | One neural acoustic-generation architecture |
| Retrieval | [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) | Retrieval and generation as distinct mechanisms |
| MCP | [Specification edition 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) | Versioned integration protocol |
| Browser media | [WebRTC specification](https://www.w3.org/TR/webrtc/) | Browser media API and connection behavior |
| Network traversal | [ICE: RFC 8445](https://www.rfc-editor.org/rfc/rfc8445) | Connectivity establishment |
| WebSocket | [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) | Bidirectional framed transport |
| SIP | [RFC 3261](https://www.rfc-editor.org/rfc/rfc3261) | Session signaling |
| RTP | [RFC 3550](https://www.rfc-editor.org/rfc/rfc3550) | Media packet timing and sequencing |
| DTMF events | [RFC 4733](https://www.rfc-editor.org/rfc/rfc4733) | Telephone events over RTP |
| Opus | [RFC 6716](https://www.rfc-editor.org/rfc/rfc6716) | Audio codec specification |
| Diarization | [pyannote.audio](https://github.com/pyannote/pyannote-audio) | Speaker processing implementation entry point |
| Voice reference code | [TEN pinned revision](https://github.com/ten-framework/ten-framework/tree/1b78cb725910d6f63389ef4ae69b182854d5b9d9) | [Source-reading exercises](../code-reading/README.md) |
| VAD | [TEN VAD](https://github.com/ten-framework/ten-vad) | Speech-activity implementation reference |
| Turn detection | [TEN turn detection](https://github.com/ten-framework/ten-turn-detection) | Completion-detection reference |

The machine-readable [source manifest](sources.json) records verification methods. Opening a landing page verifies the source identity, not every claim in a paper, source package, or video. A contributor adding an implementation-specific claim should identify the exact section, symbol, or timestamp they inspected.

## Resource maintenance

Keep stable theory separate from current provider setup. Record revision/date for mutable APIs. Replace broken links with authoritative equivalents where possible. Explain limitations honestly: a title-only verification cannot support a detailed talk summary, and a source-path verification cannot prove live latency.

[Course](../README.md) · [Contribution guidance](../CONTRIBUTING.md)
