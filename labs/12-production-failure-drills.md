# Lab 12. Run production failure drills

**Read:** [chapters 21–22](../chapters/21-security-and-privacy.md) and [the checklist](../reference/production-checklist.md). **Mode:** development deployment. **Time:** 3–4 hours.

## Build

1. Deploy the voice runtime to an environment appropriate for its long-lived connections. Keep credentials server-side and data synthetic.
2. Limit session duration and admission concurrency. Distinguish readiness from liveness.
3. Inject a delayed tool reply, recognition disconnect, synthesis failure, and transport interruption one at a time.
4. Terminate a worker after a mock write commits but before its reply reaches the controller. Reconcile by operation key before retrying.
5. Test two synthetic tenants across retrieval, memory, tool arguments, and caches.
6. Drain active sessions during a version change and demonstrate rollback of code/configuration.

## Deliver

Submit a failure table: trigger, user experience, authoritative state, recovery, resource cleanup, and evidence link. Include measured workload and remaining limitations.

## Acceptance

- No cross-tenant access occurs in tested paths.
- A retried write remains single under process failure.
- Obsolete output is bounded and rejected after interruption.
- Sessions have bounded resources and a clear failure message.
- Rollback is described separately from reversing external actions.

**Failure experiment:** remove one admission or timeout limit in a controlled small load test, observe queue growth, then restore it. Avoid uncontrolled traffic to real provider services.

**Transfer:** identify which operational requirements remain if you change framework and hosting provider.

[Capstone](../capstone/README.md) · [All labs](README.md)
