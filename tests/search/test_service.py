from src.search.service import filter_papers, papers_to_csv


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


def test_filter_papers_combines_keyword_year_and_journal() -> None:
    results = filter_papers(
        PAPERS,
        keyword="diabetes",
        start_year=2023,
        end_year=2025,
        journal="Nature Medicine",
    )
    assert [paper["pmid"] for paper in results] == ["1"]


def test_papers_to_csv_uses_utf8_bom() -> None:
    csv_content = papers_to_csv(filter_papers(PAPERS))
    assert csv_content.startswith(b"\xef\xbb\xbf")
    assert b"Diabetes treatment review" in csv_content

