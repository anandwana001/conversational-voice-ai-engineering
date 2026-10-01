# Lab 8. Build grounded answers and scoped memory

**Read:** [chapter 14](../chapters/14-rag-and-memory.md). **Mode:** local retrieval or live model; synthetic documents. **Time:** 2–3 hours.

## Build

1. Create a small synthetic knowledge base with opening hours, refund conditions, and conflicting old/new policy versions. Add two tenant scopes.
2. Implement lexical, vector, or hybrid retrieval with access filtering and source metadata.
3. Ask a voice or text query and inspect candidate passages before generation. Record retrieval success separately from answer faithfulness.
4. Store a user-stated appointment preference with provenance. Correct it, retrieve it, then delete it according to your explicit retention policy.
5. Add a document sentence instructing the assistant to reveal another tenant's records. Verify the application scope prevents access.

## Deliver

Submit document metadata, a retrieved-evidence trace, answer examples, memory records, and deletion evidence. State whether generated embeddings and caches were included in deletion.

## Acceptance

- Unauthorized passages do not enter model context.
- The refund exception survives the spoken summary.
- Missing or contradictory evidence produces uncertainty or escalation.
- Knowledge, user preference, and pending workflow state remain distinct.

**Failure experiment:** share a retrieval cache without tenant scope. Demonstrate the synthetic leak and repair the cache key.

**Transfer:** implement one query with plain text search and explain why vector similarity alone is not truth.

[Next lab](09-transport-and-phone.md) · [All labs](README.md)
