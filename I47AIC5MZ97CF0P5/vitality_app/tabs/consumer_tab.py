"""Migration × category spending analysis tab."""
from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from vitality_app import data
from vitality_app.i18n import categories, t

_LAG_MONTHS = [0, 1, 2, 3, 6]


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


# ── Aggregation helper ──────────────────────────────────────────────────────
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


def _corr_safe(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 6:
        return float("nan")
    try:
        c = np.corrcoef(x, y)[0, 1]
        return float(c) if not np.isnan(c) else float("nan")
    except Exception:
        return float("nan")


# ── Main render ─────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header(t("consumer.header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:14px;margin-top:-12px'>{t('consumer.intro')}</p>",
        unsafe_allow_html=True,
    )

    _CATS = categories()

    with st.spinner(t("consumer.spinner")):
        all_cities_df = data.load_available_cities()
        all_city_codes = tuple(all_cities_df["CITY_CODE"].tolist())
        all_city_name_map = all_cities_df.set_index("CITY_CODE")["CITY_KOR_NAME"].to_dict()

        df_mig = data.load_migration_by_city(all_city_codes)
        df_age = data.load_age_population_by_city(all_city_codes)
        df_vit = data.load_vitality_data(all_city_codes)

    if df_mig.empty or df_vit.empty:
        st.warning(t("common.no_data"))
        return

    df_cons = _agg_vitality_to_city(df_vit)

    avail = set(df_mig["CITY_CODE"].unique())
    options = {k: v for k, v in all_city_name_map.items() if k in avail}

    if not options:
        st.warning(t("common.no_data"))
        return

    selected_city = st.selectbox(
        t("consumer.select_gu"),
        options=list(options.keys()),
        format_func=lambda x: options.get(x, x),
    )
    city_name = options[selected_city]

    mig = df_mig[df_mig["CITY_CODE"] == selected_city].sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)
    age = df_age[df_age["CITY_CODE"] == selected_city].sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)
    cons = df_cons[df_cons["CITY_CODE"] == selected_city].sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)

    merged = pd.merge(
        mig[["STANDARD_YEAR_MONTH", "CITY_CODE", "MOVE_IN", "MOVE_OUT", "NET_MOVEMENT"]],
        cons.drop(columns=["CITY_KOR_NAME"], errors="ignore"),
        on=["STANDARD_YEAR_MONTH", "CITY_CODE"],
        how="inner",
    ).sort_values("STANDARD_YEAR_MONTH").reset_index(drop=True)

    # ── KPI cards ────────────────────────────────────────────────────────────
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

    best_cat, best_corr = "N/A", 0.0
    if len(merged) >= 8:
        for col, label in _CATS.items():
            c = _corr_safe(merged["MOVE_IN"].values[:-1], merged[col].values[1:])
            if not np.isnan(c) and abs(c) > abs(best_corr):
                best_corr, best_cat = c, label

    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric(
        t("consumer.kpi_move_in", name=city_name),
        f"{move_in_now:,}",
        t("consumer.kpi_move_in_delta", pct=f"{delta_pct:+.1f}"),
    )
    kc2.metric(t("consumer.kpi_net"), f"{net_val:,}", t("consumer.kpi_net_desc"))
    kc3.metric(t("consumer.kpi_young"), f"{young_ratio:.1f}%", t("consumer.kpi_young_desc"))
    kc4.metric(
        t("consumer.kpi_best_cat"),
        best_cat,
        f"r = {best_corr:.2f}" if best_cat != "N/A" else "",
    )

    st.divider()

    # ── Section 1: Migration trend ───────────────────────────────────────────
    st.subheader(t("consumer.mig_header", name=city_name))

    _series = t("c.series")
    _count = t("consumer.mig_count")
    _period = t("c.period")
    _mig_in = t("consumer.mig_in")
    _mig_out = t("consumer.mig_out")
    _mig_net = t("consumer.mig_net")

    x_ticks = mig["STANDARD_YEAR_MONTH"].unique()[::6].tolist()
    mig_long = mig.melt(
        id_vars=["STANDARD_YEAR_MONTH"],
        value_vars=["MOVE_IN", "MOVE_OUT", "NET_MOVEMENT"],
        var_name=_series, value_name=_count,
    )
    mig_long[_series] = mig_long[_series].map(
        {"MOVE_IN": _mig_in, "MOVE_OUT": _mig_out, "NET_MOVEMENT": _mig_net}
    )

    mig_chart = _apply_theme(
        alt.Chart(mig_long)
        .mark_line(point=alt.OverlayMarkDef(size=30), strokeWidth=2)
        .encode(
            x=alt.X("STANDARD_YEAR_MONTH:N", title=_period,
                    axis=alt.Axis(labelAngle=-45, values=x_ticks)),
            y=alt.Y(f"{_count}:Q", title=t("consumer.pop_axis")),
            color=alt.Color(
                f"{_series}:N",
                scale=alt.Scale(
                    domain=[_mig_in, _mig_out, _mig_net],
                    range=["#359efa", "#ff5252", "#7de12f"],
                ),
            ),
            tooltip=[
                alt.Tooltip("STANDARD_YEAR_MONTH:N", title=_period),
                alt.Tooltip(f"{_series}:N"),
                alt.Tooltip(f"{_count}:Q", format=","),
            ],
        )
        .properties(height=320)
        .interactive(),
        dark_mode,
    )
    st.altair_chart(mig_chart, use_container_width=True)

    st.divider()

    # ── Section 2: Normalized comparison ─────────────────────────────────────
    st.subheader(t("consumer.norm_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('consumer.norm_desc')}</p>",
        unsafe_allow_html=True,
    )

    selected_cats = st.multiselect(
        t("consumer.select_cats"),
        options=list(_CATS.keys()),
        default=["COFFEE_SALES", "ENTERTAINMENT_SALES"],
        format_func=lambda x: _CATS[x],
        max_selections=3,
    )

    _val = t("c.value")

    if selected_cats and not merged.empty:
        norm_rows: list[dict] = []

        def _norm(series: pd.Series) -> pd.Series:
            mn, mx = series.min(), series.max()
            return (series - mn) / (mx - mn + 1e-9) * 100

        norm_mi = _norm(merged["MOVE_IN"])
        for i, row in merged.iterrows():
            norm_rows.append({
                _period: row["STANDARD_YEAR_MONTH"],
                _val: float(norm_mi.iloc[i]),
                _series: t("consumer.move_in_label"),
            })

        for col in selected_cats:
            norm_col = _norm(merged[col])
            for i, row in merged.iterrows():
                norm_rows.append({
                    _period: row["STANDARD_YEAR_MONTH"],
                    _val: float(norm_col.iloc[i]),
                    _series: _CATS[col],
                })

        df_norm = pd.DataFrame(norm_rows)
        x_ticks2 = merged["STANDARD_YEAR_MONTH"].unique()[::6].tolist()

        compare_chart = _apply_theme(
            alt.Chart(df_norm)
            .mark_line(point=alt.OverlayMarkDef(size=25), strokeWidth=2)
            .encode(
                x=alt.X(f"{_period}:N", title=_period,
                        axis=alt.Axis(labelAngle=-45, values=x_ticks2)),
                y=alt.Y(f"{_val}:Q", title=t("consumer.norm_axis")),
                color=alt.Color(f"{_series}:N"),
                tooltip=[
                    alt.Tooltip(f"{_period}:N"),
                    alt.Tooltip(f"{_series}:N"),
                    alt.Tooltip(f"{_val}:Q", format=".1f"),
                ],
            )
            .properties(height=380)
            .interactive(),
            dark_mode,
        )
        st.altair_chart(compare_chart, use_container_width=True)
        st.caption(t("consumer.caption_norm"))

    st.divider()

    # ── Section 3: Lag correlation heatmap ───────────────────────────────────
    st.subheader(t("consumer.lag_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('consumer.lag_desc')}</p>",
        unsafe_allow_html=True,
    )

    _cat_label = t("c.category")
    _corr = t("c.correlation")
    _display = t("c.display_val")

    corr_rows: list[dict] = []
    if len(merged) >= 8:
        for col, label in _CATS.items():
            for lag in _LAG_MONTHS:
                if lag == 0:
                    x = merged["MOVE_IN"].values
                    y = merged[col].values
                else:
                    x = merged["MOVE_IN"].values[:-lag]
                    y = merged[col].values[lag:]
                c = _corr_safe(x, y)
                corr_rows.append({
                    _cat_label: label,
                    "Lag": t("c.n_months", n=lag),
                    _corr: round(c, 3) if not np.isnan(c) else 0.0,
                    _display: f"{c:.2f}" if not np.isnan(c) else "N/A",
                })

    if corr_rows:
        df_corr = pd.DataFrame(corr_rows)

        lag_labels = [t("c.n_months", n=l) for l in _LAG_MONTHS]

        heat = (
            alt.Chart(df_corr)
            .mark_rect()
            .encode(
                x=alt.X("Lag:N", title=t("consumer.lag_x_axis"),
                        sort=lag_labels),
                y=alt.Y(f"{_cat_label}:N", title=_cat_label),
                color=alt.Color(
                    f"{_corr}:Q",
                    scale=alt.Scale(domain=[-1, 0, 1],
                                    range=["#ff5252", "#292a2d" if dark_mode else "#dbdcdf", "#359efa"]),
                    title=t("consumer.lag_corr_r"),
                    legend=alt.Legend(gradientLength=150),
                ),
                tooltip=[
                    alt.Tooltip(f"{_cat_label}:N"),
                    alt.Tooltip("Lag:N", title=t("consumer.lag_tooltip_months")),
                    alt.Tooltip(f"{_corr}:Q", format=".3f"),
                ],
            )
        )

        text = (
            alt.Chart(df_corr)
            .mark_text(fontSize=13, fontWeight=600)
            .encode(
                x=alt.X("Lag:N", sort=lag_labels),
                y=alt.Y(f"{_cat_label}:N"),
                text=alt.Text(f"{_display}:N"),
                color=alt.condition(
                    f"abs(datum['{_corr}']) > 0.35",
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
        st.caption(t("consumer.lag_caption"))
    else:
        st.info(t("consumer.lag_no_data"))

    st.divider()

    # ── Section 4: Age group population trend ────────────────────────────────
    st.subheader(t("consumer.age_header", name=city_name))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('consumer.age_desc')}</p>",
        unsafe_allow_html=True,
    )

    _age_group = t("consumer.age_group")
    _age_ratio = t("consumer.age_ratio")
    _age_20_30 = t("consumer.age_20_30")
    _age_40_50 = t("consumer.age_40_50")
    _age_60_plus = t("consumer.age_60_plus")

    if not age.empty:
        age = age.copy()
        safe_total = age["POP_TOTAL"].replace(0, np.nan)
        age[_age_20_30] = (age["POP_20S"] + age["POP_30S"]) / safe_total * 100
        age[_age_40_50] = (age["POP_40S"] + age["POP_50S"]) / safe_total * 100
        age[_age_60_plus] = (age["POP_60S"] + age["POP_OVER70"]) / safe_total * 100

        age_long = age.melt(
            id_vars=["STANDARD_YEAR_MONTH"],
            value_vars=[_age_20_30, _age_40_50, _age_60_plus],
            var_name=_age_group, value_name=_age_ratio,
        ).dropna(subset=[_age_ratio])

        x_ticks3 = age["STANDARD_YEAR_MONTH"].unique()[::6].tolist()

        age_chart = _apply_theme(
            alt.Chart(age_long)
            .mark_line(point=alt.OverlayMarkDef(size=25), strokeWidth=2)
            .encode(
                x=alt.X("STANDARD_YEAR_MONTH:N", title=_period,
                        axis=alt.Axis(labelAngle=-45, values=x_ticks3)),
                y=alt.Y(f"{_age_ratio}:Q", title=t("consumer.pop_ratio_axis")),
                color=alt.Color(
                    f"{_age_group}:N",
                    scale=alt.Scale(
                        domain=[_age_20_30, _age_40_50, _age_60_plus],
                        range=["#359efa", "#ff5252", "#989ba2"],
                    ),
                ),
                tooltip=[
                    alt.Tooltip("STANDARD_YEAR_MONTH:N", title=_period),
                    alt.Tooltip(f"{_age_group}:N"),
                    alt.Tooltip(f"{_age_ratio}:Q", format=".1f"),
                ],
            )
            .properties(height=300)
            .interactive(),
            dark_mode,
        )
        st.altair_chart(age_chart, use_container_width=True)
        st.caption(t("consumer.caption_age"))
    else:
        st.info(t("consumer.no_age_data"))
