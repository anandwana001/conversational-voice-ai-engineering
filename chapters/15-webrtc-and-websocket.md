# 15. WebRTC, WebSocket, and the media/control boundary

**Prerequisites:** chapters 2–3 and 10. **Goal:** choose a transport based on timing and lifecycle requirements.

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

## Check your understanding

1. Why can TCP ordering increase audible delay after loss?
2. What is missing from WebRTC without application signaling?
3. Why is transport reconnect insufficient to resume dialogue?

Continue with [telephony](16-sip-rtp-and-telephony.md). [Lab 9](../labs/09-transport-and-phone.md). Primary references: [WebSocket RFC](https://www.rfc-editor.org/rfc/rfc6455), [WebRTC specification](https://www.w3.org/TR/webrtc/), and [ICE RFC](https://www.rfc-editor.org/rfc/rfc8445).
