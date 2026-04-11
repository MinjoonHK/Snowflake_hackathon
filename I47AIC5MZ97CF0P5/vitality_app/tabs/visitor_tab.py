"""Visitor-dominant neighborhood analysis — high visit / low spend pass-through detection."""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from vitality_app import data
from vitality_app.i18n import quadrants, t

# ── Design system colors ─────────────────────────────────────────────────────
_C_SPECTATOR = "#ff5252"   # error-50
_C_ACTIVE    = "#7de12f"   # secondary-40
_C_LOCAL     = "#359efa"   # primary-40
_C_STAGNANT  = "#989ba2"   # neutral-40


def _quad_colors() -> dict[str, str]:
    q = quadrants()
    return {
        q["spectator"]: _C_SPECTATOR,
        q["active"]:    _C_ACTIVE,
        q["local"]:     _C_LOCAL,
        q["stagnant"]:  _C_STAGNANT,
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
    q = quadrants()
    high_visit = score_visit >= visit_med
    high_cons  = score_cons  >= cons_med
    if high_visit and not high_cons:
        return q["spectator"]
    if high_visit and high_cons:
        return q["active"]
    if not high_visit and high_cons:
        return q["local"]
    return q["stagnant"]


def render(city_codes: tuple, city_code_to_name: dict, selected_month: str, dark_mode: bool = True):
    st.header(t("visitor.header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:14px;margin-top:-12px'>{t('visitor.intro')}</p>",
        unsafe_allow_html=True,
    )

    df_all = data.load_visitor_data(city_codes)
    if df_all.empty:
        st.warning(t("common.no_data"))
        return

    df = df_all[df_all["STANDARD_YEAR_MONTH"] == selected_month].copy()
    if df.empty:
        st.warning(t("common.no_data_period"))
        return

    n = len(df)
    df["PCT_VISITING"]    = df["SCORE_VISITING"].rank(method="average") / n * 100
    df["PCT_CONSUMPTION"] = df["SCORE_CONSUMPTION"].rank(method="average") / n * 100

    visit_med = 50.0
    cons_med  = 50.0
    df["QUADRANT"] = df.apply(
        lambda r: _classify_quadrant(
            r["PCT_VISITING"], r["PCT_CONSUMPTION"], visit_med, cons_med
        ),
        axis=1,
    )
    df["LABEL"] = df["CITY_KOR_NAME"] + " " + df["DISTRICT_KOR_NAME"]

    q = quadrants()
    qcolors = _quad_colors()

    spectators = df[df["QUADRANT"] == q["spectator"]]
    ridership_med = spectators["TOTAL_RIDERSHIP"].median() if not spectators.empty else 0
    confirmed = spectators[spectators["TOTAL_RIDERSHIP"] > ridership_med]

    # ── KPI cards ────────────────────────────────────────────────────────────
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(
        t("visitor.kpi_spectator"),
        f"{len(spectators)}",
        t("visitor.kpi_spectator_total", total=len(df)),
    )
    kpi2.metric(t("visitor.kpi_passthrough"), f"{len(confirmed)}", t("visitor.kpi_passthrough_desc"))
    kpi3.metric(t("visitor.kpi_visit_pct"), "50.0", t("visitor.kpi_median_quadrant"))
    kpi4.metric(t("visitor.kpi_spend_pct"), "50.0", t("visitor.kpi_median_quadrant"))

    st.divider()

    # ── Quadrant scatter ─────────────────────────────────────────────────────
    st.subheader(t("visitor.quad_header"))

    _type = t("c.type")

    color_scale = alt.Scale(
        domain=list(qcolors.keys()),
        range=list(qcolors.values()),
    )

    quad_labels = pd.DataFrame([
        {"lx": 75, "ly": 25, "text": f"{q['spectator']} 🚇"},
        {"lx": 75, "ly": 75, "text": f"{q['active']} ✨"},
        {"lx": 25, "ly": 75, "text": f"{q['local']} 🏘️"},
        {"lx": 25, "ly": 25, "text": f"{q['stagnant']} 💤"},
    ])

    scatter = (
        alt.Chart(df)
        .mark_circle(opacity=0.8)
        .encode(
            x=alt.X("PCT_VISITING:Q", title=t("visitor.axis_visit_pct"),
                    scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("PCT_CONSUMPTION:Q", title=t("visitor.axis_spend_pct"),
                    scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("QUADRANT:N", title=_type, scale=color_scale),
            size=alt.Size("TOTAL_RIDERSHIP:Q", title=t("visitor.legend_subway"),
                          scale=alt.Scale(range=[40, 500])),
            tooltip=[
                alt.Tooltip("LABEL:N",             title=t("c.district")),
                alt.Tooltip("QUADRANT:N",           title=_type),
                alt.Tooltip("PCT_VISITING:Q",       title=t("visitor.axis_visit_pct"),   format=".1f"),
                alt.Tooltip("PCT_CONSUMPTION:Q",    title=t("visitor.axis_spend_pct"),   format=".1f"),
                alt.Tooltip("TOTAL_RIDERSHIP:Q",    title=t("visitor.tooltip_ridership"), format=","),
                alt.Tooltip("STATION_CNT:Q",        title=t("visitor.tooltip_station")),
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
    st.caption(t("visitor.caption_scatter"))

    st.divider()

    # ── Spectator zone detail list ───────────────────────────────────────────
    st.subheader(t("visitor.list_header"))

    if spectators.empty:
        st.info(t("visitor.no_spectator"))
    else:
        spec = spectators.copy()
        _gap_col = t("visitor.col_pct_gap")
        _pt_col = t("visitor.col_passthrough")
        spec[_gap_col] = (spec["PCT_VISITING"] - spec["PCT_CONSUMPTION"]).round(1)
        spec[_pt_col] = spec["TOTAL_RIDERSHIP"].apply(
            lambda x: t("visitor.passthrough_yes") if x > ridership_med else t("visitor.passthrough_no")
        )
        display = spec[[
            "CITY_KOR_NAME", "DISTRICT_KOR_NAME",
            "PCT_VISITING", "PCT_CONSUMPTION", _gap_col,
            "TOTAL_VISITING", "TOTAL_CARD_SALES",
            "STATION_CNT", "MIN_DISTANCE", "TOTAL_RIDERSHIP", _pt_col,
        ]].sort_values(_gap_col, ascending=False).reset_index(drop=True)
        display.index += 1
        display.columns = [
            t("c.gu"), t("c.dong"),
            t("visitor.col_visit_pct"), t("visitor.col_spend_pct"), t("visitor.col_gap"),
            t("visitor.col_visitors"), t("visitor.col_sales"),
            t("visitor.col_stations"), t("visitor.col_distance"),
            t("visitor.col_ridership"), t("visitor.col_passthrough"),
        ]
        st.dataframe(display, use_container_width=True, height=400)

    st.divider()

    # ── Subway ridership vs card spend ───────────────────────────────────────
    st.subheader(t("visitor.subway_header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:13px;margin-top:-10px'>"
        f"{t('visitor.subway_desc')}</p>",
        unsafe_allow_html=True,
    )

    df_transit = df[df["TOTAL_RIDERSHIP"] > 0].copy()
    if not df_transit.empty:
        transit_chart = _apply_theme(
            alt.Chart(df_transit)
            .mark_circle(size=70, opacity=0.8)
            .encode(
                x=alt.X("TOTAL_RIDERSHIP:Q", title=t("visitor.axis_ridership"),
                        scale=alt.Scale(zero=False)),
                y=alt.Y("TOTAL_CARD_SALES:Q", title=t("visitor.axis_card_sales"),
                        scale=alt.Scale(zero=False)),
                color=alt.Color("QUADRANT:N", title=_type, scale=color_scale),
                tooltip=[
                    alt.Tooltip("LABEL:N",             title=t("c.district")),
                    alt.Tooltip("QUADRANT:N",           title=_type),
                    alt.Tooltip("TOTAL_RIDERSHIP:Q",   title=t("visitor.tooltip_ridership"), format=","),
                    alt.Tooltip("TOTAL_CARD_SALES:Q",  title=t("visitor.tooltip_card_sales"), format=","),
                    alt.Tooltip("STATION_CNT:Q",        title=t("visitor.tooltip_station")),
                ],
            )
            .properties(height=400)
            .interactive(),
            dark_mode,
        )
        st.altair_chart(transit_chart, use_container_width=True)
    else:
        st.info(t("visitor.no_subway"))

    st.divider()

    # ── Spectator zone visit & spend trends ──────────────────────────────────
    st.subheader(t("visitor.trend_header"))

    if not spectators.empty:
        top_codes = spectators.nlargest(5, "PCT_VISITING")["DISTRICT_CODE"].tolist()
        district_options = {
            row["DISTRICT_CODE"]: f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
            for _, row in spectators.iterrows()
        }
        selected = st.multiselect(
            t("visitor.select_spectator"),
            options=list(district_options.keys()),
            default=top_codes[:3],
            format_func=lambda x: district_options.get(x, x),
            max_selections=5,
        )

        if selected:
            df_trend = df_all[df_all["DISTRICT_CODE"].isin(selected)].copy()
            df_trend["LABEL"] = df_trend["CITY_KOR_NAME"] + " " + df_trend["DISTRICT_KOR_NAME"]

            _district = t("c.district")
            _period = t("c.period")
            _score = t("c.score")
            _series = t("c.series")
            _visit_score = t("visitor.visit_score")
            _spend_score = t("visitor.spend_score")

            trend_rows = []
            for _, row in df_trend.iterrows():
                trend_rows.append({
                    _district: row["LABEL"], _period: row["STANDARD_YEAR_MONTH"],
                    _score: row["SCORE_VISITING"],    _series: _visit_score,
                })
                trend_rows.append({
                    _district: row["LABEL"], _period: row["STANDARD_YEAR_MONTH"],
                    _score: row["SCORE_CONSUMPTION"], _series: _spend_score,
                })
            df_trend_long = pd.DataFrame(trend_rows)
            x_ticks = df_trend_long[_period].unique()[::6].tolist()

            trend_chart = _apply_theme(
                alt.Chart(df_trend_long)
                .mark_line(point=alt.OverlayMarkDef(size=50), strokeWidth=2)
                .encode(
                    x=alt.X(f"{_period}:N", title=_period,
                            axis=alt.Axis(labelAngle=-45, values=x_ticks)),
                    y=alt.Y(f"{_score}:Q", title=_score, scale=alt.Scale(zero=False)),
                    color=alt.Color(f"{_district}:N"),
                    strokeDash=alt.StrokeDash(
                        f"{_series}:N",
                        scale=alt.Scale(
                            domain=[_visit_score, _spend_score],
                            range=[[1, 0], [6, 3]],
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip(f"{_district}:N"),
                        alt.Tooltip(f"{_period}:N"),
                        alt.Tooltip(f"{_series}:N"),
                        alt.Tooltip(f"{_score}:Q", format=".1f"),
                    ],
                )
                .properties(height=380)
                .interactive(),
                dark_mode,
            )
            st.altair_chart(trend_chart, use_container_width=True)
            st.caption(t("visitor.caption_trend"))
