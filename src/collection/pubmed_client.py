"""HTTP client for the PubMed E-utilities endpoints."""

from __future__ import annotations

from typing import Mapping, Protocol

from .search_criteria import SearchCriteria, build_search_request, get_ncbi_api_key

PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
REQUEST_TIMEOUT_SECONDS = 15


class HttpResponse(Protocol):
    """The small response surface required from an HTTP client."""

    def json(self) -> object: ...

    @property
    def text(self) -> str: ...

    def raise_for_status(self) -> None: ...


class HttpSession(Protocol):
    """The small session surface required from an HTTP client."""

    def get(
        self,
        url: str,
        *,
        params: Mapping[str, str | int],
        timeout: int,
    ) -> HttpResponse: ...


def get_default_session() -> HttpSession:
    """Create the requests session only when a real PubMed request is needed."""

    import requests

    return requests.Session()


class PubMedClient:
    """Fetch PubMed identifiers and metadata with explicit timeout handling."""

    def __init__(
        self,
        session: HttpSession | None = None,
        environment: Mapping[str, str] | None = None,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self.session = session if session is not None else get_default_session()
        self.environment = environment
        self.timeout = timeout

    def search_pmids(self, criteria: SearchCriteria) -> list[str]:
        """Return PubMed identifiers for validated search criteria."""

        url, parameters = build_search_request(criteria, self.environment)
        response = self.session.get(url, params = parameters, timeout = self.timeout)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("PubMed 검색 응답 형식이 올바르지 않습니다.")

        result = payload.get("esearchresult", {})

        if not isinstance(result, dict):
            raise ValueError("PubMed 검색 응답 형식이 올바르지 않습니다.")

        id_list = result.get("idlist", [])

        if not isinstance(id_list, list) or not all(isinstance(pmid, str) for pmid in id_list):
            raise ValueError("PubMed 검색 응답에 PMID 목록이 없습니다.")

        return id_list[: criteria.max_results]

    def fetch_articles(self, pmids: list[str]) -> str:
        """Return XML metadata for a batch of PubMed identifiers."""

        if not pmids:
            return ""

        parameters: dict[str, str | int] = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        api_key = get_ncbi_api_key(self.environment)

        if api_key:
            parameters["api_key"] = api_key

        response = self.session.get(
            PUBMED_EFETCH_URL,
            params = parameters,
            timeout = self.timeout,
        )
        response.raise_for_status()
        return response.text
