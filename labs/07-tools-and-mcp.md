# Lab 7. Add validated tools and an MCP boundary

**Read:** [chapters 12–13](../chapters/12-tool-calling-and-workflows.md). **Mode:** offline mock actions plus a real local MCP exchange. **Time:** 2–3 hours.

## Build

1. Run `python3 examples/tool_idempotency.py`. Inspect same-key retries and different-request conflicts.
2. Define a read-only availability tool and a mock booking tool. Validate date, time, account scope, and confirmation before executing.
3. Expose the tools through a version-compatible MCP SDK and connect a genuine MCP client. Record initialization, discovery, request ID, and result correlation.
4. Simulate a lost reply after booking commits. Retry with the same business operation key.
5. Interrupt the conversation while a delayed result is pending. Preserve the result in workflow state without speaking for an invalid generation.

## Deliver

Submit schemas, a redacted MCP trace, a mock operation ledger, and assertions for malformed input, unauthorized account, duplicate retry, and conflicting retry.

## Acceptance

- Exactly one mock write occurs for repeated identical operation keys.
- Reusing a key with different arguments fails.
- Protocol request IDs and business operation keys have distinct roles.
- Discovery alone does not authorize a caller to execute a write.

**Failure experiment:** generate a new key for each retry and show the duplicate-write risk.

**Transfer:** describe the same policy around an ordinary HTTP tool instead of MCP. The in-memory example is not a durable ledger or MCP server.

[Next lab](08-rag-and-memory.md) · [All labs](README.md)
