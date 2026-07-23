"""Supabase persistence for normalized PubMed papers."""

from __future__ import annotations;

from typing import Any, Protocol;

from .models import Paper;


class PaperStore(Protocol):
    """Persistence contract shared by collection, overview, and search."""

    def savePapers(self, papers: list[Paper]) -> tuple[int, int]: ...

    def loadPapers(self, limit: int = 1000) -> list[dict[str, Any]]: ...


class PaperRepository:
    """Store and load PubMed papers from the shared Supabase table."""

    def __init__(self, client: Any | None = None) -> None:
        if client is not None:
            self.client = client;
            return;
        from src.config import getSupabaseCredentials;

        supabaseUrl, supabaseKey = getSupabaseCredentials();
        if not supabaseUrl or not supabaseKey:
            raise RuntimeError("Supabase URL과 서버 키를 secrets.toml에 설정해 주세요.");
        if supabaseKey.startswith("sb_publishable_"):
            raise RuntimeError(
                "SUPABASE_SECRET_KEY에는 publishable 키가 아닌 sb_secret 서버 키를 설정해 주세요."
            );
        from supabase import create_client;

        self.client = create_client(supabaseUrl, supabaseKey);

    def savePapers(self, papers: list[Paper]) -> tuple[int, int]:
        if not papers:
            return 0, 0;
        pmids = [paper.pmid for paper in papers];
        existingResponse = (
            self.client.table("papers")
            .select("pmid")
            .in_("pmid", pmids)
            .execute()
        );
        existingPmids = {str(row["pmid"]) for row in existingResponse.data or []};
        newPapers = [paper for paper in papers if paper.pmid not in existingPmids];
        if newPapers:
            self.client.table("papers").insert(
                [self.serializePaper(paper) for paper in newPapers]
            ).execute();
        return len(newPapers), len(papers) - len(newPapers);

    def loadPapers(self, limit: int = 1000) -> list[dict[str, Any]]:
        response = (
            self.client.table("papers")
            .select("pmid, title, abstract, journal, pub_year, authors")
            .order("pub_year", desc = True)
            .limit(limit)
            .execute()
        );
        return list(response.data or []);

    @staticmethod
    def serializePaper(paper: Paper) -> dict[str, Any]:
        return {
            "pmid": paper.pmid,
            "title": paper.title,
            "abstract": paper.abstract,
            "journal": paper.journal,
            "pub_year": paper.pubYear,
            "authors": paper.authors,
        };


def savePapers(repository: PaperStore, papers: list[Paper]) -> tuple[int, int]:
    """Save papers through the shared repository contract."""

    return repository.savePapers(papers);
