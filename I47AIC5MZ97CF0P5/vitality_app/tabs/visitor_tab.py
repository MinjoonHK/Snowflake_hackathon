"""구경꾼 동네 분석 탭 — 방문↑ 소비↓ 통과 동네 탐지 (지하철 승하차 검증)"""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from vitality_app import data

# ── Design system colors ─────────────────────────────────────────────────────
_C_SPECTATOR = "#ff5252"   # error-50       — 구경꾼 동네
_C_ACTIVE    = "#7de12f"   # secondary-40   — 활성 상권
_C_LOCAL     = "#359efa"   # primary-40     — 지역 소비
_C_STAGNANT  = "#989ba2"   # neutral-40     — 침체 동네

_QUAD_COLORS = {
    "구경꾼 동네": _C_SPECTATOR,
    "활성 상권":   _C_ACTIVE,
    "지역 소비":   _C_LOCAL,
    "침체 동네":   _C_STAGNANT,
}


def _apply_theme(chart, dark: bool):
    bg    = "#171719" if dark else "#ffffff"
    grid  = "#292a2d" if dark else "#dbdcdf"
    label = "#989ba2" if dark else "#70737c"
    title = "#ffffff"  if dark else "#0f0f10"
    return (
        chart.configure(background=bg)
        .configure_axis(
            labelColor=label, titleColor=title,
            gridColor=grid, domainColor=grid, tickColor=grid,
            labelFontSize=12, titleFontSize=13,
        )
        .configure_legend(
            labelColor=title, titleColor=label,
            labelFontSize=12, titleFontSize=12,
        )
        .configure_view(stroke=grid)
    )


def _classify_quadrant(score_visit: float, score_cons: float,
                        visit_med: float, cons_med: float) -> str:
    high_visit = score_visit >= visit_med
    high_cons  = score_cons  >= cons_med
    if high_visit and not high_cons:
        return "구경꾼 동네"
    if high_visit and high_cons:
        return "활성 상권"
    if not high_visit and high_cons:
        return "지역 소비"
    return "침체 동네"


