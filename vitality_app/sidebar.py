from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st

from vitality_app import data


@dataclass
class SidebarState:
    selected_cities: list
    city_code_to_name: dict
    selected_month: str
    df: pd.DataFrame
    geo_df: pd.DataFrame
    months: list
    w_pop: int
    w_visit: int
    w_cons: int
    w_div: int
    w_inc: int
    w_cred: int


def render_sidebar() -> Optional[SidebarState]:
    st.sidebar.title("🏙️ Urban Vitality Index")
    st.sidebar.markdown("서울 도시 활력 분석 플랫폼")
    st.sidebar.divider()

    city_df = data.load_available_cities()
    city_code_to_name = city_df.set_index("CITY_CODE")["CITY_KOR_NAME"].to_dict()

    selected_cities = st.sidebar.multiselect(
        "🏙️ 분석할 구 선택",
        options=city_df["CITY_CODE"].tolist(),
        default=city_df["CITY_CODE"].tolist(),
        format_func=lambda x: city_code_to_name.get(x, x),
    )

    if not selected_cities:
        st.warning("분석할 구를 하나 이상 선택하세요.")
        return None

    df = data.load_vitality_data(tuple(selected_cities))
    geo_df = data.load_geo_data(tuple(selected_cities))
    months = sorted(df["STANDARD_YEAR_MONTH"].unique())

    st.sidebar.divider()

    selected_month = st.sidebar.select_slider(
        "📅 분석 기간",
        options=months,
        value=months[-1],
        format_func=lambda x: f"{x[:4]}년 {x[4:]}월",
    )

    st.sidebar.divider()
    st.sidebar.subheader("⚖️ 지수 가중치 조정")
    w_pop = st.sidebar.slider("유동인구", 0, 100, 15, 5)
    w_visit = st.sidebar.slider("방문인구 비율", 0, 100, 15, 5)
    w_cons = st.sidebar.slider("소비 규모", 0, 100, 20, 5)
    w_div = st.sidebar.slider("소비 다양성", 0, 100, 10, 5)
    w_inc = st.sidebar.slider("소득 수준", 0, 100, 20, 5)
    w_cred = st.sidebar.slider("신용 건전성", 0, 100, 20, 5)

    return SidebarState(
        selected_cities=selected_cities,
        city_code_to_name=city_code_to_name,
        selected_month=selected_month,
        df=df,
        geo_df=geo_df,
        months=months,
        w_pop=w_pop,
        w_visit=w_visit,
        w_cons=w_cons,
        w_div=w_div,
        w_inc=w_inc,
        w_cred=w_cred,
    )


def render_footer():
    st.sidebar.divider()
    st.sidebar.caption("Built with Snowflake + Streamlit")
    st.sidebar.caption("Data: SPH (SKT 유동인구, KCB 자산소득, 신한카드 소비)")
