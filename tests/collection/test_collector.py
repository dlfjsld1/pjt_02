"""Unit tests for PubMed collection, XML parsing, and SQLite deduplication."""

from __future__ import annotations;

from pathlib import Path;
import sqlite3;
import tempfile;
import unittest;

from src.collection.collector import collectPapers;
from src.collection.pubmedClient import PUBMED_EFETCH_URL, PubMedClient;
from src.collection.xmlParser import parsePubMedArticles;

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
""";


class FakeResponse:
    """A deterministic response used instead of a real PubMed API response."""

    def __init__(self, payload: dict[str, object] | None = None, text: str = "") -> None:
        self.payload = payload or {};
        self.text = text;
        self.error: Exception | None = None;

    def json(self) -> dict[str, object]:
        return self.payload;

    def raise_for_status(self) -> None:
        if self.error:
            raise self.error;


class FakeSession:
    """A session that records requests and returns fixed search and fetch payloads."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str | int], int]] = [];
        self.searchError: Exception | None = None;

    def get(
        self,
        url: str,
        *,
        params: dict[str, str | int],
        timeout: int,
    ) -> FakeResponse:
        self.calls.append((url, params, timeout));

        if url == PUBMED_EFETCH_URL:
            return FakeResponse(text = SAMPLE_XML);

        response = FakeResponse(payload = {"esearchresult": {"idlist": ["1001", "1002"]}});
        response.error = self.searchError;
        return response;


class CollectorTest(unittest.TestCase):
    """Verify collection behavior without calling the real PubMed API."""

    def setUp(self) -> None:
        self.temporaryDirectory = tempfile.TemporaryDirectory();
        self.databasePath = Path(self.temporaryDirectory.name) / "pubmed.db";
        self.session = FakeSession();
        self.client = PubMedClient(session = self.session, environment = {"NCBI_API_KEY": "test-key"});

    def tearDown(self) -> None:
        self.temporaryDirectory.cleanup();

    def testCollectPapersStoresMetadataAndSkipsExistingPmids(self) -> None:
        firstResult = collectPapers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            databasePath = self.databasePath,
            client = self.client,
        );
        secondResult = collectPapers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            databasePath = self.databasePath,
            client = self.client,
        );

        self.assertEqual(firstResult.requestedCount, 2);
        self.assertEqual(firstResult.fetchedCount, 2);
        self.assertEqual(firstResult.insertedCount, 2);
        self.assertEqual(firstResult.skippedCount, 0);
        self.assertEqual(firstResult.pmids, ["1001", "1002"]);
        connection = sqlite3.connect(self.databasePath);

        try:
            paper = connection.execute(
                "SELECT pmid, title, abstract, journal, pub_year, authors FROM papers WHERE pmid = ?",
                ("1001",),
            ).fetchone();
        finally:
            connection.close();

        self.assertEqual(
            paper,
            (
                "1001",
                "First vaccine paper",
                "Background text. Result text.",
                "Vaccine",
                2022,
                "Ada Kim, Research Group",
            ),
        );
        self.assertEqual(secondResult.insertedCount, 0);
        self.assertEqual(secondResult.skippedCount, 2);

    def testCollectPapersUsesBatchFetchWithTimeoutAndApiKey(self) -> None:
        collectPapers(
            "COVID-19 vaccine",
            2022,
            2025,
            100,
            databasePath = self.databasePath,
            client = self.client,
        );

        searchUrl, searchParameters, searchTimeout = self.session.calls[0];
        fetchUrl, fetchParameters, fetchTimeout = self.session.calls[1];
        self.assertIn("esearch.fcgi", searchUrl);
        self.assertEqual(searchParameters["api_key"], "test-key");
        self.assertEqual(searchTimeout, 15);
        self.assertEqual(fetchUrl, PUBMED_EFETCH_URL);
        self.assertEqual(fetchParameters["id"], "1001,1002");
        self.assertEqual(fetchParameters["api_key"], "test-key");
        self.assertEqual(fetchTimeout, 15);

    def testParsePubMedArticlesHandlesMissingMetadata(self) -> None:
        papers = parsePubMedArticles(SAMPLE_XML);

        self.assertEqual(papers[0].abstract, "Background text. Result text.");
        self.assertEqual(papers[0].authors, "Ada Kim, Research Group");
        self.assertEqual(papers[1].journal, "Journal Two");
        self.assertEqual(papers[1].pubYear, 2023);
        self.assertEqual(papers[1].abstract, "");
        self.assertEqual(papers[1].authors, "");

    def testCollectPapersRejectsInvalidInputBeforeRequest(self) -> None:
        with self.assertRaisesRegex(ValueError, "검색 키워드"):
            collectPapers(
                " ",
                2022,
                2025,
                100,
                databasePath = self.databasePath,
                client = self.client,
            );

        self.assertEqual(self.session.calls, []);

    def testCollectPapersPropagatesHttpErrors(self) -> None:
        self.session.searchError = RuntimeError("HTTP 500");

        with self.assertRaisesRegex(RuntimeError, "HTTP 500"):
            collectPapers(
                "COVID-19 vaccine",
                2022,
                2025,
                100,
                databasePath = self.databasePath,
                client = self.client,
            );
