"""Streamlit overview page for collected PubMed papers."""

from __future__ import annotations

import streamlit as st

from components.collection_sidebar import render_collection_sidebar
from src.analytics.overview import get_overview_metrics
from src.auth.service import require_login
from src.ui.theme import apply_theme

st.set_page_config(page_title = "논문 개요", page_icon = "📊", layout = "wide")
require_login()
apply_theme()

render_collection_sidebar()
last_collection_result = st.session_state.get(
    "collectionLastResult",
    {"insertedCount": 0, "skippedCount": 0},
)
overview_metrics = get_overview_metrics()

st.title("PubMed 논문 개요")
st.caption("수집한 논문의 규모와 연도, 저널 분포를 한눈에 확인하세요.")
total_column, inserted_column, skipped_column, journal_column = st.columns(4)
total_column.metric("전체 논문 수", overview_metrics.total_papers)
inserted_column.metric("방금 수집한 신규 논문 수", last_collection_result["insertedCount"])
skipped_column.metric("방금 건너뛴 중복 논문 수", last_collection_result["skippedCount"])
journal_column.metric("총 저널 수", overview_metrics.total_journals)

year_column, journal_chart_column = st.columns(2)

with year_column:
    st.subheader("연도별 논문 수")

    if overview_metrics.papers_by_year:
        st.bar_chart(overview_metrics.papers_by_year, x = "year", y = "count")
    else:
        st.info("표시할 연도별 논문 데이터가 없습니다.")

with journal_chart_column:
    st.subheader("논문 수 기준 상위 저널")

    if overview_metrics.top_journals:
        st.bar_chart(overview_metrics.top_journals, x = "journal", y = "count")
    else:
        st.info("표시할 저널 데이터가 없습니다.")
