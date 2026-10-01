# Offline engineering experiments

These small standard-library programs isolate mechanisms. They do not implement a real voice agent, train models, open MCP connections, or measure provider performance.

| Script | Demonstrates | Does not demonstrate |
| --- | --- | --- |
| [audio_frames.py](audio_frames.py) | PCM byte accounting and a synthetic WAV | Real resampling, codecs, microphone capture |
| [turn_runtime.py](turn_runtime.py) | Silence policy, queue clear, generation fencing | Trained VAD, threads, sockets, device playback |
| [tool_idempotency.py](tool_idempotency.py) | Retry keys and conflicting argument rejection | Durable atomic storage, real booking authorization |
| [latency_report.py](latency_report.py) | Named intervals, nearest-rank p50/p95, failure counts | Cross-machine clock synchronization or real benchmarks |

Run from the repository root using the commands in [README](../README.md). The synthetic latency fixture uses one sequential clock domain with ordered milestones. Real systems can overlap spans; adapt the trace schema rather than forcing reality into this assumption.

The idempotency ledger is intentionally single-process. Multiple workers require a durable transaction/uniqueness design and account-scoped keys. Do not use this teaching dictionary as a production booking service.

Experiment by removing stale-generation checking, changing endpoint thresholds, or corrupting a format contract. Predict the failure before running the changed example. The [tests](../tests/test_experiments.py) check important invariants and edge cases.
