import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import vt  # noqa: E402


class TestPipelineHelpers(unittest.TestCase):
    def test_url_normalization_and_id(self):
        u1 = "https://Example.COM/blog/post/?utm_source=x&fbclid=123&id=7"
        u2 = "https://example.com/blog/post?id=7"
        self.assertEqual(vt.normalize_url(u1), vt.normalize_url(u2))
        self.assertEqual(vt.url_id(u1), vt.url_id(u2))

    def test_title_simhash_dedup(self):
        h1 = vt.title_simhash("Unitree G1 open-source LeRobot integration released")
        h2 = vt.title_simhash("Unitree G1 open-source LeRobot integration released!")
        h3 = vt.title_simhash("Quantum computing breakthrough in superconducting qubits")
        self.assertLessEqual(vt.hamming64(h1, h2), 3)
        self.assertGreater(vt.hamming64(h1, h3), 10)

    def test_consecutive_days_proposal(self):
        self.assertTrue(vt.has_consecutive_days(["2026-11-20", "2026-11-22", "2026-11-23"], 2))
        self.assertFalse(vt.has_consecutive_days(["2026-11-20", "2026-11-22", "2026-11-24"], 2))

    def test_momentum_surge_and_emerging(self):
        cfg = {"min_excess": 2, "lift": 0.10, "min_count": 3, "new_min": 2}
        cur = {"robot-harness": 5, "unitree": 2, "claude": 1}
        base = {"robot-harness": 2, "claude": 18}
        res = vt.compute_momentum(cur, base, cfg)
        surging_topics = [x["topic"] for x in res["surging"]]
        emerging_topics = [x["topic"] for x in res["emerging"]]
        self.assertIn("robot-harness", surging_topics)
        self.assertIn("unitree", emerging_topics)


if __name__ == "__main__":
    unittest.main()
