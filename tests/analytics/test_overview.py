"""Unit tests for collection overview SQL aggregates."""

from __future__ import annotations;

from pathlib import Path;
import tempfile;
import unittest;

from src.analytics.overview import getOverviewMetrics;
from src.collection.models import Paper;
from src.collection.paperRepository import connectDatabase, savePapers;


class OverviewMetricsTest(unittest.TestCase):
    """Verify overview totals and charts from temporary SQLite data."""

    def setUp(self) -> None:
        self.temporaryDirectory = tempfile.TemporaryDirectory();
        self.databasePath = Path(self.temporaryDirectory.name) / "pubmed.db";

    def tearDown(self) -> None:
        self.temporaryDirectory.cleanup();

    def testGetOverviewMetricsReturnsZeroStateForEmptyDatabase(self) -> None:
        metrics = getOverviewMetrics(self.databasePath);

        self.assertEqual(metrics.totalPapers, 0);
        self.assertEqual(metrics.totalJournals, 0);
        self.assertEqual(metrics.papersByYear, []);
        self.assertEqual(metrics.topJournals, []);

    def testGetOverviewMetricsGroupsYearsAndTopJournals(self) -> None:
        papers = [
            Paper("1", "A", "", "Journal A", 2022, "Author A"),
            Paper("2", "B", "", "Journal A", 2022, "Author B"),
            Paper("3", "C", "", "Journal B", 2023, "Author C"),
            Paper("4", "D", "", "", None, "Author D"),
        ];
        connection = connectDatabase(self.databasePath);

        try:
            savePapers(connection, papers);
        finally:
            connection.close();

        metrics = getOverviewMetrics(self.databasePath, topJournalLimit = 1);

        self.assertEqual(metrics.totalPapers, 4);
        self.assertEqual(metrics.totalJournals, 2);
        self.assertEqual(
            metrics.papersByYear,
            [{"year": 2022, "count": 2}, {"year": 2023, "count": 1}],
        );
        self.assertEqual(metrics.topJournals, [{"journal": "Journal A", "count": 2}]);
