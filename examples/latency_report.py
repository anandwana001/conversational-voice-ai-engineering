"""Report explicitly named synthetic/live trace boundaries; nearest-rank percentiles."""
import argparse
import json
import math
from pathlib import Path

BOUNDARIES = ("speech_end_ms", "turn_commit_ms", "text_segment_ms", "audio_ready_ms", "playback_start_ms")


def percentile(values, p):
    if not values or not 0 < p <= 100:
        raise ValueError("Need nonempty values and percentile in (0, 100]")
    ordered = sorted(values)
    return ordered[math.ceil(p / 100 * len(ordered)) - 1]


def summarize(rows):
    if not rows:
        raise ValueError("Trace is empty")
    successful = []
    failed = 0
    for row in rows:
        if row.get("status") not in ("success", "failed"):
            raise ValueError("Each turn must declare success or failed")
        if row["status"] == "failed":
            failed += 1
            continue
        times = [row[key] for key in BOUNDARIES]
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) for t in times):
            raise ValueError("Boundaries must be finite numeric timestamps")
        if times != sorted(times):
            raise ValueError("This sequential teaching trace requires ordered boundaries")
        successful.append(row)
    report = {"turns": len(rows), "successful": len(successful), "failed": failed,
              "failure_rate": failed / len(rows), "percentile_method": "nearest-rank"}
    intervals = {
        "speech_end_to_playback_ms": ("speech_end_ms", "playback_start_ms"),
        "endpoint_delay_ms": ("speech_end_ms", "turn_commit_ms"),
        "post_commit_to_text_segment_ms": ("turn_commit_ms", "text_segment_ms"),
        "text_segment_to_audio_ready_ms": ("text_segment_ms", "audio_ready_ms"),
        "audio_ready_to_playback_ms": ("audio_ready_ms", "playback_start_ms"),
    }
    for name, (start, end) in intervals.items():
        values = [r[end] - r[start] for r in successful]
        report[name] = {"p50": percentile(values, 50), "p95": percentile(values, 95)} if values else None
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    try:
        rows = [json.loads(line) for line in args.trace.read_text().splitlines() if line.strip()]
        print(json.dumps(summarize(rows), indent=2))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, "Invalid trace: " + str(error) + "\n")
