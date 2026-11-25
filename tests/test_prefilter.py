import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import vt  # noqa: E402


class TestPrefilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.interests = vt.load_yaml(ROOT / "config" / "interests.yaml")
        cls.keywords = vt.load_yaml(ROOT / "config" / "keywords.yaml")

    def test_claude_code_disambiguation(self):
        km = vt.prefilter_item("Claude Code adds hooks for agent harnesses", "", self.interests, self.keywords)
        self.assertEqual(km["fixed"], "claude-code")

    def test_claude_opus_variant(self):
        km = vt.prefilter_item("Claude Opus 5 released with improved vision", "", self.interests, self.keywords)
        self.assertEqual(km["fixed"], "claude")
        self.assertEqual(km["variant"], "opus")

    def test_gemini_robotics_disambiguation(self):
        km = vt.prefilter_item("Gemini Robotics achieves long-horizon manipulation", "", self.interests, self.keywords)
        self.assertIn("gemini-robotics", [km["fixed"]] + km["candidates"])
        self.assertIn("long-horizon", km["keywords"])

    def test_yam_disambiguation_requires_robot_context(self):
        km_food = vt.prefilter_item("Sweet yam recipe for Thanksgiving dinner", "", self.interests, self.keywords)
        self.assertIsNone(km_food["fixed"])
        self.assertNotIn("yam-i2rt", km_food["candidates"])
        self.assertNotIn("YAM", km_food["keywords"])

        km_robot = vt.prefilter_item("Bimanual YAM robot arm integration in LeRobot", "", self.interests, self.keywords)
        self.assertIn("yam-i2rt", [km_robot["fixed"]] + km_robot["candidates"])
        self.assertIn("YAM", km_robot["keywords"])

    def test_unitree_and_direction_signal(self):
        km = vt.prefilter_item("Unitree announcing open-source SDK for G1 humanoid", "", self.interests, self.keywords)
        self.assertIn("unitree", km["labs"])
        self.assertTrue(km["direction_signal"])
        self.assertIn("Unitree", km["keywords"])

    def test_no_direction_signal_on_plain_funding(self):
        km = vt.prefilter_item("OpenAI raises $40B in latest funding round", "", self.interests, self.keywords)
        self.assertIn("openai", km["labs"])
        self.assertFalse(km["direction_signal"])


if __name__ == "__main__":
    unittest.main()
