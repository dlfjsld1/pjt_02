"""Unit tests for PubMed collection, XML parsing, and repository deduplication."""

from __future__ import annotations

import unittest

from src.collection.collector import collectPapers
from src.collection.models import Paper
from src.collection.pubmedClient import PUBMED_EFETCH_URL, PubMedClient
from src.collection.xmlParser import parsePubMedArticles

SAMPLE_XML = """
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation><PMID>1001</PMID><Article>
      <ArticleTitle>First vaccine paper</ArticleTitle>
      <Abstract><AbstractText Label="BACKGROUND">Background text.</AbstractText>
      <AbstractText>Result text.</AbstractText></Abstract>
      <Journal><ISOAbbreviation>Vaccine</ISOAbbreviation><JournalIssue>
        <PubDate><Year>2022</Year></PubDate>
      </JournalIssue></Journal>
      <AuthorList><Author><ForeName>Ada</ForeName><LastName>Kim</LastName></Author>
      <Author><CollectiveName>Research Group</CollectiveName></Author></AuthorList>
    </Article></MedlineCitation>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation><PMID>1002</PMID><Article>
      <ArticleTitle>Second vaccine paper</ArticleTitle>
      <Journal><Title>Journal Two</Title><JournalIssue>
        <PubDate><MedlineDate>2023 Jan-Feb</MedlineDate></PubDate>
      </JournalIssue></Journal>
      <AuthorList />
    </Article></MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


class FakeResponse:
    """A deterministic response used instead of a real PubMed API response."""

    def __init__(self, payload: object = None, text: str = "") -> None:
        self.payload = payload if payload is not None else {}
        self.text = text
        self.error: Exception | None = None

    def json(self) -> object:
        return self.payload

    def raise_for_status(self) -> None:
        if self.error:
            raise self.error


class FakeSession:
    """A session that records requests and returns fixed search and fetch payloads."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str | int], int]] = []
        self.searchError: Exception | None = None
        self.searchPayload: object = {"esearchresult": {"idlist": ["1001", "1002"]}}

    def get(
        self,
        url: str,
        *,
        params: dict[str, str | int],
        timeout: int,
    ) -> FakeResponse:
        self.calls.append((url, params, timeout))

        if url == PUBMED_EFETCH_URL:
            return FakeResponse(text = SAMPLE_XML)

        response = FakeResponse(payload = self.searchPayload)
        response.error = self.searchError
        return response


class InMemoryPaperRepository:
    """Repository double that follows the shared Supabase contract."""

    def __init__(self) -> None:
        self.papers: dict[str, Paper] = {}

    def savePapers(self, papers: list[Paper]) -> tuple[int, int]:
        insertedCount = 0
        for paper in papers:
            if paper.pmid in self.papers:
                continue
            self.papers[paper.pmid] = paper
            insertedCount += 1
        return insertedCount, len(papers) - insertedCount

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
        ]


class CollectorTest(unittest.TestCase):
    """Verify collection behavior without calling the real PubMed API."""

    def setUp(self) -> None:
        self.session = FakeSession()
        self.client = PubMedClient(session = self.session, environment = {"NCBI_API_KEY": "test-key"})
        self.repository = InMemoryPaperRepository()

    def testCollectPapersStoresMetadataAndSkipsExistingPmids(self) -> None:
        firstResult = collectPapers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            client = self.client,
            repository = self.repository,
        )
        secondResult = collectPapers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            client = self.client,
            repository = self.repository,
        )

        self.assertEqual(firstResult.requestedCount, 2)
        self.assertEqual(firstResult.fetchedCount, 2)
        self.assertEqual(firstResult.insertedCount, 2)
        self.assertEqual(firstResult.skippedCount, 0)
        self.assertEqual(firstResult.pmids, ["1001", "1002"])
        storedPaper = self.repository.papers["1001"]
        self.assertEqual(
            (
                storedPaper.pmid,
                storedPaper.title,
                storedPaper.abstract,
                storedPaper.journal,
                storedPaper.pubYear,
                storedPaper.authors,
            ),
            (
                "1001",
                "First vaccine paper",
                "Background text. Result text.",
                "Vaccine",
                2022,
                "Ada Kim, Research Group",
            ),
        )
        self.assertEqual(secondResult.insertedCount, 0)
        self.assertEqual(secondResult.skippedCount, 2)

    def testCollectPapersUsesBatchFetchWithTimeoutAndApiKey(self) -> None:
        collectPapers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            client = self.client,
            repository = self.repository,
        )

        searchUrl, searchParameters, searchTimeout = self.session.calls[0]
        fetchUrl, fetchParameters, fetchTimeout = self.session.calls[1]
        self.assertIn("esearch.fcgi", searchUrl)
        self.assertEqual(searchParameters["api_key"], "test-key")
        self.assertEqual(searchTimeout, 15)
        self.assertEqual(fetchUrl, PUBMED_EFETCH_URL)
        self.assertEqual(fetchParameters["id"], "1001,1002")
        self.assertEqual(fetchParameters["api_key"], "test-key")
        self.assertEqual(fetchTimeout, 15)

    def testParsePubMedArticlesHandlesMissingMetadata(self) -> None:
        papers = parsePubMedArticles(SAMPLE_XML)

        self.assertEqual(papers[0].abstract, "Background text. Result text.")
        self.assertEqual(papers[0].authors, "Ada Kim, Research Group")
        self.assertEqual(papers[1].journal, "Journal Two")
        self.assertEqual(papers[1].pubYear, 2023)
        self.assertEqual(papers[1].abstract, "")
        self.assertEqual(papers[1].authors, "")

    def testCollectPapersRejectsInvalidInputBeforeRequest(self) -> None:
        with self.assertRaisesRegex(ValueError, "검색 키워드"):
            collectPapers(
                " ",
                2022,
                2025,
                100,
                client = self.client,
                repository = self.repository,
            )

        self.assertEqual(self.session.calls, [])

    def testCollectPapersPropagatesHttpErrors(self) -> None:
        self.session.searchError = RuntimeError("HTTP 500")

        with self.assertRaisesRegex(RuntimeError, "HTTP 500"):
            collectPapers(
                "COVID-19 vaccine",
                2022,
                2025,
                100,
                client = self.client,
                repository = self.repository,
            )

    def testCollectPapersRejectsMalformedSearchResponse(self) -> None:
        self.session.searchPayload = ["not", "an", "object"]

        with self.assertRaisesRegex(ValueError, "응답 형식"):
            collectPapers(
                "COVID-19 vaccine",
                2022,
                2025,
                100,
                client = self.client,
                repository = self.repository,
            )
