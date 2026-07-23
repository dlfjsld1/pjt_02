"""Sidebar controls for PubMed paper collection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.collection.collector import collect_papers
from src.collection.models import CollectionResult
from src.collection.search_criteria import SearchCriteria, validate_search_criteria


@dataclass(frozen = True)
class CollectionSidebarResult:
    """The validated sidebar submission for the collection workflow."""

    criteria: SearchCriteria | None
    collect_requested: bool
    collection_result: CollectionResult | None


def render_collection_sidebar() -> CollectionSidebarResult:
    """Render collection inputs and return criteria only when the submission is valid."""

    import streamlit as st

    current_year = date.today().year
    st.sidebar.header("논문 수집")
    keyword = st.sidebar.text_input("검색 키워드", key = "collectionKeyword")
    start_year = st.sidebar.number_input(
        "검색 시작 연도",
        min_value = 1900,
        max_value = current_year,
        value = current_year,
        step = 1,
        key = "collectionStartYear",
    )
    end_year = st.sidebar.number_input(
        "검색 종료 연도",
        min_value = 1900,
        max_value = current_year,
        value = current_year,
        step = 1,
        key = "collectionEndYear",
    )
    max_results = st.sidebar.number_input(
        "최대 수집 논문 수",
        min_value = 1,
        max_value = 100,
        value = 100,
        step = 1,
        key = "collectionMaxResults",
    )
    collect_requested = st.sidebar.button("논문 수집", key = "collectPapers")

    if not collect_requested:
        return CollectionSidebarResult(
            criteria = None,
            collect_requested = False,
            collection_result = None,
        )

    criteria, errors = validate_search_criteria(
        keyword = keyword,
        start_year = int(start_year),
        end_year = int(end_year),
        max_results = int(max_results),
    )

    for error in errors:
        st.sidebar.error(error)

    if criteria is None:
        return CollectionSidebarResult(
            criteria = None,
            collect_requested = True,
            collection_result = None,
        )

    try:
        with st.sidebar.spinner("PubMed 논문을 수집하고 있습니다..."):
            collection_result = collect_papers(
                criteria.keyword,
                criteria.start_year,
                criteria.end_year,
                criteria.max_results,
            )
    except Exception:
        st.sidebar.error("논문 수집에 실패했습니다. 네트워크와 API 설정을 확인한 뒤 다시 시도해 주세요.")
        return CollectionSidebarResult(
            criteria = criteria,
            collect_requested = True,
            collection_result = None,
        )

    st.sidebar.success(
        f"신규 {collection_result.inserted_count}건, "
        f"중복 건너뜀 {collection_result.skipped_count}건"
    )
    st.session_state["collectionLastResult"] = {
        "insertedCount": collection_result.inserted_count,
        "skippedCount": collection_result.skipped_count,
    }
    return CollectionSidebarResult(
        criteria = criteria,
        collect_requested = True,
        collection_result = collection_result,
    )
