# 14. RAG, conversation context, and durable memory

**Prerequisites:** chapters 4 and 12–13. **Goal:** retrieve grounded evidence while keeping knowledge, conversation state, and personal memory distinct.

<!-- chapter-navigation:start -->
**In this chapter**

- [Three stores with different purposes](#three-stores-with-different-purposes)
- [Retrieval internals](#retrieval-internals)
- [Access control before generation](#access-control-before-generation)
- [Grounding in a spoken channel](#grounding-in-a-spoken-channel)
- [Memory internals](#memory-internals)
- [Speculative retrieval and workflows](#speculative-retrieval-and-workflows)
- [Work through retrieval as a measurable pipeline](#work-through-retrieval-as-a-measurable-pipeline)
- [Calculate a similarity score and understand its limits](#calculate-a-similarity-score-and-understand-its-limits)
- [Separate topical relevance from authoritative selection](#separate-topical-relevance-from-authoritative-selection)
- [Evaluate retrieval and generation separately](#evaluate-retrieval-and-generation-separately)
- [Define a durable memory record](#define-a-durable-memory-record)
- [Manage summaries as lossy indexes](#manage-summaries-as-lossy-indexes)
- [Debugging drill](#debugging-drill)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## Three stores with different purposes

Conversation context is what the model can see for the current exchange. Knowledge is external information such as product documentation. Memory is retained information about a user or prior interaction. A database can contain all three, but their meaning and retention rules differ.

“I prefer morning appointments” might become a user preference. “Our office opens at nine” belongs in organizational knowledge. “The agent has not yet confirmed the slot” is workflow state. Converting every transcript into permanent memory mixes facts, guesses, and incomplete operations.

## Retrieval internals

A RAG pipeline ingests documents, extracts text and structure, divides it into passages, attaches metadata and access scope, and indexes it. At query time, it finds candidates, optionally reranks them, selects evidence, and supplies that evidence to generation.

Dense retrieval compares learned vector representations. Lexical search matches terms and can be strong for exact identifiers. Hybrid retrieval combines signals. Vector similarity is not a probability that an answer is true.

Chunking changes what can be retrieved. Tiny passages may omit conditions and exceptions. Large passages can bury the relevant sentence and consume context. Preserve headings, document versions, effective dates, and references so retrieved evidence can be interpreted correctly.

## Access control before generation

Filter candidates by the caller's allowed scope before presenting evidence to the model. Asking the model to ignore unauthorized passages is weaker than preventing their retrieval. Cache keys also need tenant and access scope; otherwise a correct initial retrieval can leak through a shared cache.

External documents can contain prompt injection. Treat them as evidence, not instructions to change tools or reveal secrets. Do not let a retrieved passage authorize a write.

## Grounding in a spoken channel

A spoken answer should be concise but preserve qualifications. If the relevant policy says “refunds within 30 days except customized items,” omitting the exception changes the answer.

Use evidence citations in a companion UI or written summary where practical; speak an understandable attribution rather than a long URL. If evidence is missing, stale, or conflicting, say so and offer escalation. Do not force a confident response from weak retrieval.

Evaluate retrieval recall and final answer faithfulness separately. A correct passage retrieved but ignored is a generation problem; no correct passage in candidates is a retrieval problem. ASR can corrupt the retrieval query, especially names and product codes, so test the entire audio path.

## Memory internals

A memory write should identify the subject, assertion, provenance, confidence or verification status, scope, timestamp, and expiry where needed. Distinguish “user stated” from “application verified.” Maintain correction and deletion paths.

Summaries compress context but can lose negation, speaker identity, uncertainty, or delivery state. Keep structured fields for critical workflow facts rather than relying solely on prose summaries. Never treat an interrupted assistant sentence as an accepted user preference.

A durable memory retrieval also needs authentication and tenant scope. Speaker diarization labels alone cannot determine which account to load.

## Speculative retrieval and workflows

Read-only retrieval can begin from a stable partial transcript to reduce delay. When the query changes, invalidate or rerun it. Label speculative results so they do not become permanent memory or authorize an action before turn commitment.

Multi-agent handoffs need a compact state package: user intent, allowed scope, known facts, unresolved questions, pending operations, and spoken-delivery status. Passing the entire transcript can increase latency and expose unnecessary data.

## Work through retrieval as a measurable pipeline

Create three synthetic documents: current shop hours, an old hours policy, and a refund policy containing an exception for customized repairs. Each passage needs document ID, version/effective time, section, tenant/access scope, and source location.

At ingestion, extract meaningful structure. A PDF footer repeated on every page is not useful evidence. A table may need headers attached to each row to preserve meaning. Chunk boundaries should follow content where possible, and overlap should be deliberate rather than duplicating every passage arbitrarily.

At query time, normalize the user's request without erasing important names or negation. Retrieve candidates within authorized scope, rerank if appropriate, select evidence within a context budget, and generate a response that preserves conditions.

## Calculate a similarity score and understand its limits

For vectors `q` and `d`, cosine similarity is:

```text
cosine(q, d) = dot(q, d) / (norm(q) × norm(d))
```

Take `q = [1, 0]`, document A `=[0.9, 0.1]`, and document B `=[0, 1]`. A has cosine about 0.9939 and B has zero. This demonstrates geometric proximity, not factual truth. A wrong but topically similar outdated passage can rank highly.

The actual embedding space is learned and high-dimensional. The toy's coordinates are not representations from a real model. Use it to understand scoring, then inspect real retrieval results rather than interpreting score 0.9 as “90% correct.”

Lexical search can handle exact product codes that embeddings blur. Hybrid ranking can combine lexical and dense candidate lists. One simple fusion rule sums `1 / (k + rank)` from each list. Its ranks are not probabilities; `k` controls how strongly top ranks dominate. Reranking can compare query/passage relevance more directly but adds latency and still does not replace version or access validation.

## Separate topical relevance from authoritative selection

Both current and old shop-hour documents can be relevant to “When do you open?” Metadata should let the application prefer the applicable version. If a migration policy has future effective dates, blindly choosing the newest ingestion timestamp is also wrong.

Define authority rules for the domain: effective period, document status, source trust, and unresolved contradictions. An LLM can help explain selected evidence, but your retrieval pipeline should not leave every access and version decision to model intuition.

Retrieval is not always a vector database problem. For a small shop catalog, SQL or a direct lookup can be more reliable. Use model-assisted interpretation to derive a validated query, then fetch exact structured fields where possible.

## Evaluate retrieval and generation separately

For each test query, annotate which passages contain the answer and exceptions. Recall@k measures whether relevant evidence appears among candidates. Precision-oriented measures ask whether selected passages are relevant. Answer faithfulness asks whether generated claims follow the evidence.

Suppose retrieval finds the refund exception but the spoken response says “all repairs are refundable.” Retrieval succeeded; generation or response compression failed. Suppose only the old hours document is retrieved; authority-aware selection failed upstream. Different fixes are needed.

Evaluate the audio path too. “Model X-15” misrecognized as “model X-50” can retrieve a perfectly relevant answer to the wrong query. Entity clarification may improve outcomes more than changing the index.

## Define a durable memory record

An illustrative preference record is:

```json
{
  "subject": "authenticated-customer-42",
  "scope": "repair-shop-A",
  "fact_type": "appointment_preference",
  "value": "morning",
  "provenance": "user_stated",
  "source_turn": "session-A:7",
  "status": "active",
  "version": 2
}
```

This is an application schema, not an upstream memory product format. Keep timestamps and retention metadata appropriate to the policy. A correction updates or supersedes the earlier assertion; a deletion workflow removes/invalidates derived copies as required.

Do not store “prefers morning” because the assistant suggested it or because another speaker said it. Memory writes require subject attribution and appropriate permission. The source turn and provenance make later correction understandable.

## Manage summaries as lossy indexes

A summary can be a useful shortcut to a long conversation, but critical fields should remain structured. “The customer booked Saturday” omits whether the booking succeeded, whether the customer confirmed, and whether confirmation was heard.

Keep workflow state and the authoritative operation ledger separate. Let a summary point to them rather than become their replacement. Mark uncertainty, speaker attribution, and interrupted delivery when compressing dialogue.

## Debugging drill

Ask the same synthetic query as two tenants, with a warm cache, before and after a policy-version change. Verify access scope, cache key, selected version, and final answer. Then correct and delete a preference and inspect memory retrieval plus derived summaries. This exposes failures hidden by a successful cold-cache demo.

## Check your understanding

1. Why should knowledge and personal memory use different retention rules?
2. Where must document access be enforced?
3. Why can summaries lose essential conversational state?

Continue with [transport](15-webrtc-and-websocket.md). [Lab 8](../labs/08-rag-and-memory.md). Further reading: [RAG research](https://arxiv.org/abs/2005.11401).
