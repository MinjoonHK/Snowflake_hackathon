"""Model diagnostics tab — factor predictiveness analysis & weight optimization."""
from __future__ import annotations

from itertools import product as iter_product

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from vitality_app import data
from vitality_app.i18n import business_presets, category_label, factors, t
from vitality_app.tabs.report_tab import (
    _SCORING_WEIGHTS,
    _classify_business,
    _score_districts,
)

# ── Factor definitions ──────────────────────────────────────────────────────
_FACTOR_PCT_COLS = [
    "pct_category", "pct_visiting", "pct_income",
    "pct_population", "pct_growth", "pct_diversity",
]

_WEIGHT_KEYS = [
    "w_category", "w_visiting", "w_income",
    "w_population", "w_growth", "w_diversity",
]


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


# ── Factor predictiveness analysis ──────────────────────────────────────────
def _analyze_factor_predictiveness(
    df_all: pd.DataFrame,
    category_col: str,
    eval_months: int = 3,
) -> pd.DataFrame | None:
    months = sorted(df_all["STANDARD_YEAR_MONTH"].unique())
    if len(months) < eval_months + 2:
        return None

    pct_cols = _FACTOR_PCT_COLS
    records: list[dict] = []

    for i in range(len(months) - eval_months):
        base_month = months[i]
        future_months = months[i + 1: i + 1 + eval_months]

        df_base = df_all[df_all["STANDARD_YEAR_MONTH"] == base_month].copy()
        if len(df_base) < 10:
            continue

        n = len(df_base)
        df_base["MOM_CHANGE_PCT"] = df_base["MOM_CHANGE_PCT"].fillna(0)
        df_base["pct_category"] = df_base[category_col].rank(method="average") / n * 100
        df_base["pct_visiting"] = df_base["SCORE_VISITING"].rank(method="average") / n * 100
        df_base["pct_income"] = df_base["SCORE_INCOME"].rank(method="average") / n * 100
        df_base["pct_population"] = df_base["SCORE_POPULATION"].rank(method="average") / n * 100
        df_base["pct_diversity"] = df_base["SCORE_DIVERSITY"].rank(method="average") / n * 100
        df_base["pct_growth"] = df_base["MOM_CHANGE_PCT"].rank(method="average") / n * 100

        base_sales = df_base.set_index("DISTRICT_CODE")[category_col]
        df_future = df_all[
            (df_all["STANDARD_YEAR_MONTH"].isin(future_months))
            & (df_all["DISTRICT_CODE"].isin(df_base["DISTRICT_CODE"]))
        ]
        if df_future.empty:
            continue

        future_avg = df_future.groupby("DISTRICT_CODE")[category_col].mean()
        common = base_sales.index.intersection(future_avg.index)
        if len(common) < 10:
            continue

        base_c = base_sales.loc[common].replace(0, np.nan)
        growth = ((future_avg.loc[common] - base_c) / base_c * 100).dropna()
        if len(growth) < 10:
            continue

        df_base_indexed = df_base.set_index("DISTRICT_CODE")
        valid = growth.index.intersection(df_base_indexed.index)

        row = {"base_month": base_month}
        for col in pct_cols:
            factor_vals = df_base_indexed.loc[valid, col]
            growth_vals = growth.loc[valid]
            common_idx = factor_vals.dropna().index.intersection(growth_vals.dropna().index)
            if len(common_idx) >= 8:
                corr = np.corrcoef(factor_vals.loc[common_idx], growth_vals.loc[common_idx])[0, 1]
                row[col] = float(corr) if not np.isnan(corr) else 0.0
            else:
                row[col] = 0.0
        records.append(row)

    return pd.DataFrame(records) if records else None


