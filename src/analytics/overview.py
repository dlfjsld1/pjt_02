"""Paper aggregates for the Supabase-backed overview page."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from src.collection.paperRepository import PaperRepository, PaperStore


@dataclass(frozen = True)
class OverviewMetrics:
    """Database totals and chart-ready aggregates."""

    totalPapers: int
    totalJournals: int
    papersByYear: list[dict[str, int]]
    topJournals: list[dict[str, str | int]]


def getOverviewMetrics(
    repository: PaperStore | None = None,
    topJournalLimit: int = 10,
) -> OverviewMetrics:
    """Load the same Supabase papers used by collection and search."""

    paperRepository = repository if repository is not None else PaperRepository()
    papers = paperRepository.loadPapers(limit = 10000)
    yearCounts = Counter(
        int(paper["pub_year"])
        for paper in papers
        if paper.get("pub_year") is not None
    )
    journalCounts = Counter(
        str(paper["journal"]).strip()
        for paper in papers
        if str(paper.get("journal") or "").strip()
    )
    papersByYear = [
        {"year": year, "count": yearCounts[year]}
        for year in sorted(yearCounts)
    ]
    topJournals: list[dict[str, Any]] = [
        {"journal": journal, "count": count}
        for journal, count in sorted(
            journalCounts.items(),
            key = lambda item: (-item[1], item[0]),
        )[:topJournalLimit]
    ]
    return OverviewMetrics(
        totalPapers = len(papers),
        totalJournals = len(journalCounts),
        papersByYear = papersByYear,
        topJournals = topJournals,
    )
