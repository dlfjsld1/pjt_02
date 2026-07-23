"""Business workflow for collecting and storing PubMed papers."""

from __future__ import annotations;

from pathlib import Path;

from .models import CollectionResult;
from .paperRepository import DEFAULT_DATABASE_PATH, connectDatabase, savePapers;
from .pubmedClient import PubMedClient;
from .searchCriteria import validateSearchCriteria;
from .xmlParser import parsePubMedArticles;


def collectPapers(
    keyword: str,
    startYear: int,
    endYear: int,
    maxResults: int,
    *,
    databasePath: str | Path = DEFAULT_DATABASE_PATH,
    client: PubMedClient | None = None,
) -> CollectionResult:
    """Collect PubMed papers in batches and save only previously unseen PMIDs."""

    criteria, errors = validateSearchCriteria(keyword, startYear, endYear, maxResults);

    if errors or criteria is None:
        raise ValueError(" ".join(errors));

    pubmedClient = client if client is not None else PubMedClient();
    pmids = pubmedClient.searchPmids(criteria);
    xmlText = pubmedClient.fetchArticles(pmids);
    papers = parsePubMedArticles(xmlText);

    connection = connectDatabase(databasePath);

    try:
        insertedCount, skippedCount = savePapers(connection, papers);
    finally:
        connection.close();

    return CollectionResult(
        requestedCount = len(pmids),
        fetchedCount = len(papers),
        insertedCount = insertedCount,
        skippedCount = skippedCount,
        pmids = pmids,
    );
