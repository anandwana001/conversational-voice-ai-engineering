"""Deterministic turn-policy and generation-fencing simulations.

No microphone, real VAD, sockets, threading, or audio device is modeled.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class EndpointPolicy:
    silence_ms: int = 500
    threshold: float = 0.6
    active: bool = False
    last_speech_end_ms: Optional[int] = None
    last_frame_end_ms: int = 0
    committed_turns: int = 0

    def __post_init__(self):
        if self.silence_ms <= 0 or not 0 <= self.threshold <= 1:
            raise ValueError("Invalid endpoint settings")

    def feed(self, frame_start_ms: int, duration_ms: int, speech_probability: float) -> bool:
        if duration_ms <= 0 or frame_start_ms < self.last_frame_end_ms:
            raise ValueError("Frames must have positive duration and ordered nonoverlapping times")
        if not 0 <= speech_probability <= 1:
            raise ValueError("Probability must be between zero and one")
        # Simulation assumes a complete contiguous timeline; gaps are not silence evidence.
        if frame_start_ms != self.last_frame_end_ms:
            raise ValueError("Missing frames require explicit discontinuity handling")
        end = frame_start_ms + duration_ms
        self.last_frame_end_ms = end
        if speech_probability >= self.threshold:
            self.active = True
            self.last_speech_end_ms = end
            return False
        if self.active and end - self.last_speech_end_ms >= self.silence_ms:
            self.active = False
            self.committed_turns += 1
            return True
        return False


@dataclass
class ResponseRuntime:
    generation: int = 0
    responding: bool = False
    queue: List[Tuple[int, str]] = field(default_factory=list)
    stale_drops: int = 0

    def start_response(self) -> int:
        self.generation += 1
        self.queue.clear()
        self.responding = True
        return self.generation

    def receive(self, generation: int, chunk: str) -> bool:
        if not self.responding or generation != self.generation:
            self.stale_drops += 1
            return False
        self.queue.append((generation, chunk))
        return True

    def interrupt(self):
        # Invalidate first: provider cancellation would happen after this transition.
        self.generation += 1
        self.responding = False
        self.queue.clear()

    def play_next(self) -> Optional[str]:
        if not self.queue:
            return None
        generation, chunk = self.queue.pop(0)
        return chunk if self.responding and generation == self.generation else None


if __name__ == "__main__":
    endpoint = EndpointPolicy(silence_ms=500)
    for index, probability in enumerate([0.9] * 10 + [0.1] * 30):
        if endpoint.feed(index * 20, 20, probability):
            print("Turn committed at", (index + 1) * 20, "ms (speech ended at 200 ms)")
    runtime = ResponseRuntime()
    old = runtime.start_response()
    runtime.receive(old, "obsolete audio A")
    runtime.receive(old, "obsolete audio B")
    runtime.interrupt()
    print("Late old chunk accepted:", runtime.receive(old, "late obsolete audio"))
    new = runtime.start_response()
    runtime.receive(new, "new valid audio")
    print("Playback:", runtime.play_next(), "| stale drops:", runtime.stale_drops)
