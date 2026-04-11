"""Backtesting tab — validates how accurate the recommendation model has been historically."""
from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from vitality_app import data
from vitality_app.i18n import business_presets, category_label, t
from vitality_app.tabs.report_tab import (
    _SCORING_WEIGHTS,
    _classify_business,
    _score_districts,
)

# ── Confidence labels ──────────────────────────────────────────────────────
def _confidence_label(hit_rate: float) -> tuple[str, str]:
    if hit_rate >= 65:
        return t("backtest.conf_high"), "#7de12f"
    if hit_rate >= 50:
        return t("backtest.conf_mid"), "#ff9f40"
    return t("backtest.conf_low"), "#ff5252"


def _apply_theme(chart, dark: bool):
    bg = "#171719" if dark else "#ffffff"
    grid = "#292a2d" if dark else "#dbdcdf"
    label = "#989ba2" if dark else "#70737c"
    title = "#ffffff" if dark else "#0f0f10"
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


# ── Backtest engine ─────────────────────────────────────────────────────────
def _run_backtest(
    df_all: pd.DataFrame,
    category_col: str,
    eval_months: int = 3,
    n_recommend: int = 5,
) -> list[dict] | None:
    months = sorted(df_all["STANDARD_YEAR_MONTH"].unique())
    if len(months) < eval_months + 2:
        return None

    results: list[dict] = []

    for i in range(len(months) - eval_months):
        base_month = months[i]
        future_months = months[i + 1: i + 1 + eval_months]
        if len(future_months) < 1:
            continue

        df_base = df_all[df_all["STANDARD_YEAR_MONTH"] == base_month].copy()
        if df_base.empty or len(df_base) < n_recommend:
            continue

        scored = _score_districts(df_base, category_col)
        top_codes = scored.head(n_recommend)["DISTRICT_CODE"].tolist()
        top_labels = scored.head(n_recommend)["LABEL"].tolist()
        all_codes = scored["DISTRICT_CODE"].tolist()

        base_sales = df_base.set_index("DISTRICT_CODE")[category_col]

        df_future = df_all[
            (df_all["STANDARD_YEAR_MONTH"].isin(future_months))
            & (df_all["DISTRICT_CODE"].isin(all_codes))
        ]
        if df_future.empty:
            continue

        future_avg_sales = df_future.groupby("DISTRICT_CODE")[category_col].mean()

        common = base_sales.index.intersection(future_avg_sales.index)
        if len(common) < n_recommend:
            continue

        base_common = base_sales.loc[common].replace(0, np.nan)
        growth = (
            (future_avg_sales.loc[common] - base_common) / base_common * 100
        ).dropna()

        if growth.empty:
            continue

        median_growth = growth.median()
        avg_growth_all = growth.mean()

        rec_in_growth = [c for c in top_codes if c in growth.index]
        if not rec_in_growth:
            continue

        rec_growth = growth.loc[rec_in_growth]
        avg_growth_rec = float(rec_growth.mean())
        hits = int((rec_growth > median_growth).sum())

        results.append({
            "base_month": base_month,
            "eval_end": future_months[-1],
            "avg_growth_recommended": avg_growth_rec,
            "avg_growth_all": avg_growth_all,
            "median_growth_all": float(median_growth),
            "hits": hits,
            "total": len(rec_in_growth),
            "hit_rate": hits / len(rec_in_growth) * 100,
            "alpha": avg_growth_rec - avg_growth_all,
            "top_labels": top_labels[:len(rec_in_growth)],
            "top_growths": [float(rec_growth.get(c, 0)) for c in rec_in_growth],
        })

    return results if results else None


