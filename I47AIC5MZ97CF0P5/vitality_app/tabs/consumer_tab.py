"""전입 인구 × 업종 소비 연관 분석 탭
특정 연령대 전입 증가 → 어떤 업종 매출이 따라 오르는지 Lag 상관 분석.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from vitality_app import data

# ── 업종 컬럼 → 한국어 레이블 ────────────────────────────────────────────────
_CATEGORIES: dict[str, str] = {
    "COFFEE_SALES":         "커피",
    "ENTERTAINMENT_SALES":  "엔터테인먼트",
    "FOOD_SALES":           "음식",
    "FASHION_SALES":        "패션",
    "LEISURE_SALES":        "여가",
    "SMALL_RETAIL_SALES":   "소매",
}

_LAG_MONTHS = [0, 1, 2, 3, 6]


# ── 테마 헬퍼 ────────────────────────────────────────────────────────────────
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


# ── 집계 헬퍼 ────────────────────────────────────────────────────────────────
def _agg_vitality_to_city(df: pd.DataFrame) -> pd.DataFrame:
    """법정동(district) 단위 vitality → 구(city) 단위 집계"""
    return (
        df.groupby(["STANDARD_YEAR_MONTH", "CITY_CODE", "CITY_KOR_NAME"])
        .agg(
            FOOD_SALES=("FOOD_SALES", "sum"),
            COFFEE_SALES=("COFFEE_SALES", "sum"),
            ENTERTAINMENT_SALES=("ENTERTAINMENT_SALES", "sum"),
            SMALL_RETAIL_SALES=("SMALL_RETAIL_SALES", "sum"),
            FASHION_SALES=("FASHION_SALES", "sum"),
            LEISURE_SALES=("LEISURE_SALES", "sum"),
            TOTAL_CARD_SALES=("TOTAL_CARD_SALES", "sum"),
        )
        .reset_index()
    )


def _corr_safe(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 6:
        return float("nan")
    try:
        c = np.corrcoef(x, y)[0, 1]
        return float(c) if not np.isnan(c) else float("nan")
    except Exception:
        return float("nan")


# ── 메인 렌더 ────────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header("전입 인구 × 업종 소비 연관 분석")
    st.markdown(
        "<p style='color:#989ba2;font-size:14px;margin-top:-12px'>"
        "20~30대 전입 증가 이후 어떤 업종 매출이 따라 오르는지 Lag 상관 분석으로 추적합니다."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── 데이터 로드 (서울 전체 구 — 사이드바 선택과 무관) ────────────────────
    with st.spinner("전입·인구 데이터 로딩 중…"):
        all_cities_df = data.load_available_cities()
        all_city_codes = tuple(all_cities_df["CITY_CODE"].tolist())
        all_city_name_map = all_cities_df.set_index("CITY_CODE")["CITY_KOR_NAME"].to_dict()

        df_mig = data.load_migration_by_city(all_city_codes)
        df_age = data.load_age_population_by_city(all_city_codes)
        df_vit = data.load_vitality_data(all_city_codes)

    if df_mig.empty or df_vit.empty:
        st.warning("데이터가 없습니다.")
        return

    df_cons = _agg_vitality_to_city(df_vit)

    # ── 구 선택 (서울 전체 25개 구) ───────────────────────────────────────────
    avail = set(df_mig["CITY_CODE"].unique())
    options = {k: v for k, v in all_city_name_map.items() if k in avail}

    if not options:
        st.warning("전입 데이터가 없습니다.")
        return

    selected_city = st.selectbox(
        "분석할 구 선택",
        options=list(options.keys()),
        format_func=lambda x: options.get(x, x),
    )
    city_name = options[selected_city]

    # ── 선택 구 필터 ─────────────────────────────────────────────────────────
    mig = df_mig[df_mig["CITY_CODE"] == selected_city].sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)
    age = df_age[df_age["CITY_CODE"] == selected_city].sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)
    cons = df_cons[df_cons["CITY_CODE"] == selected_city].sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)

    merged = pd.merge(
        mig[["STANDARD_YEAR_MONTH", "CITY_CODE", "MOVE_IN", "MOVE_OUT", "NET_MOVEMENT"]],
        cons.drop(columns=["CITY_KOR_NAME"], errors="ignore"),
        on=["STANDARD_YEAR_MONTH", "CITY_CODE"],
        how="inner",
    ).sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)

    # ── KPI 카드 ─────────────────────────────────────────────────────────────
    latest_mig = mig[mig["STANDARD_YEAR_MONTH"] == selected_month]
    prev_mig   = mig[mig["STANDARD_YEAR_MONTH"] < selected_month].tail(1)

    move_in_now  = int(latest_mig["MOVE_IN"].iloc[0])  if not latest_mig.empty else 0
    move_in_prev = int(prev_mig["MOVE_IN"].iloc[0])     if not prev_mig.empty  else 0
    delta_pct    = (move_in_now - move_in_prev) / move_in_prev * 100 if move_in_prev else 0.0
    net_val      = int(latest_mig["NET_MOVEMENT"].iloc[0]) if not latest_mig.empty else 0

    age_latest = age[age["STANDARD_YEAR_MONTH"] <= selected_month].tail(1)
    young_ratio = 0.0
    if not age_latest.empty:
        r = age_latest.iloc[0]
        if r["POP_TOTAL"] > 0:
            young_ratio = (r["POP_20S"] + r["POP_30S"]) / r["POP_TOTAL"] * 100

    # 1개월 lag 기준 최상관 업종
    best_cat, best_corr = "N/A", 0.0
    if len(merged) >= 8:
        for col, label in _CATEGORIES.items():
            c = _corr_safe(merged["MOVE_IN"].values[:-1], merged[col].values[1:])
            if not np.isnan(c) and abs(c) > abs(best_corr):
                best_corr, best_cat = c, label

    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric(f"{city_name} 전입인구", f"{move_in_now:,}명", f"{delta_pct:+.1f}% vs 전월")
    kc2.metric("순이동 (전입−전출)", f"{net_val:,}명", "양수 = 순유입")
    kc3.metric("20-30대 인구 비중", f"{young_ratio:.1f}%", "전체 대비")
    kc4.metric(
        "1개월 후 최상관 업종",
        best_cat,
        f"r = {best_corr:.2f}" if best_cat != "N/A" else "",
    )

    st.divider()

    # ── Section 1: 전입·전출·순이동 추이 ────────────────────────────────────
    st.subheader(f"{city_name} 전입·전출·순이동 추이")

    x_ticks = mig["STANDARD_YEAR_MONTH"].unique()[::6].tolist()
    mig_long = mig.melt(
        id_vars=["STANDARD_YEAR_MONTH"],
        value_vars=["MOVE_IN", "MOVE_OUT", "NET_MOVEMENT"],
        var_name="구분", value_name="인구수",
    )
    mig_long["구분"] = mig_long["구분"].map(
        {"MOVE_IN": "전입", "MOVE_OUT": "전출", "NET_MOVEMENT": "순이동"}
    )

    mig_chart = _apply_theme(
        alt.Chart(mig_long)
        .mark_line(point=alt.OverlayMarkDef(size=30), strokeWidth=2)
        .encode(
            x=alt.X("STANDARD_YEAR_MONTH:N", title="기간",
                    axis=alt.Axis(labelAngle=-45, values=x_ticks)),
            y=alt.Y("인구수:Q", title="인구 (명)"),
            color=alt.Color(
                "구분:N",
                scale=alt.Scale(
                    domain=["전입", "전출", "순이동"],
                    range=["#359efa", "#ff5252", "#7de12f"],
                ),
            ),
            tooltip=[
                alt.Tooltip("STANDARD_YEAR_MONTH:N", title="기간"),
                alt.Tooltip("구분:N"),
                alt.Tooltip("인구수:Q", format=","),
            ],
        )
        .properties(height=320)
        .interactive(),
        dark_mode,
    )
    st.altair_chart(mig_chart, use_container_width=True)

    st.divider()

    # ── Section 2: 전입 + 업종 정규화 비교 (이중 추이) ──────────────────────
    st.subheader("전입 증가 → 업종 매출 시계열 비교")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "각 지표를 0~100으로 정규화해 추세 방향과 피크 시점을 비교합니다. "
        "전입 피크 이후 매출이 뒤따라 오르면 인과 신호입니다.</p>",
        unsafe_allow_html=True,
    )

    selected_cats = st.multiselect(
        "비교할 업종 선택 (최대 3개)",
        options=list(_CATEGORIES.keys()),
        default=["COFFEE_SALES", "ENTERTAINMENT_SALES"],
        format_func=lambda x: _CATEGORIES[x],
        max_selections=3,
    )

    if selected_cats and not merged.empty:
        norm_rows: list[dict] = []

        def _norm(series: pd.Series) -> pd.Series:
            mn, mx = series.min(), series.max()
            return (series - mn) / (mx - mn + 1e-9) * 100

        norm_mi = _norm(merged["MOVE_IN"])
        for i, row in merged.iterrows():
            norm_rows.append({
                "기간": row["STANDARD_YEAR_MONTH"],
                "값": float(norm_mi.iloc[i]),
                "구분": "전입인구",
            })

        for col in selected_cats:
            norm_col = _norm(merged[col])
            for i, row in merged.iterrows():
                norm_rows.append({
                    "기간": row["STANDARD_YEAR_MONTH"],
                    "값": float(norm_col.iloc[i]),
                    "구분": _CATEGORIES[col],
                })

        df_norm = pd.DataFrame(norm_rows)
        x_ticks2 = merged["STANDARD_YEAR_MONTH"].unique()[::6].tolist()

        compare_chart = _apply_theme(
            alt.Chart(df_norm)
            .mark_line(point=alt.OverlayMarkDef(size=25), strokeWidth=2)
            .encode(
                x=alt.X("기간:N", title="기간",
                        axis=alt.Axis(labelAngle=-45, values=x_ticks2)),
                y=alt.Y("값:Q", title="정규화 지수 (0~100)"),
                color=alt.Color("구분:N"),
                tooltip=[
                    alt.Tooltip("기간:N"),
                    alt.Tooltip("구분:N"),
                    alt.Tooltip("값:Q", format=".1f"),
                ],
            )
            .properties(height=380)
            .interactive(),
            dark_mode,
        )
        st.altair_chart(compare_chart, use_container_width=True)
        st.caption("0~100 정규화 — 추세 방향과 피크 시점만 비교하세요 (절댓값 아님)")

    st.divider()

    # ── Section 3: Lag 상관계수 히트맵 ──────────────────────────────────────
    st.subheader("전입 증가 후 N개월 업종 매출 상관계수 (Lag 분석)")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "Lag = N개월: 전입이 증가한 달로부터 N개월 뒤 업종 매출과의 상관계수. "
        "<b style='color:#359efa'>파란색</b> = 양의 상관 (전입↑ → 매출↑), "
        "<b style='color:#ff5252'>빨간색</b> = 음의 상관.</p>",
        unsafe_allow_html=True,
    )

    corr_rows: list[dict] = []
    if len(merged) >= 8:
        for col, label in _CATEGORIES.items():
            for lag in _LAG_MONTHS:
                if lag == 0:
                    x = merged["MOVE_IN"].values
                    y = merged[col].values
                else:
                    x = merged["MOVE_IN"].values[:-lag]
                    y = merged[col].values[lag:]
                c = _corr_safe(x, y)
                corr_rows.append({
                    "업종": label,
                    "Lag": f"{lag}개월",
                    "상관계수": round(c, 3) if not np.isnan(c) else 0.0,
                    "표시값": f"{c:.2f}" if not np.isnan(c) else "N/A",
                })

    if corr_rows:
        df_corr = pd.DataFrame(corr_rows)

        label_color = "#ffffff" if dark_mode else "#0f0f10"

        heat = (
            alt.Chart(df_corr)
            .mark_rect()
            .encode(
                x=alt.X("Lag:N", title="전입 후 경과 개월",
                        sort=[f"{l}개월" for l in _LAG_MONTHS]),
                y=alt.Y("업종:N", title="업종"),
                color=alt.Color(
                    "상관계수:Q",
                    scale=alt.Scale(domain=[-1, 0, 1],
                                    range=["#ff5252", "#292a2d" if dark_mode else "#dbdcdf", "#359efa"]),
                    title="상관계수 r",
                    legend=alt.Legend(gradientLength=150),
                ),
                tooltip=[
                    alt.Tooltip("업종:N"),
                    alt.Tooltip("Lag:N", title="경과 개월"),
                    alt.Tooltip("상관계수:Q", format=".3f"),
                ],
            )
        )

        text = (
            alt.Chart(df_corr)
            .mark_text(fontSize=13, fontWeight=600)
            .encode(
                x=alt.X("Lag:N", sort=[f"{l}개월" for l in _LAG_MONTHS]),
                y=alt.Y("업종:N"),
                text=alt.Text("표시값:N"),
                color=alt.condition(
                    "abs(datum['상관계수']) > 0.35",
                    alt.value("#ffffff"),
                    alt.value("#989ba2"),
                ),
            )
        )

        heatmap_chart = _apply_theme(
            (heat + text).properties(height=280),
            dark_mode,
        )
        st.altair_chart(heatmap_chart, use_container_width=True)
        st.caption("|r| > 0.5 강한 상관  |  |r| > 0.3 유의미  |  |r| < 0.1 무상관")
    else:
        st.info("상관계수 계산에 충분한 데이터가 없습니다 (최소 8개월 필요).")

    st.divider()

    # ── Section 4: 20-30대 인구 비중 추이 ────────────────────────────────────
    st.subheader(f"{city_name} 연령대별 인구 비중 추이")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "20-30대 비중 상승 시기와 전입 증가 시기가 겹치면 청년 유입 시그널입니다.</p>",
        unsafe_allow_html=True,
    )

    if not age.empty:
        age = age.copy()
        safe_total = age["POP_TOTAL"].replace(0, np.nan)
        age["20-30대 비중(%)"] = (age["POP_20S"] + age["POP_30S"]) / safe_total * 100
        age["40-50대 비중(%)"] = (age["POP_40S"] + age["POP_50S"]) / safe_total * 100
        age["60대 이상 비중(%)"] = (age["POP_60S"] + age["POP_OVER70"]) / safe_total * 100

        age_long = age.melt(
            id_vars=["STANDARD_YEAR_MONTH"],
            value_vars=["20-30대 비중(%)", "40-50대 비중(%)", "60대 이상 비중(%)"],
            var_name="연령대", value_name="비중(%)",
        ).dropna(subset=["비중(%)"])

        x_ticks3 = age["STANDARD_YEAR_MONTH"].unique()[::6].tolist()

        age_chart = _apply_theme(
            alt.Chart(age_long)
            .mark_line(point=alt.OverlayMarkDef(size=25), strokeWidth=2)
            .encode(
                x=alt.X("STANDARD_YEAR_MONTH:N", title="기간",
                        axis=alt.Axis(labelAngle=-45, values=x_ticks3)),
                y=alt.Y("비중(%):Q", title="인구 비중 (%)"),
                color=alt.Color(
                    "연령대:N",
                    scale=alt.Scale(
                        domain=["20-30대 비중(%)", "40-50대 비중(%)", "60대 이상 비중(%)"],
                        range=["#359efa", "#ff5252", "#989ba2"],
                    ),
                ),
                tooltip=[
                    alt.Tooltip("STANDARD_YEAR_MONTH:N", title="기간"),
                    alt.Tooltip("연령대:N"),
                    alt.Tooltip("비중(%):Q", format=".1f"),
                ],
            )
            .properties(height=300)
            .interactive(),
            dark_mode,
        )
        st.altair_chart(age_chart, use_container_width=True)
        st.caption("데이터 출처: 행정안전부 주민등록 인구통계")
    else:
        st.info("연령대 인구 데이터가 없습니다.")
