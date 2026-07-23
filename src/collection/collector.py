"""Business workflow for collecting and storing PubMed papers."""

from __future__ import annotations;

from .models import CollectionResult;
from .paperRepository import PaperRepository, PaperStore;
from .pubmedClient import PubMedClient;
from .searchCriteria import validateSearchCriteria;
from .xmlParser import parsePubMedArticles;


def collectPapers(
    keyword: str,
    startYear: int,
    endYear: int,
    maxResults: int,
    *,
    client: PubMedClient | None = None,
    repository: PaperStore | None = None,
) -> CollectionResult:
    """Collect PubMed papers in batches and save only previously unseen PMIDs."""

    criteria, errors = validateSearchCriteria(keyword, startYear, endYear, maxResults);

    if errors or criteria is None:
        raise ValueError(" ".join(errors));

    pubmedClient = client if client is not None else PubMedClient();
    pmids = pubmedClient.searchPmids(criteria);
    xmlText = pubmedClient.fetchArticles(pmids);
    papers = parsePubMedArticles(xmlText);

    paperRepository = repository if repository is not None else PaperRepository();
    insertedCount, skippedCount = paperRepository.savePapers(papers);

    return CollectionResult(
        requestedCount = len(pmids),
        fetchedCount = len(papers),
        insertedCount = insertedCount,
        skippedCount = skippedCount,
        pmids = pmids,
    );
