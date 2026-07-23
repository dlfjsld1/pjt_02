"""Paper aggregates for the Supabase-backed overview page."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from src.collection.paper_repository import PaperRepository, PaperStore


@dataclass(frozen = True)
class OverviewMetrics:
    """Database totals and chart-ready aggregates."""

    total_papers: int
    total_journals: int
    papers_by_year: list[dict[str, int]]
    top_journals: list[dict[str, str | int]]


def get_overview_metrics(
    repository: PaperStore | None = None,
    top_journal_limit: int = 10,
) -> OverviewMetrics:
    """Load the same Supabase papers used by collection and search."""

    paper_repository = repository if repository is not None else PaperRepository()
    papers = paper_repository.load_papers(limit = 10000)
    year_counts = Counter(
        int(paper["pub_year"])
        for paper in papers
        if paper.get("pub_year") is not None
    )
    journal_counts = Counter(
        str(paper["journal"]).strip()
        for paper in papers
        if str(paper.get("journal") or "").strip()
    )
    papers_by_year = [
        {"year": year, "count": year_counts[year]}
        for year in sorted(year_counts)
    ]
    top_journals: list[dict[str, Any]] = [
        {"journal": journal, "count": count}
        for journal, count in sorted(
            journal_counts.items(),
            key = lambda item: (-item[1], item[0]),
        )[:top_journal_limit]
    ]
    return OverviewMetrics(
        total_papers = len(papers),
        total_journals = len(journal_counts),
        papers_by_year = papers_by_year,
        top_journals = top_journals,
    )
