# Study guide: The Voice-First AI Overlay

**Resource:** [The Voice-First AI Overlay: Designing Conversational Co-Pilots - Gregory Bruss](https://www.youtube.com/watch?v=y9YQc9a3gNw), published on the AI Engineer channel.

Title/channel metadata was verified via YouTube oEmbed on 2026-10-01. The talk was not transcribed or viewed during authoring. These prompts are course-authored; they are not a verified summary of the talk.

## Prepare

Read [multimodal agents and co-pilots](../chapters/18-multimodal-and-conversational-copilots.md). Describe the difference between a directly addressed assistant and an observer offering contextual help.

## Questions to investigate while watching

1. What user problem motivates the overlay?
2. Who is the assistant serving in a multi-person interaction?
3. Which interaction channels are used for assistance, if demonstrated?
4. How is intervention timing controlled or evaluated, if discussed?
5. Which privacy, distraction, or stale-context tradeoffs are surfaced?

Record timestamps for actual examples. Distinguish demonstrations, measured results, design hypotheses, and your own interpretation. Mark topics the talk does not address as open questions.

## Apply it

Write an intervention policy with actions `stay_silent`, `show_private_note`, `wait_for_pause`, and `speak_on_request`. Add freshness checks, cooldown, deduplication, and dismissal. Test it on a scripted conversation with useful moments and moments where silence is best.

Compare against a no-assistance baseline. Evaluate unwanted interventions and late suggestions alongside information accuracy. A technically correct note can still distract or embarrass a participant.

## Notes template

Record timestamp, observed design choice, evidence, tradeoff, and possible implementation. Label untested implementation ideas as hypotheses.

## Discussion

What evidence would convince you that an overlay improves the conversation rather than simply adding more generated content? Which participants should control recording, memory, and visibility?

[Resource index](README.md) · [Lab 10](../labs/10-speakers-and-copilot.md)
