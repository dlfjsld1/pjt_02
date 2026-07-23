"""Business workflow for collecting and storing PubMed papers."""

from __future__ import annotations

from .models import CollectionResult
from .paper_repository import PaperRepository, PaperStore
from .pubmed_client import PubMedClient
from .search_criteria import validate_search_criteria
from .xml_parser import parse_pubmed_articles


def collect_papers(
    keyword: str,
    start_year: int,
    end_year: int,
    max_results: int,
    *,
    client: PubMedClient | None = None,
    repository: PaperStore | None = None,
) -> CollectionResult:
    """Collect PubMed papers in batches and save only previously unseen PMIDs."""

    criteria, errors = validate_search_criteria(keyword, start_year, end_year, max_results)

    if errors or criteria is None:
        raise ValueError(" ".join(errors))

    pubmed_client = client if client is not None else PubMedClient()
    pmids = pubmed_client.search_pmids(criteria)
    xml_text = pubmed_client.fetch_articles(pmids)
    papers = parse_pubmed_articles(xml_text)

    paper_repository = repository if repository is not None else PaperRepository()
    inserted_count, skipped_count = paper_repository.save_papers(papers)

    return CollectionResult(
        requested_count = len(pmids),
        fetched_count = len(papers),
        inserted_count = inserted_count,
        skipped_count = skipped_count,
        pmids = pmids,
    )
