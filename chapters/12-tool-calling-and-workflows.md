# 12. Tools, confirmation, idempotency, and workflow state

**Prerequisites:** chapters 4, 9–11. **Goal:** convert model proposals into controlled, retry-safe actions.

## The model proposes; the application executes

A tool definition describes a name, purpose, and argument schema. The model chooses a call based on context. Arguments may arrive incrementally, so wait for a complete tool-call event before parsing and executing. Partial JSON is not a complete authorization request.

Validation has layers: syntax, types, required fields, allowed values, business rules, account access, and user intent. A schema allowing a `customer_id` does not prove the caller can access that customer.

Return structured outcomes such as `success`, `not_found`, `permission_denied`, `timeout`, or `conflict`. Preserve call IDs so concurrent calls cannot exchange results accidentally.

## A booking workflow

```text
collect intent -> resolve date/time -> check availability
-> present proposed action -> obtain confirmation
-> execute booking -> reconcile authoritative result -> report
```

Availability is a read. Booking is a write. The available slot can disappear between them, so the write must atomically enforce availability. The model should not claim success based on an earlier search.

Use the user's timezone and a fixed interpretation timestamp for relative dates. When “tomorrow at eight” is ambiguous, clarify AM/PM or the intended timezone before confirmation. Re-read critical fields if ASR confidence or entity resolution is uncertain.

## Idempotency handles retries, not every failure

The client supplies an operation key for one logical write. The server atomically stores that key, the request fingerprint, and the outcome. A retry with the same key and same request returns the prior outcome; the same key with different arguments must be rejected.

The key should represent the business operation, not a new network attempt. If you generate a fresh key for each retry, every retry can become a fresh booking.

The [offline experiment](../examples/tool_idempotency.py) demonstrates duplicate request handling and conflict detection in memory. A production service needs a durable store with transaction or uniqueness guarantees; a Python dictionary is not distributed idempotency.

## The ambiguous timeout

```text
client sends booking -> server commits -> reply is lost -> client times out
```

The timeout means outcome unknown. Retrying without a stable key can duplicate the booking. Query by operation key or repeat the same keyed request. If the external provider cannot support reconciliation, make the ambiguity visible and arrange human recovery rather than inventing success or failure.

## Permissions and confirmation

Read tools and write tools may have different permissions. Bind authenticated identity on the server rather than trusting model-supplied identity. Confirmation is conversational evidence of intent; authentication is evidence of who can perform an action. They are complementary.

Interruption can revoke permission to continue a pending workflow but cannot reverse an already committed side effect. Preserve the operation ledger and follow a separate compensation workflow when permitted.

## Latency during actions

A long-running tool should have a deadline and cancellation policy. A brief truthful status message can reduce uncertainty, but repeated filler increases annoyance. Track tool execution separately from model delay. Parallelize independent reads when useful; keep dependent or consequential mutations ordered.

Avoid promising action before the authoritative result arrives. “I'm checking” is different from “It's done.” If a tool fails, state the failure and a usable next step.

## Check your understanding

1. Why must a retry reuse its operation key?
2. Why should the server bind account identity?
3. What does a timeout after an external write prove?

Continue with [MCP](13-mcp.md). [Lab 7](../labs/07-tools-and-mcp.md).