# ── Weight grid search optimization ─────────────────────────────────────────
def _optimize_weights(
    df_all: pd.DataFrame,
    category_col: str,
    eval_months: int = 3,
    n_recommend: int = 5,
    grid_step: float = 0.10,
) -> tuple[dict, float, list] | None:
    months = sorted(df_all["STANDARD_YEAR_MONTH"].unique())
    if len(months) < eval_months + 2:
        return None

    factor_corr = _analyze_factor_predictiveness(df_all, category_col, eval_months)
    if factor_corr is None:
        return None

    pct_cols = _FACTOR_PCT_COLS
    avg_corrs = {col: factor_corr[col].mean() for col in pct_cols}

    sorted_factors = sorted(avg_corrs.items(), key=lambda x: x[1], reverse=True)

    top3 = [f[0] for f in sorted_factors[:3]]
    bottom3 = [f[0] for f in sorted_factors[3:]]

    candidates: list[tuple[dict, float]] = []
    main_steps = [round(x * 0.05, 2) for x in range(1, 13)]

    factor_to_wkey = dict(zip(pct_cols, _WEIGHT_KEYS))

    for w1, w2, w3 in iter_product(main_steps, main_steps, main_steps):
        remaining = round(1.0 - w1 - w2 - w3, 2)
        if remaining < 0 or remaining > 0.30:
            continue
        w_bottom = round(remaining / 3, 3)

        weights = {}
        for f in top3[:1]:
            weights[factor_to_wkey[f]] = w1
        for f in top3[1:2]:
            weights[factor_to_wkey[f]] = w2
        for f in top3[2:3]:
            weights[factor_to_wkey[f]] = w3
        for f in bottom3:
            weights[factor_to_wkey[f]] = w_bottom

        total = sum(weights.values())
        if abs(total - 1.0) > 0.02:
            continue

        hits, total_recs = _quick_backtest(df_all, category_col, weights, eval_months, n_recommend, months)
        if total_recs > 0:
            hr = hits / total_recs * 100
            candidates.append((weights, hr))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[1], reverse=True)
    best_weights, best_hr = candidates[0]

    top_candidates = candidates[:5]
    return best_weights, best_hr, top_candidates


def _quick_backtest(
    df_all: pd.DataFrame,
    category_col: str,
    weights: dict,
    eval_months: int,
    n_recommend: int,
    months: list,
) -> tuple[int, int]:
    total_hits = 0
    total_recs = 0

    for i in range(len(months) - eval_months):
        base_month = months[i]
        future_months = months[i + 1: i + 1 + eval_months]

        df_base = df_all[df_all["STANDARD_YEAR_MONTH"] == base_month].copy()
        if len(df_base) < n_recommend:
            continue

        n = len(df_base)
        df_base["MOM_CHANGE_PCT"] = df_base["MOM_CHANGE_PCT"].fillna(0)
        df_base["pct_category"] = df_base[category_col].rank(method="average") / n * 100
        df_base["pct_visiting"] = df_base["SCORE_VISITING"].rank(method="average") / n * 100
        df_base["pct_income"] = df_base["SCORE_INCOME"].rank(method="average") / n * 100
        df_base["pct_population"] = df_base["SCORE_POPULATION"].rank(method="average") / n * 100
        df_base["pct_diversity"] = df_base["SCORE_DIVERSITY"].rank(method="average") / n * 100
        df_base["pct_growth"] = df_base["MOM_CHANGE_PCT"].rank(method="average") / n * 100

        df_base["SCORE"] = (
            df_base["pct_category"] * weights.get("w_category", 0)
            + df_base["pct_visiting"] * weights.get("w_visiting", 0)
            + df_base["pct_income"] * weights.get("w_income", 0)
            + df_base["pct_population"] * weights.get("w_population", 0)
            + df_base["pct_growth"] * weights.get("w_growth", 0)
            + df_base["pct_diversity"] * weights.get("w_diversity", 0)
        )

        top_codes = df_base.nlargest(n_recommend, "SCORE")["DISTRICT_CODE"].tolist()

        base_sales = df_base.set_index("DISTRICT_CODE")[category_col]
        df_future = df_all[
            (df_all["STANDARD_YEAR_MONTH"].isin(future_months))
            & (df_all["DISTRICT_CODE"].isin(df_base["DISTRICT_CODE"]))
        ]
        if df_future.empty:
            continue

        future_avg = df_future.groupby("DISTRICT_CODE")[category_col].mean()
        common = base_sales.index.intersection(future_avg.index)
        if len(common) < n_recommend:
            continue

        base_c = base_sales.loc[common].replace(0, np.nan)
        growth = ((future_avg.loc[common] - base_c) / base_c * 100).dropna()
        if growth.empty:
            continue

        median_g = growth.median()
        rec_codes = [c for c in top_codes if c in growth.index]
        if not rec_codes:
            continue

        total_hits += int((growth.loc[rec_codes] > median_g).sum())
        total_recs += len(rec_codes)

    return total_hits, total_recs


