import pandas as pd
import streamlit as st

from src.auth.service import require_login
from src.search.repository import PaperRepository
from src.search.service import filter_papers, get_journal_options, normalize_paper, papers_to_csv
from src.ui.theme import apply_theme


require_login()
apply_theme()
st.title("논문 검색")
st.caption("Supabase에 수집된 PubMed 논문을 키워드, 출판 연도, 저널로 좁혀 보세요.")


@st.cache_data(ttl=300, show_spinner=False)
def load_papers() -> list[dict]:
    return PaperRepository().load_papers()


try:
    raw_papers = load_papers()
except Exception:
    st.error("논문 데이터를 불러오지 못했습니다. Supabase 설정과 papers 테이블을 확인해 주세요.")
    st.stop()

if not raw_papers:
    st.info("아직 수집된 논문이 없습니다. 먼저 PubMed 수집을 실행해 주세요.")
    st.stop()

normalized_papers = [normalize_paper(paper) for paper in raw_papers]
available_years = [paper["year"] for paper in normalized_papers if paper["year"] is not None]
minimum_year = min(available_years) if available_years else 1900
maximum_year = max(available_years) if available_years else 2100

keyword = st.text_input("검색어", placeholder="예: diabetes, cancer immunotherapy")
filter_column, journal_column = st.columns([2, 1])
with filter_column:
    selected_years = st.slider(
        "출판 연도",
        min_value=minimum_year,
        max_value=maximum_year,
        value=(minimum_year, maximum_year),
    )
with journal_column:
    selected_journal = st.selectbox("저널", get_journal_options(raw_papers))

filtered_papers = filter_papers(
    raw_papers,
    keyword=keyword,
    start_year=selected_years[0],
    end_year=selected_years[1],
    journal=selected_journal,
)

result_column, download_column = st.columns([4, 1])
with result_column:
    st.subheader(f"검색 결과 {len(filtered_papers):,}건")
with download_column:
    st.download_button(
        "CSV 다운로드",
        data=papers_to_csv(filtered_papers),
        file_name="meditoktok_papers.csv",
        mime="text/csv",
        disabled=not filtered_papers,
        use_container_width=True,
    )

if not filtered_papers:
    st.info("조건에 맞는 논문이 없습니다. 검색어나 필터 범위를 바꿔 보세요.")
else:
    display_columns = ["pmid", "title", "journal", "year", "doi"]
    st.dataframe(
        pd.DataFrame(filtered_papers)[display_columns],
        hide_index=True,
        use_container_width=True,
        column_config={
            "pmid": "PMID",
            "title": "논문 제목",
            "journal": "저널",
            "year": "출판 연도",
            "doi": "DOI",
        },
    )
