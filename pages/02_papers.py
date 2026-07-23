import pandas as pd
import streamlit as st

from src.auth.service import requireLogin
from src.search.repository import PaperRepository
from src.search.service import filterPapers, getJournalOptions, normalizePaper, papersToCsv
from src.ui.theme import applyTheme


requireLogin()
applyTheme()
st.title("논문 검색")
st.caption("Supabase에 수집된 PubMed 논문을 키워드, 출판 연도, 저널로 좁혀 보세요.")


@st.cache_data(ttl=300, show_spinner=False)
def loadPapers() -> list[dict]:
    return PaperRepository().loadPapers()


try:
    rawPapers = loadPapers()
except Exception:
    st.error("논문 데이터를 불러오지 못했습니다. Supabase 설정과 papers 테이블을 확인해 주세요.")
    st.stop()

if not rawPapers:
    st.info("아직 수집된 논문이 없습니다. 먼저 PubMed 수집을 실행해 주세요.")
    st.stop()

normalizedPapers = [normalizePaper(paper) for paper in rawPapers]
availableYears = [paper["year"] for paper in normalizedPapers if paper["year"] is not None]
minimumYear = min(availableYears) if availableYears else 1900
maximumYear = max(availableYears) if availableYears else 2100

keyword = st.text_input("검색어", placeholder="예: diabetes, cancer immunotherapy")
filterColumn, journalColumn = st.columns([2, 1])
with filterColumn:
    selectedYears = st.slider(
        "출판 연도",
        min_value=minimumYear,
        max_value=maximumYear,
        value=(minimumYear, maximumYear),
    )
with journalColumn:
    selectedJournal = st.selectbox("저널", getJournalOptions(rawPapers))

filteredPapers = filterPapers(
    rawPapers,
    keyword=keyword,
    startYear=selectedYears[0],
    endYear=selectedYears[1],
    journal=selectedJournal,
)

resultColumn, downloadColumn = st.columns([4, 1])
with resultColumn:
    st.subheader(f"검색 결과 {len(filteredPapers):,}건")
with downloadColumn:
    st.download_button(
        "CSV 다운로드",
        data=papersToCsv(filteredPapers),
        file_name="meditoktok_papers.csv",
        mime="text/csv",
        disabled=not filteredPapers,
        use_container_width=True,
    )

if not filteredPapers:
    st.info("조건에 맞는 논문이 없습니다. 검색어나 필터 범위를 바꿔 보세요.")
else:
    displayColumns = ["pmid", "title", "journal", "year", "doi"]
    st.dataframe(
        pd.DataFrame(filteredPapers)[displayColumns],
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
