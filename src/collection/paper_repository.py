"""Supabase persistence for normalized PubMed papers."""

from __future__ import annotations

from typing import Any, Protocol

from .models import Paper


class PaperStore(Protocol):
    """Persistence contract shared by collection, overview, and search."""

    def save_papers(self, papers: list[Paper]) -> tuple[int, int]: ...

    def load_papers(self, limit: int = 1000) -> list[dict[str, Any]]: ...


class PaperRepository:
    """Store and load PubMed papers from the shared Supabase table."""

    def __init__(self, client: Any | None = None) -> None:
        if client is not None:
            self.client = client
            return
        from src.config import get_supabase_credentials

        supabase_url, supabase_key = get_supabase_credentials()
        if not supabase_url or not supabase_key:
            raise RuntimeError("Supabase URL과 서버 키를 secrets.toml에 설정해 주세요.")
        if supabase_key.startswith("sb_publishable_"):
            raise RuntimeError(
                "SUPABASE_SECRET_KEY에는 publishable 키가 아닌 sb_secret 서버 키를 설정해 주세요."
            )
        from supabase import create_client

        self.client = create_client(supabase_url, supabase_key)

    def save_papers(self, papers: list[Paper]) -> tuple[int, int]:
        if not papers:
            return 0, 0
        pmids = [paper.pmid for paper in papers]
        existing_response = (
            self.client.table("papers")
            .select("pmid")
            .in_("pmid", pmids)
            .execute()
        )
        existing_pmids = {str(row["pmid"]) for row in existing_response.data or []}
        new_papers = [paper for paper in papers if paper.pmid not in existing_pmids]
        if new_papers:
            self.client.table("papers").insert(
                [self.serialize_paper(paper) for paper in new_papers]
            ).execute()
        return len(new_papers), len(papers) - len(new_papers)

    def load_papers(self, limit: int = 1000) -> list[dict[str, Any]]:
        response = (
            self.client.table("papers")
            .select("pmid, title, abstract, journal, pub_year, authors")
            .order("pub_year", desc = True)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])

    @staticmethod
    def serialize_paper(paper: Paper) -> dict[str, Any]:
        return {
            "pmid": paper.pmid,
            "title": paper.title,
            "abstract": paper.abstract,
            "journal": paper.journal,
            "pub_year": paper.pub_year,
            "authors": paper.authors,
        }


def save_papers(repository: PaperStore, papers: list[Paper]) -> tuple[int, int]:
    """Save papers through the shared repository contract."""

    return repository.save_papers(papers)
