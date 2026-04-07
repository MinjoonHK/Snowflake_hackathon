import streamlit as st

from vitality_app import indices, sidebar
from vitality_app.session import get_session
from vitality_app.tabs import ai_tab, map_tab, trend_tab

st.set_page_config(page_title="Urban Vitality Index", page_icon="🏙️", layout="wide")

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

tab1, tab2, tab3 = st.tabs(["🗺️ 활력 지도", "📊 트렌드 분석", "🤖 AI 상담"])

with tab1:
    map_tab.render(
        state.df,
        state.geo_df,
        state.selected_month,
        state.selected_cities,
        state.city_code_to_name,
    )

with tab2:
    trend_tab.render(state.df, state.selected_month)

with tab3:
    ai_tab.render(
        session,
        state.df,
        state.months,
        state.selected_cities,
        state.city_code_to_name,
    )

sidebar.render_footer()
