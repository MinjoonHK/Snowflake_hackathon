import altair as alt
import pandas as pd
import streamlit as st


def render(df, selected_month: str):
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

    st.subheader("활력 지수 추이")
    chart_trend = (
        alt.Chart(df_trend)
        .mark_line(point=True, strokeWidth=2)
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
            color=alt.Color("LABEL:N", title="법정동"),
            tooltip=[
                "LABEL",
                "STANDARD_YEAR_MONTH",
                alt.Tooltip("CUSTOM_INDEX:Q", format=".1f"),
            ],
        )
        .properties(height=400)
        .interactive()
    )
    st.altair_chart(chart_trend, width="stretch")

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

        chart_radar = (
            alt.Chart(df_radar_chart)
            .mark_bar(opacity=0.8)
            .encode(
                x=alt.X("지표:N", title=None),
                y=alt.Y("점수:Q", title="점수 (0~100)", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("법정동:N"),
                xOffset="법정동:N",
                tooltip=["법정동", "지표", alt.Tooltip("점수:Q", format=".1f")],
            )
            .properties(height=400)
        )
        st.altair_chart(chart_radar, width="stretch")

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
                    {
                        "동": label,
                        "업종": "엔터",
                        "비율": round(row["ENTERTAINMENT_SALES"] / total * 100, 1),
                    },
                    {
                        "동": label,
                        "업종": "소매",
                        "비율": round(row["SMALL_RETAIL_SALES"] / total * 100, 1),
                    },
                    {"동": label, "업종": "패션", "비율": round(row["FASHION_SALES"] / total * 100, 1)},
                    {"동": label, "업종": "레저", "비율": round(row["LEISURE_SALES"] / total * 100, 1)},
                ]
            )
        df_sales = pd.DataFrame(sales_data)

        chart_sales = (
            alt.Chart(df_sales)
            .mark_bar()
            .encode(
                x=alt.X("동:N", title=None),
                y=alt.Y("비율:Q", title="비율 (%)", stack="normalize"),
                color=alt.Color("업종:N", scale=alt.Scale(scheme="set2")),
                tooltip=["동", "업종", alt.Tooltip("비율:Q", format=".1f")],
            )
            .properties(height=400)
        )
        st.altair_chart(chart_sales, width="stretch")
