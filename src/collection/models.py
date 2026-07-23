"""Data models used by the PubMed collection workflow."""

from __future__ import annotations;

from dataclasses import dataclass;


@dataclass(frozen = True)
class Paper:
    """Normalized PubMed paper metadata stored in the papers table."""

    pmid: str;
    title: str;
    abstract: str;
    journal: str;
    pubYear: int | None;
    authors: str;


@dataclass(frozen = True)
class CollectionResult:
    """Counts and identifiers produced by one collection request."""

    requestedCount: int;
    fetchedCount: int;
    insertedCount: int;
    skippedCount: int;
    pmids: list[str];
