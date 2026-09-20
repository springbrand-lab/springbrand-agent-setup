import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / ".scratch/jev-ask-springbrand-dev-validation"
SKILL = FIXTURE / "ask-springbrand-dev/SKILL.md"


class JevDevSkillTests(unittest.TestCase):
    def test_fixture_has_required_contract_and_handoff_rules(self):
        text = SKILL.read_text()
        for phrase in (
            "name: ask-springbrand-dev",
            "recommend_springbrand_domain",
            '{ "query": "<the user\'s current request>" }',
            "platform",
            "action_api",
            "connector",
            "none",
            "jev_unavailable",
            "jev_invalid_response",
            "confidence below `0.70`",
            "springbrand-platform",
            "springbrand-action-api",
            "springbrand-connector",
            "Then stop.",
        ):
            self.assertIn(phrase, text)
        for tool in (
            "search_tools", "get_tool_schemas", "manage_connections",
            "execute_tools", "get_execution",
        ):
            self.assertEqual(text.count(f"`{tool}`"), 1, tool)

    def test_dev_fixture_points_at_only_the_dev_mcp_entry(self):
        manifest = json.loads((FIXTURE / "dev-plugin/plugin.json").read_text())
        mcp = json.loads((FIXTURE / "dev-plugin/.mcp.json").read_text())
        self.assertEqual(manifest["name"], "springbrand-dev")
        self.assertEqual(manifest["skills"], "../ask-springbrand-dev")
        self.assertEqual(list(mcp["mcpServers"]), ["springbrand-dev"])
        self.assertEqual(
            mcp["mcpServers"]["springbrand-dev"]["url"],
            "https://devconnector.springbrand.ai/mcp",
        )

    def test_corpus_is_complete_and_metrics_are_comparable(self):
        rows = json.loads((FIXTURE / "jev-routing-corpus.json").read_text())
        self.assertGreaterEqual(len(rows), 8)
        self.assertTrue({
            "plugin-management", "creation", "action-api", "connector-read",
            "connector-write", "cross-domain", "none", "ambiguous", "in-flight",
        } <= {row["category"] for row in rows})
        output = subprocess.check_output(
            ["python3", str(FIXTURE / "evaluate_corpus.py")], text=True
        )
        metrics = json.loads(output)
        self.assertEqual(metrics["requests"], len(rows))
        self.assertEqual(metrics["jev_correct"], 9)
        self.assertEqual(metrics["legacy_correct"], 9)
        self.assertEqual(metrics["low_confidence"], 1)

    def test_production_skill_and_mcp_manifest_are_unchanged(self):
        production_skill = ROOT / "skills/ask-springbrand/SKILL.md"
        expected_skill = subprocess.check_output(
            ["git", "show", "HEAD:skills/ask-springbrand/SKILL.md"], text=True
        )
        self.assertEqual(production_skill.read_text(), expected_skill)
        production_mcp = (ROOT / ".mcp.json").read_text()
        self.assertIn("https://connector.springbrand.ai/mcp", production_mcp)
        self.assertNotIn("https://devconnector.springbrand.ai/mcp", production_mcp)


if __name__ == "__main__":
    unittest.main()
