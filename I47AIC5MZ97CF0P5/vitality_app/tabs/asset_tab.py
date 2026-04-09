"""소득 대비 소비 성향 탭
아파트 시세(자산 수준 proxy) × 연령 구조 → 업종별 소비 패턴 비교
데이터 가용 구: 중구·영등포구·서초구 3개 고정 비교
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from vitality_app import data

# 아파트 시세 데이터가 있는 3개 구 (고정)
_APT_CITY_CODES = ("11140", "11560", "11650")  # 중구, 영등포구, 서초구

_CITY_COLORS = {
    "중구":    "#359efa",
    "영등포구": "#7de12f",
    "서초구":  "#ff9f40",
}

_CATEGORIES: dict[str, str] = {
    "COFFEE_SALES":        "커피",
    "ENTERTAINMENT_SALES": "엔터테인먼트",
    "FOOD_SALES":          "음식",
    "FASHION_SALES":       "패션",
    "LEISURE_SALES":       "여가",
    "SMALL_RETAIL_SALES":  "소매",
}


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


def _add_consumption_share(df: pd.DataFrame) -> pd.DataFrame:
    """각 업종 비중(%) 컬럼 추가"""
    df = df.copy()
    total = df["TOTAL_CARD_SALES"].replace(0, np.nan)
    for col, label in _CATEGORIES.items():
        df[f"{col}_SHARE"] = df[col] / total * 100
    return df


# ── 메인 렌더 ────────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header("자산 수준 × 소비 성향 분석")
    st.markdown(
        "<p style='color:#989ba2;font-size:14px;margin-top:-12px'>"
        "아파트 시세(자산 수준 proxy)와 연령 구조가 업종별 소비 패턴에 어떻게 반영되는지 분석합니다. "
        "데이터 가용 구: <b style='color:#ffffff'>중구 · 영등포구 · 서초구</b></p>",
        unsafe_allow_html=True,
    )

    # ── 데이터 로드 ──────────────────────────────────────────────────────────
    with st.spinner("데이터 로딩 중…"):
        df_apt  = data.load_apt_price_by_city(_APT_CITY_CODES)
        df_age  = data.load_age_population_by_city(_APT_CITY_CODES)
        df_vit  = data.load_vitality_data(_APT_CITY_CODES)

    if df_apt.empty or df_vit.empty:
        st.warning("데이터가 없습니다.")
        return

    df_cons = _agg_vitality_to_city(df_vit)
    df_cons = _add_consumption_share(df_cons)

    # ── 기준월 스냅샷 ────────────────────────────────────────────────────────
    # 아파트 시세: 선택월 or 가장 가까운 과거
    apt_snap = (
        df_apt[df_apt["STANDARD_YEAR_MONTH"] <= selected_month]
        .sort_values("STANDARD_YEAR_MONTH")
        .groupby("CITY_CODE")
        .last()
        .reset_index()
    )
    cons_snap = (
        df_cons[df_cons["STANDARD_YEAR_MONTH"] <= selected_month]
        .sort_values("STANDARD_YEAR_MONTH")
        .groupby("CITY_CODE")
        .last()
        .reset_index()
    )
    age_snap = (
        df_age[df_age["STANDARD_YEAR_MONTH"] <= selected_month]
        .sort_values("STANDARD_YEAR_MONTH")
        .groupby("CITY_CODE")
        .last()
        .reset_index()
    )

    # 3개 스냅샷 병합
    snap = apt_snap.merge(
        cons_snap[["CITY_CODE"] + [c for c in cons_snap.columns if c not in apt_snap.columns]],
        on="CITY_CODE", how="left",
    ).merge(
        age_snap[["CITY_CODE"] + [c for c in age_snap.columns if c not in apt_snap.columns and c not in cons_snap.columns]],
        on="CITY_CODE", how="left",
    )

    cities = snap["CITY_KOR_NAME"].tolist()

    # ── Section 1: KPI 카드 ──────────────────────────────────────────────────
    st.subheader(f"구별 자산·소비 현황 ({selected_month})")

    for _, row in snap.iterrows():
        city = row["CITY_KOR_NAME"]
        color = _CITY_COLORS.get(city, "#359efa")
        meme  = row.get("AVG_MEME_PRICE", 0) or 0
        jeon  = row.get("AVG_JEONSE_PRICE", 0) or 0
        total_sales = row.get("TOTAL_CARD_SALES", 0) or 0

        pop_total = row.get("POP_TOTAL", 0) or 1
        young_ratio = (
            ((row.get("POP_20S", 0) or 0) + (row.get("POP_30S", 0) or 0))
            / pop_total * 100
        )
        senior_ratio = (
            ((row.get("POP_60S", 0) or 0) + (row.get("POP_OVER70", 0) or 0))
            / pop_total * 100
        )

        # 주요 소비 업종 (비중 최대)
        top_cat = max(_CATEGORIES.keys(), key=lambda c: row.get(f"{c}_SHARE", 0) or 0)
        top_label = _CATEGORIES[top_cat]
        top_share = row.get(f"{top_cat}_SHARE", 0) or 0

        st.markdown(
            f"<div style='border:1px solid {color};border-radius:10px;padding:16px 20px;margin-bottom:12px;background:#171719'>"
            f"<div style='font-size:18px;font-weight:700;color:{color};margin-bottom:12px'>{city}</div>"
            f"<div style='display:flex;gap:32px;flex-wrap:wrap'>",
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("매매가/평 (만원)", f"{meme:,.0f}")
        c2.metric("전세가/평 (만원)", f"{jeon:,.0f}")
        c3.metric("전세가율", f"{jeon/meme*100:.1f}%" if meme else "—")
        c4.metric("20-30대 비중", f"{young_ratio:.1f}%")
        c5.metric("주요 소비 업종", f"{top_label} ({top_share:.1f}%)")
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.divider()

    # ── Section 2: 자산 × 소비 산점도 ────────────────────────────────────────
    st.subheader("아파트 시세 × 업종 소비 비중 (버블 차트)")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "X축: 매매가/평(만원) · Y축: 선택 업종 소비 비중 · 버블 크기: 총 카드 매출</p>",
        unsafe_allow_html=True,
    )

    sel_cat = st.selectbox(
        "비교 업종",
        options=list(_CATEGORIES.keys()),
        format_func=lambda x: _CATEGORIES[x],
        key="asset_cat_select",
    )

    bubble_data = snap[["CITY_KOR_NAME", "AVG_MEME_PRICE", f"{sel_cat}_SHARE", "TOTAL_CARD_SALES"]].dropna()
    bubble_data = bubble_data.rename(columns={
        "CITY_KOR_NAME":      "구",
        "AVG_MEME_PRICE":     "매매가_평당",
        f"{sel_cat}_SHARE":   "소비비중",
        "TOTAL_CARD_SALES":   "총매출",
    })

    if not bubble_data.empty:
        color_domain = list(_CITY_COLORS.keys())
        color_range  = list(_CITY_COLORS.values())

        bubble_chart = _apply_theme(
            alt.Chart(bubble_data)
            .mark_point(filled=True, opacity=0.85)
            .encode(
                x=alt.X("매매가_평당:Q", title="아파트 매매가/평 (만원)",
                        scale=alt.Scale(zero=False)),
                y=alt.Y("소비비중:Q", title=f"{_CATEGORIES[sel_cat]} 소비 비중 (%)"),
                size=alt.Size("총매출:Q", legend=None,
                              scale=alt.Scale(range=[800, 4000])),
                color=alt.Color(
                    "구:N",
                    scale=alt.Scale(domain=color_domain, range=color_range),
                ),
                tooltip=[
                    alt.Tooltip("구:N"),
                    alt.Tooltip("매매가_평당:Q", format=",.0f", title="매매가/평(만원)"),
                    alt.Tooltip("소비비중:Q", format=".1f", title="소비 비중(%)"),
                    alt.Tooltip("총매출:Q", format=",", title="총 카드매출"),
                ],
            )
            .properties(height=340),
            dark_mode,
        )
        st.altair_chart(bubble_chart, use_container_width=True)

    st.divider()

    # ── Section 3: 연령 구조 비교 (Grouped Bar) ──────────────────────────────
    st.subheader("구별 연령 구조 비교")

    if not age_snap.empty:
        age_cols = {
            "POP_UNDER20": "20세 미만",
            "POP_20S":     "20대",
            "POP_30S":     "30대",
            "POP_40S":     "40대",
            "POP_50S":     "50대",
            "POP_60S":     "60대",
            "POP_OVER70":  "70대 이상",
        }

        age_rows = []
        for _, row in age_snap.iterrows():
            city = row["CITY_KOR_NAME"]
            total = row.get("POP_TOTAL", 1) or 1
            for col, label in age_cols.items():
                val = row.get(col, 0) or 0
                age_rows.append({
                    "구": city,
                    "연령대": label,
                    "비중(%)": val / total * 100,
                })

        df_age_bar = pd.DataFrame(age_rows)
        age_order = list(age_cols.values())

        age_chart = _apply_theme(
            alt.Chart(df_age_bar)
            .mark_bar()
            .encode(
                x=alt.X("연령대:N", title="연령대",
                         sort=age_order,
                         axis=alt.Axis(labelAngle=0)),
                y=alt.Y("비중(%):Q", title="인구 비중 (%)"),
                color=alt.Color(
                    "구:N",
                    scale=alt.Scale(domain=list(_CITY_COLORS.keys()),
                                    range=list(_CITY_COLORS.values())),
                ),
                xOffset=alt.XOffset("구:N"),
                tooltip=[
                    alt.Tooltip("구:N"),
                    alt.Tooltip("연령대:N"),
                    alt.Tooltip("비중(%):Q", format=".1f"),
                ],
            )
            .properties(height=320),
            dark_mode,
        )
        st.altair_chart(age_chart, use_container_width=True)

    st.divider()

    # ── Section 4: 소비 구성 비교 (Normalized Stacked Bar) ───────────────────
    st.subheader("구별 업종 소비 구성 비교 (정규화)")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "동일 시점, 각 구의 총 카드 매출 기준 업종 비중. "
        "자산 수준에 따라 소비 구성이 어떻게 달라지는지 확인합니다.</p>",
        unsafe_allow_html=True,
    )

    comp_rows = []
    for _, row in cons_snap.iterrows():
        city = row["CITY_KOR_NAME"]
        for col, label in _CATEGORIES.items():
            share = row.get(f"{col}_SHARE", 0) or 0
            comp_rows.append({"구": city, "업종": label, "소비비중(%)": share})

    df_comp = pd.DataFrame(comp_rows)

    cat_colors = ["#359efa", "#7de12f", "#ff5252", "#ff9f40", "#c07df5", "#98ccfa"]
    cat_domain = list(_CATEGORIES.values())

    comp_chart = _apply_theme(
        alt.Chart(df_comp)
        .mark_bar()
        .encode(
            x=alt.X("구:N", title="구", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("소비비중(%):Q", title="소비 비중 (%)", stack="normalize"),
            color=alt.Color(
                "업종:N",
                scale=alt.Scale(domain=cat_domain, range=cat_colors),
            ),
            tooltip=[
                alt.Tooltip("구:N"),
                alt.Tooltip("업종:N"),
                alt.Tooltip("소비비중(%):Q", format=".1f"),
            ],
        )
        .properties(height=320),
        dark_mode,
    )
    st.altair_chart(comp_chart, use_container_width=True)

    st.divider()

    # ── Section 5: 시계열 — 매매가 vs 소비 ──────────────────────────────────
    st.subheader("아파트 시세 × 소비 추이 비교 (정규화)")
    st.markdown(
        "<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        "각 지표를 0~100으로 정규화. 매매가 상승/하락이 소비 패턴 변화와 동행하는지 확인합니다.</p>",
        unsafe_allow_html=True,
    )

    col_ts1, col_ts2 = st.columns(2)
    with col_ts1:
        ts_city = st.selectbox(
            "구 선택",
            options=apt_snap["CITY_CODE"].tolist(),
            format_func=lambda x: apt_snap.set_index("CITY_CODE").loc[x, "CITY_KOR_NAME"],
            key="asset_ts_city",
        )
    with col_ts2:
        ts_cat = st.selectbox(
            "비교 업종",
            options=list(_CATEGORIES.keys()),
            format_func=lambda x: _CATEGORIES[x],
            key="asset_ts_cat",
        )

    apt_ts  = df_apt[df_apt["CITY_CODE"] == ts_city].sort_values("STANDARD_YEAR_MONTH")
    cons_ts = df_cons[df_cons["CITY_CODE"] == ts_city].sort_values("STANDARD_YEAR_MONTH")

    ts_merged = apt_ts[["STANDARD_YEAR_MONTH", "AVG_MEME_PRICE"]].merge(
        cons_ts[["STANDARD_YEAR_MONTH", ts_cat]],
        on="STANDARD_YEAR_MONTH", how="inner",
    )

    if not ts_merged.empty:
        def _norm(s: pd.Series) -> pd.Series:
            mn, mx = s.min(), s.max()
            return (s - mn) / (mx - mn + 1e-9) * 100

        ts_norm_rows = []
        for _, row in ts_merged.iterrows():
            ts_norm_rows.append({"기간": row["STANDARD_YEAR_MONTH"],
                                  "값": None, "구분": "매매가/평"})
            ts_norm_rows.append({"기간": row["STANDARD_YEAR_MONTH"],
                                  "값": None, "구분": _CATEGORIES[ts_cat]})

        df_ts_norm = ts_merged.copy()
        df_ts_norm["매매가_norm"] = _norm(df_ts_norm["AVG_MEME_PRICE"])
        df_ts_norm["소비_norm"]   = _norm(df_ts_norm[ts_cat])

        ts_rows = []
        for _, row in df_ts_norm.iterrows():
            ts_rows.append({"기간": row["STANDARD_YEAR_MONTH"], "값": row["매매가_norm"], "구분": "매매가/평"})
            ts_rows.append({"기간": row["STANDARD_YEAR_MONTH"], "값": row["소비_norm"],   "구분": _CATEGORIES[ts_cat]})

        df_ts = pd.DataFrame(ts_rows)
        x_ticks = df_ts_norm["STANDARD_YEAR_MONTH"].unique()[::12].tolist()

        city_name_ts = apt_snap[apt_snap["CITY_CODE"] == ts_city]["CITY_KOR_NAME"].iloc[0]
        ts_chart = _apply_theme(
            alt.Chart(df_ts)
            .mark_line(point=alt.OverlayMarkDef(size=20), strokeWidth=2)
            .encode(
                x=alt.X("기간:N", title="기간",
                        axis=alt.Axis(labelAngle=-45, values=x_ticks)),
                y=alt.Y("값:Q", title="정규화 지수 (0~100)"),
                color=alt.Color(
                    "구분:N",
                    scale=alt.Scale(
                        domain=["매매가/평", _CATEGORIES[ts_cat]],
                        range=["#ff9f40", "#359efa"],
                    ),
                ),
                tooltip=[
                    alt.Tooltip("기간:N"),
                    alt.Tooltip("구분:N"),
                    alt.Tooltip("값:Q", format=".1f"),
                ],
            )
            .properties(height=320, title=f"{city_name_ts} — 매매가 vs {_CATEGORIES[ts_cat]} 소비 추이")
            .interactive(),
            dark_mode,
        )
        st.altair_chart(ts_chart, use_container_width=True)
        st.caption("0~100 정규화 — 절대값이 아닌 추세 방향을 비교합니다")
    else:
        st.info("시계열 데이터가 충분하지 않습니다.")

    st.divider()
    st.caption("데이터 출처: 리치고 아파트 시세 · 행정안전부 주민등록 인구통계 · SPH/GRANDATA 소비 데이터")
