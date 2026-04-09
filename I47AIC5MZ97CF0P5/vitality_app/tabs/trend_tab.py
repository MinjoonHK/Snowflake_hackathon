import altair as alt
import pandas as pd
import streamlit as st

# Design system color palette for multi-series charts
_SERIES_COLORS = [
    "#359efa",  # primary-40
    "#7de12f",  # secondary-40
    "#ff8585",  # error-40
    "#98ccfa",  # primary-30
    "#96e15c",  # secondary-30
]

_SALES_COLORS = [
    "#359efa",  # 외식 — primary-40
    "#7de12f",  # 커피 — secondary-40
    "#98ccfa",  # 엔터 — primary-30
    "#62ad24",  # 소매 — secondary-50
    "#ff8585",  # 패션 — error-40
    "#cae4fa",  # 레저 — primary-20
]

# Shared Altair dark-theme configuration
def _apply_theme(chart, dark: bool):
    if dark:
        bg = "#171719"      # neutral-80
        grid = "#292a2d"    # neutral-70
        label = "#989ba2"   # neutral-40
        title = "#ffffff"   # neutral-10
    else:
        bg = "#ffffff"      # neutral-10
        grid = "#dbdcdf"    # neutral-30
        label = "#70737c"   # neutral-50
        title = "#0f0f10"   # neutral-90

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
    st.header("법정동 트렌드 분석")

    available_districts = df[
        ["CITY_KOR_NAME", "DISTRICT_KOR_NAME", "DISTRICT_CODE"]
    ].drop_duplicates()
    available_districts["LABEL"] = (
        available_districts["CITY_KOR_NAME"] + " " + available_districts["DISTRICT_KOR_NAME"]
    )
    district_options = available_districts.set_index("DISTRICT_CODE")["LABEL"].to_dict()

    selected_districts = st.multiselect(
        "비교할 법정동 선택 (최대 5개)",
        options=list(district_options.keys()),
        default=list(district_options.keys())[:3],
        format_func=lambda x: district_options.get(x, x),
        max_selections=5,
    )

    if not selected_districts:
        st.info("비교할 법정동을 선택하세요.")
        return

    df_trend = df[df["DISTRICT_CODE"].isin(selected_districts)].copy()
    df_trend["LABEL"] = df_trend["CITY_KOR_NAME"] + " " + df_trend["DISTRICT_KOR_NAME"]

    # ── 활력 지수 추이 ────────────────────────────────────────────────────────
    st.subheader("활력 지수 추이")

    color_scale = alt.Scale(range=_SERIES_COLORS[: len(selected_districts)])

    chart_trend = _apply_theme(
        alt.Chart(df_trend)
        .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2)
        .encode(
            x=alt.X(
                "STANDARD_YEAR_MONTH:N",
                title="기간",
                axis=alt.Axis(
                    labelAngle=-45,
                    values=df_trend["STANDARD_YEAR_MONTH"].unique()[::6].tolist(),
                ),
            ),
            y=alt.Y("CUSTOM_INDEX:Q", title="활력 지수", scale=alt.Scale(zero=False)),
            color=alt.Color("LABEL:N", title="법정동", scale=color_scale),
            tooltip=[
                alt.Tooltip("LABEL:N", title="법정동"),
                alt.Tooltip("STANDARD_YEAR_MONTH:N", title="기간"),
                alt.Tooltip("CUSTOM_INDEX:Q", title="활력지수", format=".1f"),
            ],
        )
        .properties(height=400)
        .interactive(),
        dark_mode,
    )
    st.altair_chart(chart_trend, use_container_width=True)

    # ── 세부 지표 비교 ────────────────────────────────────────────────────────
    st.subheader("세부 지표 비교 (최신 월)")
    df_radar = df_trend[df_trend["STANDARD_YEAR_MONTH"] == selected_month].copy()

    if len(df_radar) > 0:
        radar_data = []
        for _, row in df_radar.iterrows():
            label = f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
            radar_data.extend(
                [
                    {"법정동": label, "지표": "유동인구", "점수": row["SCORE_POPULATION"]},
                    {"법정동": label, "지표": "방문비율", "점수": row["SCORE_VISITING"]},
                    {"법정동": label, "지표": "소비규모", "점수": row["SCORE_CONSUMPTION"]},
                    {"법정동": label, "지표": "소비다양성", "점수": row["SCORE_DIVERSITY"]},
                    {"법정동": label, "지표": "소득수준", "점수": row["SCORE_INCOME"]},
                    {"법정동": label, "지표": "신용건전성", "점수": row["SCORE_CREDIT"]},
                ]
            )
        df_radar_chart = pd.DataFrame(radar_data)

        chart_radar = _apply_theme(
            alt.Chart(df_radar_chart)
            .mark_bar(opacity=0.85, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("지표:N", title=None),
                y=alt.Y("점수:Q", title="점수 (0~100)", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("법정동:N", scale=color_scale),
                xOffset="법정동:N",
                tooltip=[
                    alt.Tooltip("법정동:N"),
                    alt.Tooltip("지표:N"),
                    alt.Tooltip("점수:Q", format=".1f"),
                ],
            )
            .properties(height=400),
            dark_mode,
        )
        st.altair_chart(chart_radar, use_container_width=True)

    # ── 업종별 카드 매출 구성 ────────────────────────────────────────────────
    st.subheader("업종별 카드 매출 구성")
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
                    {"동": label, "업종": "외식", "비율": round(row["FOOD_SALES"] / total * 100, 1)},
                    {"동": label, "업종": "커피", "비율": round(row["COFFEE_SALES"] / total * 100, 1)},
                    {"동": label, "업종": "엔터", "비율": round(row["ENTERTAINMENT_SALES"] / total * 100, 1)},
                    {"동": label, "업종": "소매", "비율": round(row["SMALL_RETAIL_SALES"] / total * 100, 1)},
                    {"동": label, "업종": "패션", "비율": round(row["FASHION_SALES"] / total * 100, 1)},
                    {"동": label, "업종": "레저", "비율": round(row["LEISURE_SALES"] / total * 100, 1)},
                ]
            )
        df_sales = pd.DataFrame(sales_data)

        chart_sales = _apply_theme(
            alt.Chart(df_sales)
            .mark_bar()
            .encode(
                x=alt.X("동:N", title=None),
                y=alt.Y("비율:Q", title="비율 (%)", stack="normalize"),
                color=alt.Color(
                    "업종:N",
                    scale=alt.Scale(
                        domain=["외식", "커피", "엔터", "소매", "패션", "레저"],
                        range=_SALES_COLORS,
                    ),
                ),
                tooltip=[
                    alt.Tooltip("동:N"),
                    alt.Tooltip("업종:N"),
                    alt.Tooltip("비율:Q", format=".1f"),
                ],
            )
            .properties(height=400),
            dark_mode,
        )
        st.altair_chart(chart_sales, use_container_width=True)
