"""Unit tests for the shared Supabase paper repository."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from src.collection.models import Paper
from src.collection.paper_repository import PaperRepository


class FakePaperQuery:
    """Small PostgREST query double used by repository tests."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.selected_fields = "*"
        self.filtered_pmids: set[str] | None = None
        self.insert_rows: list[dict[str, Any]] | None = None
        self.result_limit: int | None = None

    def select(self, fields: str) -> FakePaperQuery:
        self.selected_fields = fields
        return self

    def in_(self, field_name: str, values: list[str]) -> FakePaperQuery:
        assert field_name == "pmid"
        self.filtered_pmids = set(values)
        return self

    def insert(self, rows: list[dict[str, Any]]) -> FakePaperQuery:
        self.insert_rows = rows
        return self

    def order(self, field_name: str, desc: bool = False) -> FakePaperQuery:
        assert field_name == "pub_year"
        self.rows.sort(key = lambda row: row.get(field_name) or 0, reverse = desc)
        return self

    def limit(self, limit: int) -> FakePaperQuery:
        self.result_limit = limit
        return self

    def execute(self) -> SimpleNamespace:
        if self.insert_rows is not None:
            self.rows.extend(self.insert_rows)
            return SimpleNamespace(data = list(self.insert_rows))
        result_rows = list(self.rows)
        if self.filtered_pmids is not None:
            result_rows = [
                row for row in result_rows
                if str(row.get("pmid")) in self.filtered_pmids
            ]
        if self.selected_fields == "pmid":
            result_rows = [{"pmid": row["pmid"]} for row in result_rows]
        if self.result_limit is not None:
            result_rows = result_rows[:self.result_limit]
        return SimpleNamespace(data = result_rows)


class FakeSupabaseClient:
    """Return a fresh query builder over one shared papers table."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def table(self, table_name: str) -> FakePaperQuery:
        assert table_name == "papers"
        return FakePaperQuery(self.rows)


def test_paper_repository_stores_loads_and_skips_three_duplicate_papers() -> None:
    client = FakeSupabaseClient()
    repository = PaperRepository(client = client)
    papers = [
        Paper("1", "Asthma A", "A", "Journal A", 2024, "Author A"),
        Paper("2", "Asthma B", "B", "Journal A", 2024, "Author B"),
        Paper("3", "Asthma C", "C", "Journal B", 2023, "Author C"),
    ]

    first_inserted, first_skipped = repository.save_papers(papers)
    second_inserted, second_skipped = repository.save_papers(papers)
    stored_papers = repository.load_papers()

    assert (first_inserted, first_skipped) == (3, 0)
    assert (second_inserted, second_skipped) == (0, 3)
    assert len(stored_papers) == 3
    assert {paper["pmid"] for paper in stored_papers} == {"1", "2", "3"}
