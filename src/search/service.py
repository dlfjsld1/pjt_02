import csv
import io
from collections.abc import Iterable
from typing import Any


def firstValue(paper: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = paper.get(key)
        if value not in (None, ""):
            return value
    return default


def parseYear(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(str(value)[:4])
    except ValueError:
        return None


def normalizePaper(paper: dict[str, Any]) -> dict[str, Any]:
    return {
        "pmid": str(firstValue(paper, "pmid", "id")),
        "title": str(firstValue(paper, "title", "article_title")),
        "abstract": str(firstValue(paper, "abstract", "abstract_text")),
        "journal": str(firstValue(paper, "journal", "journal_name", "source")),
        "year": parseYear(firstValue(paper, "year", "pub_year", "publication_year", "publication_date")),
        "authors": firstValue(paper, "authors", "author_list"),
        "doi": str(firstValue(paper, "doi")),
    }


def filterPapers(
    papers: Iterable[dict[str, Any]],
    keyword: str = "",
    startYear: int | None = None,
    endYear: int | None = None,
    journal: str = "전체",
) -> list[dict[str, Any]]:
    normalizedKeyword = keyword.strip().casefold()
    results: list[dict[str, Any]] = []
    for rawPaper in papers:
        paper = normalizePaper(rawPaper)
        searchableText = f"{paper['title']} {paper['abstract']}".casefold()
        if normalizedKeyword and normalizedKeyword not in searchableText:
            continue
        if startYear is not None and (paper["year"] is None or paper["year"] < startYear):
            continue
        if endYear is not None and (paper["year"] is None or paper["year"] > endYear):
            continue
        if journal and journal != "전체" and paper["journal"] != journal:
            continue
        results.append(paper)
    return sorted(results, key=lambda paper: paper["year"] or 0, reverse=True)


def getJournalOptions(papers: Iterable[dict[str, Any]]) -> list[str]:
    journals = {normalizePaper(paper)["journal"] for paper in papers}
    return ["전체", *sorted(journal for journal in journals if journal)]


def papersToCsv(papers: Iterable[dict[str, Any]]) -> bytes:
    output = io.StringIO()
    fieldNames = ["pmid", "title", "abstract", "journal", "year", "authors", "doi"]
    writer = csv.DictWriter(output, fieldnames=fieldNames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(papers)
    return output.getvalue().encode("utf-8-sig")

