"""Unit tests for the shared Supabase paper repository."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from src.collection.models import Paper
from src.collection.paperRepository import PaperRepository


class FakePaperQuery:
    """Small PostgREST query double used by repository tests."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.selectedFields = "*"
        self.filteredPmids: set[str] | None = None
        self.insertRows: list[dict[str, Any]] | None = None
        self.resultLimit: int | None = None

    def select(self, fields: str) -> FakePaperQuery:
        self.selectedFields = fields
        return self

    def in_(self, fieldName: str, values: list[str]) -> FakePaperQuery:
        assert fieldName == "pmid"
        self.filteredPmids = set(values)
        return self

    def insert(self, rows: list[dict[str, Any]]) -> FakePaperQuery:
        self.insertRows = rows
        return self

    def order(self, fieldName: str, desc: bool = False) -> FakePaperQuery:
        assert fieldName == "pub_year"
        self.rows.sort(key = lambda row: row.get(fieldName) or 0, reverse = desc)
        return self

    def limit(self, limit: int) -> FakePaperQuery:
        self.resultLimit = limit
        return self

    def execute(self) -> SimpleNamespace:
        if self.insertRows is not None:
            self.rows.extend(self.insertRows)
            return SimpleNamespace(data = list(self.insertRows))
        resultRows = list(self.rows)
        if self.filteredPmids is not None:
            resultRows = [
                row for row in resultRows
                if str(row.get("pmid")) in self.filteredPmids
            ]
        if self.selectedFields == "pmid":
            resultRows = [{"pmid": row["pmid"]} for row in resultRows]
        if self.resultLimit is not None:
            resultRows = resultRows[:self.resultLimit]
        return SimpleNamespace(data = resultRows)


class FakeSupabaseClient:
    """Return a fresh query builder over one shared papers table."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def table(self, tableName: str) -> FakePaperQuery:
        assert tableName == "papers"
        return FakePaperQuery(self.rows)


def testPaperRepositoryStoresLoadsAndSkipsThreeDuplicatePapers() -> None:
    client = FakeSupabaseClient()
    repository = PaperRepository(client = client)
    papers = [
        Paper("1", "Asthma A", "A", "Journal A", 2024, "Author A"),
        Paper("2", "Asthma B", "B", "Journal A", 2024, "Author B"),
        Paper("3", "Asthma C", "C", "Journal B", 2023, "Author C"),
    ]

    firstInserted, firstSkipped = repository.savePapers(papers)
    secondInserted, secondSkipped = repository.savePapers(papers)
    storedPapers = repository.loadPapers()

    assert (firstInserted, firstSkipped) == (3, 0)
    assert (secondInserted, secondSkipped) == (0, 3)
    assert len(storedPapers) == 3
    assert {paper["pmid"] for paper in storedPapers} == {"1", "2", "3"}
