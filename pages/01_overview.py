"""Streamlit overview page for collected PubMed papers."""

from __future__ import annotations

import streamlit as st

from components.collection_sidebar import renderCollectionSidebar
from src.analytics.overview import getOverviewMetrics

st.set_page_config(page_title = "논문 개요", page_icon = "📊", layout = "wide")

renderCollectionSidebar()
lastCollectionResult = st.session_state.get(
    "collectionLastResult",
    {"insertedCount": 0, "skippedCount": 0},
)
overviewMetrics = getOverviewMetrics()

st.title("PubMed 논문 개요")
totalColumn, insertedColumn, skippedColumn, journalColumn = st.columns(4)
totalColumn.metric("전체 논문 수", overviewMetrics.totalPapers)
insertedColumn.metric("방금 수집한 신규 논문 수", lastCollectionResult["insertedCount"])
skippedColumn.metric("방금 건너뛴 중복 논문 수", lastCollectionResult["skippedCount"])
journalColumn.metric("총 저널 수", overviewMetrics.totalJournals)

yearColumn, journalChartColumn = st.columns(2)

with yearColumn:
    st.subheader("연도별 논문 수")

    if overviewMetrics.papersByYear:
        st.bar_chart(overviewMetrics.papersByYear, x = "year", y = "count")
    else:
        st.info("표시할 연도별 논문 데이터가 없습니다.")

with journalChartColumn:
    st.subheader("논문 수 기준 상위 저널")

    if overviewMetrics.topJournals:
        st.bar_chart(overviewMetrics.topJournals, x = "journal", y = "count")
    else:
        st.info("표시할 저널 데이터가 없습니다.")
