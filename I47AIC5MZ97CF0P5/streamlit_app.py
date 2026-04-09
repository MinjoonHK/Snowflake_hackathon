import streamlit as st

from vitality_app import indices, sidebar
from vitality_app.session import get_session
from vitality_app.tabs import map_tab, trend_tab, visitor_tab, consumer_tab, asset_tab

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
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #ffffff !important; }
    section[data-testid="stSidebar"] p { color: #989ba2 !important; }
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

_inject_theme(st.session_state.dark_mode)

session = get_session()

state = sidebar.render_sidebar()
if state is None:
    st.stop()

indices.apply_custom_index(
    state.df,
    state.w_pop,
    state.w_visit,
    state.w_cons,
    state.w_div,
    state.w_inc,
    state.w_cred,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 활력 지도", "📊 트렌드 분석", "🚇 구경꾼 동네", "📈 전입×소비", "🏠 자산×소비"])

dark_mode = st.session_state.get("dark_mode", True)

with tab1:
    map_tab.render(
        state.df,
        state.geo_df,
        state.selected_month,
        state.selected_cities,
        state.city_code_to_name,
        dark_mode=dark_mode,
    )

with tab2:
    trend_tab.render(state.df, state.selected_month, dark_mode=dark_mode)

with tab3:
    visitor_tab.render(
        tuple(state.selected_cities),
        state.city_code_to_name,
        state.selected_month,
        dark_mode=dark_mode,
    )

with tab4:
    consumer_tab.render(
        tuple(state.selected_cities),
        state.city_code_to_name,
        state.selected_month,
        dark_mode=dark_mode,
    )

with tab5:
    asset_tab.render(
        tuple(state.selected_cities),
        state.city_code_to_name,
        state.selected_month,
        dark_mode=dark_mode,
    )

sidebar.render_footer()
