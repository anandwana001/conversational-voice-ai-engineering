# 18. Multimodal agents and conversational co-pilots

**Prerequisites:** chapters 9–10 and 17. **Goal:** decide when an assistant should intervene and bind evidence to the moment it describes.

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

## Check your understanding

1. Why is correct content insufficient for a good intervention?
2. Which frame should accompany a time-dependent reference like “this one”?
3. What must stop when an animated assistant is interrupted?

Continue with [latency](19-latency-and-observability.md). [Lab 10](../labs/10-speakers-and-copilot.md).