# ── Main render ─────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header(t("diagnostic.header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:14px;margin-top:-12px'>{t('diagnostic.intro')}</p>",
        unsafe_allow_html=True,
    )

    _presets = business_presets()

    # ── Settings ─────────────────────────────────────────────────────────────
    col_biz, col_eval = st.columns(2)
    with col_biz:
        preset_labels = [p["label"] for p in _presets]
        selected_preset = st.selectbox(t("diagnostic.select_business"), preset_labels, key="diag_biz")
        idx = preset_labels.index(selected_preset)
        business_type = _presets[idx]["value"]
    with col_eval:
        eval_months = st.select_slider(
            t("diagnostic.eval_period"), options=[1, 2, 3, 6], value=3, key="diag_eval",
        )

    category_col = _classify_business(business_type)
    cat_label_val = category_label(category_col)

    st.divider()
    run = st.button(t("diagnostic.run"), type="primary", use_container_width=True)

    sig = f"{business_type}_{eval_months}"
    if st.session_state.get("_diag_sig") != sig:
        st.session_state.pop("_diag_result", None)

    if run:
        with st.spinner(t("diagnostic.analyzing")):
            df_all = data.load_vitality_data(city_codes)
            if df_all.empty:
                st.warning(t("diagnostic.no_data"))
                return

            factor_corr = _analyze_factor_predictiveness(df_all, category_col, eval_months)
            if factor_corr is None:
                st.warning(t("diagnostic.insufficient"))
                return

        with st.spinner(t("diagnostic.optimizing")):
            opt_result = _optimize_weights(df_all, category_col, eval_months)

        current_weights = _SCORING_WEIGHTS.get(category_col, _SCORING_WEIGHTS["FOOD_SALES"])
        months = sorted(df_all["STANDARD_YEAR_MONTH"].unique())
        curr_hits, curr_total = _quick_backtest(
            df_all, category_col, current_weights, eval_months, 5, months,
        )
        curr_hr = curr_hits / curr_total * 100 if curr_total > 0 else 0

        st.session_state["_diag_result"] = {
            "factor_corr": factor_corr,
            "opt_result": opt_result,
            "curr_hr": curr_hr,
            "curr_weights": current_weights,
            "cat_label": cat_label_val,
            "category_col": category_col,
            "business_type": business_type,
            "eval_months": eval_months,
        }
        st.session_state["_diag_sig"] = sig

    # ── Results ──────────────────────────────────────────────────────────────
    result = st.session_state.get("_diag_result")
    if not result:
        return

    factor_corr = result["factor_corr"]
    opt_result = result["opt_result"]
    curr_hr = result["curr_hr"]
    curr_weights = result["curr_weights"]
    cat_label_val = result["cat_label"]
    business_type = result["business_type"]
    eval_months = result["eval_months"]

    _FACTORS = factors()
    pct_cols = _FACTOR_PCT_COLS

    _factor_col = t("c.factor")
    _avg_corr = t("diagnostic.avg_corr")
    _direction = t("c.direction")
    _period = t("c.period")
    _corr = t("c.correlation")

    # ── Section 1: Diagnosis ─────────────────────────────────────────────────
    st.subheader(t("diagnostic.s1_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('diagnostic.s1_desc')}</p>",
        unsafe_allow_html=True,
    )

    avg_corrs = {col: factor_corr[col].mean() for col in pct_cols}

    corr_data = pd.DataFrame([
        {_factor_col: _FACTORS[col], _avg_corr: round(avg_corrs[col], 3),
         _direction: t("diagnostic.dir_positive") if avg_corrs[col] > 0 else t("diagnostic.dir_negative")}
        for col in pct_cols
    ])

    corr_bar = _apply_theme(
        alt.Chart(corr_data)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y(f"{_factor_col}:N", title="", sort="-x"),
            x=alt.X(f"{_avg_corr}:Q", title=t("diagnostic.corr_axis")),
            color=alt.condition(
                alt.datum[_avg_corr] > 0,
                alt.value("#7de12f"),
                alt.value("#ff5252"),
            ),
            tooltip=[
                alt.Tooltip(f"{_factor_col}:N"),
                alt.Tooltip(f"{_avg_corr}:Q", format=".3f"),
            ],
        )
        .properties(height=220),
        dark_mode,
    )

    zero_rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(
        strokeDash=[4, 4], color="#989ba2", opacity=0.5,
    ).encode(x="x:Q")

    st.altair_chart(corr_bar + zero_rule, use_container_width=True)

    negative_factors = [(_FACTORS[c], avg_corrs[c]) for c in pct_cols if avg_corrs[c] < -0.02]
    positive_factors = [(_FACTORS[c], avg_corrs[c]) for c in pct_cols if avg_corrs[c] > 0.02]

    if negative_factors:
        neg_text = ", ".join(f"**{f}** (r={v:.3f})" for f, v in negative_factors)
        st.markdown(
            f"<div style='background:#2d1a1a;border:1px solid #ff5252;border-radius:8px;"
            f"padding:12px 16px;margin:8px 0'>"
            f"<p style='color:#ff5252;font-weight:600;margin:0 0 4px'>{t('diagnostic.neg_title')}</p>"
            f"<p style='color:#ffffff;margin:0'>{neg_text} — {t('diagnostic.neg_text')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if positive_factors:
        pos_text = ", ".join(f"**{f}** (r={v:.3f})" for f, v in positive_factors)
        st.markdown(
            f"<div style='background:#1a2d1a;border:1px solid #7de12f;border-radius:8px;"
            f"padding:12px 16px;margin:8px 0'>"
            f"<p style='color:#7de12f;font-weight:600;margin:0 0 4px'>{t('diagnostic.pos_title')}</p>"
            f"<p style='color:#ffffff;margin:0'>{pos_text} — {t('diagnostic.pos_text')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Section 2: Heatmap ───────────────────────────────────────────────────
    st.subheader(t("diagnostic.s2_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('diagnostic.s2_desc')}</p>",
        unsafe_allow_html=True,
    )

    heat_rows = []
    for _, row in factor_corr.iterrows():
        for col in pct_cols:
            heat_rows.append({
                _period: row["base_month"],
                _factor_col: _FACTORS[col],
                _corr: round(row[col], 3),
            })
    df_heat = pd.DataFrame(heat_rows)

    all_months = factor_corr["base_month"].tolist()
    step = max(1, len(all_months) // 15)
    x_ticks = all_months[::step]

    heat = (
        alt.Chart(df_heat)
        .mark_rect()
        .encode(
            x=alt.X(f"{_period}:N", title=t("backtest.axis_rec_time"),
                    axis=alt.Axis(labelAngle=-45, values=x_ticks)),
            y=alt.Y(f"{_factor_col}:N", title=""),
            color=alt.Color(
                f"{_corr}:Q",
                scale=alt.Scale(
                    domain=[-0.3, 0, 0.3],
                    range=["#ff5252", "#292a2d" if dark_mode else "#dbdcdf", "#7de12f"],
                ),
                title="r",
            ),
            tooltip=[
                alt.Tooltip(f"{_period}:N"),
                alt.Tooltip(f"{_factor_col}:N"),
                alt.Tooltip(f"{_corr}:Q", format=".3f"),
            ],
        )
        .properties(height=240)
    )

    heat_chart = _apply_theme(heat, dark_mode)
    st.altair_chart(heat_chart, use_container_width=True)

    st.divider()

    # ── Section 3: Weight optimization results ───────────────────────────────
    st.subheader(t("diagnostic.s3_header"))

    if opt_result is None:
        st.warning(t("diagnostic.opt_failed"))
        return

    best_weights, best_hr, top_candidates = opt_result

    improvement = best_hr - curr_hr
    k1, k2, k3 = st.columns(3)
    k1.metric(t("diagnostic.kpi_current"), f"{curr_hr:.1f}%", t("diagnostic.kpi_current_desc"))
    k2.metric(t("diagnostic.kpi_optimized"), f"{best_hr:.1f}%", t("diagnostic.kpi_improvement", v=f"{improvement:+.1f}"))

    _model = t("c.model")
    _weight = t("c.weight")
    _model_current = t("diagnostic.model_current")
    _model_optimized = t("diagnostic.model_optimized")

    if best_hr >= 55:
        k3.markdown(
            "<div style='padding:16px;border:1px solid #7de12f;border-radius:8px;"
            f"background:{'#171719' if dark_mode else '#ffffff'};text-align:center'>"
            f"<p style='font-size:12px;color:#989ba2;margin:0'>{t('diagnostic.trust_label')}</p>"
            f"<p style='font-size:28px;font-weight:700;color:#7de12f;margin:4px 0 0'>{t('diagnostic.trust_valid')}</p></div>",
            unsafe_allow_html=True,
        )
    else:
        k3.markdown(
            "<div style='padding:16px;border:1px solid #ff9f40;border-radius:8px;"
            f"background:{'#171719' if dark_mode else '#ffffff'};text-align:center'>"
            f"<p style='font-size:12px;color:#989ba2;margin:0'>{t('diagnostic.trust_label')}</p>"
            f"<p style='font-size:28px;font-weight:700;color:#ff9f40;margin:4px 0 0'>{t('diagnostic.trust_moderate')}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    pct_to_wkey = dict(zip(pct_cols, _WEIGHT_KEYS))
    weight_rows = []
    for col in pct_cols:
        wk = pct_to_wkey[col]
        weight_rows.append({
            _factor_col: _FACTORS[col],
            _weight: curr_weights.get(wk, 0) * 100,
            _model: _model_current,
        })
        weight_rows.append({
            _factor_col: _FACTORS[col],
            _weight: best_weights.get(wk, 0) * 100,
            _model: _model_optimized,
        })

    df_weights = pd.DataFrame(weight_rows)

    weight_chart = _apply_theme(
        alt.Chart(df_weights)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{_factor_col}:N", title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{_weight}:Q", title=t("diagnostic.weight_axis")),
            color=alt.Color(
                f"{_model}:N",
                scale=alt.Scale(
                    domain=[_model_current, _model_optimized],
                    range=["#989ba2", "#359efa"],
                ),
            ),
            xOffset=alt.XOffset(f"{_model}:N"),
            tooltip=[
                alt.Tooltip(f"{_factor_col}:N"),
                alt.Tooltip(f"{_model}:N"),
                alt.Tooltip(f"{_weight}:Q", format=".1f"),
            ],
        )
        .properties(height=300),
        dark_mode,
    )
    st.altair_chart(weight_chart, use_container_width=True)

    st.divider()

    # ── Section 4: Optimal weight details ────────────────────────────────────
    st.subheader(t("diagnostic.s4_header"))

    detail_rows = []
    for col, wk in zip(pct_cols, _WEIGHT_KEYS):
        detail_rows.append({
            _factor_col: _FACTORS[col],
            t("diagnostic.col_current"): f"{curr_weights.get(wk, 0) * 100:.0f}%",
            t("diagnostic.col_optimized"): f"{best_weights.get(wk, 0) * 100:.0f}%",
            t("diagnostic.col_change"): f"{(best_weights.get(wk, 0) - curr_weights.get(wk, 0)) * 100:+.0f}%p",
        })
    st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    st.divider()

    # ── Section 5: Apply ─────────────────────────────────────────────────────
    st.subheader(t("diagnostic.s5_header"))

    if improvement > 0:
        st.markdown(
            t("diagnostic.apply_good",
              curr=f"{curr_hr:.1f}", best=f"{best_hr:.1f}", imp=f"{improvement:.1f}")
        )
    else:
        st.markdown(
            t("diagnostic.apply_bad", best=f"{best_hr:.1f}")
        )

    if st.button(t("diagnostic.apply_btn"), type="primary"):
        st.session_state["_optimized_weights"] = {
            "category_col": result["category_col"],
            "weights": best_weights,
            "hit_rate": best_hr,
        }
        st.success(
            t("diagnostic.apply_success",
              curr=f"{curr_hr:.1f}", best=f"{best_hr:.1f}")
        )

    st.divider()

    # ── Section 6: Interpretation guide ──────────────────────────────────────
    st.subheader(t("diagnostic.s6_header"))

    sorted_by_corr = sorted(avg_corrs.items(), key=lambda x: x[1], reverse=True)
    interpretations = []
    for col, corr in sorted_by_corr:
        label = _FACTORS[col]
        if corr < -0.05:
            interpretations.append(
                f"- **{label}** (r={corr:.3f}): {t('diagnostic.interp_saturated')}"
            )
        elif corr < 0.02:
            interpretations.append(
                f"- **{label}** (r={corr:.3f}): {t('diagnostic.interp_useless')}"
            )
        else:
            interpretations.append(
                f"- **{label}** (r={corr:.3f}): {t('diagnostic.interp_valid')}"
            )

    st.markdown("\n".join(interpretations))
