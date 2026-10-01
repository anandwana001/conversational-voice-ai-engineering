# 18. Multimodal agents and conversational co-pilots

**Prerequisites:** chapters 9–10 and 17. **Goal:** decide when an assistant should intervene and bind evidence to the moment it describes.

<!-- chapter-navigation:start -->
**In this chapter**

- [A co-pilot is not always the next speaker](#a-co-pilot-is-not-always-the-next-speaker)
- [An intervention policy](#an-intervention-policy)
- [Audio and visual evidence](#audio-and-visual-evidence)
- [Visual processing internally](#visual-processing-internally)
- [Avatar and lip-sync output](#avatar-and-lip-sync-output)
- [Conversational context and consent](#conversational-context-and-consent)
- [Experiment](#experiment)
- [Build an intervention pipeline with a private proposal stage](#build-an-intervention-pipeline-with-a-private-proposal-stage)
- [Express delivery eligibility as testable rules](#express-delivery-eligibility-as-testable-rules)
- [Synchronize a deictic reference with visual evidence](#synchronize-a-deictic-reference-with-visual-evidence)
- [Understand image representations and sampling costs](#understand-image-representations-and-sampling-costs)
- [Define usefulness and timing evaluation separately](#define-usefulness-and-timing-evaluation-separately)
- [Coordinate animated output with the device timeline](#coordinate-animated-output-with-the-device-timeline)
- [Debugging drill](#debugging-drill)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## A co-pilot is not always the next speaker

A dyadic voice agent exchanges turns directly with a user. A conversational co-pilot may observe a human conversation and offer assistance at an appropriate moment. The central problem changes from “answer every turn” to “decide whether, when, and through which channel assistance is useful.”

An accurate suggestion can still be harmful if it interrupts a sensitive exchange or arrives after the decision is made. Evaluate intervention timing, frequency, usefulness, and perceived intrusiveness as separate qualities.

## An intervention policy

Separate observation, candidate generation, eligibility, and delivery. A model can propose a helpful note while a controller checks whether the context is fresh, the interaction permits intervention, the note duplicates an earlier one, and the chosen channel is appropriate.

Possible actions include staying silent, displaying a private suggestion, waiting for a pause, or speaking after an explicit request. A confidence score alone does not encode all these product choices.

Use cooldowns and deduplication to avoid repeated suggestions. Let users dismiss, mute, and correct assistance. Suppressing a note should not require starting a new session.

## Audio and visual evidence

Multimodal input can combine speech, camera frames, screen context, images, and structured application events. Each has its own timing, permissions, bandwidth, and semantic scope.

If a user says “this one” while pointing to an object, the relevant video frame is the one near the utterance, not necessarily the newest frame when inference finishes. Attach capture timestamps and source identity, select a bounded context window, and mark stale evidence.

Screens can change while tools run. A suggestion based on an earlier document must identify its source and freshness. Revalidate before performing an action against a changed application state.

## Visual processing internally

A vision encoder can transform patches or regions into representations that a multimodal model combines with text or audio. Exact architectures vary. Image resolution, sampling frequency, and number of frames affect cost and delay.

Uploading every video frame is rarely a necessary default. Sample based on the task, scene change, explicit requests, or event triggers. Preserve useful metadata and avoid collecting visual content unrelated to assistance.

## Avatar and lip-sync output

An avatar animation must align with audio playback, not only synthesis callbacks. Animation arriving before sound or continuing after an interruption breaks the experience.

Map animation timestamps to the playback timeline. Cancel both obsolete speech and motion on barge-in. If audio buffering changes, adjust alignment or degrade gracefully to simpler animation. A polished avatar does not compensate for incorrect tool state or poor turn handling.

## Conversational context and consent

A multi-person conversation may contain private statements from people who did not request assistance. Define capture permissions, visibility, retention, and speaker scope explicitly. Never equate being in microphone range with authorizing account access or memory retention.

Separate model suggestions from final product decisions. A co-pilot should explain why a suggestion is relevant when helpful, and admit missing or ambiguous evidence.

## Experiment

Create a recorded or scripted conversation with five potential assistance moments and five situations where silence is preferable. Annotate useful windows before running the system. Measure false interventions, missed opportunities, delay, and participant ratings. Always compare with a no-assistance baseline.

The supplied [Voice-First AI Overlay guide](../resources/voice-first-overlay.md) provides complementary viewing questions without asserting unverified details from the talk.

## Build an intervention pipeline with a private proposal stage

The co-pilot receives observations but should not speak every generated suggestion. Use four stages: capture eligible context, generate a candidate, evaluate delivery policy, and deliver or discard. Candidate generation can run asynchronously while humans continue speaking; policy evaluates again when the candidate is ready.

A candidate record should include its evidence references, capture time, relevant participants, topic, suggested action, generation ID, expiry, and visibility scope. Do not store only its text. Without evidence/time metadata, the policy cannot know that a formerly useful suggestion is stale.

For example, the model proposes, “Ask whether the repair is under warranty.” During the 800 ms generation interval, the human already asks that question. The suggestion is now redundant. Revalidation at delivery time should suppress it, even if it was useful when generated.

## Express delivery eligibility as testable rules

An illustrative policy might require explicit assistance permission, fresh evidence, no duplicate suggestion, an eligible channel, and an appropriate conversational window. These are product choices, not universal rules:

```text
deliver(candidate, current_context):
    if permission no longer valid: discard
    if candidate expired: discard
    if source topic changed: discard or regenerate
    if equivalent help was already given: discard
    if user muted or dismissed this category: discard
    if speaking would interrupt an ineligible moment: wait within expiry
    otherwise: deliver through allowed channel
```

The model can estimate relevance or urgency. The controller enforces permissions, expiry, deduplication, and channel constraints. A high model confidence score does not override a mute setting or make an expired screen reference current.

## Synchronize a deictic reference with visual evidence

The user says “What about this one?” at media time 12.0 s while pointing at part A. The camera captures frames at 11.8, 12.0, and 12.2 s. By 13.0 s, the camera points at part B. If inference uses only the newest frame at 13.0 s, it can answer about B instead of A.

Select evidence near the utterance's media interval, with an appropriate context window and known capture offsets. Track whether audio and video clocks share an origin or require synchronization. Network arrival time is not capture time.

If the visual evidence is ambiguous or missing, ask which object rather than inventing a binding. If a tool action depends on the selected object, revalidate the object/state before executing, because the interface can change while the model reasons.

## Understand image representations and sampling costs

A vision frontend can divide an image into patches or regions and encode them into learned vectors. A multimodal model combines these with other context. Resolution and cropping change which details survive: a small serial number may disappear when the whole frame is downscaled.

Choosing more frames increases information but also computation, context, bandwidth, and privacy exposure. Sample according to the task. A static document may need one high-quality capture; moving gestures may need a short temporal sequence; a co-pilot observing a conversation may not need visual input at all.

Record the actual evidence supplied to the model. Debugging a wrong visual answer from an unlogged “camera enabled” flag is difficult because you cannot know what the model saw.

## Define usefulness and timing evaluation separately

Annotate an assistance opportunity with a useful delivery window, not just a topic label. A note delivered after a decision is complete can be correct but ineffective. A note delivered during a sensitive sentence can be disruptive.

Measure offered suggestions, accepted suggestions, unnecessary interventions, missed opportunities, delivery delay, and participant feedback. An acceptance click is imperfect evidence: users can accept out of politeness or reject a useful note because it arrived too late.

Compare a no-assistance baseline and, where practical, randomize order across comparable tasks. Distinguish improved task outcome from participants merely reporting that the interface is novel or engaging.

## Coordinate animated output with the device timeline

Synthesis events describe generated audio; animation should track played audio. If audio is buffered for 300 ms, immediate mouth motion leads sound. Attach viseme or motion timing to a response item and media position, then schedule against actual playout progress where supported.

On interruption, invalidate motion and audio together. A late animation callback for generation 12 should not affect generation 13. If accurate lip synchronization fails, degrade to simpler motion rather than maintaining confidently incorrect timing.

## Debugging drill

Create candidates that become stale while generation runs: a question already asked, a camera object replaced, a dismissed suggestion category, and an interrupted spoken hint. Verify the policy rejects them at delivery. Then compare a correct timely suggestion with a correct late one in the evaluation rubric. Content correctness is only one column.

## Check your understanding

1. Why is correct content insufficient for a good intervention?
2. Which frame should accompany a time-dependent reference like “this one”?
3. What must stop when an animated assistant is interrupted?

Continue with [latency](19-latency-and-observability.md). [Lab 10](../labs/10-speakers-and-copilot.md).
