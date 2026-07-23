from pathlib import Path

import streamlit as st

from src.auth.service import getCurrentUserName, isAuthConfigured, isLoggedIn
from src.ui.theme import applyTheme


st.set_page_config(page_title="Meditoktok", page_icon="🔬", layout="wide")
applyTheme()


def renderLanding() -> None:
    st.markdown(
        """
        <section class="hero-shell">
            <p class="hero-kicker">PubMed research workspace</p>
            <h1 class="hero-title">논문 탐색을<br>더 또렷하게.</h1>
            <p class="hero-copy">Meditoktok은 PubMed 메타데이터를 검색하고, 필터링하고, 연구 맥락 안에서 대화할 수 있는 분석 도구입니다.</p>
            <div class="feature-line">
                <span class="feature-chip">키워드 검색</span>
                <span class="feature-chip">연도·저널 필터</span>
                <span class="feature-chip">연구 대화 메모리</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


if isAuthConfigured() and not isLoggedIn():
    st.markdown(
        "<style>[data-testid=\"stSidebar\"] { display: none; }</style>",
        unsafe_allow_html=True,
    )
    renderLanding()
    _, loginColumn, _ = st.columns([1, 1, 1])
    with loginColumn:
        if st.button("Google로 시작하기", use_container_width=True):
            st.login()
    st.stop()

if not isAuthConfigured():
    st.info("Google OAuth가 아직 설정되지 않아 개발 모드로 실행 중입니다.", icon="ℹ️")

pageDefinitions = []
overviewPath = Path("pages/01_overview.py")
if overviewPath.exists():
    pageDefinitions.append(st.Page(str(overviewPath), title="개요", icon="📊"))
pageDefinitions.extend(
    [
        st.Page("pages/02_papers.py", title="논문 검색", icon="🔎"),
        st.Page("pages/03_chat.py", title="연구 챗봇", icon="💬"),
    ]
)

with st.sidebar:
    st.caption(f"{getCurrentUserName()}님")
    if isAuthConfigured() and st.button("로그아웃", use_container_width=True):
        st.logout()

navigation = st.navigation(pageDefinitions)
navigation.run()
