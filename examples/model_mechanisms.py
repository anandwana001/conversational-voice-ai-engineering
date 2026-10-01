"""Small numeric mechanisms, not trained models or production DSP.

Run from the repository root: python3 examples/model_mechanisms.py
CTC enumeration is intentionally exponential and only suitable for tiny examples.
"""
import itertools
import math


def softmax(scores):
    if not scores or any(not math.isfinite(value) for value in scores):
        raise ValueError("Need nonempty finite scores")
    maximum = max(scores)
    weights = [math.exp(value - maximum) for value in scores]
    total = sum(weights)
    return [weight / total for weight in weights]


def attention_mix(scaled_scores, values):
    if len(scaled_scores) != len(values) or not values:
        raise ValueError("One value vector is required per score")
    width = len(values[0])
    if not width or any(len(vector) != width for vector in values):
        raise ValueError("Value vectors must have equal positive width")
    weights = softmax(scaled_scores)
    return [sum(w * vector[column] for w, vector in zip(weights, values))
            for column in range(width)]


def ctc_collapse(path, blank="_"):
    output = []
    previous = None
    for label in path:
        if label != previous and label != blank:
            output.append(label)
        previous = label
    return tuple(output)


def ctc_probability(frames, target, blank="_"):
    if not frames:
        raise ValueError("Need at least one frame")
    alphabet = tuple(frames[0])
    if blank not in alphabet:
        raise ValueError("Blank must be in the alphabet")
    if len(alphabet) ** len(frames) > 100000:
        raise ValueError("This enumerator is for tiny teaching examples only")
    for frame in frames:
        if set(frame) != set(alphabet):
            raise ValueError("Frames must use the same alphabet")
        if any(not math.isfinite(p) or p < 0 or p > 1 for p in frame.values()):
            raise ValueError("Invalid frame probability")
        if not math.isclose(sum(frame.values()), 1.0, abs_tol=1e-9):
            raise ValueError("Each frame distribution must sum to one")
    probability = 0.0
    for path in itertools.product(alphabet, repeat=len(frames)):
        if ctc_collapse(path, blank) == tuple(target):
            probability += math.prod(frame[label] for frame, label in zip(frames, path))
    return probability


def rms_dbfs(samples):
    if not samples or any(not math.isfinite(value) for value in samples):
        raise ValueError("Need finite normalized samples")
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    return float("-inf") if rms == 0 else 20 * math.log10(rms)


def cosine(left, right):
    if not left or len(left) != len(right):
        raise ValueError("Need equal nonzero dimensions")
    if any(not math.isfinite(value) for value in list(left) + list(right)):
        raise ValueError("Vectors must be finite")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Cosine is undefined for a zero vector")
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


if __name__ == "__main__":
    print("Toy attention weights:", softmax([2.0, 0.0]))
    print("Toy attention output:", attention_mix([2.0, 0.0], [[10.0, 0.0], [0.0, 10.0]]))
    frames = [{"_": 0.6, "a": 0.4}, {"_": 0.3, "a": 0.7}, {"_": 0.5, "a": 0.5}]
    print("CTC probability of a:", ctc_probability(frames, ["a"]))
    print("CTC probability of aa:", ctc_probability(frames, ["a", "a"]))
    print("CTC probability of empty:", ctc_probability(frames, []))
    print("Normalized RMS dBFS:", rms_dbfs([0.0, 0.5, 0.0, -0.5]))
    print("Toy retrieval cosine:", cosine([1.0, 0.0], [0.9, 0.1]))
    cache_bytes = 2 * 32 * 4096 * 8 * 128 * 2
    print("Illustrative KV cache MiB:", cache_bytes / 1024 ** 2)
