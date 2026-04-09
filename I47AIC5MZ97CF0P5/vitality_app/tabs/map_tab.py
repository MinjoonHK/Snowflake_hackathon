import pandas as pd
import pydeck as pdk
import streamlit as st


# Design system colors (RGB tuples for pydeck)
_COLOR_LOW = [255, 82, 82]     # error-50
_COLOR_MID = [53, 158, 250]    # primary-40
_COLOR_HIGH = [125, 225, 47]   # secondary-40


def _vitality_color(val, vmin, vrange):
    ratio = (val - vmin) / vrange
    if ratio < 0.5:
        t = ratio * 2
        r = int(_COLOR_LOW[0] + (_COLOR_MID[0] - _COLOR_LOW[0]) * t)
        g = int(_COLOR_LOW[1] + (_COLOR_MID[1] - _COLOR_LOW[1]) * t)
        b = int(_COLOR_LOW[2] + (_COLOR_MID[2] - _COLOR_LOW[2]) * t)
    else:
        t = (ratio - 0.5) * 2
        r = int(_COLOR_MID[0] + (_COLOR_HIGH[0] - _COLOR_MID[0]) * t)
        g = int(_COLOR_MID[1] + (_COLOR_HIGH[1] - _COLOR_MID[1]) * t)
        b = int(_COLOR_MID[2] + (_COLOR_HIGH[2] - _COLOR_MID[2]) * t)
    return [r, g, b, 200]


def render(
    df,
    geo_df,
    selected_month: str,
    selected_cities: list,
    city_code_to_name: dict,
    dark_mode: bool = True,
):
    st.header("서울 법정동 활력 지도")

    df_month = df[df["STANDARD_YEAR_MONTH"] == selected_month].copy()

    if len(df_month) == 0:
        st.warning("선택한 기간에 데이터가 없습니다.")
        return

    # ── KPI metrics ──────────────────────────────────────────────────────────
    kpi_cols = st.columns(len(selected_cities))
    for col, city_code in zip(kpi_cols, selected_cities):
        city_name = city_code_to_name.get(city_code, city_code)
        city_data = df_month[df_month["CITY_CODE"] == city_code]
        avg_idx = city_data["CUSTOM_INDEX"].mean()
        rising = len(city_data[city_data["TREND_DIRECTION"] == "RISING"])
        declining = len(city_data[city_data["TREND_DIRECTION"] == "DECLINING"])
        with col:
            st.metric(
                label=f"{city_name} 평균 활력",
                value=f"{avg_idx:.1f}" if not pd.isna(avg_idx) else "N/A",
                delta=f"↑{rising} ↓{declining} 개동",
            )

    st.divider()

    # ── Map ──────────────────────────────────────────────────────────────────
    map_data = df_month.merge(
        geo_df[["DISTRICT_CODE", "CENTER_LON", "CENTER_LAT"]],
        on="DISTRICT_CODE",
        how="inner",
    )

    vmin = map_data["CUSTOM_INDEX"].min()
    vmax = map_data["CUSTOM_INDEX"].max()
    vrange = max(vmax - vmin, 1)

    map_data["COLOR"] = map_data["CUSTOM_INDEX"].apply(
        lambda v: _vitality_color(v, vmin, vrange)
    )
    map_data["RADIUS"] = (
        (map_data["CUSTOM_INDEX"] - vmin) / vrange * 300 + 100
    ).astype(int)

    center_lat = map_data["CENTER_LAT"].mean()
    center_lon = map_data["CENTER_LON"].mean()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[CENTER_LON, CENTER_LAT]",
        get_color="COLOR",
        get_radius="RADIUS",
        pickable=True,
        opacity=0.85,
        radius_min_pixels=4,
        radius_max_pixels=20,
    )

    view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=12, pitch=0)

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={
            "html": (
                "<div style='font-family:sans-serif;padding:4px'>"
                "<b style='font-size:14px;color:#ffffff'>{DISTRICT_KOR_NAME}</b><br>"
                "<span style='color:#989ba2;font-size:12px'>활력지수</span> "
                "<span style='color:#359efa;font-weight:600'>{CUSTOM_INDEX}</span><br>"
                "<span style='color:#989ba2;font-size:12px'>유동인구</span> {TOTAL_POPULATION}<br>"
                "<span style='color:#989ba2;font-size:12px'>카드매출</span> {TOTAL_CARD_SALES}<br>"
                "<span style='color:#989ba2;font-size:12px'>평균소득</span> {AVG_INCOME}"
                "</div>"
            ),
            "style": {
                "backgroundColor": "#171719",
                "border": "1px solid #292a2d",
                "borderRadius": "8px",
                "padding": "8px 12px",
                "color": "#ffffff",
                "fontSize": "13px",
            },
        },
        map_style="mapbox://styles/mapbox/dark-v10" if dark_mode else "mapbox://styles/mapbox/light-v10",
    )

    st.pydeck_chart(deck, height=500)

    # ── Legend ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display:flex;gap:24px;margin-top:8px;margin-bottom:4px">
            <span style="color:#ff5252;font-size:13px">● 낮은 활력</span>
            <span style="color:#359efa;font-size:13px">● 중간 활력</span>
            <span style="color:#7de12f;font-size:13px">● 높은 활력</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Ranking table ────────────────────────────────────────────────────────
    st.subheader("법정동 활력 순위")
    ranking = df_month[
        [
            "CITY_KOR_NAME",
            "DISTRICT_KOR_NAME",
            "CUSTOM_INDEX",
            "VITALITY_LEVEL",
            "TREND_DIRECTION",
            "MOM_CHANGE_PCT",
            "TOTAL_POPULATION",
            "TOTAL_CARD_SALES",
            "AVG_INCOME",
        ]
    ].copy()
    ranking.columns = ["구", "동", "활력지수", "등급", "추세", "전월비(%)", "유동인구", "카드매출", "평균소득"]
    ranking = ranking.sort_values("활력지수", ascending=False).reset_index(drop=True)
    ranking.index += 1
    st.dataframe(ranking, use_container_width=True, height=400)
