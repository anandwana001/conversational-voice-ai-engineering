import math
import unittest

from examples.model_mechanisms import (
    attention_mix, cosine, ctc_collapse, ctc_probability, rms_dbfs, softmax,
)


class MechanismTests(unittest.TestCase):
    def test_softmax_stays_stable_with_large_common_offset(self):
        weights = softmax([1002.0, 1000.0])
        self.assertAlmostEqual(weights[0], 0.8807970779778823)
        self.assertAlmostEqual(sum(weights), 1.0)
        output = attention_mix([2.0, 0.0], [[10.0, 0.0], [0.0, 10.0]])
        self.assertAlmostEqual(output[0], 8.807970779778823)
        self.assertAlmostEqual(sum(output), 10.0)

    def test_blank_separates_repeated_ctc_labels(self):
        self.assertEqual(ctc_collapse(["b", "b", "_", "o", "o", "_", "o", "k", "k"]), tuple("book"))
        self.assertEqual(ctc_collapse(["b", "o", "o", "k"]), tuple("bok"))

    def test_ctc_sums_alignments_and_preserves_total_mass(self):
        frames = [{"_": 0.6, "a": 0.4}, {"_": 0.3, "a": 0.7}, {"_": 0.5, "a": 0.5}]
        probabilities = [ctc_probability(frames, target) for target in [[], ["a"], ["a", "a"]]]
        self.assertAlmostEqual(probabilities[0], 0.09)
        self.assertAlmostEqual(probabilities[1], 0.85)
        self.assertAlmostEqual(probabilities[2], 0.06)
        self.assertAlmostEqual(sum(probabilities), 1.0)

    def test_ctc_rejects_invalid_distribution_and_unbounded_enumeration(self):
        with self.assertRaises(ValueError):
            ctc_probability([{"_": 0.9, "a": 0.9}], ["a"])
        with self.assertRaises(ValueError):
            ctc_probability([{"_": 0.5, "a": 0.5}] * 20, ["a"])

    def test_rms_and_cosine_have_defined_edge_cases(self):
        self.assertAlmostEqual(rms_dbfs([0.0, 0.5, 0.0, -0.5]), -9.030899869919436)
        self.assertEqual(rms_dbfs([0.0]), float("-inf"))
        self.assertAlmostEqual(cosine([1.0, 0.0], [0.9, 0.1]), 0.9938837346736189)
        self.assertEqual(cosine([1.0, 0.0], [0.0, 1.0]), 0.0)
        with self.assertRaises(ValueError):
            cosine([0.0, 0.0], [1.0, 0.0])
        with self.assertRaises(ValueError):
            softmax([math.nan])


if __name__ == "__main__":
    unittest.main()
