"""Read-only SQLite aggregates for the collection overview page."""

from __future__ import annotations;

from dataclasses import dataclass;
from pathlib import Path;

from src.collection.paperRepository import DEFAULT_DATABASE_PATH, connectDatabase;


@dataclass(frozen = True)
class OverviewMetrics:
    """Database totals and chart-ready aggregates for the overview."""

    totalPapers: int;
    totalJournals: int;
    papersByYear: list[dict[str, int]];
    topJournals: list[dict[str, str | int]];


def getOverviewMetrics(
    databasePath: str | Path = DEFAULT_DATABASE_PATH,
    topJournalLimit: int = 10,
) -> OverviewMetrics:
    """Load overview metrics without placing SQL or transformation logic in the UI."""

    connection = connectDatabase(databasePath);

    try:
        totalPapers = connection.execute("SELECT COUNT(*) FROM papers").fetchone()[0];
        totalJournals = connection.execute(
            """
            SELECT COUNT(DISTINCT journal)
            FROM papers
            WHERE TRIM(COALESCE(journal, '')) != ''
            """
        ).fetchone()[0];
        yearRows = connection.execute(
            """
            SELECT pub_year, COUNT(*) AS paper_count
            FROM papers
            WHERE pub_year IS NOT NULL
            GROUP BY pub_year
            ORDER BY pub_year
            """
        ).fetchall();
        journalRows = connection.execute(
            """
            SELECT journal, COUNT(*) AS paper_count
            FROM papers
            WHERE TRIM(COALESCE(journal, '')) != ''
            GROUP BY journal
            ORDER BY paper_count DESC, journal ASC
            LIMIT ?
            """,
            (topJournalLimit,),
        ).fetchall();
    finally:
        connection.close();

    papersByYear = [
        {"year": year, "count": count}
        for year, count in yearRows
    ];
    topJournals = [
        {"journal": journal, "count": count}
        for journal, count in journalRows
    ];
    return OverviewMetrics(
        totalPapers = totalPapers,
        totalJournals = totalJournals,
        papersByYear = papersByYear,
        topJournals = topJournals,
    );
