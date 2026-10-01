# 13. MCP: tool discovery and integration boundaries

**Prerequisites:** chapter 12. **Goal:** understand what Model Context Protocol standardizes and what policy remains yours.

## The integration problem

Without a common interface, each application implements its own discovery, argument schema, transport, and result wrapper for every integration. MCP defines an interoperable client/server protocol for exposing capabilities such as tools, resources, and prompts.

The agent runtime can host an MCP client. The client discovers server capabilities and adapts supported tools to the model's tool interface. A model does not need to directly open an MCP socket.

## Lifecycle and messages

An MCP connection begins with initialization and capability negotiation. After initialization, supported methods let a client discover or invoke capabilities. The protocol uses JSON-RPC messages with request IDs and structured results or errors. Local stdio and remote Streamable HTTP have different process and network lifecycles.

Pin the protocol and SDK versions you implement. The [2025-11-25 specification](https://modelcontextprotocol.io/specification/2025-11-25) is the reference edition for this course, not a promise that it is the newest version forever. Check compatibility before adopting a new server or copying examples from an older transport.

## Tool schemas are not security policy

A tool's description tells the model what it does. Its schema describes input structure. The application still decides whether the current user, session, and turn may invoke it. A server-provided description is external text and can be misleading or malicious.

Maintain an allowlist of servers and tools for the application. Review tools that create, delete, send, or spend. Reconfirm consequential intent through the workflow from chapter 12. Limit result size and execution duration so an integration cannot consume unbounded context or hold a conversation indefinitely.

## Authentication boundaries

Remote deployments may use protocol-specified authorization flows; local stdio has a different trust model. Follow the versioned authorization specification rather than assuming one bearer token arrangement fits every transport.

Never put an administrative credential into model-visible context. Bind user-scoped credentials to the server-side session. Avoid sending a token issued for one service to another service, and enforce appropriate audience and resource boundaries. A tool's availability in discovery does not imply authorization for every caller.

## Voice-specific coordination

The runtime needs to correlate an MCP result with the tool proposal, user turn, and active response generation. If the caller interrupts while the request runs, the action can finish without permission to speak for that old response.

For write tools, distinguish protocol request IDs from business idempotency keys. A new JSON-RPC request ID is useful for transport correlation but should not create a new booking during a retry of the same logical operation.

Map integration errors to structured application outcomes. Do not read a large server stack trace aloud. The controller needs a recoverable error; the user needs a short explanation and next step.

## Integration exercise

Expose a read-only catalog tool and a mock booking tool through your chosen MCP SDK. Discover them, inspect their schemas, call the read tool, then call the write tool under explicit confirmation and a stable operation key. Test a denied caller, malformed arguments, an oversized result, and a delayed reply after interruption.

Use mock side effects until the behavior is understood. The offline idempotency experiment is not an MCP server; this exercise requires a genuine client/server exchange.

## Check your understanding

1. Why can a runtime expose MCP tools without the model speaking MCP?
2. How does a protocol request ID differ from an operation key?
3. Why does discovery not grant authorization?

Continue with [retrieval and memory](14-rag-and-memory.md). [Lab 7](../labs/07-tools-and-mcp.md). Primary reference: [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25).
