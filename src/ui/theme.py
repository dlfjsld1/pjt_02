import streamlit as st


APP_CSS = """
<style>
:root {
    --canvas: #edf3f1;
    --surface: #f5faf8;
    --ink: #173832;
    --muted: #5d756f;
    --accent: #147d6b;
    --accent-dark: #0d5f51;
    --radius: 22px;
}
.stApp {
    background:
        radial-gradient(circle at 85% 8%, rgba(93, 189, 167, 0.24), transparent 24rem),
        var(--canvas);
    color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
.block-container {
    max-width: 1200px;
    padding-top: clamp(1.5rem, 4vw, 3rem);
    padding-bottom: 2.5rem;
}
h1, h2, h3, p, label { color: var(--ink); }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
.hero-shell {
    max-width: 920px;
    margin: clamp(2rem, 8vh, 5rem) auto 1.5rem;
    padding: clamp(2rem, 6vw, 4.5rem);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 34px;
    background: rgba(245, 250, 248, 0.78);
    box-shadow: 18px 18px 42px rgba(85, 113, 106, 0.18), -18px -18px 42px rgba(255, 255, 255, 0.82);
}
.hero-kicker {
    color: var(--accent-dark);
    font-size: 0.82rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.hero-title {
    max-width: 760px;
    margin: 0.5rem 0 1rem;
    font-size: clamp(2.5rem, 7vw, 5.6rem);
    line-height: 0.96;
    letter-spacing: -0.055em;
}
.hero-copy {
    max-width: 620px;
    color: var(--muted);
    font-size: 1.08rem;
    line-height: 1.75;
}
.feature-line {
    display: flex;
    flex-wrap: wrap;
    gap: 0.7rem;
    margin-top: 1.8rem;
}
.feature-chip {
    padding: 0.58rem 0.86rem;
    border: 1px solid rgba(20, 125, 107, 0.16);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.52);
    color: var(--accent-dark);
    font-size: 0.88rem;
    font-weight: 650;
}
.stButton > button, .stDownloadButton > button {
    min-height: 2.75rem;
    border: 0;
    border-radius: 14px;
    background: var(--accent);
    color: white;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 7px 7px 16px rgba(57, 101, 92, 0.18), -5px -5px 13px rgba(255, 255, 255, 0.72);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: var(--accent-dark);
    color: white;
}
[data-testid="stMain"] button[data-testid^="stBaseButton"] p {
    color: white !important;
}
.stTextInput input, .stNumberInput input, [data-baseweb="select"] > div {
    border: 1px solid rgba(20, 125, 107, 0.25);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.78);
    color: var(--ink);
}
[data-testid="stMetric"] {
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: var(--radius);
    background: rgba(245, 250, 248, 0.72);
    box-shadow: 8px 8px 20px rgba(85, 113, 106, 0.10), -8px -8px 20px rgba(255, 255, 255, 0.68);
}
[data-testid="stChatMessage"] {
    border: 1px solid rgba(255, 255, 255, 0.72);
    border-radius: var(--radius);
    background: rgba(245, 250, 248, 0.72);
    box-shadow: 8px 8px 20px rgba(85, 113, 106, 0.11), -8px -8px 20px rgba(255, 255, 255, 0.72);
}
[data-testid="stDataFrame"] {
    border: 1px solid rgba(20, 125, 107, 0.12);
    border-radius: var(--radius);
    overflow: hidden;
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition: none !important;
        animation: none !important;
    }
}
@media (max-width: 640px) {
    .block-container {
        padding: 1.25rem 1rem 2rem;
    }
    .hero-shell {
        margin-top: 1.25rem;
        border-radius: 26px;
    }
    .hero-title {
        font-size: clamp(2.4rem, 13vw, 3.6rem);
    }
    [data-testid="stSidebar"] {
        min-width: 0;
    }
}
</style>
"""


def apply_theme() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)

