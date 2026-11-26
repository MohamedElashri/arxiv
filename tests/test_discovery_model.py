"""Optional smoke tests for the pinned model on varied research examples."""

import json
import os
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.prepare_feed import SemanticFocus


ARCHIVE_CASES = {
    "2025-11-23": {"2511.18423": "agentic-systems", "2511.18640": None},
    "2025-12-22": {"2512.19861": None},
    "2026-03-23": {"2603.22206": "ai-engineering"},
    "2026-07-19": {"2607.17352": "agentic-systems", "2607.17283": "ai-engineering"},
    "2026-08-16": {"2608.15762": "ai-engineering", "2608.15840": None},
    "2026-09-23": {"2609.28007": "ai-engineering", "2609.28756": None},
    "2026-10-29": {"2610.40616": None},
}

NOVEL_WORDING_CASES = [
    (
        "Palimpsest Machines",
        "Given a destination state in an unfamiliar application, Palimpsest figures out "
        "intermediate checkpoints, changes records through the available controls, reads "
        "rejection messages, and revises its next move until the requested change is complete.",
        "agentic-systems",
    ),
    (
        "AmberQueues",
        "We replace a global waiting line with groups keyed on projected hardware use. "
        "At the same output quality, machines generating thousands of responses per hour "
        "use less memory and power and return their first result faster. We measure the gains "
        "under realistic bursts of demand and failures.",
        "ai-engineering",
    ),
    (
        "An agentic motivation for Chebyshev inequalities",
        "Agentic applications can motivate scalar bounds. This paper proves a concentration "
        "inequality for estimating the mean of independent random variables. We derive tight "
        "asymptotic constants under a bounded fourth moment and validate the theoretical "
        "limit in Monte Carlo experiments.",
        None,
    ),
]


@unittest.skipUnless(os.environ.get("ARXIV_TEST_MODEL") == "1", "enable the real-model audit with ARXIV_TEST_MODEL=1")
class ModelDiscoveryTests(unittest.TestCase):
    def test_archived_papers_and_novel_terminology(self):
        root = Path(__file__).resolve().parents[1]
        config = tomllib.loads((root / "config.toml").read_text(encoding="utf-8"))
        model = SemanticFocus(config["extra"]["feed"], root / ".nida/models")
        cases = []
        for date, expected in ARCHIVE_CASES.items():
            archive = root / "data/archive" / f"{date}.json"
            issue = json.loads(archive.read_text(encoding="utf-8"))
            papers = {
                paper["id"].partition("v")[0]: paper
                for group in issue["categories"].values()
                for paper in group["papers"]
            }
            cases.extend((papers[paper_id], category) for paper_id, category in expected.items())
        cases.extend(
            ({"title": title, "summary": summary}, category)
            for title, summary, category in NOVEL_WORDING_CASES
        )

        with patch.object(model, "_paper_vectors", wraps=model._embed):
            matches = model.classify([paper for paper, _ in cases])

        for (paper, expected), match in zip(cases, matches, strict=True):
            with self.subTest(title=paper["title"]):
                self.assertEqual(match[0] if match else None, expected)
