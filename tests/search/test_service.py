from src.search.service import filterPapers, papersToCsv


PAPERS = [
    {
        "pmid": "1",
        "title": "Diabetes treatment review",
        "abstract": "A systematic review",
        "journal": "Nature Medicine",
        "pub_year": 2024,
    },
    {
        "pmid": "2",
        "title": "Cancer immunotherapy",
        "abstract": "Long-term outcomes",
        "journal": "The Lancet",
        "pub_year": 2021,
    },
]


def testFilterPapersCombinesKeywordYearAndJournal() -> None:
    results = filterPapers(
        PAPERS,
        keyword="diabetes",
        startYear=2023,
        endYear=2025,
        journal="Nature Medicine",
    )
    assert [paper["pmid"] for paper in results] == ["1"]


def testPapersToCsvUsesUtf8Bom() -> None:
    csvContent = papersToCsv(filterPapers(PAPERS))
    assert csvContent.startswith(b"\xef\xbb\xbf")
    assert b"Diabetes treatment review" in csvContent

