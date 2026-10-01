# Getting started

## Choose a route

If you are new to voice AI, read chapters 1–6 before running a framework. You should be able to draw the audio-to-text-to-audio path and explain which information each stage loses. Then complete labs 1–3.

If you already have a voice demo, start with chapters 7–10 and labs 4–5. Bring a trace of a user interruption. Determine whether your system stops model generation, server queues, and actual device playback.

For production work, complete chapters 18–22 and labs 10–12. Use the capstone rubric to expose gaps in an existing service.

## Offline setup

Clone this repository, open a terminal in its root, and run:

```bash
python3 --version
python3 examples/audio_frames.py
python3 examples/turn_runtime.py
```

The scripts require Python 3.9+. They print deterministic teaching results. The PCM experiment also creates a synthetic WAV in `artifacts/`; it contains a tone, not speech. Generated artifacts are ignored by Git.

Read each script before modifying it. Change one parameter, predict the result, then run it. This makes a stronger experiment than repeatedly executing a black box.

## Live setup

Live labs use your chosen runtime and model providers. TEN is the reference route; follow [the pinned source guide](code-reading/README.md) and the upstream example's README. Start with `voice-assistant`; do not simultaneously add phone integration, memory, and video.

You need a microphone, headphones, a supported execution environment, and credentials for your chosen STT, LLM, TTS, and transport. A local model can replace a hosted model if its hardware and streaming contract fit. Realtime speech-to-speech uses a different session contract and may need different credentials or quotas.

Create an ignored `.env` only in the application you run. Do not paste secrets into Markdown, screenshots, committed graph properties, fixtures, or issue reports. Public app identifiers and signing secrets have different roles: only the former may belong in a browser. Mint expiring client credentials through a trusted backend where the transport requires them.

Before opening a live session, set a spending limit, use a development project, and arrange a session timeout. Run with synthetic user data. Stop workers and containers when finished. Live completion is evidenced by recordings, traces, and assertions, not by this repository's offline checks.

## Keep an engineering notebook

For every lab record the input, expected behavior, observed behavior, settings, source commit, and conclusion. Store a small redacted trace with monotonic timestamps. Record deliberate tradeoffs: a more patient endpoint can improve accuracy while increasing the turn gap.

Create your notes in `artifacts/` or a separate private repository. Do not commit real caller audio or personal data into this public learning repository.

## When stuck

Use [troubleshooting](reference/troubleshooting.md). Identify the first broken boundary: capture, transport, recognition, controller, generation, synthesis, or playback. Validate the format and event contract at that boundary before changing the prompt.

[Back to the course](README.md) · [Learning path](SYLLABUS.md)