def render(city_codes: tuple, city_code_to_name: dict, selected_month: str, dark_mode: bool = True):
    st.header("구경꾼 동네 분석")
    st.markdown(
        "<p style='color:#989ba2;font-size:14px;margin-top:-12px'>"
        "방문인구는 많지만 카드 소비가 낮은 '통과 동네'를 탐지합니다. "
        "지하철 승하차 데이터로 진짜 통과 동네 여부를 검증합니다."
        "</p>",
        unsafe_allow_html=True,
    )

    df_all = data.load_visitor_data(city_codes)
    if df_all.empty:
        st.warning("데이터가 없습니다.")
        return

    df = df_all[df_all["STANDARD_YEAR_MONTH"] == selected_month].copy()
    if df.empty:
        st.warning("선택한 기간에 데이터가 없습니다.")
        return

    # ── 백분위 정규화 (SCORE 컬럼 간 스케일 불일치 보정) ──────────────────────
    # SCORE_VISITING: 0~100 스케일 / SCORE_CONSUMPTION: 0~76 but 중앙값 0.1로 편향
    # → 둘 다 백분위 순위(0~100)로 통일
    n = len(df)
    df["PCT_VISITING"]    = df["SCORE_VISITING"].rank(method="average") / n * 100
    df["PCT_CONSUMPTION"] = df["SCORE_CONSUMPTION"].rank(method="average") / n * 100

    # ── 사분면 분류 ──────────────────────────────────────────────────────────
    visit_med = 50.0   # 백분위 기준 중앙값은 항상 50
    cons_med  = 50.0
    df["QUADRANT"] = df.apply(
        lambda r: _classify_quadrant(
            r["PCT_VISITING"], r["PCT_CONSUMPTION"], visit_med, cons_med
        ),
        axis=1,
    )
    df["LABEL"] = df["CITY_KOR_NAME"] + " " + df["DISTRICT_KOR_NAME"]

    spectators = df[df["QUADRANT"] == "구경꾼 동네"]
    ridership_med = spectators["TOTAL_RIDERSHIP"].median() if not spectators.empty else 0
    confirmed = spectators[spectators["TOTAL_RIDERSHIP"] > ridership_med]

    # ── KPI 카드 ─────────────────────────────────────────────────────────────
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("구경꾼 동네 수",  f"{len(spectators)}개 동", f"전체 {len(df)}개 동 중")
    kpi2.metric("통과 동네 확정",  f"{len(confirmed)}개 동",  "지하철 승하차 상위 50%")
    kpi3.metric("방문 백분위 기준", "50.0",                   "중앙값 기준 사분면")
    kpi4.metric("소비 백분위 기준", "50.0",                   "중앙값 기준 사분면")

    st.divider()

    # ── 사분면 산점도 ─────────────────────────────────────────────────────────
    st.subheader("방문 vs 소비 사분면 분석")

    color_scale = alt.Scale(
        domain=list(_QUAD_COLORS.keys()),
        range=list(_QUAD_COLORS.values()),
    )

    quad_labels = pd.DataFrame([
        {"lx": 75, "ly": 25, "text": "구경꾼 동네 🚇"},
        {"lx": 75, "ly": 75, "text": "활성 상권 ✨"},
        {"lx": 25, "ly": 75, "text": "지역 소비 🏘️"},
        {"lx": 25, "ly": 25, "text": "침체 동네 💤"},
    ])

    scatter = (
        alt.Chart(df)
        .mark_circle(opacity=0.8)
        .encode(
            x=alt.X("PCT_VISITING:Q",    title="방문 백분위",
                    scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("PCT_CONSUMPTION:Q", title="소비 백분위",
                    scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("QUADRANT:N", title="유형", scale=color_scale),
            size=alt.Size("TOTAL_RIDERSHIP:Q", title="지하철 승하차",
                          scale=alt.Scale(range=[40, 500])),
            tooltip=[
                alt.Tooltip("LABEL:N",             title="법정동"),
                alt.Tooltip("QUADRANT:N",           title="유형"),
                alt.Tooltip("PCT_VISITING:Q",       title="방문 백분위",   format=".1f"),
                alt.Tooltip("PCT_CONSUMPTION:Q",    title="소비 백분위",   format=".1f"),
                alt.Tooltip("TOTAL_RIDERSHIP:Q",    title="지하철 승하차", format=","),
                alt.Tooltip("STATION_CNT:Q",        title="인근 역 수"),
            ],
        )
    )

    vline = alt.Chart(pd.DataFrame({"x": [50]})).mark_rule(
        strokeDash=[4, 4], opacity=0.4, color="#989ba2"
    ).encode(x="x:Q")

    hline = alt.Chart(pd.DataFrame({"y": [50]})).mark_rule(
        strokeDash=[4, 4], opacity=0.4, color="#989ba2"
    ).encode(y="y:Q")

    text_layer = (
        alt.Chart(quad_labels)
        .mark_text(fontSize=11, opacity=0.4, fontWeight=600)
        .encode(
            x=alt.X("lx:Q"),
            y=alt.Y("ly:Q"),
            text="text:N",
            color=alt.value("#989ba2"),
        )
    )

    chart = _apply_theme(
        (scatter + vline + hline + text_layer).properties(height=480).interactive(),
        dark_mode,
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption("점 크기 = 지하철 총 승하차 수 | 기준선: 백분위 50 (중앙값)")

    st.divider()

    # ── 구경꾼 동네 상세 랭킹 ─────────────────────────────────────────────────
    st.subheader("구경꾼 동네 상세 목록")

    if spectators.empty:
        st.info("이번 달 구경꾼 동네로 분류된 법정동이 없습니다.")
    else:
        spec = spectators.copy()
        spec["백분위_갭"] = (spec["PCT_VISITING"] - spec["PCT_CONSUMPTION"]).round(1)
        spec["통과동네"] = spec["TOTAL_RIDERSHIP"].apply(
            lambda x: "✅ 통과 동네" if x > ridership_med else "△ 주의"
        )
        display = spec[[
            "CITY_KOR_NAME", "DISTRICT_KOR_NAME",
            "PCT_VISITING", "PCT_CONSUMPTION", "백분위_갭",
            "TOTAL_VISITING", "TOTAL_CARD_SALES",
            "STATION_CNT", "MIN_DISTANCE", "TOTAL_RIDERSHIP", "통과동네",
        ]].sort_values("백분위_갭", ascending=False).reset_index(drop=True)
        display.index += 1
        display.columns = [
            "구", "동", "방문백분위", "소비백분위", "갭",
            "방문인구", "카드매출", "인근역수", "최근역거리(m)", "지하철승하차", "통과동네",
        ]
        st.dataframe(display, use_container_width=True, height=400)

    st.divider()

    # ── 지하철 승하차 vs 소비 ────────────────────────────────────────────────
    st.subheader("지하철 승하차 vs 카드 소비")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "승하차↑ + 소비↓ → 진짜 통과 동네 | 버블 색상 = 동네 유형</p>",
        unsafe_allow_html=True,
    )

    df_transit = df[df["TOTAL_RIDERSHIP"] > 0].copy()
    if not df_transit.empty:
        transit_chart = _apply_theme(
            alt.Chart(df_transit)
            .mark_circle(size=70, opacity=0.8)
            .encode(
                x=alt.X("TOTAL_RIDERSHIP:Q", title="지하철 총 승하차수",
                        scale=alt.Scale(zero=False)),
                y=alt.Y("TOTAL_CARD_SALES:Q", title="카드 총 매출",
                        scale=alt.Scale(zero=False)),
                color=alt.Color("QUADRANT:N", title="유형", scale=color_scale),
                tooltip=[
                    alt.Tooltip("LABEL:N",             title="법정동"),
                    alt.Tooltip("QUADRANT:N",           title="유형"),
                    alt.Tooltip("TOTAL_RIDERSHIP:Q",   title="지하철 승하차", format=","),
                    alt.Tooltip("TOTAL_CARD_SALES:Q",  title="카드 매출",    format=","),
                    alt.Tooltip("STATION_CNT:Q",        title="인근 역 수"),
                ],
            )
            .properties(height=400)
            .interactive(),
            dark_mode,
        )
        st.altair_chart(transit_chart, use_container_width=True)
    else:
        st.info("지하철 데이터가 있는 법정동이 없습니다.")

    st.divider()

    # ── 구경꾼 동네 방문·소비 추이 ────────────────────────────────────────────
    st.subheader("구경꾼 동네 방문·소비 추이")

    if not spectators.empty:
        top_codes = spectators.nlargest(5, "PCT_VISITING")["DISTRICT_CODE"].tolist()
        district_options = {
            row["DISTRICT_CODE"]: f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
            for _, row in spectators.iterrows()
        }
        selected = st.multiselect(
            "구경꾼 동네 선택 (최대 5개)",
            options=list(district_options.keys()),
            default=top_codes[:3],
            format_func=lambda x: district_options.get(x, x),
            max_selections=5,
        )

        if selected:
            df_trend = df_all[df_all["DISTRICT_CODE"].isin(selected)].copy()
            df_trend["LABEL"] = df_trend["CITY_KOR_NAME"] + " " + df_trend["DISTRICT_KOR_NAME"]

            trend_rows = []
            for _, row in df_trend.iterrows():
                trend_rows.append({
                    "법정동": row["LABEL"], "기간": row["STANDARD_YEAR_MONTH"],
                    "점수": row["SCORE_VISITING"],    "구분": "방문 점수",
                })
                trend_rows.append({
                    "법정동": row["LABEL"], "기간": row["STANDARD_YEAR_MONTH"],
                    "점수": row["SCORE_CONSUMPTION"], "구분": "소비 점수",
                })
            df_trend_long = pd.DataFrame(trend_rows)
            x_ticks = df_trend_long["기간"].unique()[::6].tolist()

            trend_chart = _apply_theme(
                alt.Chart(df_trend_long)
                .mark_line(point=alt.OverlayMarkDef(size=50), strokeWidth=2)
                .encode(
                    x=alt.X("기간:N", title="기간",
                            axis=alt.Axis(labelAngle=-45, values=x_ticks)),
                    y=alt.Y("점수:Q", title="점수", scale=alt.Scale(zero=False)),
                    color=alt.Color("법정동:N"),
                    strokeDash=alt.StrokeDash(
                        "구분:N",
                        scale=alt.Scale(
                            domain=["방문 점수", "소비 점수"],
                            range=[[1, 0], [6, 3]],
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip("법정동:N"),
                        alt.Tooltip("기간:N"),
                        alt.Tooltip("구분:N"),
                        alt.Tooltip("점수:Q", format=".1f"),
                    ],
                )
                .properties(height=380)
                .interactive(),
                dark_mode,
            )
            st.altair_chart(trend_chart, use_container_width=True)
            st.caption("실선 = 방문 점수 / 점선 = 소비 점수 — 격차가 클수록 통과 동네 성격이 강함")
