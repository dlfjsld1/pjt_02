"""Unit tests for Supabase-backed collection overview aggregates."""

from __future__ import annotations

import unittest

from src.analytics.overview import get_overview_metrics
from src.collection.models import Paper


class InMemoryPaperRepository:
    """Paper store double used to verify aggregate behavior."""

    def __init__(self, papers: list[Paper] | None = None) -> None:
        self.papers = papers or []

    def save_papers(self, papers: list[Paper]) -> tuple[int, int]:
        self.papers.extend(papers)
        return len(papers), 0

    def load_papers(self, limit: int = 1000) -> list[dict[str, object]]:
        return [
            {
                "pmid": paper.pmid,
                "title": paper.title,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "pub_year": paper.pub_year,
                "authors": paper.authors,
            }
            for paper in self.papers[:limit]
        ]


class OverviewMetricsTest(unittest.TestCase):
    """Verify overview totals and charts from the shared paper store."""

    def test_get_overview_metrics_returns_zero_state_for_empty_repository(self) -> None:
        metrics = get_overview_metrics(InMemoryPaperRepository())

        self.assertEqual(metrics.total_papers, 0)
        self.assertEqual(metrics.total_journals, 0)
        self.assertEqual(metrics.papers_by_year, [])
        self.assertEqual(metrics.top_journals, [])

    def test_get_overview_metrics_groups_years_and_top_journals(self) -> None:
        repository = InMemoryPaperRepository(
            [
                Paper("1", "A", "", "Journal A", 2022, "Author A"),
                Paper("2", "B", "", "Journal A", 2022, "Author B"),
                Paper("3", "C", "", "Journal B", 2023, "Author C"),
                Paper("4", "D", "", "", None, "Author D"),
            ]
        )
        metrics = get_overview_metrics(repository, top_journal_limit = 1)

        self.assertEqual(metrics.total_papers, 4)
        self.assertEqual(metrics.total_journals, 2)
        self.assertEqual(
            metrics.papers_by_year,
            [{"year": 2022, "count": 2}, {"year": 2023, "count": 1}],
        )
        self.assertEqual(metrics.top_journals, [{"journal": "Journal A", "count": 2}])
