import altair as alt
import pandas as pd
import streamlit as st

from vitality_app.i18n import categories_short, t

# Design system color palette for multi-series charts
_SERIES_COLORS = [
    "#359efa",  # primary-40
    "#7de12f",  # secondary-40
    "#ff8585",  # error-40
    "#98ccfa",  # primary-30
    "#96e15c",  # secondary-30
]

_SALES_COLORS = [
    "#359efa",  # Dining — primary-40
    "#7de12f",  # Coffee — secondary-40
    "#98ccfa",  # Entertainment — primary-30
    "#62ad24",  # Retail — secondary-50
    "#ff8585",  # Fashion — error-40
    "#cae4fa",  # Leisure — primary-20
]

# Shared Altair theme configuration
def _apply_theme(chart, dark: bool):
    if dark:
        bg = "#171719"
        grid = "#292a2d"
        label = "#989ba2"
        title = "#ffffff"
    else:
        bg = "#ffffff"
        grid = "#dbdcdf"
        label = "#70737c"
        title = "#0f0f10"

    return (
        chart.configure(background=bg)
        .configure_axis(
            labelColor=label,
            titleColor=title,
            gridColor=grid,
            domainColor=grid,
            tickColor=grid,
            labelFontSize=12,
            titleFontSize=13,
        )
        .configure_legend(
            labelColor=title,
            titleColor=label,
            labelFontSize=12,
            titleFontSize=12,
        )
        .configure_view(stroke=grid)
    )


