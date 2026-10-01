# 17. Diarization, overlap, and conversational understanding

**Prerequisites:** chapters 5, 7–8. **Goal:** preserve who spoke when without treating acoustic clusters as authenticated people.

<!-- chapter-navigation:start -->
**In this chapter**

- [Transcription answers only part of the question](#transcription-answers-only-part-of-the-question)
- [A common diarization pipeline](#a-common-diarization-pipeline)
- [Overlapping speech](#overlapping-speech)
- [Word and speaker alignment](#word-and-speaker-alignment)
- [Evaluation](#evaluation)
- [Understanding beyond words](#understanding-beyond-words)
- [Trace a two-person conversation through attribution](#trace-a-two-person-conversation-through-attribution)
- [Understand speaker embeddings and clustering](#understand-speaker-embeddings-and-clustering)
- [Speaker-label permutation in evaluation](#speaker-label-permutation-in-evaluation)
- [Compute a simple DER example](#compute-a-simple-der-example)
- [Align text to speaker time carefully](#align-text-to-speaker-time-carefully)
- [Turn structure and conversational intent](#turn-structure-and-conversational-intent)
- [Debugging drill](#debugging-drill)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Trace a two-person conversation through attribution

Create this synthetic timeline:

| Media interval | Actual activity | Words |
| --- | --- | --- |
| 0–1.5 s | A | “I prefer morning appointments.” |
| 1.7–3.0 s | B | “Evenings work better for me.” |
| 2.8–3.2 s | A and B | Overlap: A starts “Except Friday” while B finishes |
| 3.3–4.0 s | A | “Friday afternoon is fine.” |

A diarization pipeline first identifies speech intervals, then derives speaker evidence, assigns labels, and refines the timeline. Recognition supplies words or text segments. The application aligns the two without erasing overlap.

If a whole 2.8–3.2 s interval is labeled only B, A's exception may be misattributed. If the transcript has one merged sentence, correct speaker activity alone cannot recover every word assignment. Preserve uncertainty at the boundary rather than claiming an exact preference history.

## Understand speaker embeddings and clustering

A speaker embedding is a learned representation intended to capture voice-related characteristics from an audio region. Comparing embeddings can help group speech from the same source. It is not a guaranteed biometric identity and can be affected by channel, noise, emotion, and duration.

Short regions contain less evidence. A 100 ms “yes” may not support the same speaker distinction as several seconds of clean speech. Longer windows improve available context but can straddle speaker changes or delay online decisions.

Clustering groups embeddings according to a distance rule and a policy about the number of speakers. A threshold that merges similar voices can collapse A and B; one that splits too aggressively can assign several labels to A. Threshold tuning should use representative held-out recordings, not one easy example.

Online assignment can update clusters as evidence arrives. Decide how label revisions affect already stored transcripts and memory. An early `speaker_2` label becoming `speaker_1` later should not silently leave permanent preferences attached to an obsolete label.

## Speaker-label permutation in evaluation

Reference labels A/B and predicted labels 1/2 are arbitrary names. If prediction 1 consistently matches B and prediction 2 consistently matches A, the system has not necessarily confused the speakers. Evaluation first finds an appropriate mapping, then measures temporal error under its scoring policy.

Without that mapping, a perfect but differently named result can appear completely wrong. Conversely, if label 1 alternates between A and B, one global mapping cannot repair the confusion.

## Compute a simple DER example

Assume the reference has 10 seconds of scored speaker time, with no overlap in this toy case. The system misses 1 second, invents 0.5 seconds of speech, and assigns 1 second to the wrong speaker. A simplified DER is `(1 + 0.5 + 1) / 10 = 25%`.

The denominator and scoring become more nuanced with overlap and boundary collars. State whether overlapped regions are included, how near-boundary errors are treated, and which reference conventions you use. A collar can exclude uncertain boundary neighborhoods; changing it can change the score without changing system output.

Now consider downstream impact. If the one second of speaker confusion contains consent to a booking, a 25% or even much lower aggregate error rate says little about authorization correctness. Evaluate attributed entities, preferences, and intent separately. Actual identity/permissions remain independent of diarization.

## Align text to speaker time carefully

If ASR gives word times, intersect those intervals with speaker activity and define rules for ambiguous overlaps. If it gives only segment times, a long segment crossing several turns cannot be assigned to one speaker without further evidence.

Do not use callback arrival time for alignment. Recognition may finish after a segment ends, and diarization may revise labels later. Both should refer to a shared media timeline. Account for preprocessing that changes timing, such as trimmed silence or resampler delay.

For archival analysis, you may revise annotations retrospectively. For live assistance, the controller may have acted before revisions were available. Evaluate what was knowable at decision time, not only the final offline transcript.

## Turn structure and conversational intent

Speaker alternation, pause duration, interruptions, and acknowledgements can help characterize interaction. They still do not reveal every intention. “Sure” can be agreement, sarcasm, or a backchannel depending on context.

A co-pilot should combine acoustic/linguistic evidence with an explicit intervention policy. A booking workflow should bind consent to a current proposal and authorized user. Do not treat a diarized affirmative word as a generic approval signal.

## Debugging drill

Compare one-speaker summaries, speaker-attributed summaries, and structured preference records on the synthetic timeline. Deliberately shift word timing by 300 ms and observe boundary mistakes. Then permute label names without changing assignments and verify your evaluator does not report false confusion.

## Check your understanding

1. Why is “speaker 1” not an authenticated account?
2. How can overlap require a different annotation model?
3. Why must DER scoring assumptions be reported?

Continue with [multimodal co-pilots](18-multimodal-and-conversational-copilots.md). [Lab 10](../labs/10-speakers-and-copilot.md). Reference implementation: [pyannote.audio](https://github.com/pyannote/pyannote-audio).
