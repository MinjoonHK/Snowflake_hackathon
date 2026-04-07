import pandas as pd
import pydeck as pdk
import streamlit as st


def render(
    df,
    geo_df,
    selected_month: str,
    selected_cities: list,
    city_code_to_name: dict,
):
    st.header("서울 법정동 활력 지도")
    df_month = df[df["STANDARD_YEAR_MONTH"] == selected_month].copy()

    if len(df_month) == 0:
        st.warning("선택한 기간에 데이터가 없습니다.")
        return

    kpi_cols = st.columns(len(selected_cities))
    for col, city_code in zip(kpi_cols, selected_cities):
        city_name = city_code_to_name.get(city_code, city_code)
        city_data = df_month[df_month["CITY_CODE"] == city_code]
        avg_idx = city_data["CUSTOM_INDEX"].mean()
        rising = len(city_data[city_data["TREND_DIRECTION"] == "RISING"])
        declining = len(city_data[city_data["TREND_DIRECTION"] == "DECLINING"])
        with col:
            st.metric(
                label=f"📍 {city_name} 평균 활력",
                value=f"{avg_idx:.1f}" if not pd.isna(avg_idx) else "N/A",
                delta=f"↑{rising} ↓{declining} 개동",
            )

    st.divider()

    map_data = df_month.merge(
        geo_df[["DISTRICT_CODE", "CENTER_LON", "CENTER_LAT"]],
        on="DISTRICT_CODE",
        how="inner",
    )

    vmin = map_data["CUSTOM_INDEX"].min()
    vmax = map_data["CUSTOM_INDEX"].max()
    vrange = max(vmax - vmin, 1)

    def vitality_color(val):
        ratio = (val - vmin) / vrange
        if ratio < 0.5:
            r, g, b = 220, int(60 + ratio * 2 * 180), 60
        else:
            r, g, b = int(220 - (ratio - 0.5) * 2 * 180), 220, 60
        return [r, g, b, 180]

    map_data["COLOR"] = map_data["CUSTOM_INDEX"].apply(vitality_color)
    map_data["RADIUS"] = ((map_data["CUSTOM_INDEX"] - vmin) / vrange * 300 + 100).astype(
        int
    )

    center_lat = map_data["CENTER_LAT"].mean()
    center_lon = map_data["CENTER_LON"].mean()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[CENTER_LON, CENTER_LAT]",
        get_color="COLOR",
        get_radius="RADIUS",
        pickable=True,
        opacity=0.8,
    )

    view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=12, pitch=0)

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={
            "html": "<b>{DISTRICT_KOR_NAME}</b><br>"
            "활력지수: {CUSTOM_INDEX}<br>"
            "유동인구: {TOTAL_POPULATION}<br>"
            "카드매출: {TOTAL_CARD_SALES}<br>"
            "평균소득: {AVG_INCOME}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "fontSize": "13px",
            },
        },
        map_style="mapbox://styles/mapbox/light-v10",
    )

    st.pydeck_chart(deck, height=500)

    lcol1, lcol2, lcol3 = st.columns(3)
    lcol1.markdown("🔴 **낮은 활력**")
    lcol2.markdown("🟡 **중간 활력**")
    lcol3.markdown("🟢 **높은 활력**")

    st.divider()

    st.subheader("📋 법정동 활력 순위")
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
    ranking.columns = [
        "구",
        "동",
        "활력지수",
        "등급",
        "추세",
        "전월비(%)",
        "유동인구",
        "카드매출",
        "평균소득",
    ]
    ranking = ranking.sort_values("활력지수", ascending=False).reset_index(drop=True)
    ranking.index += 1
    st.dataframe(ranking, width="stretch", height=400)
