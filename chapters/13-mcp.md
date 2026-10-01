# 13. MCP: tool discovery and integration boundaries

**Prerequisites:** chapter 12. **Goal:** understand what Model Context Protocol standardizes and what policy remains yours.

<!-- chapter-navigation:start -->
**In this chapter**

- [The integration problem](#the-integration-problem)
- [Lifecycle and messages](#lifecycle-and-messages)
- [Tool schemas are not security policy](#tool-schemas-are-not-security-policy)
- [Authentication boundaries](#authentication-boundaries)
- [Voice-specific coordination](#voice-specific-coordination)
- [Integration exercise](#integration-exercise)
- [Follow an MCP exchange on the wire](#follow-an-mcp-exchange-on-the-wire)
- [Discover and map tools](#discover-and-map-tools)
- [Separate protocol errors from tool outcomes](#separate-protocol-errors-from-tool-outcomes)
- [Local and remote lifecycle ownership](#local-and-remote-lifecycle-ownership)
- [A voice-adapter state record](#a-voice-adapter-state-record)
- [Debugging exercise](#debugging-exercise)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

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

## Follow an MCP exchange on the wire

The following messages illustrate the versioned JSON-RPC lifecycle and tool interface. They are protocol examples; transport framing, authorization, and SDK setup are omitted. A real client should use a compatible implementation rather than send arbitrary JSON into an unknown server.

Initialization begins with a request identifying the requested protocol version, client capabilities, and client implementation:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": {"name": "course-voice-client", "version": "0.1.0"}
  }
}
```

The server responds with its selected version, capabilities, and implementation information. The client verifies compatibility and sends the initialized notification before normal operations. The [lifecycle specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) defines this sequence.

Do not confuse a successfully opened HTTP connection or child process with a successfully negotiated MCP session. Capability negotiation tells the client which protocol features it can use.

## Discover and map tools

A `tools/list` request returns tool descriptions and input schemas under the server's supported tool capability. Pagination can require additional requests. The application's catalog should retain the originating server and tool identity, even if model-facing names are adapted to avoid collisions.

Suppose two servers expose `search`. If you flatten them into one unqualified name, the model's proposal can execute against the wrong data source. Keep a registry mapping model-facing tool names to exact server and tool names, scope, timeout, and policy.

The model sees a useful description and schema. The controller sees additional trusted policy such as allowed account scope, consequential-write classification, and confirmation requirement. Do not accept server-provided prose as the source of that policy.

An illustrative call is:

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "check_availability",
    "arguments": {"service": "repair", "date": "2030-01-05"}
  }
}
```

The fields inside `arguments` belong to this hypothetical tool's schema. MCP standardizes the invocation wrapper, not the semantics of repair-shop availability.

## Separate protocol errors from tool outcomes

A malformed JSON-RPC request or unsupported method can produce a protocol-level error. A recognized tool that fails its business operation can return a tool result indicating failure, including the protocol's tool-error convention. Read the [tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) for the exact result fields and supported content types.

Your adapter should normalize these into distinct application outcomes. A protocol error may require integration repair; an unavailable slot may require proposing another slot. Reading either as ordinary successful text can cause false spoken confirmations.

Bound content before adding it to model context. A tool can return large text or multiple content items. Preserve provenance, surface essential structured data where supported, and avoid silently truncating a critical exception from a policy answer.

## Local and remote lifecycle ownership

For stdio, the client often owns the server process and communicates through its standard streams. Logs mixed into the protocol output can corrupt parsing; diagnostic logging must follow the implementation's prescribed path. The client also needs process-exit handling and bounded cleanup.

For remote HTTP, the client must handle network errors, authorization, session semantics where used, and response delivery under the chosen protocol edition. Do not reuse an older transport tutorial without checking edition compatibility.

Reconnect does not automatically grant permission to replay a consequential `tools/call`. Its JSON-RPC ID correlates one exchange; an application operation key identifies the intended business effect. Pass and enforce that key only where the actual tool schema and service support it.

## A voice-adapter state record

Keep the model tool-call ID, MCP request ID, server/tool identity, user turn, response generation, business operation key where applicable, authenticated scope, and deadline. Each answers a different correlation question.

When an MCP result arrives after speech interruption, validate request correlation and update operation state. Decide separately whether the current generation can speak. A server result can be valid and useful without authorizing an obsolete response to resume.

## Debugging exercise

Test an unknown method, an unknown tool, malformed arguments, a legitimate unavailable slot, a delayed reply, and a duplicated write attempt. Observe how each appears at protocol, adapter, workflow, and speech layers. Build the spoken error from the normalized outcome rather than reading raw server diagnostics.

## Check your understanding

1. Why can a runtime expose MCP tools without the model speaking MCP?
2. How does a protocol request ID differ from an operation key?
3. Why does discovery not grant authorization?

Continue with [retrieval and memory](14-rag-and-memory.md). [Lab 7](../labs/07-tools-and-mcp.md). Primary reference: [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25).