def render(df, selected_month: str, dark_mode: bool = True):
    st.header(t("trend.header"))

    available_districts = df[
        ["CITY_KOR_NAME", "DISTRICT_KOR_NAME", "DISTRICT_CODE"]
    ].drop_duplicates()
    available_districts["LABEL"] = (
        available_districts["CITY_KOR_NAME"] + " " + available_districts["DISTRICT_KOR_NAME"]
    )
    district_options = available_districts.set_index("DISTRICT_CODE")["LABEL"].to_dict()

    selected_districts = st.multiselect(
        t("trend.select"),
        options=list(district_options.keys()),
        default=list(district_options.keys())[:3],
        format_func=lambda x: district_options.get(x, x),
        max_selections=5,
    )

    if not selected_districts:
        st.info(t("trend.select_prompt"))
        return

    df_trend = df[df["DISTRICT_CODE"].isin(selected_districts)].copy()
    df_trend["LABEL"] = df_trend["CITY_KOR_NAME"] + " " + df_trend["DISTRICT_KOR_NAME"]

    # ── Vitality index trend ─────────────────────────────────────────────────
    st.subheader(t("trend.vitality_trend"))

    _district = t("c.district")
    _period = t("c.period")

    color_scale = alt.Scale(range=_SERIES_COLORS[: len(selected_districts)])

    chart_trend = _apply_theme(
        alt.Chart(df_trend)
        .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2)
        .encode(
            x=alt.X(
                "STANDARD_YEAR_MONTH:N",
                title=_period,
                axis=alt.Axis(
                    labelAngle=-45,
                    values=df_trend["STANDARD_YEAR_MONTH"].unique()[::6].tolist(),
                ),
            ),
            y=alt.Y("CUSTOM_INDEX:Q", title=t("trend.vitality_index"), scale=alt.Scale(zero=False)),
            color=alt.Color("LABEL:N", title=_district, scale=color_scale),
            tooltip=[
                alt.Tooltip("LABEL:N", title=_district),
                alt.Tooltip("STANDARD_YEAR_MONTH:N", title=_period),
                alt.Tooltip("CUSTOM_INDEX:Q", title=t("map.col_vitality"), format=".1f"),
            ],
        )
        .properties(height=400)
        .interactive(),
        dark_mode,
    )
    st.altair_chart(chart_trend, use_container_width=True)

    # ── Detailed metric comparison ───────────────────────────────────────────
    st.subheader(t("trend.detail_compare"))
    df_radar = df_trend[df_trend["STANDARD_YEAR_MONTH"] == selected_month].copy()

    _metric = t("c.item")
    _score = t("c.score")

    if len(df_radar) > 0:
        radar_data = []
        for _, row in df_radar.iterrows():
            label = f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
            radar_data.extend(
                [
                    {_district: label, _metric: t("trend.m_population"), _score: row["SCORE_POPULATION"]},
                    {_district: label, _metric: t("trend.m_visiting"), _score: row["SCORE_VISITING"]},
                    {_district: label, _metric: t("trend.m_consumption"), _score: row["SCORE_CONSUMPTION"]},
                    {_district: label, _metric: t("trend.m_diversity"), _score: row["SCORE_DIVERSITY"]},
                    {_district: label, _metric: t("trend.m_income"), _score: row["SCORE_INCOME"]},
                    {_district: label, _metric: t("trend.m_credit"), _score: row["SCORE_CREDIT"]},
                ]
            )
        df_radar_chart = pd.DataFrame(radar_data)

        chart_radar = _apply_theme(
            alt.Chart(df_radar_chart)
            .mark_bar(opacity=0.85, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X(f"{_metric}:N", title=None),
                y=alt.Y(f"{_score}:Q", title=t("trend.score_axis"), scale=alt.Scale(domain=[0, 100])),
                color=alt.Color(f"{_district}:N", scale=color_scale),
                xOffset=f"{_district}:N",
                tooltip=[
                    alt.Tooltip(f"{_district}:N"),
                    alt.Tooltip(f"{_metric}:N"),
                    alt.Tooltip(f"{_score}:Q", format=".1f"),
                ],
            )
            .properties(height=400),
            dark_mode,
        )
        st.altair_chart(chart_radar, use_container_width=True)

    # ── Card sales by category ───────────────────────────────────────────────
    st.subheader(t("trend.sales_header"))

    _dong = t("c.dong")
    _cat = t("c.category")
    _ratio = t("c.ratio_pct")
    cat_short = categories_short()

    # Build ordered label lists for chart domain
    cat_order = [
        cat_short["FOOD_SALES"], cat_short["COFFEE_SALES"],
        cat_short["ENTERTAINMENT_SALES"], cat_short["SMALL_RETAIL_SALES"],
        cat_short["FASHION_SALES"], cat_short["LEISURE_SALES"],
    ]

    if len(df_radar) > 0:
        sales_data = []
        for _, row in df_radar.iterrows():
            label = f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
            total = max(
                row["FOOD_SALES"]
                + row["COFFEE_SALES"]
                + row["ENTERTAINMENT_SALES"]
                + row["SMALL_RETAIL_SALES"]
                + row["FASHION_SALES"]
                + row["LEISURE_SALES"],
                1,
            )
            sales_data.extend(
                [
                    {_dong: label, _cat: cat_short["FOOD_SALES"], _ratio: round(row["FOOD_SALES"] / total * 100, 1)},
                    {_dong: label, _cat: cat_short["COFFEE_SALES"], _ratio: round(row["COFFEE_SALES"] / total * 100, 1)},
                    {_dong: label, _cat: cat_short["ENTERTAINMENT_SALES"], _ratio: round(row["ENTERTAINMENT_SALES"] / total * 100, 1)},
                    {_dong: label, _cat: cat_short["SMALL_RETAIL_SALES"], _ratio: round(row["SMALL_RETAIL_SALES"] / total * 100, 1)},
                    {_dong: label, _cat: cat_short["FASHION_SALES"], _ratio: round(row["FASHION_SALES"] / total * 100, 1)},
                    {_dong: label, _cat: cat_short["LEISURE_SALES"], _ratio: round(row["LEISURE_SALES"] / total * 100, 1)},
                ]
            )
        df_sales = pd.DataFrame(sales_data)

        chart_sales = _apply_theme(
            alt.Chart(df_sales)
            .mark_bar()
            .encode(
                x=alt.X(f"{_dong}:N", title=None),
                y=alt.Y(f"{_ratio}:Q", title=_ratio, stack="normalize"),
                color=alt.Color(
                    f"{_cat}:N",
                    scale=alt.Scale(
                        domain=cat_order,
                        range=_SALES_COLORS,
                    ),
                ),
                tooltip=[
                    alt.Tooltip(f"{_dong}:N"),
                    alt.Tooltip(f"{_cat}:N"),
                    alt.Tooltip(f"{_ratio}:Q", format=".1f"),
                ],
            )
            .properties(height=400),
            dark_mode,
        )
        st.altair_chart(chart_sales, use_container_width=True)