# ── Main render ─────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header(t("backtest.header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:14px;margin-top:-12px'>{t('backtest.intro')}</p>",
        unsafe_allow_html=True,
    )

    # ── Settings UI ──────────────────────────────────────────────────────────
    st.subheader(t("backtest.sub_settings"))

    _presets = business_presets()
    col_biz, col_eval = st.columns(2)

    with col_biz:
        preset_labels = [p["label"] for p in _presets]
        selected_preset = st.selectbox(
            t("backtest.select_business"),
            preset_labels,
            key="bt_business_select",
        )
        idx = preset_labels.index(selected_preset)
        business_type = _presets[idx]["value"]

    with col_eval:
        eval_months = st.select_slider(
            t("backtest.eval_period"),
            options=[1, 2, 3, 6],
            value=3,
            key="bt_eval_months",
        )

    category_col = _classify_business(business_type)
    cat_label_val = category_label(category_col)

    st.markdown(
        f"<p style='font-size:13px;color:#989ba2'>"
        f"{t('backtest.desc', cat=cat_label_val, n=eval_months)}"
        f"</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    generate = st.button(t("backtest.run"), type="primary", use_container_width=True)

    key_sig = f"{business_type}_{eval_months}"
    if st.session_state.get("_bt_sig") != key_sig:
        st.session_state.pop("_bt_result", None)

    if generate:
        with st.spinner(t("backtest.running")):
            df_all = data.load_vitality_data(city_codes)
            if df_all.empty:
                st.warning(t("common.no_data"))
                return

            results = _run_backtest(df_all, category_col, eval_months=eval_months)
            if results is None:
                st.warning(t("backtest.warn_insufficient_history"))
                return

            st.session_state["_bt_result"] = results
            st.session_state["_bt_sig"] = key_sig
            st.session_state["_bt_cat"] = cat_label_val
            st.session_state["_bt_biz"] = business_type
            st.session_state["_bt_eval"] = eval_months

    # ── Results ──────────────────────────────────────────────────────────────
    results = st.session_state.get("_bt_result")
    if not results:
        return

    cat_label_val = st.session_state["_bt_cat"]
    business_type = st.session_state["_bt_biz"]
    eval_months = st.session_state["_bt_eval"]

    df_bt = pd.DataFrame(results)

    # ── KPI cards ────────────────────────────────────────────────────────────
    overall_hit_rate = df_bt["hits"].sum() / df_bt["total"].sum() * 100
    avg_alpha = df_bt["alpha"].mean()
    win_periods = (df_bt["avg_growth_recommended"] > df_bt["avg_growth_all"]).sum()
    win_rate = win_periods / len(df_bt) * 100
    conf_label, conf_color = _confidence_label(overall_hit_rate)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(t("backtest.kpi_hit_rate"), f"{overall_hit_rate:.1f}%", t("backtest.kpi_hit_desc"))
    k2.metric(t("backtest.kpi_alpha"), f"{avg_alpha:+.2f}%p", t("backtest.kpi_alpha_desc"))
    k3.metric(t("backtest.kpi_win_rate"), f"{win_rate:.0f}%", t("backtest.kpi_win_desc", w=win_periods, t=len(df_bt)))

    k4.markdown(
        f"<div style='padding:16px 20px;border:1px solid {conf_color};border-radius:8px;"
        f"background:{'#171719' if dark_mode else '#ffffff'};text-align:center'>"
        f"<p style='font-size:12px;color:#989ba2;margin:0'>{t('backtest.kpi_confidence')}</p>"
        f"<p style='font-size:28px;font-weight:700;color:{conf_color};margin:4px 0 0'>"
        f"{conf_label}</p></div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Hit rate trend ───────────────────────────────────────────────────────
    _rec_time = t("backtest.axis_rec_time")
    _hit_rate = t("backtest.axis_hit_rate")

    st.subheader(t("backtest.hit_trend"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('backtest.hit_trend_desc')}</p>",
        unsafe_allow_html=True,
    )

    hit_data = df_bt[["base_month", "hit_rate"]].copy()

    hit_line = (
        alt.Chart(hit_data)
        .mark_line(point=alt.OverlayMarkDef(size=40), strokeWidth=2, color="#359efa")
        .encode(
            x=alt.X("base_month:N", title=_rec_time,
                    axis=alt.Axis(labelAngle=-45,
                                  values=hit_data["base_month"].tolist()[::max(1, len(hit_data) // 10)])),
            y=alt.Y("hit_rate:Q", title=_hit_rate,
                    scale=alt.Scale(domain=[0, 100])),
            tooltip=[
                alt.Tooltip("base_month:N", title=_rec_time),
                alt.Tooltip("hit_rate:Q", title=_hit_rate, format=".1f"),
            ],
        )
    )

    baseline_rule = (
        alt.Chart(pd.DataFrame({"y": [50]}))
        .mark_rule(strokeDash=[6, 3], color="#ff5252", opacity=0.6)
        .encode(y="y:Q")
    )

    baseline_label = (
        alt.Chart(pd.DataFrame({"y": [50], "text": [t("backtest.random_baseline")]}))
        .mark_text(align="left", dx=5, dy=-8, fontSize=11, color="#ff5252", opacity=0.7)
        .encode(y="y:Q", text="text:N")
    )

    chart_hit = _apply_theme(
        (hit_line + baseline_rule + baseline_label).properties(height=320).interactive(),
        dark_mode,
    )
    st.altair_chart(chart_hit, use_container_width=True)

    st.divider()

    # ── Recommended vs overall growth ────────────────────────────────────────
    _period = t("c.period")
    _growth_rate = t("c.value")
    _series = t("c.series")
    _rec_label = t("backtest.growth_rec")
    _all_label = t("backtest.growth_all")

    st.subheader(t("backtest.growth_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('backtest.growth_desc')}</p>",
        unsafe_allow_html=True,
    )

    growth_rows: list[dict] = []
    for _, row in df_bt.iterrows():
        growth_rows.append({
            _period: row["base_month"],
            _growth_rate: row["avg_growth_recommended"],
            _series: _rec_label,
        })
        growth_rows.append({
            _period: row["base_month"],
            _growth_rate: row["avg_growth_all"],
            _series: _all_label,
        })

    df_growth = pd.DataFrame(growth_rows)
    x_ticks = df_bt["base_month"].tolist()[::max(1, len(df_bt) // 10)]

    growth_chart = _apply_theme(
        alt.Chart(df_growth)
        .mark_line(point=alt.OverlayMarkDef(size=30), strokeWidth=2)
        .encode(
            x=alt.X(f"{_period}:N", title=_rec_time,
                    axis=alt.Axis(labelAngle=-45, values=x_ticks)),
            y=alt.Y(f"{_growth_rate}:Q", title=f"{cat_label_val} {t('backtest.kpi_alpha')} (%)"),
            color=alt.Color(
                f"{_series}:N",
                scale=alt.Scale(
                    domain=[_rec_label, _all_label],
                    range=["#359efa", "#989ba2"],
                ),
            ),
            tooltip=[
                alt.Tooltip(f"{_period}:N"),
                alt.Tooltip(f"{_series}:N"),
                alt.Tooltip(f"{_growth_rate}:Q", format=".2f"),
            ],
        )
        .properties(height=340)
        .interactive(),
        dark_mode,
    )
    st.altair_chart(growth_chart, use_container_width=True)

    st.divider()

    # ── Cumulative alpha ─────────────────────────────────────────────────────
    _cum_alpha = t("backtest.alpha_axis")

    st.subheader(t("backtest.alpha_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('backtest.alpha_desc')}</p>",
        unsafe_allow_html=True,
    )

    alpha_data = df_bt[["base_month", "alpha"]].copy()
    alpha_data[_cum_alpha] = alpha_data["alpha"].cumsum().round(2)

    alpha_chart = _apply_theme(
        alt.Chart(alpha_data)
        .mark_area(
            line={"color": "#7de12f", "strokeWidth": 2},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="rgba(125,225,47,0.3)", offset=0),
                    alt.GradientStop(color="rgba(125,225,47,0.02)", offset=1),
                ],
                x1=1, x2=1, y1=1, y2=0,
            ),
        )
        .encode(
            x=alt.X("base_month:N", title=_rec_time,
                    axis=alt.Axis(labelAngle=-45, values=x_ticks)),
            y=alt.Y(f"{_cum_alpha}:Q", title=_cum_alpha),
            tooltip=[
                alt.Tooltip("base_month:N", title=_rec_time),
                alt.Tooltip("alpha:Q", title=t("backtest.alpha_tooltip"), format="+.2f"),
                alt.Tooltip(f"{_cum_alpha}:Q", format="+.2f"),
            ],
        )
        .properties(height=300)
        .interactive(),
        dark_mode,
    )
    st.altair_chart(alpha_chart, use_container_width=True)

    st.divider()

    # ── Latest case details ──────────────────────────────────────────────────
    st.subheader(t("backtest.case_header"))
    latest = results[-1]
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('backtest.case_desc', base=latest['base_month'], end=latest['eval_end'])}"
        f"</p>",
        unsafe_allow_html=True,
    )

    _col_area = t("backtest.col_rec_area")
    _col_actual = t("backtest.col_actual_growth")
    _col_median = t("backtest.col_median")
    _col_verdict = t("backtest.col_verdict")

    case_rows: list[dict] = []
    for lbl, grw in zip(latest["top_labels"], latest["top_growths"]):
        beat = grw > latest["median_growth_all"]
        case_rows.append({
            _col_area: lbl,
            _col_actual: round(grw, 2),
            _col_median: round(latest["median_growth_all"], 2),
            _col_verdict: t("backtest.hit") if beat else t("backtest.miss"),
        })

    df_case = pd.DataFrame(case_rows)

    _chart_rec = t("backtest.chart_rec_growth")
    _chart_baseline = t("backtest.chart_baseline")
    _region = t("c.region")

    case_chart_data: list[dict] = []
    for _, row in df_case.iterrows():
        case_chart_data.append({
            _region: row[_col_area],
            _growth_rate: row[_col_actual],
            _series: _chart_rec,
        })
    case_chart_data.append({
        _region: t("backtest.chart_median_label"),
        _growth_rate: latest["median_growth_all"],
        _series: _chart_baseline,
    })

    df_case_chart = pd.DataFrame(case_chart_data)

    case_bar = _apply_theme(
        alt.Chart(df_case_chart)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y(f"{_region}:N", title="", sort="-x"),
            x=alt.X(f"{_growth_rate}:Q", title=f"{cat_label_val} {t('backtest.kpi_alpha')} (%)"),
            color=alt.Color(
                f"{_series}:N",
                scale=alt.Scale(
                    domain=[_chart_rec, _chart_baseline],
                    range=["#359efa", "#ff5252"],
                ),
            ),
            tooltip=[
                alt.Tooltip(f"{_region}:N"),
                alt.Tooltip(f"{_growth_rate}:Q", format=".2f"),
            ],
        )
        .properties(height=max(200, len(case_chart_data) * 40)),
        dark_mode,
    )
    st.altair_chart(case_bar, use_container_width=True)

    st.dataframe(df_case, use_container_width=True, hide_index=True)

    st.divider()

    # ── Full backtest results table ──────────────────────────────────────────
    st.subheader(t("backtest.full_result"))

    display = df_bt[[
        "base_month", "eval_end",
        "avg_growth_recommended", "avg_growth_all", "alpha",
        "hits", "total", "hit_rate",
    ]].copy()
    display.columns = [
        t("backtest.col_rec_time"), t("backtest.col_eval_end"),
        t("backtest.col_rec_growth"), t("backtest.col_all_growth"), t("backtest.col_alpha"),
        t("backtest.col_hits"), t("backtest.col_recs"), t("backtest.col_hit_rate"),
    ]
    for col in [t("backtest.col_rec_growth"), t("backtest.col_all_growth"), t("backtest.col_alpha"), t("backtest.col_hit_rate")]:
        display[col] = display[col].round(2)
    display.index = range(1, len(display) + 1)
    st.dataframe(display, use_container_width=True, height=400)

    # ── Verdict ──────────────────────────────────────────────────────────────
    st.divider()

    if overall_hit_rate >= 55:
        verdict_icon = "✅"
        verdict = t("backtest.verdict_good",
                     biz=business_type, n=len(df_bt),
                     hr=f"{overall_hit_rate:.1f}", alpha=f"{avg_alpha:+.2f}")
    elif overall_hit_rate >= 45:
        verdict_icon = "⚠️"
        verdict = t("backtest.verdict_mid",
                     biz=business_type, hr=f"{overall_hit_rate:.1f}")
    else:
        verdict_icon = "❌"
        verdict = t("backtest.verdict_bad",
                     biz=business_type, hr=f"{overall_hit_rate:.1f}")

    st.markdown(f"### {verdict_icon} {t('backtest.verdict_header')}\n\n{verdict}")
