# 4. LLM internals and their effect on voice

**Prerequisites:** chapters 1–3. **Goal:** connect tokenization, attention, inference, and context construction to audible behavior.

<!-- chapter-navigation:start -->
**In this chapter**

- [What an LLM computes](#what-an-llm-computes)
- [Prefill, decode, and cache](#prefill-decode-and-cache)
- [Context is assembled by the application](#context-is-assembled-by-the-application)
- [Generation is a proposal](#generation-is-a-proposal)
- [Spoken response design](#spoken-response-design)
- [Exercise](#exercise)
- [Walk one token through a decoder](#walk-one-token-through-a-decoder)
- [Training versus inference](#training-versus-inference)
- [Estimate KV memory and explain the consequence](#estimate-kv-memory-and-explain-the-consequence)
- [From logits to decoding behavior](#from-logits-to-decoding-behavior)
- [Debug the audible path, not only the token path](#debug-the-audible-path-not-only-the-token-path)
- [Inspect the layer shapes and training objective](#inspect-the-layer-shapes-and-training-objective)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Walk one token through a decoder

Suppose the visible context ends with “The next appointment is”. Tokenization converts that string into integer IDs according to the model's vocabulary. The IDs index an embedding table, producing one vector per position. These vectors are learned representations, not dictionaries containing the meaning of a word.

Within an attention layer, learned projections generate queries, keys, and values. For one attention head, if there are `T` positions and head width `d`, Q, K, and V each commonly have shape `T × d`. Multiplying `QKᵀ` yields a `T × T` matrix: one row describes how a position scores the available positions.

Divide by `sqrt(d)` to control score scale, apply the causal mask, and apply softmax over each row. A weighted sum of value vectors produces the head output. Several heads can represent different relationships, and their outputs are combined through a learned projection. Residual paths and normalization help information flow through many layers; feed-forward sublayers transform each position's representation further.

After the final layer, the current position is projected into vocabulary scores called logits. A decoding policy chooses the next token. The token might be “ Saturday” or merely a subword fragment. The application receives text only after the tokenizer maps IDs back into text. This explains why raw token boundaries do not reliably match word or sentence boundaries.

### Calculate a toy attention result

Assume one query gives scaled scores `[2, 0]` against two previous positions. Softmax gives approximately `[0.8808, 0.1192]`. If their value vectors are `[10, 0]` and `[0, 10]`, the output is approximately `[8.808, 1.192]`. The query selects a mixture; it does not copy an entire sentence or verify that either value represents a true fact.

This standard-library program computes that example:

```python
import math

def softmax(scores):
    largest = max(scores)
    weights = [math.exp(score - largest) for score in scores]
    total = sum(weights)
    return [weight / total for weight in weights]

weights = softmax([2.0, 0.0])
values = [[10.0, 0.0], [0.0, 10.0]]
output = [sum(w * v[column] for w, v in zip(weights, values))
          for column in range(2)]
print(weights)
print(output)
```

Subtracting the largest score avoids unnecessarily large exponentials without changing the normalized probabilities. This is a numeric-stability trick, not a different attention mechanism. The toy does not implement embeddings, training, multiple heads, or a language model. For an implementation-oriented companion, inspect the [PyTorch scaled-attention tutorial](https://docs.pytorch.org/tutorials/intermediate/scaled_dot_product_attention_tutorial.html).

## Training versus inference

During autoregressive training, a model can receive a sequence and predict the next token at each eligible position. A loss penalizes low probability on target tokens, and gradient-based optimization updates parameters. The causal mask permits many positions to be processed together without leaking future targets.

At inference, there is no known next token for the application to supply. The system generates one, appends it, and generates another. Instruction tuning and preference-oriented training can change behavior, but they do not create a database transaction or an authorization system. The model still produces proposals based on its learned distribution and supplied context.

Distinguish facts embedded imperfectly in learned weights from current facts returned by tools. A model's apparent knowledge of shop hours may be stale. Retrieve the authoritative policy when freshness matters, and tell the model which evidence is current.

## Estimate KV memory and explain the consequence

For a simplified decoder, approximate KV-cache bytes per sequence as:

```text
2 × layers × cached_tokens × kv_heads × head_dimension × bytes_per_element
```

The factor of two represents keys and values. With illustrative values of 32 layers, 4,096 cached tokens, 8 KV heads, width 128, and two-byte elements, this gives 536,870,912 bytes, or 512 MiB. This excludes model weights, allocator overhead, attention workspaces, batching, and other state. Actual architectures can use different head sharing, compression, and precision.

The calculation makes a design issue visible: conversation length can consume substantial per-session memory even when model weights are shared. If ten sessions each retain large contexts, they do not necessarily have the same resource footprint as ten short questions.

Prefix caching can avoid recomputing an identical reusable prefix in systems that support it. It does not automatically cache arbitrary paraphrases or repair changed context. Measure cache behavior with the actual runtime rather than assuming every repeated system prompt is free.

## From logits to decoding behavior

Greedy decoding chooses the highest-scoring next token. Sampling chooses from a distribution, sometimes transformed by temperature or truncated by top-k/top-p policies. Lower temperature generally concentrates the distribution; it does not guarantee correctness. If the highest-probability completion is an incorrect date, making it more deterministic can make the error repeat consistently.

Constrained decoding can restrict output to syntactically valid structures. That is useful for tool arguments, but application validation must still determine whether a requested slot exists, whether the caller can book it, and whether intent was confirmed.

## Debug the audible path, not only the token path

Imagine first token at 150 ms, a complete speakable clause at 800 ms, synthesized audio at 1,000 ms, and client playback at 1,200 ms after turn commitment. Optimizing first token from 150 to 100 ms may change little if the clause boundary remains at 800 ms.

Inspect exactly which tokens enter the speakable channel. A tool-call argument stream such as `{"slot":...}` should be assembled for validation, not spoken. A model can emit a status clause before a tool result; the controller must ensure the clause does not falsely claim success. Route by semantic output type, not “whatever text arrived most recently.”

## Inspect the layer shapes and training objective

The attention result still needs to become a representation the next layer can use. With model width `d_model`, a position-wise feed-forward block commonly expands each vector to a larger intermediate width, applies a nonlinear function, then projects back. A simplified form is:

```text
FFN(x) = activation(x W1 + b1) W2 + b2
x:     [T, d_model]
W1:    [d_model, d_ff]
W2:    [d_ff, d_model]
output:[T, d_model]
```

Attention mixes information across positions; this feed-forward block transforms features at each position. Modern models can use gated activations, experts, different normalization placement, and other variants. The shape accounting still helps distinguish sequence mixing from feature transformation.

For next-token training, if the correct target token has probability `p`, its negative log-likelihood contribution is `−ln(p)`. Probability 0.8 gives about 0.223; probability 0.1 gives about 2.303. The optimizer is penalized more strongly for assigning little probability to the observed target. This objective trains prediction, not direct factual verification.

A fluent prediction can therefore be well formed while unsupported. Fine-tuning can reward desired response behavior, but a calendar state change still requires an actual calendar operation. Keep the model's optimization objective conceptually separate from the application's success condition.

### Exercise with an expected explanation

If an attention matrix has shape `100 × 100`, increasing context to 200 positions makes the naive score matrix `200 × 200`: four times as many entries. That does not mean every optimized implementation uses four times the memory or takes exactly four times the time. Fused kernels, cache reuse, attention variants, and scheduling change realized behavior.

When evaluating long-context voice sessions, report actual cache/resource growth and first-response latency. Use the shape derivation to form hypotheses, then measure the chosen runtime. Avoid promising a performance ratio from algebra alone.

## Check your understanding

1. How do prefill and decode affect latency differently?
2. Why does valid JSON not guarantee a valid booking?
3. Why should retrieved text remain separate from application policy?

Continue with [STT](05-stt-internals.md). [Lab 3](../labs/03-first-cascade.md). Further reading: [Attention Is All You Need](https://arxiv.org/abs/1706.03762).
