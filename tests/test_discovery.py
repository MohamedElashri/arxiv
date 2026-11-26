import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

from scripts.arxiv_fetcher import ArXivFetcher
from scripts.prepare_feed import Feed


class SemanticDiscoveryTests(unittest.TestCase):
    def test_focus_follows_the_contribution_and_keeps_uncertain_papers(self):
        config = {
            "categories": {"cs.AI": "Artificial Intelligence"},
            "settings": {"max_authors_display": 3},
            "focus": {
                "agents": {"descriptions": ["autonomous computer work"]},
                "engineering": {"descriptions": ["system efficiency"]},
            },
            "semantic": {"background": ["general research"], "min_margin": 0.02},
        }
        papers = [
            {"id": "1v1", "title": "Browser tasks with feedback", "summary": "Multi-step control."},
            {"id": "2v1", "title": "An agentic benchmark", "summary": "A new statistical estimator."},
            {"id": "3v1", "title": "Deployed workflow", "summary": "Measured scheduling gains."},
            {"id": "4v1", "title": "Mixed scope", "summary": "An ambiguous result."},
        ]
        for paper in papers:
            paper.update(submitted_date="2026-11-19T00:00:00Z", categories=["cs.AI"])

        vectors = {
            "autonomous computer work": [1, 0, 0],
            "system efficiency": [0, 1, 0],
            "general research": [0, 0, 1],
            "Browser tasks with feedback\nMulti-step control.": [1, 0, 0],
            "An agentic benchmark\nA new statistical estimator.": [0.1, 0, 0.99],
            "Deployed workflow\nMeasured scheduling gains.": [0.55, 0.8, 0.2],
            "Mixed scope\nAn ambiguous result.": [0.71, 0, 0.70],
        }
        with tempfile.TemporaryDirectory() as directory:
            feed = Feed(config, Path(directory))
            stored = {"cs.AI": {"papers": papers}}
            future = dict(papers[0], submitted_date="2035-03-23T00:00:00Z")
            with patch.object(feed.semantic, "_embed", side_effect=lambda docs: np.array([vectors[d] for d in docs])):
                sections = feed.group_papers(stored)
                future_issue = feed.group_papers({"cs.AI": {"papers": [future]}})
            with patch.object(feed.semantic, "_embed") as embed:
                self.assertEqual(feed.group_papers(stored), sections)
                embed.assert_not_called()
            self.assertEqual(sections["agents"], [papers[0]])
            self.assertEqual(sections["engineering"], [papers[2]])
            self.assertEqual(sections["cs.AI"], [papers[1], papers[3]])
            self.assertEqual(future_issue, {"agents": [future]})


class PaginationTests(unittest.TestCase):
    def test_fetch_starts_the_next_page_after_the_entries_returned(self):
        fetcher = ArXivFetcher()
        fetcher.config["settings"]["papers_per_request"] = 2
        offsets = []

        def respond(url, *, params, timeout):
            offset = params["start"]
            offsets.append(offset)
            ids = [0] if offset == 0 else [1, 2]
            entries = "".join(f'<entry><id>{number}</id></entry>' for number in ids)
            return Mock(content=f'''
                <feed xmlns="http://www.w3.org/2005/Atom"
                      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
                    <opensearch:totalResults>3</opensearch:totalResults>
                    {entries}
                </feed>
            ''')

        with (
            patch("scripts.arxiv_fetcher.requests.get", side_effect=respond),
            patch("scripts.arxiv_fetcher.time.sleep"),
            patch.object(fetcher, "parse_paper_entry", side_effect=lambda entry, ns: {
                "id": entry.findtext("atom:id", namespaces=ns)
            }),
        ):
            papers = fetcher.fetch_papers_for_category("cs.AI", "2026-11-19")

        self.assertEqual(offsets, [0, 1])
        self.assertEqual([paper["id"] for paper in papers], ["0", "1", "2"])
