"""Integration test for collection, overview, and search sharing one store."""

from __future__ import annotations;

from typing import Any;

from src.analytics.overview import getOverviewMetrics;
from src.collection.collector import collectPapers;
from src.collection.models import Paper;
from src.search.service import filterPapers;


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
""";


class FakePubMedClient:
    """Return three deterministic PubMed records."""

    def searchPmids(self, criteria: Any) -> list[str]:
        return ["91001", "91002", "91003"];

    def fetchArticles(self, pmids: list[str]) -> str:
        return THREE_PAPERS_XML;


class InMemoryPaperRepository:
    """One shared store observed by every feature in the test."""

    def __init__(self) -> None:
        self.papers: dict[str, Paper] = {};

    def savePapers(self, papers: list[Paper]) -> tuple[int, int]:
        insertedCount = 0;
        for paper in papers:
            if paper.pmid in self.papers:
                continue;
            self.papers[paper.pmid] = paper;
            insertedCount += 1;
        return insertedCount, len(papers) - insertedCount;

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
            for paper in list(self.papers.values())[:limit]
        ];


def testCollectionOverviewAndSearchUseTheSameThreePapers() -> None:
    repository = InMemoryPaperRepository();
    client = FakePubMedClient();

    firstResult = collectPapers(
        "asthma",
        2023,
        2024,
        3,
        client = client,
        repository = repository,
    );
    secondResult = collectPapers(
        "asthma",
        2023,
        2024,
        3,
        client = client,
        repository = repository,
    );
    storedPapers = repository.loadPapers();
    overviewMetrics = getOverviewMetrics(repository);
    searchResults = filterPapers(storedPapers, keyword = "asthma");

    assert firstResult.insertedCount == 3;
    assert firstResult.skippedCount == 0;
    assert secondResult.insertedCount == 0;
    assert secondResult.skippedCount == 3;
    assert len(storedPapers) == 3;
    assert overviewMetrics.totalPapers == 3;
    assert len(searchResults) == 3;
    assert {paper["pmid"] for paper in searchResults} == {"91001", "91002", "91003"};
