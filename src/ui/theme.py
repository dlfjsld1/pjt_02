import streamlit as st


APP_CSS = """
<style>
:root {
    --canvas: #edf1f9;
    --surface: #f7f9fe;
    --ink: #14213d;
    --muted: #71809d;
    --accent: #5b6bff;
    --accent-dark: #4858e8;
    --accent-soft: #e1e5ff;
    --radius: 22px;
    --shadow: 13px 15px 30px rgba(77, 91, 139, 0.16), -10px -10px 24px rgba(255, 255, 255, 0.86), inset 1px 1px 1px rgba(255, 255, 255, 0.78), inset -1px -1px 1px rgba(75, 87, 133, 0.08);
    --shadow-soft: 8px 10px 22px rgba(77, 91, 139, 0.12), -7px -7px 18px rgba(255, 255, 255, 0.80);
}
.stApp {
    background:
        radial-gradient(circle at 13% 12%, rgba(255, 143, 120, 0.14), transparent 24rem),
        radial-gradient(circle at 90% 85%, rgba(102, 117, 232, 0.14), transparent 30rem),
        var(--canvas);
    color: var(--ink);
    font-family: "Plus Jakarta Sans", Pretendard, "Noto Sans KR", ui-sans-serif, system-ui, sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: rgba(235, 239, 251, 0.74);
    border-right: 1px solid rgba(255, 255, 255, 0.78);
}
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
    border-radius: 42px 30px 42px 30px;
    background: rgba(247, 249, 254, 0.82);
    box-shadow: var(--shadow);
}
.hero-kicker {
    color: var(--accent-dark);
    font-size: 0.82rem;
    font-weight: 750;
    letter-spacing: 0.09em;
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
    border: 1px solid rgba(255, 255, 255, 0.86);
    border-radius: 999px;
    background: var(--accent-soft);
    color: var(--accent-dark);
    font-size: 0.88rem;
    font-weight: 650;
    box-shadow: var(--shadow-soft);
}
.stButton > button, .stDownloadButton > button {
    min-height: 2.75rem;
    border: 0;
    border-radius: 16px 13px 18px 13px;
    background: linear-gradient(145deg, #7b89ef, var(--accent-dark));
    color: white;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 6px 8px 15px rgba(79, 95, 212, 0.27), inset 2px 2px 2px rgba(255, 255, 255, 0.23);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(145deg, #8b98f4, var(--accent-dark));
    color: white;
    transform: translateY(-2px);
}
[data-testid="stMain"] button[data-testid^="stBaseButton"] p {
    color: white !important;
}
.stTextInput input, .stNumberInput input, [data-baseweb="select"] > div, [data-testid="stChatInput"] textarea {
    border: 1px solid transparent;
    border-radius: 14px;
    background: var(--surface);
    color: var(--ink);
    box-shadow: inset 5px 5px 12px rgba(75, 87, 133, 0.13), inset -5px -5px 12px rgba(255, 255, 255, 0.82);
}
.stTextInput input:focus, .stNumberInput input:focus, [data-testid="stChatInput"] textarea:focus {
    border-color: rgba(91, 107, 255, 0.35);
    box-shadow: inset 5px 5px 12px rgba(75, 87, 133, 0.13), inset -5px -5px 12px rgba(255, 255, 255, 0.82), 0 0 0 4px rgba(91, 107, 255, 0.12);
}
[data-testid="stNumberInputContainer"] {
    overflow: hidden;
    border: 1px solid transparent;
    border-radius: 14px;
    background: var(--surface);
    box-shadow: inset 5px 5px 12px rgba(75, 87, 133, 0.13), inset -5px -5px 12px rgba(255, 255, 255, 0.82);
}
[data-testid="stNumberInputContainer"] input {
    box-shadow: none;
}
[data-testid="stNumberInputContainer"] button {
    min-width: 2rem;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: var(--ink);
    box-shadow: none;
}
[data-testid="stNumberInputContainer"] button:hover:not(:disabled) {
    background: var(--accent-soft);
    color: var(--accent-dark);
    transform: none;
}
[data-testid="stMetric"] {
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: var(--radius) 16px 26px 16px;
    background: rgba(255, 255, 255, 0.70);
    box-shadow: var(--shadow-soft);
}
[data-testid="stChatMessage"] {
    border: 1px solid rgba(255, 255, 255, 0.80);
    border-radius: 22px 22px 22px 8px;
    background: rgba(255, 255, 255, 0.86);
    box-shadow: var(--shadow-soft);
}
[data-testid="stChatInput"] {
    border: 1px solid rgba(255, 255, 255, 0.86);
    border-radius: 24px 18px 26px 18px;
    background: rgba(255, 255, 255, 0.86);
    box-shadow: var(--shadow);
}
[data-testid="stChatInput"] > div {
    background: transparent;
}
[data-testid="stChatInput"] textarea {
    padding: 0.55rem 0.9rem;
    border: 0;
    border-radius: 16px;
    background: transparent;
    box-shadow: none;
}
[data-testid="stChatInput"] textarea:focus {
    border: 0;
    box-shadow: none;
}
[data-testid="stChatInput"] button {
    min-width: 2.5rem;
    min-height: 2.5rem;
    border-radius: 16px 13px 18px 13px;
    background: linear-gradient(145deg, #7b89ef, var(--accent-dark));
    box-shadow: 6px 8px 15px rgba(79, 95, 212, 0.27), inset 2px 2px 2px rgba(255, 255, 255, 0.23);
}
[data-testid="stAlert"] {
    border-radius: 16px 13px 18px 13px;
    border: 1px solid rgba(255, 255, 255, 0.82);
    box-shadow: var(--shadow-soft);
}
[data-testid="stDataFrame"] {
    border: 1px solid rgba(91, 107, 255, 0.14);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}
[data-testid="stVegaLiteChart"] {
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.80);
    border-radius: var(--radius);
    background: rgba(255, 255, 255, 0.70);
    box-shadow: var(--shadow-soft);
}
[data-testid="stVegaLiteChart"] svg.marks {
    background-color: transparent !important;
}
[data-testid="stVegaLiteChart"] .role-axis text {
    fill: var(--ink) !important;
}
[data-testid="stVegaLiteChart"] .role-axis-grid line,
[data-testid="stVegaLiteChart"] .role-axis path,
[data-testid="stVegaLiteChart"] .role-axis line {
    stroke: rgba(20, 33, 61, 0.16) !important;
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

