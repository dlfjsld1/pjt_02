from pathlib import Path

import streamlit as st

from src.auth.service import get_current_user_name, is_auth_configured, is_logged_in
from src.ui.theme import apply_theme


st.set_page_config(page_title="Meditoktok", page_icon="🔬", layout="wide")
apply_theme()


def render_landing() -> None:
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


if is_auth_configured() and not is_logged_in():
    st.markdown(
        "<style>[data-testid=\"stSidebar\"] { display: none; }</style>",
        unsafe_allow_html=True,
    )
    render_landing()
    _, login_column, _ = st.columns([1, 1, 1])
    with login_column:
        if st.button("Google로 시작하기", use_container_width=True):
            st.login()
    st.stop()

if not is_auth_configured():
    st.info("Google OAuth가 아직 설정되지 않아 개발 모드로 실행 중입니다.", icon="ℹ️")

page_definitions = []
overview_path = Path("pages/01_overview.py")
if overview_path.exists():
    page_definitions.append(st.Page(str(overview_path), title="개요", icon="📊"))
page_definitions.extend(
    [
        st.Page("pages/02_papers.py", title="논문 검색", icon="🔎"),
        st.Page("pages/03_chat.py", title="연구 챗봇", icon="💬"),
    ]
)

with st.sidebar:
    st.caption(f"{get_current_user_name()}님")
    if is_auth_configured() and st.button("로그아웃", use_container_width=True):
        st.logout()

navigation = st.navigation(page_definitions)
navigation.run()
