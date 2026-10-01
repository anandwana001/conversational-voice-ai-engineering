# 12. Tools, confirmation, idempotency, and workflow state

**Prerequisites:** chapters 4, 9–11. **Goal:** convert model proposals into controlled, retry-safe actions.

<!-- chapter-navigation:start -->
**In this chapter**

- [The model proposes; the application executes](#the-model-proposes-the-application-executes)
- [A booking workflow](#a-booking-workflow)
- [Idempotency handles retries, not every failure](#idempotency-handles-retries-not-every-failure)
- [The ambiguous timeout](#the-ambiguous-timeout)
- [Permissions and confirmation](#permissions-and-confirmation)
- [Latency during actions](#latency-during-actions)
- [Design the operation ledger, not just a tool function](#design-the-operation-ledger-not-just-a-tool-function)
- [The crash window that a local ledger cannot eliminate](#the-crash-window-that-a-local-ledger-cannot-eliminate)
- [Canonical request fingerprints](#canonical-request-fingerprints)
- [Confirmation is bound to a proposal](#confirmation-is-bound-to-a-proposal)
- [Read/write scheduling and deadlines](#readwrite-scheduling-and-deadlines)
- [Debugging by authoritative state](#debugging-by-authoritative-state)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Design the operation ledger, not just a tool function

For the repair shop, define a booking proposal with canonical customer, service, slot, timezone, and confirmation reference. The server obtains customer/tenant scope from authenticated session context and verifies every supplied field against that scope.

The operation ledger stores one logical write. An illustrative relational design is:

```sql
CREATE TABLE tool_operations (
    tenant_id TEXT NOT NULL,
    operation_key TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('pending', 'succeeded', 'failed', 'unknown')),
    result_json TEXT,
    PRIMARY KEY (tenant_id, operation_key)
);
```

This is a teaching schema, not a complete migration. Real deployments need timestamps, ownership/recovery metadata, an appropriate structured result type, retention, and authorization. The uniqueness boundary is tenant plus key so two tenants do not accidentally share an operation identity.

### Claiming an operation atomically

Two workers can receive the same retry simultaneously. “Check dictionary, then insert” is unsafe across workers. Use a database transaction or equivalent atomic uniqueness mechanism to create the operation record. The loser reads the existing record and compares the fingerprint rather than executing the write again.

In PostgreSQL, conflict-aware insertion is one primitive for this claim, as documented in [INSERT](https://www.postgresql.org/docs/current/sql-insert.html). It is not by itself a full distributed workflow. The application must define what pending, unknown, and completed records mean.

For a completed matching operation, return the saved outcome. For a mismatched fingerprint, reject the retry. For a pending matching operation, wait, report pending, or reconcile according to a bounded policy. Do not assume “pending” means another healthy worker is still processing it.

## The crash window that a local ledger cannot eliminate

```text
1. worker creates pending operation
2. worker calls external calendar
3. external calendar commits booking
4. worker crashes before saving the outcome
```

The local ledger says pending while the external action succeeded. A replacement worker must not blindly execute step 2 again. Prefer an external idempotency key or authoritative operation lookup. If the external service has neither, the integration may require human reconciliation or another task-specific recovery design.

A lease can determine which worker owns recovery, but it cannot prove that the external booking did not happen. Exactly-once business outcomes depend on the participating systems, not a boolean in the agent runtime.

If the calendar and ledger are in the same database, a single transaction can update both atomically. That is a materially different situation from writing to an external service. Teach and document the boundary instead of claiming all tools can be made transactional in the same way.

## Canonical request fingerprints

Hash a canonical representation of the validated operation, including relevant scope and version. JSON objects can have different key orders while meaning the same thing; raw byte comparison can produce false conflicts. Normalize dates and timezones before fingerprinting.

Conversely, omit too much and different operations look identical. A fingerprint containing only a customer ID cannot distinguish booking Saturday from booking Sunday. It should represent the business fields that define the logical request, not volatile transport headers or timestamps for each attempt.

## Confirmation is bound to a proposal

Show or speak the intended service and slot, then bind confirmation to that exact proposal version. If the user says “yes” and the slot changes before execution, the old confirmation should not silently authorize the new slot. Reconfirm material changes.

Keep a proposal ID or version in workflow state. ASR text containing “yes” is evidence to interpret within the expected state, not universal approval for any queued tool. “Yes, but make it three” should update the proposal rather than book the earlier time.

## Read/write scheduling and deadlines

Availability search and service-catalog lookup may run in parallel if independent. Booking depends on their validated results and confirmation, so it remains ordered. Put a deadline on tool execution and return truthful progress if needed.

Retry reads under an appropriate policy. Retry writes only when idempotency/reconciliation makes the attempt safe. A circuit breaker may stop new requests during repeated provider failures, but must not erase unknown outcomes already in flight.

## Debugging by authoritative state

For every tool proposal, log its call ID, operation key, validated argument fingerprint, permission decision, proposal/confirmation version, start, and authoritative result. Redact sensitive values where needed. Compare that ledger to what was spoken.

If the assistant says “booked” with no successful operation, inspect output routing and result interpretation. If two bookings exist for one key, inspect atomicity and external idempotency. If one correct booking exists but the user never heard confirmation, inspect delivery. These are three different defects.

## Check your understanding

1. Why must a retry reuse its operation key?
2. Why should the server bind account identity?
3. What does a timeout after an external write prove?

Continue with [MCP](13-mcp.md). [Lab 7](../labs/07-tools-and-mcp.md).
