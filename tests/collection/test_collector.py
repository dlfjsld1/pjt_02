"""Unit tests for PubMed collection, XML parsing, and repository deduplication."""

from __future__ import annotations

import unittest

from src.collection.collector import collect_papers
from src.collection.models import Paper
from src.collection.pubmed_client import PUBMED_EFETCH_URL, PubMedClient
from src.collection.xml_parser import parse_pubmed_articles

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
        self.search_error: Exception | None = None
        self.search_payload: object = {"esearchresult": {"idlist": ["1001", "1002"]}}

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

        response = FakeResponse(payload = self.search_payload)
        response.error = self.search_error
        return response


class InMemoryPaperRepository:
    """Repository double that follows the shared Supabase contract."""

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


class CollectorTest(unittest.TestCase):
    """Verify collection behavior without calling the real PubMed API."""

    def setUp(self) -> None:
        self.session = FakeSession()
        self.client = PubMedClient(session = self.session, environment = {"NCBI_API_KEY": "test-key"})
        self.repository = InMemoryPaperRepository()

    def test_collect_papers_stores_metadata_and_skips_existing_pmids(self) -> None:
        first_result = collect_papers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            client = self.client,
            repository = self.repository,
        )
        second_result = collect_papers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            client = self.client,
            repository = self.repository,
        )

        self.assertEqual(first_result.requested_count, 2)
        self.assertEqual(first_result.fetched_count, 2)
        self.assertEqual(first_result.inserted_count, 2)
        self.assertEqual(first_result.skipped_count, 0)
        self.assertEqual(first_result.pmids, ["1001", "1002"])
        stored_paper = self.repository.papers["1001"]
        self.assertEqual(
            (
                stored_paper.pmid,
                stored_paper.title,
                stored_paper.abstract,
                stored_paper.journal,
                stored_paper.pub_year,
                stored_paper.authors,
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
        self.assertEqual(second_result.inserted_count, 0)
        self.assertEqual(second_result.skipped_count, 2)

    def test_collect_papers_uses_batch_fetch_with_timeout_and_api_key(self) -> None:
        collect_papers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            client = self.client,
            repository = self.repository,
        )

        search_url, search_parameters, search_timeout = self.session.calls[0]
        fetch_url, fetch_parameters, fetch_timeout = self.session.calls[1]
        self.assertIn("esearch.fcgi", search_url)
        self.assertEqual(search_parameters["api_key"], "test-key")
        self.assertEqual(search_timeout, 15)
        self.assertEqual(fetch_url, PUBMED_EFETCH_URL)
        self.assertEqual(fetch_parameters["id"], "1001,1002")
        self.assertEqual(fetch_parameters["api_key"], "test-key")
        self.assertEqual(fetch_timeout, 15)

    def test_parse_pub_med_articles_handles_missing_metadata(self) -> None:
        papers = parse_pubmed_articles(SAMPLE_XML)

        self.assertEqual(papers[0].abstract, "Background text. Result text.")
        self.assertEqual(papers[0].authors, "Ada Kim, Research Group")
        self.assertEqual(papers[1].journal, "Journal Two")
        self.assertEqual(papers[1].pub_year, 2023)
        self.assertEqual(papers[1].abstract, "")
        self.assertEqual(papers[1].authors, "")

    def test_collect_papers_rejects_invalid_input_before_request(self) -> None:
        with self.assertRaisesRegex(ValueError, "검색 키워드"):
            collect_papers(
                " ",
                2022,
                2025,
                100,
                client = self.client,
                repository = self.repository,
            )

        self.assertEqual(self.session.calls, [])

    def test_collect_papers_propagates_http_errors(self) -> None:
        self.session.search_error = RuntimeError("HTTP 500")

        with self.assertRaisesRegex(RuntimeError, "HTTP 500"):
            collect_papers(
                "COVID-19 vaccine",
                2022,
                2025,
                100,
                client = self.client,
                repository = self.repository,
            )

    def test_collect_papers_rejects_malformed_search_response(self) -> None:
        self.session.search_payload = ["not", "an", "object"]

        with self.assertRaisesRegex(ValueError, "응답 형식"):
            collect_papers(
                "COVID-19 vaccine",
                2022,
                2025,
                100,
                client = self.client,
                repository = self.repository,
            )
