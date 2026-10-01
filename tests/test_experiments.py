import json
from pathlib import Path
import tempfile
import unittest
import wave

from examples.audio_frames import PCMFormat, write_tone
from examples.turn_runtime import EndpointPolicy, ResponseRuntime
from examples.tool_idempotency import BookingLedger
from examples.latency_report import summarize, percentile


class AudioTests(unittest.TestCase):
    def test_wav_contract_matches_samples(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "tone.wav"
            write_tone(target)
            with wave.open(str(target)) as audio:
                self.assertEqual((audio.getframerate(), audio.getnchannels(), audio.getsampwidth(), audio.getnframes()), (16000, 1, 2, 16000))
                self.assertEqual(len(audio.readframes(16000)), 32000)

    def test_fractional_samples_rejected(self):
        with self.assertRaises(ValueError):
            PCMFormat(44100, 1, 2).frame_bytes(1)
        self.assertEqual(PCMFormat(24000, 1, 2).frame_bytes(100), 4800)


class TurnTests(unittest.TestCase):
    def test_resumed_speech_prevents_early_commit_and_duplicate(self):
        policy = EndpointPolicy(silence_ms=100)
        probabilities = [0.9, 0.1, 0.1, 0.9] + [0.1] * 8
        commits = [i for i, p in enumerate(probabilities) if policy.feed(i * 20, 20, p)]
        self.assertEqual(commits, [8])
        self.assertEqual(policy.committed_turns, 1)

    def test_missing_audio_is_not_assumed_silence(self):
        policy = EndpointPolicy()
        policy.feed(0, 20, 0.9)
        with self.assertRaises(ValueError):
            policy.feed(1000, 20, 0.1)

    def test_interruption_clears_queue_and_fences_late_callbacks(self):
        runtime = ResponseRuntime()
        old = runtime.start_response()
        runtime.receive(old, "queued")
        runtime.interrupt()
        self.assertIsNone(runtime.play_next())
        self.assertFalse(runtime.receive(old, "late"))
        new = runtime.start_response()
        self.assertFalse(runtime.receive(old, "later"))
        self.assertTrue(runtime.receive(new, "current"))
        self.assertEqual(runtime.play_next(), "current")


class ToolTests(unittest.TestCase):
    def test_lost_reply_retry_is_single_write_and_conflict_fails(self):
        ledger = BookingLedger()
        first = ledger.book("op", "account", "slot-1")
        first["status"] = "mutated outside ledger"
        self.assertEqual(ledger.book("op", "account", "slot-1")["status"], "success")
        with self.assertRaises(ValueError):
            ledger.book("op", "account", "slot-2")
        self.assertEqual(ledger.writes, 1)


class LatencyTests(unittest.TestCase):
    def test_fixture_preserves_failures_and_end_to_end_tail(self):
        path = Path(__file__).resolve().parents[1] / "fixtures" / "turns.jsonl"
        report = summarize([json.loads(line) for line in path.read_text().splitlines()])
        self.assertEqual(report["failure_rate"], 0.2)
        self.assertEqual(report["speech_end_to_playback_ms"], {"p50": 950, "p95": 2400})

    def test_invalid_trace_and_empty_percentile_fail(self):
        with self.assertRaises(ValueError):
            percentile([], 95)
        with self.assertRaises(ValueError):
            summarize([{"status": "unknown"}])
        self.assertIsNone(summarize([{"status": "failed"}])["speech_end_to_playback_ms"])


if __name__ == "__main__":
    unittest.main()
