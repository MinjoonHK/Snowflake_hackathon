import streamlit as st

from vitality_app import data, sidebar
from vitality_app.sidebar import TAB_KEYS
from vitality_app.session import get_session
from vitality_app.tabs import asset_tab, backtest_tab, consumer_tab, diagnostic_tab, report_tab, visitor_tab

st.set_page_config(page_title="Urban Vitality Index", page_icon="🏙️", layout="wide")

_COMMON_CSS = """
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
    }
    h1 { font-size: 28px; font-weight: 700; }
    h2 { font-size: 24px; font-weight: 600; }
    h3 { font-size: 20px; font-weight: 600; }
    [data-testid="stMetricLabel"]  { font-size: 12px !important; }
    [data-testid="stMetricValue"]  { font-size: 28px !important; font-weight: 700; }
    [data-testid="stMetricDelta"]  { font-size: 12px !important; }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #359efa !important;
        border-bottom: 2px solid #359efa !important;
    }
"""

_LIGHT_CSS = """
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dbdcdf;
        border-radius: 8px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { color: #70737c !important; }
    [data-testid="stMetricValue"] { color: #0f0f10 !important; }
    hr { border-color: #dbdcdf !important; }
    [data-testid="stDataFrame"] {
        border: 1px solid #dbdcdf;
        border-radius: 8px;
        overflow: hidden;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #e3effa !important;
        color: #1a4e7c !important;
    }
    [data-testid="stTabs"] button { color: #70737c; font-size: 14px; font-weight: 500; }
"""

_DARK_CSS = """
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {
        background-color: #0f0f10 !important;
        color: #ffffff !important;
    }
    /* inputs / widgets */
    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"],
    [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] > div > div {
        background-color: #171719 !important;
        color: #ffffff !important;
        border-color: #292a2d !important;
    }
    /* dropdown menus */
    [data-baseweb="popover"] ul, [data-baseweb="menu"] {
        background-color: #171719 !important;
        border: 1px solid #292a2d !important;
    }
    [data-baseweb="menu"] li:hover { background-color: #292a2d !important; }
    /* slider */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #359efa !important;
    }
    [data-testid="stSlider"] div[class*="StyledSliderTrack"] {
        background: linear-gradient(to right, #359efa 0%, #359efa var(--progress), #292a2d var(--progress)) !important;
    }
    /* sidebar */
    section[data-testid="stSidebar"] {
        background-color: #171719 !important;
        border-right: 1px solid #292a2d;
    }
    section[data-testid="stSidebar"] label { color: #989ba2 !important; font-size: 12px; }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input[type="radio"]:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #ffffff !important; }
    section[data-testid="stSidebar"] p { color: #989ba2 !important; }
    /* theme toggle + unselected locale: dark fill, white label (primary / selected unchanged) */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-color: #292a2d !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:hover,
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:focus-visible {
        background-color: #171719 !important;
        color: #ffffff !important;
        border-color: #359efa !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] p,
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] span {
        color: #ffffff !important;
    }
    /* selected locale: keep blue fill, force white label (sidebar p rule was graying it out) */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] p,
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] span {
        color: #ffffff !important;
    }
    /* tabs */
    [data-testid="stTabs"] button { color: #989ba2; font-size: 14px; font-weight: 500; }
    /* metric cards */
    [data-testid="stMetric"] {
        background-color: #171719;
        border: 1px solid #292a2d;
        border-radius: 8px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { color: #989ba2 !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    /* divider */
    hr { border-color: #292a2d !important; }
    /* dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #292a2d;
        border-radius: 8px;
        overflow: hidden;
    }
    /* multiselect */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #0f2c45 !important;
        color: #98ccfa !important;
    }
    /* general text */
    p, span, div, label { color: #ffffff; }
    .stMarkdown p { color: #ffffff !important; }
    /* info / warning boxes */
    [data-testid="stAlert"] { background-color: #171719 !important; border-color: #292a2d !important; }
"""


def _inject_theme(dark: bool) -> None:
    css = _COMMON_CSS + (_DARK_CSS if dark else _LIGHT_CSS)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
st.session_state.setdefault("locale", "ko")

_inject_theme(st.session_state.dark_mode)

session = get_session()

selected_tab = sidebar.render_sidebar()
sidebar.render_footer()

dark_mode = st.session_state.get("dark_mode", True)

city_df = data.load_available_cities()
city_codes = tuple(city_df["CITY_CODE"].tolist())
city_code_to_name = city_df.set_index("CITY_CODE")["CITY_KOR_NAME"].to_dict()

vitality_df = data.load_vitality_data(city_codes)
months = sorted(vitality_df["STANDARD_YEAR_MONTH"].unique())
selected_month = months[-1] if months else None

if selected_tab == TAB_KEYS[0]:
    visitor_tab.render(city_codes, city_code_to_name, selected_month, dark_mode=dark_mode)
elif selected_tab == TAB_KEYS[1]:
    consumer_tab.render(city_codes, city_code_to_name, selected_month, dark_mode=dark_mode)
elif selected_tab == TAB_KEYS[2]:
    asset_tab.render(city_codes, city_code_to_name, selected_month, dark_mode=dark_mode)
elif selected_tab == TAB_KEYS[3]:
    report_tab.render(city_codes, city_code_to_name, selected_month, dark_mode=dark_mode)
elif selected_tab == TAB_KEYS[4]:
    backtest_tab.render(city_codes, city_code_to_name, selected_month, dark_mode=dark_mode)
elif selected_tab == TAB_KEYS[5]:
    diagnostic_tab.render(city_codes, city_code_to_name, selected_month, dark_mode=dark_mode)
