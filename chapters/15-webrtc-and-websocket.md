# 15. WebRTC, WebSocket, and the media/control boundary

**Prerequisites:** chapters 2–3 and 10. **Goal:** choose a transport based on timing and lifecycle requirements.

<!-- chapter-navigation:start -->
**In this chapter**

- [WebSocket provides a channel, not an audio engine](#websocket-provides-a-channel-not-an-audio-engine)
- [WebRTC supplies a media-oriented stack](#webrtc-supplies-a-media-oriented-stack)
- [SDK transport versus plain WebRTC](#sdk-transport-versus-plain-webrtc)
- [The control path matters](#the-control-path-matters)
- [Reconnection is a state problem](#reconnection-is-a-state-problem)
- [Choosing a route](#choosing-a-route)
- [Trace browser connection establishment step by step](#trace-browser-connection-establishment-step-by-step)
- [Understand network traversal with an example](#understand-network-traversal-with-an-example)
- [Design a WebSocket audio protocol explicitly](#design-a-websocket-audio-protocol-explicitly)
- [Pacing matters even on a fast connection](#pacing-matters-even-on-a-fast-connection)
- [Specify reconnect as an application protocol](#specify-reconnect-as-an-application-protocol)
- [A boundary-based transport investigation](#a-boundary-based-transport-investigation)
- [Check your understanding](#check-your-understanding)
<!-- chapter-navigation:end -->

## WebSocket provides a channel, not an audio engine

WebSocket supplies a persistent bidirectional framed connection, commonly carried over TCP with TLS for `wss`. You can send audio and JSON control events, but must define encoding, timestamps, message types, authentication, queue limits, reconnection, and playback yourself.

TCP preserves ordered delivery. Retransmission after loss can delay later bytes, a head-of-line effect. A connection can be healthy while audio is already too late for conversation. Monitor oldest-message age as well as socket status.

Use explicit message types and size limits. A binary message should not be decoded as UTF-8 JSON. A connection opening does not mean microphone permissions or output playback are ready.

## WebRTC supplies a media-oriented stack

WebRTC provides browser and native media mechanisms including negotiated codecs, encrypted media, network traversal, and realtime delivery behavior. It still requires application signaling to exchange session descriptions and connectivity information; signaling is not a universal built-in application service.

ICE tests connectivity candidates. STUN helps discover network-visible addressing; TURN relays traffic when direct paths are unavailable. A demo that works on one Wi-Fi network does not establish that TURN and enterprise firewall cases work.

Media commonly uses RTP with secure transport. Codec negotiation determines the wire representation, while the audio API exposed to an agent may provide decoded PCM. Confirm both boundaries.

## SDK transport versus plain WebRTC

A hosted RTC SDK can provide routing, room membership, token systems, and operational support. These are distinct from agent reasoning. You can keep a model/controller independent of the RTC provider by normalizing capture, playback, and session events at an adapter boundary.

TEN's reference examples use an `agora_rtc` extension for transport. Read that as one media integration, not evidence that all voice agents require Agora or that a room join solves tool security.

## The control path matters

Cancel, clear, session-close, and tool results need predictable delivery. If large output batches share one queue with controls, interruption waits behind the backlog. A runtime may use separate queues or priority handling even when the physical connection is shared.

Preserve response IDs through the client boundary so local playback rejects stale content. When the protocol cannot tag raw frames directly, maintain an explicit mapping and make buffer-clear acknowledgements meaningful.

## Reconnection is a state problem

After disconnection, distinguish resumed transport from resumed dialogue. Reopening a socket does not restore the model session, pending operation, or playback cursor. A reconnect handshake should establish session identity, resume policy, and whether old output is invalid.

At-most-once delivery is not guaranteed by your application merely because TCP is ordered. A client retry can duplicate a previously accepted event. Give important operations stable IDs and make handling idempotent where needed.

Do not replay seconds of old microphone audio as though it were current live speech. If replay is needed for transcription, mark it accordingly and avoid triggering duplicate actions.

## Choosing a route

| Need | Investigate |
| --- | --- |
| Browser media with network variability | WebRTC or an RTC SDK, including TURN and codec behavior |
| Server-to-provider streaming integration | WebSocket or provider-specific streaming protocol |
| Custom simple media relay | WebSocket plus explicit media timing and buffering |
| Telephone trunk | SIP signaling and a media bridge, usually RTP |

These are engineering starting points, not universal rankings. Measure your intended regions, mobile networks, session duration, and client capabilities.

## Trace browser connection establishment step by step

Before any model receives sound, the browser needs permission to capture audio and an output path permitted by its playback behavior. The application obtains or creates a session, exchanges signaling, negotiates media, and establishes connectivity. Model/session readiness can happen on a separate path and should be correlated with the media session.

In a typical peer-connection flow, an offer describes available media and transport parameters; an answer selects compatible parameters. ICE gathers and checks connectivity candidates. The application exchanges those descriptions/candidates through its signaling service. DTLS establishes security material used by secure media transport. Only after the relevant states are ready can usable audio flow.

This is a conceptual sequence: some work overlaps, and SDKs hide parts behind their APIs. Inspect their state events rather than requiring a particular fixed order in application code. The [WebRTC specification](https://www.w3.org/TR/webrtc/) defines the browser-facing primitives.

## Understand network traversal with an example

Two devices behind home routers may not be directly addressable using their private addresses. Candidate gathering and connectivity checks seek a viable path. A relay candidate can route media through TURN when a direct path is unavailable.

If a demo succeeds only when both participants use the same network, test a different network and a restrictive firewall. If it works on a permissive mobile hotspot but fails in an office, inspect candidate selection, relay reachability, and allowed protocols rather than changing the voice model.

Do not conclude “WebRTC is peer-to-peer” means every packet travels directly between the endpoints. Hosted RTC systems can use servers, and network traversal can require relays. The actual topology affects latency, bandwidth, and operational visibility.

## Design a WebSocket audio protocol explicitly

A custom socket needs a handshake declaring audio format and session ownership. Define binary audio records or a supported structured encoding, and a distinct set of control messages. For example, this **application-defined control event** can fence playback:

```json
{
  "type": "clear_output",
  "session_id": "session-A",
  "obsolete_generation": 12,
  "control_sequence": 31
}
```

A corresponding acknowledgement should state that the client processed sequence 31 and what “cleared” means. Do not claim it establishes instantaneous silence in audio hardware unless measured. New audio records must carry enough association to reject generation 12 after the clear.

WebSocket message boundaries are preserved at the WebSocket API level, but lower-level network reads may be fragmented. Follow the library's framing abstraction. If you serialize raw PCM inside one binary message, its interpretation still requires the handshake's encoding and sample contract.

## Pacing matters even on a fast connection

Suppose synthesis creates one second of audio in 100 ms. Sending the whole second immediately can be efficient, but the receiver now holds a second of content. The client must play at the audio rate and support clearing it on interruption.

If you pace 20 ms output chunks, use a monotonic schedule and account for drift/late wakeups. Repeatedly sleeping 20 ms after each operation can accumulate processing overhead and stretch timing. A media stack may already handle pacing; avoid adding another scheduler that creates conflicting delays.

Reliable ordered transport also means old content can block new content after loss. If an earlier TCP segment is missing, later data waits for recovery even if it has arrived. A stream deadline can make late content invalid at the application level, but cannot magically remove the connection's underlying ordering behavior.

## Specify reconnect as an application protocol

Use a reconnect request containing authenticated session/resume identity and last acknowledged application event where supported. The server responds whether it resumed existing state, recreated a model session, or rejected resumption.

Then decide input and output replay. Replay of a tool command needs stable logical identity and authorization; replay of microphone data needs media offsets and a clear transcription-versus-action policy. Replaying old assistant audio can confuse the caller, so often a new generation and concise status are safer than resuming an unverified playback cursor.

Separate connection sequence from business operation key. Sequence 42 on one socket and sequence 42 on a later socket are not automatically the same operation. A durable operation key can remain stable while transport identifiers change.

## A boundary-based transport investigation

Record capture sample counters, encoded/decoded format, send/receive times in local clock domains, connection state, selected path where exposed, queue duration, and client playback progress. For a silent call, verify capture is nonzero, media leaves the client, decoded samples reach the agent, and output reaches the device.

Do not subtract arbitrary browser and server wall times to claim one-way network delay. Use synchronized-clock assumptions explicitly or compare local spans and round-trip probes. Network and audio observations should correlate through media/session IDs rather than unexamined timestamp subtraction.

## Check your understanding

1. Why can TCP ordering increase audible delay after loss?
2. What is missing from WebRTC without application signaling?
3. Why is transport reconnect insufficient to resume dialogue?

Continue with [telephony](16-sip-rtp-and-telephony.md). [Lab 9](../labs/09-transport-and-phone.md). Primary references: [WebSocket RFC](https://www.rfc-editor.org/rfc/rfc6455), [WebRTC specification](https://www.w3.org/TR/webrtc/), and [ICE RFC](https://www.rfc-editor.org/rfc/rfc8445).
