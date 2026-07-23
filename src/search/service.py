import csv
import io
from collections.abc import Iterable
from typing import Any


def first_value(paper: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = paper.get(key)
        if value not in (None, ""):
            return value
    return default


def parse_year(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(str(value)[:4])
    except ValueError:
        return None


def normalize_paper(paper: dict[str, Any]) -> dict[str, Any]:
    return {
        "pmid": str(first_value(paper, "pmid", "id")),
        "title": str(first_value(paper, "title", "article_title")),
        "abstract": str(first_value(paper, "abstract", "abstract_text")),
        "journal": str(first_value(paper, "journal", "journal_name", "source")),
        "year": parse_year(first_value(paper, "year", "pub_year", "publication_year", "publication_date")),
        "authors": first_value(paper, "authors", "author_list"),
        "doi": str(first_value(paper, "doi")),
    }


def filter_papers(
    papers: Iterable[dict[str, Any]],
    keyword: str = "",
    start_year: int | None = None,
    end_year: int | None = None,
    journal: str = "전체",
) -> list[dict[str, Any]]:
    normalized_keyword = keyword.strip().casefold()
    results: list[dict[str, Any]] = []
    for raw_paper in papers:
        paper = normalize_paper(raw_paper)
        searchable_text = f"{paper['title']} {paper['abstract']}".casefold()
        if normalized_keyword and normalized_keyword not in searchable_text:
            continue
        if start_year is not None and (paper["year"] is None or paper["year"] < start_year):
            continue
        if end_year is not None and (paper["year"] is None or paper["year"] > end_year):
            continue
        if journal and journal != "전체" and paper["journal"] != journal:
            continue
        results.append(paper)
    return sorted(results, key=lambda paper: paper["year"] or 0, reverse=True)


def get_journal_options(papers: Iterable[dict[str, Any]]) -> list[str]:
    journals = {normalize_paper(paper)["journal"] for paper in papers}
    return ["전체", *sorted(journal for journal in journals if journal)]


def papers_to_csv(papers: Iterable[dict[str, Any]]) -> bytes:
    output = io.StringIO()
    field_names = ["pmid", "title", "abstract", "journal", "year", "authors", "doi"]
    writer = csv.DictWriter(output, fieldnames=field_names, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(papers)
    return output.getvalue().encode("utf-8-sig")

