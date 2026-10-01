# 17. Diarization, overlap, and conversational understanding

**Prerequisites:** chapters 5, 7–8. **Goal:** preserve who spoke when without treating acoustic clusters as authenticated people.

## Transcription answers only part of the question

STT estimates words. Diarization estimates speaker activity over time: who spoke when. Speaker identification attempts to match a voice to a known identity. Authentication verifies that a caller is permitted to act. These are separate tasks.

Consider a shared microphone:

```text
speaker A: I prefer mornings.
speaker B: I prefer evenings.
```

A plain transcript summary saying “the user prefers evenings” discards attribution. If durable memory uses that summary, the wrong person's preference can be stored even though every recognized word is correct.

## A common diarization pipeline

Speech activity segmentation finds intervals containing speech. Speaker representations or embeddings characterize voice regions. Clustering or assignment groups intervals that appear to belong to the same speaker. Temporal processing maps those assignments to a timeline.

Some systems integrate these steps or use end-to-end approaches. Short turns, similar voices, reverberation, overlap, and changes in microphone quality make assignment harder. “Speaker 1” is a session-relative label, not a globally stable person identifier.

Online diarization must decide with limited future context. Offline processing can revise earlier assignments after hearing more. Therefore labels may change or require reconciliation. Store versioned annotations and stable application IDs where you explicitly bind a speaker, rather than assuming early labels are permanent.

## Overlapping speech

Two people can speak at once. A single-speaker label per time interval cannot fully represent overlap. Your data model may need multiple active speakers, per-speaker transcripts, or an explicit overlap marker.

Speech separation attempts to recover individual signals from a mixture; overlap detection only says overlap exists. Neither is equivalent to diarization. If words cannot be attributed confidently, preserve ambiguity instead of assigning them arbitrarily.

## Word and speaker alignment

ASR and diarization may produce timelines at different granularities. Align words or segments to speaker intervals, and define a rule for boundaries or overlapping regions. Media timestamps matter: using event arrival time can shift attribution when network or inference delays differ.

For “A: yes” followed quickly by “B: no,” a 300 ms timing shift can attach the wrong consent to the wrong speaker. Do not authorize a write from inferred speaker attribution alone.

## Evaluation

Diarization error rate commonly combines missed speech, false-alarm speech, and speaker confusion relative to reference speaker time. Reporting depends on scoring rules, boundary collars, and treatment of overlap. State those choices so two scores can be compared meaningfully.

Also measure speaker-attributed entity accuracy and downstream task success. An agent can have a reasonable diarization score but still misattribute the one sentence that matters.

## Understanding beyond words

Pauses, interruptions, backchannels, turn exchanges, and overlap reveal interaction structure. Some applications need to know whether someone is asking the assistant or talking to another person. Use explicit product policies and evidence; do not infer consent or private intent merely from presence in a recording.

The supplied [Beyond Transcription study guide](../resources/beyond-transcription.md) belongs here. It provides viewing prompts and exercises; it is not a verified transcript summary of the talk.

## Check your understanding

1. Why is “speaker 1” not an authenticated account?
2. How can overlap require a different annotation model?
3. Why must DER scoring assumptions be reported?

Continue with [multimodal co-pilots](18-multimodal-and-conversational-copilots.md). [Lab 10](../labs/10-speakers-and-copilot.md). Reference implementation: [pyannote.audio](https://github.com/pyannote/pyannote-audio).
