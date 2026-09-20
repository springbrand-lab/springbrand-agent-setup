#!/usr/bin/env python3
"""Validate the fixed Step 2 corpus and emit comparable routing metrics."""

import json
from pathlib import Path

ROOT = Path(__file__).parent
REQUIRED_CATEGORIES = {
    "plugin-management", "creation", "action-api", "connector-read",
    "connector-write", "cross-domain", "none", "ambiguous", "in-flight",
}


def load_rows():
    rows = json.loads((ROOT / "jev-routing-corpus.json").read_text())
    assert len(rows) >= 8
    assert REQUIRED_CATEGORIES <= {row["category"] for row in rows}
    for row in rows:
        result = row["jev"]
        assert result["domain"] in {"platform", "action_api", "connector", "none"}
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["no_match"], bool)
    return rows


def evaluate(rows):
    jev_correct = sum(row["jev"]["domain"] == row["human_domain"] for row in rows)
    legacy_labeled = sum(
        row["legacy_domain"] in {"platform", "action_api", "connector", "none"}
        and row["legacy_domain"] == row["human_domain"]
        for row in rows
    )
    return {
        "requests": len(rows),
        "jev_correct": jev_correct,
        "jev_accuracy": jev_correct / len(rows),
        "legacy_correct": legacy_labeled,
        "legacy_accuracy": legacy_labeled / len(rows),
        "low_confidence": sum(row["jev"]["confidence"] < 0.70 for row in rows),
        "no_match": sum(row["jev"]["no_match"] for row in rows),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(load_rows()), indent=2, sort_keys=True))
