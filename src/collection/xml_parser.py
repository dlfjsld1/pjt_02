"""XML normalization for PubMed efetch responses."""

from __future__ import annotations

import re
from xml.etree import ElementTree

from .models import Paper


def get_node_text(node: ElementTree.Element | None) -> str:
    """Return all text in an XML node with normalized whitespace."""

    if node is None:
        return ""

    return " ".join("".join(node.itertext()).split())


def get_publication_year(article: ElementTree.Element) -> int | None:
    """Extract the best available publication year from one PubMed article."""

    year_paths = [
        ".//JournalIssue/PubDate/Year",
        ".//ArticleDate/Year",
    ]

    for path in year_paths:
        value = get_node_text(article.find(path))

        if value.isdigit() and len(value) == 4:
            return int(value)

    medline_date = get_node_text(article.find(".//JournalIssue/PubDate/MedlineDate"))
    match = re.search(r"\b(\d{4})\b", medline_date)
    return int(match.group(1)) if match else None


def get_authors(article: ElementTree.Element) -> str:
    """Normalize article author names into one text field."""

    authors: list[str] = []

    for author in article.findall(".//AuthorList/Author"):
        collective_name = get_node_text(author.find("CollectiveName"))

        if collective_name:
            authors.append(collective_name)
            continue

        fore_name = get_node_text(author.find("ForeName"))
        last_name = get_node_text(author.find("LastName"))
        full_name = " ".join(part for part in [fore_name, last_name] if part)

        if full_name:
            authors.append(full_name)

    return ", ".join(authors)


def parse_pubmed_articles(xml_text: str) -> list[Paper]:
    """Parse a PubMed efetch XML document into normalized paper metadata."""

    if not xml_text.strip():
        return []

    root = ElementTree.fromstring(xml_text)
    papers: list[Paper] = []

    for article in root.findall(".//PubmedArticle"):
        pmid = get_node_text(article.find(".//MedlineCitation/PMID"))

        if not pmid:
            continue

        papers.append(
            Paper(
                pmid = pmid,
                title = get_node_text(article.find(".//ArticleTitle")),
                abstract = " ".join(
                    get_node_text(node)
                    for node in article.findall(".//Abstract/AbstractText")
                    if get_node_text(node)
                ),
                journal = get_node_text(article.find(".//Journal/ISOAbbreviation"))
                or get_node_text(article.find(".//Journal/Title")),
                pub_year = get_publication_year(article),
                authors = get_authors(article),
            )
        )

    return papers
