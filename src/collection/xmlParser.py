"""XML normalization for PubMed efetch responses."""

from __future__ import annotations;

import re;
from xml.etree import ElementTree;

from .models import Paper;


def getNodeText(node: ElementTree.Element | None) -> str:
    """Return all text in an XML node with normalized whitespace."""

    if node is None:
        return "";

    return " ".join("".join(node.itertext()).split());


def getPublicationYear(article: ElementTree.Element) -> int | None:
    """Extract the best available publication year from one PubMed article."""

    yearPaths = [
        ".//JournalIssue/PubDate/Year",
        ".//ArticleDate/Year",
    ];

    for path in yearPaths:
        value = getNodeText(article.find(path));

        if value.isdigit() and len(value) == 4:
            return int(value);

    medlineDate = getNodeText(article.find(".//JournalIssue/PubDate/MedlineDate"));
    match = re.search(r"\b(\d{4})\b", medlineDate);
    return int(match.group(1)) if match else None;


def getAuthors(article: ElementTree.Element) -> str:
    """Normalize article author names into one text field."""

    authors: list[str] = [];

    for author in article.findall(".//AuthorList/Author"):
        collectiveName = getNodeText(author.find("CollectiveName"));

        if collectiveName:
            authors.append(collectiveName);
            continue;

        foreName = getNodeText(author.find("ForeName"));
        lastName = getNodeText(author.find("LastName"));
        fullName = " ".join(part for part in [foreName, lastName] if part);

        if fullName:
            authors.append(fullName);

    return ", ".join(authors);


def parsePubMedArticles(xmlText: str) -> list[Paper]:
    """Parse a PubMed efetch XML document into normalized paper metadata."""

    if not xmlText.strip():
        return [];

    root = ElementTree.fromstring(xmlText);
    papers: list[Paper] = [];

    for article in root.findall(".//PubmedArticle"):
        pmid = getNodeText(article.find(".//MedlineCitation/PMID"));

        if not pmid:
            continue;

        papers.append(
            Paper(
                pmid = pmid,
                title = getNodeText(article.find(".//ArticleTitle")),
                abstract = " ".join(
                    getNodeText(node)
                    for node in article.findall(".//Abstract/AbstractText")
                    if getNodeText(node)
                ),
                journal = getNodeText(article.find(".//Journal/ISOAbbreviation"))
                or getNodeText(article.find(".//Journal/Title")),
                pubYear = getPublicationYear(article),
                authors = getAuthors(article),
            )
        );

    return papers;
