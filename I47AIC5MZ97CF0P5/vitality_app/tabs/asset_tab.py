"""Asset level × spending behavior tab."""
from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from vitality_app import data
from vitality_app.i18n import categories, category_label, t

# Fixed 3 districts with apt price data
_APT_CITY_CODES = ("11140", "11560", "11650")  # Jung, Yeongdeungpo, Seocho

_CITY_COLORS = {
    "중구":    "#359efa",
    "영등포구": "#7de12f",
    "서초구":  "#ff9f40",
}


# ── Theme helper ────────────────────────────────────────────────────────────
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


# ── Aggregation helpers ─────────────────────────────────────────────────────
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
    df = df.copy()
    total = df["TOTAL_CARD_SALES"].replace(0, np.nan)
    _CATS = categories()
    for col in _CATS:
        df[f"{col}_SHARE"] = df[col] / total * 100
    return df


# ── Main render ─────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header(t("asset.header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:14px;margin-top:-12px'>{t('asset.intro_html')}</p>",
        unsafe_allow_html=True,
    )

    _CATS = categories()

    with st.spinner(t("asset.spinner")):
        df_apt  = data.load_apt_price_by_city(_APT_CITY_CODES)
        df_age  = data.load_age_population_by_city(_APT_CITY_CODES)
        df_vit  = data.load_vitality_data(_APT_CITY_CODES)

    if df_apt.empty or df_vit.empty:
        st.warning(t("common.no_data"))
        return

    df_cons = _agg_vitality_to_city(df_vit)
    df_cons = _add_consumption_share(df_cons)

    # ── Snapshot for selected month ──────────────────────────────────────────
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

    snap = apt_snap.merge(
        cons_snap[["CITY_CODE"] + [c for c in cons_snap.columns if c not in apt_snap.columns]],
        on="CITY_CODE", how="left",
    ).merge(
        age_snap[["CITY_CODE"] + [c for c in age_snap.columns if c not in apt_snap.columns and c not in cons_snap.columns]],
        on="CITY_CODE", how="left",
    )

    _gu = t("c.gu")

    # ── Section 1: KPI cards ─────────────────────────────────────────────────
    st.subheader(t("asset.section1", month=selected_month))

    for _, row in snap.iterrows():
        city = row["CITY_KOR_NAME"]
        color = _CITY_COLORS.get(city, "#359efa")
        meme  = row.get("AVG_MEME_PRICE", 0) or 0
        jeon  = row.get("AVG_JEONSE_PRICE", 0) or 0

        pop_total = row.get("POP_TOTAL", 0) or 1
        young_ratio = (
            ((row.get("POP_20S", 0) or 0) + (row.get("POP_30S", 0) or 0))
            / pop_total * 100
        )

        top_cat = max(_CATS.keys(), key=lambda c: row.get(f"{c}_SHARE", 0) or 0)
        top_label = _CATS[top_cat]
        top_share = row.get(f"{top_cat}_SHARE", 0) or 0

        st.markdown(
            f"<div style='border:1px solid {color};border-radius:10px;padding:16px 20px;margin-bottom:12px;background:#171719'>"
            f"<div style='font-size:18px;font-weight:700;color:{color};margin-bottom:12px'>{city}</div>"
            f"<div style='display:flex;gap:32px;flex-wrap:wrap'>",
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric(t("asset.kpi_meme"), f"{meme:,.0f}")
        c2.metric(t("asset.kpi_jeonse"), f"{jeon:,.0f}")
        c3.metric(t("asset.kpi_ratio"), f"{jeon/meme*100:.1f}%" if meme else "—")
        c4.metric(t("asset.kpi_young"), f"{young_ratio:.1f}%")
        c5.metric(t("asset.kpi_top_cat"), f"{top_label} ({top_share:.1f}%)")
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.divider()

    # ── Section 2: Asset × spend scatter ─────────────────────────────────────
    st.subheader(t("asset.bubble_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('asset.bubble_desc')}</p>",
        unsafe_allow_html=True,
    )

    sel_cat = st.selectbox(
        t("asset.select_cat"),
        options=list(_CATS.keys()),
        format_func=lambda x: _CATS[x],
        key="asset_cat_select",
    )

    _col_meme = t("asset.col_meme")
    _col_share = t("asset.col_share")
    _col_total = t("asset.col_total")

    bubble_data = snap[["CITY_KOR_NAME", "AVG_MEME_PRICE", f"{sel_cat}_SHARE", "TOTAL_CARD_SALES"]].dropna()
    bubble_data = bubble_data.rename(columns={
        "CITY_KOR_NAME":      _gu,
        "AVG_MEME_PRICE":     _col_meme,
        f"{sel_cat}_SHARE":   _col_share,
        "TOTAL_CARD_SALES":   _col_total,
    })

    if not bubble_data.empty:
        color_domain = list(_CITY_COLORS.keys())
        color_range  = list(_CITY_COLORS.values())

        bubble_chart = _apply_theme(
            alt.Chart(bubble_data)
            .mark_point(filled=True, opacity=0.85)
            .encode(
                x=alt.X(f"{_col_meme}:Q", title=t("asset.axis_meme"),
                        scale=alt.Scale(zero=False)),
                y=alt.Y(f"{_col_share}:Q", title=f"{_CATS[sel_cat]} {t('asset.spend_share')}"),
                size=alt.Size(f"{_col_total}:Q", legend=None,
                              scale=alt.Scale(range=[800, 4000])),
                color=alt.Color(
                    f"{_gu}:N",
                    scale=alt.Scale(domain=color_domain, range=color_range),
                ),
                tooltip=[
                    alt.Tooltip(f"{_gu}:N"),
                    alt.Tooltip(f"{_col_meme}:Q", format=",.0f", title=t("asset.tooltip_meme")),
                    alt.Tooltip(f"{_col_share}:Q", format=".1f", title=t("asset.tooltip_share")),
                    alt.Tooltip(f"{_col_total}:Q", format=",", title=t("asset.tooltip_total_sales")),
                ],
            )
            .properties(height=340),
            dark_mode,
        )
        st.altair_chart(bubble_chart, use_container_width=True)

    st.divider()

    # ── Section 3: Age structure comparison ──────────────────────────────────
    st.subheader(t("asset.age_header"))

    _age_group = t("asset.age_axis")
    _age_ratio = t("asset.pop_ratio_axis")

    if not age_snap.empty:
        age_cols = {
            "POP_UNDER20": t("asset.age_under20"),
            "POP_20S":     t("asset.age_20s"),
            "POP_30S":     t("asset.age_30s"),
            "POP_40S":     t("asset.age_40s"),
            "POP_50S":     t("asset.age_50s"),
            "POP_60S":     t("asset.age_60s"),
            "POP_OVER70":  t("asset.age_over70"),
        }

        age_rows = []
        for _, row in age_snap.iterrows():
            city = row["CITY_KOR_NAME"]
            total = row.get("POP_TOTAL", 1) or 1
            for col, label in age_cols.items():
                val = row.get(col, 0) or 0
                age_rows.append({
                    _gu: city,
                    _age_group: label,
                    _age_ratio: val / total * 100,
                })

        df_age_bar = pd.DataFrame(age_rows)
        age_order = list(age_cols.values())

        age_chart = _apply_theme(
            alt.Chart(df_age_bar)
            .mark_bar()
            .encode(
                x=alt.X(f"{_age_group}:N", title=_age_group,
                         sort=age_order,
                         axis=alt.Axis(labelAngle=0)),
                y=alt.Y(f"{_age_ratio}:Q", title=_age_ratio),
                color=alt.Color(
                    f"{_gu}:N",
                    scale=alt.Scale(domain=list(_CITY_COLORS.keys()),
                                    range=list(_CITY_COLORS.values())),
                ),
                xOffset=alt.XOffset(f"{_gu}:N"),
                tooltip=[
                    alt.Tooltip(f"{_gu}:N"),
                    alt.Tooltip(f"{_age_group}:N"),
                    alt.Tooltip(f"{_age_ratio}:Q", format=".1f"),
                ],
            )
            .properties(height=320),
            dark_mode,
        )
        st.altair_chart(age_chart, use_container_width=True)

    st.divider()

    # ── Section 4: Normalized spend composition ──────────────────────────────
    st.subheader(t("asset.comp_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('asset.comp_desc')}</p>",
        unsafe_allow_html=True,
    )

    _cat_label = t("c.category")
    _share_pct = t("asset.col_share_pct")

    comp_rows = []
    for _, row in cons_snap.iterrows():
        city = row["CITY_KOR_NAME"]
        for col, label in _CATS.items():
            share = row.get(f"{col}_SHARE", 0) or 0
            comp_rows.append({_gu: city, _cat_label: label, _share_pct: share})

    df_comp = pd.DataFrame(comp_rows)

    cat_colors = ["#359efa", "#7de12f", "#ff5252", "#ff9f40", "#c07df5", "#98ccfa"]
    cat_domain = list(_CATS.values())

    comp_chart = _apply_theme(
        alt.Chart(df_comp)
        .mark_bar()
        .encode(
            x=alt.X(f"{_gu}:N", title=_gu, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{_share_pct}:Q", title=t("asset.spend_share"), stack="normalize"),
            color=alt.Color(
                f"{_cat_label}:N",
                scale=alt.Scale(domain=cat_domain, range=cat_colors),
            ),
            tooltip=[
                alt.Tooltip(f"{_gu}:N"),
                alt.Tooltip(f"{_cat_label}:N"),
                alt.Tooltip(f"{_share_pct}:Q", format=".1f"),
            ],
        )
        .properties(height=320),
        dark_mode,
    )
    st.altair_chart(comp_chart, use_container_width=True)

    st.divider()

    # ── Section 5: Time-series — sale price vs spending ──────────────────────
    st.subheader(t("asset.ts_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('asset.ts_desc')}</p>",
        unsafe_allow_html=True,
    )

    col_ts1, col_ts2 = st.columns(2)
    with col_ts1:
        ts_city = st.selectbox(
            t("asset.select_gu"),
            options=apt_snap["CITY_CODE"].tolist(),
            format_func=lambda x: apt_snap.set_index("CITY_CODE").loc[x, "CITY_KOR_NAME"],
            key="asset_ts_city",
        )
    with col_ts2:
        ts_cat = st.selectbox(
            t("asset.select_cat"),
            options=list(_CATS.keys()),
            format_func=lambda x: _CATS[x],
            key="asset_ts_cat",
        )

    apt_ts  = df_apt[df_apt["CITY_CODE"] == ts_city].sort_values("STANDARD_YEAR_MONTH")
    cons_ts = df_cons[df_cons["CITY_CODE"] == ts_city].sort_values("STANDARD_YEAR_MONTH")

    ts_merged = apt_ts[["STANDARD_YEAR_MONTH", "AVG_MEME_PRICE"]].merge(
        cons_ts[["STANDARD_YEAR_MONTH", ts_cat]],
        on="STANDARD_YEAR_MONTH", how="inner",
    )

    _period = t("c.period")
    _val = t("c.value")
    _series = t("c.series")
    _meme_label = t("asset.meme_label")

    if not ts_merged.empty:
        def _norm(s: pd.Series) -> pd.Series:
            mn, mx = s.min(), s.max()
            return (s - mn) / (mx - mn + 1e-9) * 100

        df_ts_norm = ts_merged.copy()
        df_ts_norm["meme_norm"] = _norm(df_ts_norm["AVG_MEME_PRICE"])
        df_ts_norm["spend_norm"]   = _norm(df_ts_norm[ts_cat])

        ts_rows = []
        for _, row in df_ts_norm.iterrows():
            ts_rows.append({_period: row["STANDARD_YEAR_MONTH"], _val: row["meme_norm"], _series: _meme_label})
            ts_rows.append({_period: row["STANDARD_YEAR_MONTH"], _val: row["spend_norm"],   _series: _CATS[ts_cat]})

        df_ts = pd.DataFrame(ts_rows)
        x_ticks = df_ts_norm["STANDARD_YEAR_MONTH"].unique()[::12].tolist()

        city_name_ts = apt_snap[apt_snap["CITY_CODE"] == ts_city]["CITY_KOR_NAME"].iloc[0]
        ts_chart = _apply_theme(
            alt.Chart(df_ts)
            .mark_line(point=alt.OverlayMarkDef(size=20), strokeWidth=2)
            .encode(
                x=alt.X(f"{_period}:N", title=_period,
                        axis=alt.Axis(labelAngle=-45, values=x_ticks)),
                y=alt.Y(f"{_val}:Q", title=t("asset.norm_axis")),
                color=alt.Color(
                    f"{_series}:N",
                    scale=alt.Scale(
                        domain=[_meme_label, _CATS[ts_cat]],
                        range=["#ff9f40", "#359efa"],
                    ),
                ),
                tooltip=[
                    alt.Tooltip(f"{_period}:N"),
                    alt.Tooltip(f"{_series}:N"),
                    alt.Tooltip(f"{_val}:Q", format=".1f"),
                ],
            )
            .properties(height=320, title=f"{city_name_ts} — {_meme_label} vs {_CATS[ts_cat]}")
            .interactive(),
            dark_mode,
        )
        st.altair_chart(ts_chart, use_container_width=True)
        st.caption(t("asset.caption_norm"))
    else:
        st.info(t("asset.no_ts_data"))

    st.divider()
    st.caption(t("asset.source"))
