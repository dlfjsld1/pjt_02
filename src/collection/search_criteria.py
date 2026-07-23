"""Validation and request configuration for PubMed collection searches."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping

MIN_RESULTS = 1
MAX_RESULTS = 100
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


@dataclass(frozen = True)
class SearchCriteria:
    """A validated set of values used to collect PubMed papers."""

    keyword: str
    start_year: int
    end_year: int
    max_results: int


def validate_search_criteria(
    keyword: str,
    start_year: int,
    end_year: int,
    max_results: int,
) -> tuple[SearchCriteria | None, list[str]]:
    """Return validated criteria or the input errors without making a network request."""

    errors: list[str] = []
    normalized_keyword = keyword.strip()

    if not normalized_keyword:
        errors.append("검색 키워드를 입력하세요.")

    if start_year > end_year:
        errors.append("검색 시작 연도는 종료 연도보다 클 수 없습니다.")

    if not MIN_RESULTS <= max_results <= MAX_RESULTS:
        errors.append("최대 수집 논문 수는 1~100 사이여야 합니다.")

    if errors:
        return None, errors

    criteria = SearchCriteria(
        keyword = normalized_keyword,
        start_year = start_year,
        end_year = end_year,
        max_results = max_results,
    )
    return criteria, []


def get_ncbi_api_key(environment: Mapping[str, str] | None = None) -> str | None:
    """Read the optional NCBI API key from the environment."""

    source = environment if environment is not None else os.environ
    api_key = source.get("NCBI_API_KEY", "").strip()
    return api_key or None


def build_search_request(
    criteria: SearchCriteria,
    environment: Mapping[str, str] | None = None,
) -> tuple[str, dict[str, str | int]]:
    """Build PubMed esearch parameters after the caller has validated input."""

    parameters: dict[str, str | int] = {
        "db": "pubmed",
        "term": (
            f"{criteria.keyword} AND "
                f"({criteria.start_year}:{criteria.end_year}[pdat])"
        ),
        "retmax": criteria.max_results,
        "retmode": "json",
    }
    api_key = get_ncbi_api_key(environment)

    if api_key:
        parameters["api_key"] = api_key

    return PUBMED_ESEARCH_URL, parameters
