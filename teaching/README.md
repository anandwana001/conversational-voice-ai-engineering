# Instructor guide

Use [the six-week plan](../SYLLABUS.md) as a starting pace. Prepare one known-good live environment and an offline alternative for each session. Provider credentials and phone accounts should never be shared in public course materials.

## Session format

Start with a concrete failure, such as a booking on an interim transcript or speech continuing after interruption. Ask learners to predict the responsible layer. Explain the mechanism, inspect a source path, then run a controlled experiment. Finish by translating the framework names into generic responsibilities.

For each lab, assess the submitted evidence against its acceptance criteria. A successful command invocation is not enough; require a trace and an explanation. Simulated parts should stay labeled as simulated.

## Weekly discussion prompts

| Week | Prompt | Strong response includes |
| --- | --- | --- |
| 1 | Why does a correct transcript not guarantee a correct action? | Interim commitment, corrections, and controller state |
| 2 | What has to stop during barge-in? | Producers, downstream queues, device output, late callbacks, history |
| 3 | What does a timeout mean after a booking request? | Unknown outcome, stable operation key, reconciliation |
| 4 | Who is “speaker 1”? | Session-relative acoustic label and separate account identity |
| 5 | Can a fast response still be bad? | False endpoints, wrong actions, pronunciation, unwanted intervention |
| 6 | What survives a worker restart? | Durable operation results and explicit limits on session resumption |

## Common misconceptions to surface

- “Streaming” implies low latency: ask learners to locate every buffering stage.
- “Final” means the user finished: distinguish segment stability and turn ownership.
- Cancelling a task reverses an action: inspect the authoritative write ledger.
- A fluent answer is grounded: inspect retrieved evidence and its exceptions.
- Speaker labels prove identity: require independent authorization.
- A passing transcript judge proves voice quality: listen and inspect actions.

## Assessment

Use [the answer guide](../reference/answers.md) for reasoning checkpoints, not rote memorization. Ask learners to change one assumption, such as a new sample rate, a second speaker, or a lost tool reply, and predict the consequence.

During capstone review, first examine task state and failure evidence, then interaction quality and presentation. Have learners explain a second-runtime implementation without vendor names. This is the course's transfer test.

## Accessibility and participation

Provide readable transcripts and text-input alternatives for learning activities. Accommodate pauses, varied speaking styles, and learners who cannot use a microphone. Do not use one confident fast speaker as the sole endpointing benchmark. Let participants opt out of recording and public demos.

## Resource sessions

Use the two video guides for directed viewing and timestamped discussion. Ask learners to distinguish observed speaker claims from their own design conclusions. Do not imply that course-authored prompts are a transcript of the talk.

[Course](../README.md) · [Capstone](../capstone/README.md)
