"""Integration test for collection, overview, and search sharing one store."""

from __future__ import annotations

from typing import Any

from src.analytics.overview import get_overview_metrics
from src.collection.collector import collect_papers
from src.collection.models import Paper
from src.search.service import filter_papers


THREE_PAPERS_XML = """
<PubmedArticleSet>
  <PubmedArticle><MedlineCitation><PMID>91001</PMID><Article>
    <ArticleTitle>Asthma biomarkers study</ArticleTitle>
    <Abstract><AbstractText>Biomarker analysis.</AbstractText></Abstract>
    <Journal><Title>Respiratory Research</Title><JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue></Journal>
  </Article></MedlineCitation></PubmedArticle>
  <PubmedArticle><MedlineCitation><PMID>91002</PMID><Article>
    <ArticleTitle>Asthma treatment outcomes</ArticleTitle>
    <Abstract><AbstractText>Outcome analysis.</AbstractText></Abstract>
    <Journal><Title>Respiratory Research</Title><JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue></Journal>
  </Article></MedlineCitation></PubmedArticle>
  <PubmedArticle><MedlineCitation><PMID>91003</PMID><Article>
    <ArticleTitle>Asthma cohort review</ArticleTitle>
    <Abstract><AbstractText>Cohort analysis.</AbstractText></Abstract>
    <Journal><Title>Clinical Pulmonology</Title><JournalIssue><PubDate><Year>2023</Year></PubDate></JournalIssue></Journal>
  </Article></MedlineCitation></PubmedArticle>
</PubmedArticleSet>
"""


class FakePubMedClient:
    """Return three deterministic PubMed records."""

    def search_pmids(self, criteria: Any) -> list[str]:
        return ["91001", "91002", "91003"]

    def fetch_articles(self, pmids: list[str]) -> str:
        return THREE_PAPERS_XML


class InMemoryPaperRepository:
    """One shared store observed by every feature in the test."""

    def __init__(self) -> None:
        self.papers: dict[str, Paper] = {}

    def save_papers(self, papers: list[Paper]) -> tuple[int, int]:
        inserted_count = 0
        for paper in papers:
            if paper.pmid in self.papers:
                continue
            self.papers[paper.pmid] = paper
            inserted_count += 1
        return inserted_count, len(papers) - inserted_count

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
            for paper in list(self.papers.values())[:limit]
        ]


def test_collection_overview_and_search_use_the_same_three_papers() -> None:
    repository = InMemoryPaperRepository()
    client = FakePubMedClient()

    first_result = collect_papers(
        "asthma",
        2023,
        2024,
        3,
        client = client,
        repository = repository,
    )
    second_result = collect_papers(
        "asthma",
        2023,
        2024,
        3,
        client = client,
        repository = repository,
    )
    stored_papers = repository.load_papers()
    overview_metrics = get_overview_metrics(repository)
    search_results = filter_papers(stored_papers, keyword = "asthma")

    assert first_result.inserted_count == 3
    assert first_result.skipped_count == 0
    assert second_result.inserted_count == 0
    assert second_result.skipped_count == 3
    assert len(stored_papers) == 3
    assert overview_metrics.total_papers == 3
    assert len(search_results) == 3
    assert {paper["pmid"] for paper in search_results} == {"91001", "91002", "91003"}
