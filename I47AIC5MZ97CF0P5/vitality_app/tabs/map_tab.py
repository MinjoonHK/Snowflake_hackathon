import pandas as pd
import pydeck as pdk
import streamlit as st

from vitality_app.i18n import t


# Design system colors (RGB tuples for pydeck)
_COLOR_LOW = [255, 82, 82]     # error-50
_COLOR_MID = [53, 158, 250]    # primary-40
_COLOR_HIGH = [125, 225, 47]   # secondary-40


def _vitality_color(val, vmin, vrange):
    ratio = (val - vmin) / vrange
    if ratio < 0.5:
        t_ = ratio * 2
        r = int(_COLOR_LOW[0] + (_COLOR_MID[0] - _COLOR_LOW[0]) * t_)
        g = int(_COLOR_LOW[1] + (_COLOR_MID[1] - _COLOR_LOW[1]) * t_)
        b = int(_COLOR_LOW[2] + (_COLOR_MID[2] - _COLOR_LOW[2]) * t_)
    else:
        t_ = (ratio - 0.5) * 2
        r = int(_COLOR_MID[0] + (_COLOR_HIGH[0] - _COLOR_MID[0]) * t_)
        g = int(_COLOR_MID[1] + (_COLOR_HIGH[1] - _COLOR_MID[1]) * t_)
        b = int(_COLOR_MID[2] + (_COLOR_HIGH[2] - _COLOR_MID[2]) * t_)
    return [r, g, b, 200]


def render(
    df,
    geo_df,
    selected_month: str,
    selected_cities: list,
    city_code_to_name: dict,
    dark_mode: bool = True,
):
    st.header(t("map.header"))

    df_month = df[df["STANDARD_YEAR_MONTH"] == selected_month].copy()

    if len(df_month) == 0:
        st.warning(t("common.no_data_period"))
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
                label=t("map.avg_vitality", name=city_name),
                value=f"{avg_idx:.1f}" if not pd.isna(avg_idx) else "N/A",
                delta=t("map.delta", up=rising, down=declining),
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

    _tv = t("map.tooltip_vitality")
    _tp = t("map.tooltip_population")
    _ts = t("map.tooltip_sales")
    _ti = t("map.tooltip_income")

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={
            "html": (
                "<div style='font-family:sans-serif;padding:4px'>"
                "<b style='font-size:14px;color:#ffffff'>{DISTRICT_KOR_NAME}</b><br>"
                f"<span style='color:#989ba2;font-size:12px'>{_tv}</span> "
                "<span style='color:#359efa;font-weight:600'>{CUSTOM_INDEX}</span><br>"
                f"<span style='color:#989ba2;font-size:12px'>{_tp}</span> " + "{TOTAL_POPULATION}<br>"
                f"<span style='color:#989ba2;font-size:12px'>{_ts}</span> " + "{TOTAL_CARD_SALES}<br>"
                f"<span style='color:#989ba2;font-size:12px'>{_ti}</span> " + "{AVG_INCOME}"
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
        f"""
        <div style="display:flex;gap:24px;margin-top:8px;margin-bottom:4px">
            <span style="color:#ff5252;font-size:13px">{t("map.legend_low")}</span>
            <span style="color:#359efa;font-size:13px">{t("map.legend_mid")}</span>
            <span style="color:#7de12f;font-size:13px">{t("map.legend_high")}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Ranking table ────────────────────────────────────────────────────────
    st.subheader(t("map.ranking"))
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
        t("c.gu"), t("c.dong"), t("map.col_vitality"), t("map.col_grade"),
        t("map.col_trend"), t("map.col_mom"), t("map.col_population"),
        t("map.col_sales"), t("map.col_income"),
    ]
    ranking = ranking.sort_values(t("map.col_vitality"), ascending=False).reset_index(drop=True)
    ranking.index += 1
    st.dataframe(ranking, use_container_width=True, height=400)
