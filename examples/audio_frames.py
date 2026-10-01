"""PCM accounting experiment; creates a synthetic tone, not a speech signal."""
from dataclasses import dataclass
from pathlib import Path
import math
import struct
import wave


@dataclass(frozen=True)
class PCMFormat:
    sample_rate: int
    channels: int
    bytes_per_sample: int

    def __post_init__(self):
        for value in (self.sample_rate, self.channels, self.bytes_per_sample):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError("PCM dimensions must be positive integers")

    def frame_bytes(self, duration_ms: int) -> int:
        if not isinstance(duration_ms, int) or isinstance(duration_ms, bool) or duration_ms <= 0:
            raise ValueError("Duration must be a positive integer number of milliseconds")
        numerator = self.sample_rate * duration_ms
        if numerator % 1000:
            raise ValueError("Duration gives a fractional sample count; use explicit timing state")
        return numerator // 1000 * self.channels * self.bytes_per_sample


def write_tone(path: Path):
    rate = 16000
    samples = [round(0.15 * 32767 * math.sin(2 * math.pi * 440 * i / rate)) for i in range(rate)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(struct.pack("<" + "h" * len(samples), *samples))


if __name__ == "__main__":
    fmt = PCMFormat(16000, 1, 2)
    print("16 kHz mono signed 16-bit PCM: 20 ms =", fmt.frame_bytes(20), "bytes")
    print("24 kHz mono signed 16-bit PCM: 100 ms =", PCMFormat(24000, 1, 2).frame_bytes(100), "bytes")
    target = Path(__file__).resolve().parents[1] / "artifacts" / "tone.wav"
    write_tone(target)
    print("Wrote one-second 440 Hz synthetic tone:", target)
