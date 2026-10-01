# 4. LLM internals and their effect on voice

**Prerequisites:** chapters 1–3. **Goal:** connect tokenization, attention, inference, and context construction to audible behavior.

## What an LLM computes

A language model estimates probabilities for token sequences. A token can represent a word, part of a word, punctuation, or another encoded unit. Tokenization is not the same as splitting on spaces, and token counts differ across languages and tokenizers.

In a common autoregressive transformer, input tokens become vectors. Layers mix information through attention and nonlinear transformations. A final projection produces next-token scores; a decoding policy chooses a token and repeats. This describes a common family, not every language or multimodal model.

The basic attention operation is:

```text
Attention(Q, K, V) = softmax(QKᵀ / sqrt(d_k)) V
```

Queries and keys determine how positions relate; values supply information to combine. Causal masking prevents a decoder position from reading future tokens. Position information helps distinguish order. Attention does not establish that a statement is true: it transforms representations of available context.

## Prefill, decode, and cache

Prefill processes the existing context before generation. Decode repeatedly adds tokens. Many implementations cache previous key/value tensors so each new step need not recompute all earlier representations. The cache consumes memory and depends on exact model and runtime behavior.

A longer prompt can increase time to first token, and longer output increases total generation time. Caching, batching, hardware, concurrency, and provider scheduling alter the relationship. Measure first-token time and token cadence separately; one number cannot describe both.

For voice, first token is not first sound. “The” can arrive quickly while a sentence segmenter waits for “next available appointment is Saturday at two.” A prompt that produces a long introductory clause can add apparent delay even if model throughput is strong.

## Context is assembled by the application

Typical context includes system policy, tool descriptions, user turns, tool results, retrieved passages, and selected memory. Every addition competes for space and attention. More history is not automatically better: stale instructions, repeated retrieval, and conflicting summaries can weaken behavior.

Preserve the difference between user speech and external evidence. A retrieved page saying “ignore earlier instructions” is content from a document, not an instruction from the application. A tool result should carry provenance and structured success or failure, not masquerade as a user request.

## Generation is a proposal

A model may generate fluent falsehoods or propose invalid tool arguments. Lower temperature can reduce sampling variation, but it does not make facts correct or grant permission. Structured-output constraints can enforce syntax; they cannot guarantee that “Saturday” refers to the intended date or that the caller owns the account.

For spoken booking, convert relative dates using a known timezone, check business rules, ask for missing fields, and confirm consequential actions. Keep this deterministic validation outside the model.

## Spoken response design

Ask for one actionable idea at a time. Speak dates and numbers clearly, avoid reading raw JSON or Markdown, and provide brief status messages only when they are true. “I found a slot” and “I booked the slot” reflect different tool outcomes.

Split private reasoning, application events, and speakable response content. Do not send every model stream event into TTS. Some events are partial tool arguments or control metadata. The controller should route by event type.

## Exercise

Build three prompt variants for a receptionist: verbose, concise, and concise with explicit confirmation policy. Measure time to first token, time to first speakable clause, output length, and task success. A concise wrong answer is not an improvement.

## Check your understanding

1. How do prefill and decode affect latency differently?
2. Why does valid JSON not guarantee a valid booking?
3. Why should retrieved text remain separate from application policy?

Continue with [STT](05-stt-internals.md). [Lab 3](../labs/03-first-cascade.md). Further reading: [Attention Is All You Need](https://arxiv.org/abs/1706.03762).
