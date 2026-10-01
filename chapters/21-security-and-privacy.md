# 21. Security, privacy, and application trust boundaries

**Prerequisites:** chapters 12–18. **Goal:** protect account data and actions without delegating authorization to a model.

## Draw the trust boundaries

Microphone input, recognized text, retrieved documents, tool descriptions, browser requests, and caller metadata are external inputs. A fluent instruction inside any of them does not grant access to accounts, secrets, or administrative actions.

The model is a reasoning component operating on untrusted content. The application enforces authentication, authorization, data scope, and allowed side effects through code and infrastructure.

## Identity and tenant scope

Authenticate the user or client using the channel's appropriate flow. Bind account identity to the server-side session. Never accept a model argument saying `tenant=other_company` as sufficient authority.

Scope retrieval, memory, tool requests, caches, logs, and storage consistently. A tenant filter in the database is insufficient if the cache shares previously retrieved results across tenants. Audit every place information can persist or be reused.

Diarization and caller ID do not establish authorized identity. Voice biometric systems have their own threat models and should not be casually inferred from a speaker label. For this course, use an explicit account-authentication mechanism.

## Prompt injection

An attacker can speak an instruction, place one in a document, or embed one in a tool result. The danger increases when model output can invoke powerful tools. Prompt wording alone cannot reliably enforce every boundary.

Use scoped tool capabilities, validation, approval/confirmation policies appropriate to the action, restricted destinations, result-size limits, and deterministic authorization. Separate evidence from instructions in context construction and never expose secrets to the model merely because a tool might need them.

Log attempts and outcomes without retaining unnecessary sensitive payloads. Test attacks as part of the evaluation matrix rather than claiming an instruction hierarchy makes the application immune.

## Credential management

Keep provider credentials server-side. Mint short-lived client tokens with limited scope where supported. Do not commit real keys in graph properties, `.env`, lab notes, screenshots, or fixtures.

Environment variables are a delivery mechanism, not a complete secret-management strategy. Production deployments need access control, rotation, audit, and redaction. Be careful when debugging provider adapters that expose vendor metadata.

## Recording and memory

Decide why recording is necessary, who can access it, how long it is retained, and how deletion works. Explain capture clearly in the product. Regional legal requirements are outside this framework-neutral chapter; deployment owners must verify the obligations of their actual jurisdiction and use case.

Use synthetic data in public fixtures. Voice recordings can reveal identity and personal content. A transcript with names removed may still contain identifying details. Treat redaction as a task-specific process rather than an automatic anonymity guarantee.

Memory should have provenance and correction paths. Deletion must account for derived summaries, embeddings, caches, and exported records under the application's policy, not just the original transcript row.

## Abuse and resource control

Bound session duration, upload size, concurrency, tool rate, and generation budget. Authenticate before allocating expensive model sessions. Apply admission control and account quotas so one client cannot exhaust all workers.

Validate webhook signatures and replay protections when integrating telephony or tools. External callbacks are not trustworthy merely because they use HTTPS.

## Failure exercise

Create two synthetic tenants. Attempt to retrieve the other's knowledge, reuse a cached response, select another account through tool arguments, and inject a document instruction to reveal credentials. Verify denials in authoritative logs and absence of forbidden effects.

## Check your understanding

1. Why is model-supplied account identity untrusted?
2. Where can cross-tenant leakage occur outside retrieval?
3. What derived stores matter when deleting memory?

Continue with [operations](22-reliability-deployment-and-scaling.md). [Lab 12](../labs/12-production-failure-drills.md).
