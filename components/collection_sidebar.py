"""Sidebar controls for PubMed paper collection."""

from __future__ import annotations;

from dataclasses import dataclass;
from datetime import date;

from src.collection.collector import collectPapers;
from src.collection.models import CollectionResult;
from src.collection.searchCriteria import SearchCriteria, validateSearchCriteria;


@dataclass(frozen = True)
class CollectionSidebarResult:
    """The validated sidebar submission for the collection workflow."""

    criteria: SearchCriteria | None;
    collectRequested: bool;
    collectionResult: CollectionResult | None;


def renderCollectionSidebar() -> CollectionSidebarResult:
    """Render collection inputs and return criteria only when the submission is valid."""

    import streamlit as st;

    currentYear = date.today().year;
    st.sidebar.header("논문 수집");
    keyword = st.sidebar.text_input("검색 키워드", key = "collectionKeyword");
    startYear = st.sidebar.number_input(
        "검색 시작 연도",
        min_value = 1900,
        max_value = currentYear,
        value = currentYear,
        step = 1,
        key = "collectionStartYear",
    );
    endYear = st.sidebar.number_input(
        "검색 종료 연도",
        min_value = 1900,
        max_value = currentYear,
        value = currentYear,
        step = 1,
        key = "collectionEndYear",
    );
    maxResults = st.sidebar.number_input(
        "최대 수집 논문 수",
        min_value = 1,
        max_value = 100,
        value = 100,
        step = 1,
        key = "collectionMaxResults",
    );
    collectRequested = st.sidebar.button("논문 수집", key = "collectPapers");

    if not collectRequested:
        return CollectionSidebarResult(
            criteria = None,
            collectRequested = False,
            collectionResult = None,
        );

    criteria, errors = validateSearchCriteria(
        keyword = keyword,
        startYear = int(startYear),
        endYear = int(endYear),
        maxResults = int(maxResults),
    );

    for error in errors:
        st.sidebar.error(error);

    if criteria is None:
        return CollectionSidebarResult(
            criteria = None,
            collectRequested = True,
            collectionResult = None,
        );

    try:
        collectionResult = collectPapers(
            criteria.keyword,
            criteria.startYear,
            criteria.endYear,
            criteria.maxResults,
        );
    except Exception as error:
        st.sidebar.error(f"논문 수집에 실패했습니다: {error}");
        return CollectionSidebarResult(
            criteria = criteria,
            collectRequested = True,
            collectionResult = None,
        );

    st.sidebar.success(
        f"신규 {collectionResult.insertedCount}건, "
        f"중복 건너뜀 {collectionResult.skippedCount}건"
    );
    st.session_state["collectionLastResult"] = {
        "insertedCount": collectionResult.insertedCount,
        "skippedCount": collectionResult.skippedCount,
    };
    return CollectionSidebarResult(
        criteria = criteria,
        collectRequested = True,
        collectionResult = collectionResult,
    );
