"""Validation and request configuration for PubMed collection searches."""

from __future__ import annotations;

from dataclasses import dataclass;
import os;
from typing import Mapping;

MIN_RESULTS = 1;
MAX_RESULTS = 100;
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi";


@dataclass(frozen = True)
class SearchCriteria:
    """A validated set of values used to collect PubMed papers."""

    keyword: str;
    startYear: int;
    endYear: int;
    maxResults: int;


def validateSearchCriteria(
    keyword: str,
    startYear: int,
    endYear: int,
    maxResults: int,
) -> tuple[SearchCriteria | None, list[str]]:
    """Return validated criteria or the input errors without making a network request."""

    errors: list[str] = [];
    normalizedKeyword = keyword.strip();

    if not normalizedKeyword:
        errors.append("검색 키워드를 입력하세요.");

    if startYear > endYear:
        errors.append("검색 시작 연도는 종료 연도보다 클 수 없습니다.");

    if not MIN_RESULTS <= maxResults <= MAX_RESULTS:
        errors.append("최대 수집 논문 수는 1~100 사이여야 합니다.");

    if errors:
        return None, errors;

    criteria = SearchCriteria(
        keyword = normalizedKeyword,
        startYear = startYear,
        endYear = endYear,
        maxResults = maxResults,
    );
    return criteria, [];


def getNcbiApiKey(environment: Mapping[str, str] | None = None) -> str | None:
    """Read the optional NCBI API key from the environment."""

    source = environment if environment is not None else os.environ;
    apiKey = source.get("NCBI_API_KEY", "").strip();
    return apiKey or None;


def buildSearchRequest(
    criteria: SearchCriteria,
    environment: Mapping[str, str] | None = None,
) -> tuple[str, dict[str, str | int]]:
    """Build PubMed esearch parameters after the caller has validated input."""

    parameters: dict[str, str | int] = {
        "db": "pubmed",
        "term": (
            f"{criteria.keyword} AND "
            f"({criteria.startYear}:{criteria.endYear}[pdat])"
        ),
        "retmax": criteria.maxResults,
        "retmode": "json",
    };
    apiKey = getNcbiApiKey(environment);

    if apiKey:
        parameters["api_key"] = apiKey;

    return PUBMED_ESEARCH_URL, parameters;
