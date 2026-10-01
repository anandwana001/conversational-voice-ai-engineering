# Progressive labs

Read the relevant chapters, predict a result, run an experiment, and submit evidence. Estimated durations exclude account setup and dependency downloads. Offline exercises do not establish live voice performance.

| Lab | Mode | Core evidence |
| --- | --- | --- |
| [Lab 1. Account for audio samples and bytes](01-audio-contracts.md) | Offline | Byte/sample accounting and format map |
| [Lab 2. Model transcript revisions and commitment](02-streaming-transcripts.md) | Offline; optional live | Transcript revisions and turn commitment |
| [Lab 3. Build the first live STT → LLM → TTS cascade](03-first-cascade.md) | Live | Redacted cascade trace |
| [Lab 4. Compare silence endpoints and turn policies](04-turn-policy.md) | Offline; optional live | Endpoint tradeoff table |
| [Lab 5. Implement barge-in with stale-output rejection](05-interruption.md) | Offline, then live | Queue clear and stale-callback rejection |
| [Lab 6. Compare cascade and realtime audio sessions](06-realtime-comparison.md) | Live | Measured architecture comparison |
| [Lab 7. Add validated tools and an MCP boundary](07-tools-and-mcp.md) | Mock writes and genuine MCP | Operation ledger and MCP trace |
| [Lab 8. Build grounded answers and scoped memory](08-rag-and-memory.md) | Synthetic retrieval; optional live model | Scoped evidence and memory lifecycle |
| [Lab 9. Trace browser and telephone media](09-transport-and-phone.md) | Live browser; optional phone | Channel lifecycle and codec path |
| [Lab 10. Preserve speaker attribution and time assistance](10-speakers-and-copilot.md) | Script/recording; optional models | Speaker attribution and intervention decisions |
| [Lab 11. Measure latency and evaluate actual outcomes](11-latency-and-evaluation.md) | Offline, then live | Latency report and actual task assertions |
| [Lab 12. Run production failure drills](12-production-failure-drills.md) | Development deployment | Failure recovery and access evidence |

Each guide supplies Build, Deliver, and Acceptance sections plus a failure experiment and transfer task. Use synthetic data and keep generated notes/audio in the ignored `artifacts/` directory or a private notebook.

[Getting started](../GETTING_STARTED.md) · [Capstone](../capstone/README.md) · [Course](../README.md)
