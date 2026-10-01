# 14. RAG, conversation context, and durable memory

**Prerequisites:** chapters 4 and 12–13. **Goal:** retrieve grounded evidence while keeping knowledge, conversation state, and personal memory distinct.

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

## Check your understanding

1. Why should knowledge and personal memory use different retention rules?
2. Where must document access be enforced?
3. Why can summaries lose essential conversational state?

Continue with [transport](15-webrtc-and-websocket.md). [Lab 8](../labs/08-rag-and-memory.md). Further reading: [RAG research](https://arxiv.org/abs/2005.11401).
