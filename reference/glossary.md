# Voice AI glossary

| Term | Meaning |
| --- | --- |
| ADC | Analog-to-digital conversion; captures an electrical audio signal as samples |
| AEC | Acoustic echo cancellation; suppresses microphone pickup of playback using a reference |
| Agent controller | Application component owning state, actions, turn policy, and lifecycle |
| ASR / STT | Automatic speech recognition / speech-to-text |
| Audio frame | A timed group of samples or codec data under a stated format contract |
| Backchannel | Short acknowledgement during someone else's turn, such as “mm-hm” |
| Backpressure | Feedback or control preventing unbounded producer/consumer backlog |
| Barge-in | User interruption while assistant output is underway |
| Causal masking | Attention restriction preventing a decoder position from using future tokens |
| Codec | Audio/video encoding and decoding scheme |
| Container | Format organizing encoded media and metadata, such as WAV |
| Context window | Model input budget; token/accounting details depend on the model |
| CTC | Connectionist Temporal Classification, an alignment objective using blank and collapse rules |
| Decode (LLM) | Incremental next-token generation after context processing |
| Decode (audio) | Conversion of encoded audio into a signal representation |
| DER | Diarization error rate under explicitly stated scoring conventions |
| Diarization | Estimating who spoke when; labels are not account authentication |
| DTMF | Dual-tone multifrequency keypad input; may travel as audio or telephone events |
| Endpointing | Deciding when an audio/recognition segment or turn ends under a defined policy |
| Fencing | Rejecting results from an obsolete generation or operation owner |
| Full duplex | Input and output can occur simultaneously; does not itself guarantee natural turns |
| Generation ID | Identifier distinguishing one response's output from earlier obsolete output |
| Grounding | Supporting an answer with appropriate external evidence |
| Half duplex | Input and output alternate rather than operating simultaneously |
| Hangover | VAD policy retaining activity briefly after speech evidence falls |
| ICE | Interactive Connectivity Establishment for finding viable network paths |
| Idempotency | Repeated application of the same logical operation has the intended single effect |
| Interim transcript | Revisable recognition hypothesis before stabilization |
| Jitter | Variation in delivery timing |
| Jitter buffer | Buffer smoothing or reordering media arrival for timed playout |
| KV cache | Stored attention key/value representations reused during model generation |
| LLM | Large language model; commonly predicts/generates token sequences |
| MCP | Model Context Protocol, a versioned capability integration protocol |
| Media timestamp | Time/position in the signal timeline, not event arrival time |
| Memory | Retained user or interaction information with scope and provenance |
| Monotonic clock | Clock suited to elapsed duration measurement without wall-clock corrections |
| μ-law | Logarithmic companding encoding used by some telephony audio routes |
| Nyquist limit | Half the sampling rate; upper band limit for ideal band-limited sampling |
| Opus | Audio codec used in many realtime media systems |
| PCM | Pulse-code modulation; direct quantized sample representation |
| Percentile | Distribution position under a defined calculation rule |
| Prefill | Model processing of supplied context before incremental generation |
| Prefix padding | Preserved pre-onset audio included to avoid clipping speech beginnings |
| Prompt injection | External content attempting to redirect application/model behavior |
| Prosody | Speech rhythm, stress, timing, pitch, and intonation |
| PSTN | Public switched telephone network |
| RAG | Retrieval-augmented generation; evidence retrieval combined with answer generation |
| Resampling | Converting a signal between sample grids with appropriate filtering/state |
| RTP | Realtime media packet protocol with timing and sequence metadata |
| SDP | Session Description Protocol, used to describe negotiated media |
| SIP | Session Initiation Protocol for signaling |
| Speech separation | Estimating individual audio signals from a mixture |
| Speech-to-speech | Model/session interface consuming and producing audio |
| STUN | Mechanism helping discover network-visible addressing |
| Tool call | Structured proposed integration operation executed under application policy |
| TTFT | Time to first token; always specify request/start boundary |
| TTFB | Time to first byte; meaning depends on the measured service/boundary |
| TTS | Text-to-speech synthesis |
| TURN | Relay mechanism for network traversal when direct paths are unavailable |
| Turn detection | Estimating whether conversational floor transfer is appropriate |
| Vocoder | Component generating a waveform from an acoustic representation |
| WebRTC | Realtime media APIs and protocols with application-managed signaling |
| WebSocket | Persistent bidirectional framed transport, commonly over TCP/TLS |
| WER | Word error rate: substitutions, deletions, and insertions per reference word |

[Chapters](../chapters/README.md) · [Course](../README.md)
