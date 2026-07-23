"""Unit tests for Supabase-backed collection overview aggregates."""

from __future__ import annotations

import unittest

from src.analytics.overview import getOverviewMetrics
from src.collection.models import Paper


class InMemoryPaperRepository:
    """Paper store double used to verify aggregate behavior."""

    def __init__(self, papers: list[Paper] | None = None) -> None:
        self.papers = papers or []

    def savePapers(self, papers: list[Paper]) -> tuple[int, int]:
        self.papers.extend(papers)
        return len(papers), 0

    def loadPapers(self, limit: int = 1000) -> list[dict[str, object]]:
        return [
            {
                "pmid": paper.pmid,
                "title": paper.title,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "pub_year": paper.pubYear,
                "authors": paper.authors,
            }
            for paper in self.papers[:limit]
        ]


class OverviewMetricsTest(unittest.TestCase):
    """Verify overview totals and charts from the shared paper store."""

    def testGetOverviewMetricsReturnsZeroStateForEmptyRepository(self) -> None:
        metrics = getOverviewMetrics(InMemoryPaperRepository())

        self.assertEqual(metrics.totalPapers, 0)
        self.assertEqual(metrics.totalJournals, 0)
        self.assertEqual(metrics.papersByYear, [])
        self.assertEqual(metrics.topJournals, [])

    def testGetOverviewMetricsGroupsYearsAndTopJournals(self) -> None:
        repository = InMemoryPaperRepository(
            [
                Paper("1", "A", "", "Journal A", 2022, "Author A"),
                Paper("2", "B", "", "Journal A", 2022, "Author B"),
                Paper("3", "C", "", "Journal B", 2023, "Author C"),
                Paper("4", "D", "", "", None, "Author D"),
            ]
        )
        metrics = getOverviewMetrics(repository, topJournalLimit = 1)

        self.assertEqual(metrics.totalPapers, 4)
        self.assertEqual(metrics.totalJournals, 2)
        self.assertEqual(
            metrics.papersByYear,
            [{"year": 2022, "count": 2}, {"year": 2023, "count": 1}],
        )
        self.assertEqual(metrics.topJournals, [{"journal": "Journal A", "count": 2}])
