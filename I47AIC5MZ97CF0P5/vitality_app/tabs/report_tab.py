"""Startup location report tab — business type → optimal location analysis."""
from __future__ import annotations

import json

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from vitality_app import data
from vitality_app.i18n import business_presets, categories, category_label, factors, t
from vitality_app.session import get_session

# ── Keyword → category mapping (Korean keywords for classification) ─────────
_KEYWORD_TO_CATEGORY: list[tuple[str, str]] = [
    ("치킨", "FOOD_SALES"), ("고기", "FOOD_SALES"), ("삼겹살", "FOOD_SALES"),
    ("음식", "FOOD_SALES"), ("식당", "FOOD_SALES"), ("분식", "FOOD_SALES"),
    ("피자", "FOOD_SALES"), ("국밥", "FOOD_SALES"), ("돈까스", "FOOD_SALES"),
    ("떡볶이", "FOOD_SALES"), ("초밥", "FOOD_SALES"), ("중식", "FOOD_SALES"),
    ("한식", "FOOD_SALES"), ("양식", "FOOD_SALES"), ("일식", "FOOD_SALES"),
    ("족발", "FOOD_SALES"), ("보쌈", "FOOD_SALES"), ("곱창", "FOOD_SALES"),
    ("해장", "FOOD_SALES"), ("밥", "FOOD_SALES"),
    ("카페", "COFFEE_SALES"), ("커피", "COFFEE_SALES"), ("디저트", "COFFEE_SALES"),
    ("베이커리", "COFFEE_SALES"), ("빵", "COFFEE_SALES"), ("케이크", "COFFEE_SALES"),
    ("헬스", "LEISURE_SALES"), ("필라테스", "LEISURE_SALES"), ("요가", "LEISURE_SALES"),
    ("수영", "LEISURE_SALES"), ("스포츠", "LEISURE_SALES"), ("당구", "LEISURE_SALES"),
    ("볼링", "LEISURE_SALES"), ("짐", "LEISURE_SALES"), ("피트니스", "LEISURE_SALES"),
    ("노래방", "ENTERTAINMENT_SALES"), ("PC방", "ENTERTAINMENT_SALES"),
    ("게임", "ENTERTAINMENT_SALES"), ("오락", "ENTERTAINMENT_SALES"),
    ("방탈출", "ENTERTAINMENT_SALES"),
    ("옷", "FASHION_SALES"), ("패션", "FASHION_SALES"), ("의류", "FASHION_SALES"),
    ("신발", "FASHION_SALES"), ("액세서리", "FASHION_SALES"),
    ("미용", "FASHION_SALES"), ("네일", "FASHION_SALES"), ("헤어", "FASHION_SALES"),
    ("뷰티", "FASHION_SALES"),
    ("편의점", "SMALL_RETAIL_SALES"), ("마트", "SMALL_RETAIL_SALES"),
    ("소매", "SMALL_RETAIL_SALES"), ("약국", "SMALL_RETAIL_SALES"),
    ("세탁", "SMALL_RETAIL_SALES"), ("문구", "SMALL_RETAIL_SALES"),
    ("꽃", "SMALL_RETAIL_SALES"),
]

# ── Category scoring weights ────────────────────────────────────────────────
_SCORING_WEIGHTS: dict[str, dict[str, float]] = {
    "FOOD_SALES": {
        "w_category": 0.30, "w_visiting": 0.25, "w_income": 0.15,
        "w_population": 0.15, "w_growth": 0.10, "w_diversity": 0.05,
    },
    "COFFEE_SALES": {
        "w_category": 0.25, "w_visiting": 0.30, "w_income": 0.15,
        "w_population": 0.10, "w_growth": 0.15, "w_diversity": 0.05,
    },
    "LEISURE_SALES": {
        "w_category": 0.30, "w_visiting": 0.15, "w_income": 0.20,
        "w_population": 0.20, "w_growth": 0.10, "w_diversity": 0.05,
    },
    "ENTERTAINMENT_SALES": {
        "w_category": 0.30, "w_visiting": 0.25, "w_income": 0.10,
        "w_population": 0.20, "w_growth": 0.10, "w_diversity": 0.05,
    },
    "FASHION_SALES": {
        "w_category": 0.25, "w_visiting": 0.30, "w_income": 0.20,
        "w_population": 0.10, "w_growth": 0.10, "w_diversity": 0.05,
    },
    "SMALL_RETAIL_SALES": {
        "w_category": 0.30, "w_visiting": 0.15, "w_income": 0.10,
        "w_population": 0.30, "w_growth": 0.10, "w_diversity": 0.05,
    },
}


# ── Helpers ─────────────────────────────────────────────────────────────────
def _classify_business(business: str) -> str:
    for keyword, category in _KEYWORD_TO_CATEGORY:
        if keyword in business:
            return category
    return "FOOD_SALES"


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


def _score_districts(df: pd.DataFrame, category_col: str, override_weights: dict | None = None) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    if n == 0:
        return df

    if override_weights is None:
        opt = st.session_state.get("_optimized_weights")
        if opt and opt.get("category_col") == category_col:
            override_weights = opt["weights"]

    weights = override_weights if override_weights else _SCORING_WEIGHTS.get(category_col, _SCORING_WEIGHTS["FOOD_SALES"])

    df["MOM_CHANGE_PCT"] = df["MOM_CHANGE_PCT"].fillna(0)

    df["pct_category"] = df[category_col].rank(method="average") / n * 100
    df["pct_visiting"] = df["SCORE_VISITING"].rank(method="average") / n * 100
    df["pct_income"] = df["SCORE_INCOME"].rank(method="average") / n * 100
    df["pct_population"] = df["SCORE_POPULATION"].rank(method="average") / n * 100
    df["pct_diversity"] = df["SCORE_DIVERSITY"].rank(method="average") / n * 100
    df["pct_growth"] = df["MOM_CHANGE_PCT"].rank(method="average") / n * 100

    df["TOTAL_SCORE"] = (
        df["pct_category"] * weights["w_category"]
        + df["pct_visiting"] * weights["w_visiting"]
        + df["pct_income"] * weights["w_income"]
        + df["pct_population"] * weights["w_population"]
        + df["pct_growth"] * weights["w_growth"]
        + df["pct_diversity"] * weights["w_diversity"]
    ).round(1)

    df["LABEL"] = df["CITY_KOR_NAME"] + " " + df["DISTRICT_KOR_NAME"]
    return df.sort_values("TOTAL_SCORE", ascending=False).reset_index(drop=True)


# ── AI report generation (Snowflake Cortex) ─────────────────────────────────
def _build_cortex_prompt(business_type: str, category_col: str, top5: pd.DataFrame) -> str:
    cat_label_val = category_label(category_col)
    districts_text = ""
    for i, row in top5.iterrows():
        districts_text += f"""
{i + 1}{t("report.cortex_rank")}: {row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']} ({t("report.cortex_score_label")}: {row['TOTAL_SCORE']:.1f})
- {t("report.cortex_cat_pct", cat=cat_label_val)}: {row['pct_category']:.1f}
- {t("report.cortex_visit_pct")}: {row['pct_visiting']:.1f}
- {t("report.cortex_income_pct")}: {row['pct_income']:.1f}
- {t("report.cortex_pop_pct")}: {row['pct_population']:.1f}
- {t("report.cortex_growth_pct")}: {row['pct_growth']:.1f}
- {t("report.cortex_diversity_pct")}: {row['pct_diversity']:.1f}
- {t("report.cortex_vitality")}: {row['VITALITY_INDEX']:.1f}
- {t("report.cortex_mom")}: {row['MOM_CHANGE_PCT']:.1f}%
- {t("report.cortex_total_sales")}: {row['TOTAL_CARD_SALES']:,.0f}
- {t("report.cortex_visitors")}: {row['TOTAL_VISITING']:,.0f}
"""

    return f"""{t("report.cortex_system")}
{t("report.cortex_instruction", biz=business_type)}

## {t("report.sub_business")}: {business_type}
## {t("report.cortex_category")}: {cat_label_val}

## {t("report.cortex_top5")}:
{districts_text}

{t("report.cortex_guidelines")}

{t("report.cortex_write")}"""


def _generate_ai_report(business_type: str, category_col: str, top5: pd.DataFrame) -> str | None:
    prompt = _build_cortex_prompt(business_type, category_col, top5)

    try:
        from snowflake.cortex import Complete
        return Complete("mistral-large2", prompt)
    except Exception:
        pass

    try:
        session = get_session()
        prompt_escaped = prompt.replace("\\", "\\\\").replace("'", "''")
        result = session.sql(
            f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{prompt_escaped}')"
        ).collect()
        raw = result[0][0]
        try:
            parsed = json.loads(raw)
            if "choices" in parsed:
                return parsed["choices"][0].get("messages", parsed["choices"][0].get("message", raw))
            return str(parsed.get("content", raw))
        except (json.JSONDecodeError, TypeError, KeyError):
            return str(raw)
    except Exception:
        pass

    return None


def _template_report(business_type: str, category_col: str, top5: pd.DataFrame) -> str:
    cat_label_val = category_label(category_col)
    lines: list[str] = []
    lines.append(f"## {t('report.tpl_title', biz=business_type)}\n")
    lines.append(f"> {t('report.tpl_basis', cat=cat_label_val)}\n")

    for i, row in top5.iterrows():
        rank = i + 1
        city = row["CITY_KOR_NAME"]
        district = row["DISTRICT_KOR_NAME"]
        score = row["TOTAL_SCORE"]

        strengths: list[str] = []
        if row["pct_category"] >= 70:
            strengths.append(t("report.tpl_str_cat", cat=cat_label_val, p=f"{row['pct_category']:.0f}"))
        if row["pct_visiting"] >= 70:
            strengths.append(t("report.tpl_str_traffic", p=f"{row['pct_visiting']:.0f}"))
        if row["pct_income"] >= 70:
            strengths.append(t("report.tpl_str_income", p=f"{row['pct_income']:.0f}"))
        if row["pct_population"] >= 70:
            strengths.append(t("report.tpl_str_population", p=f"{row['pct_population']:.0f}"))
        if row["MOM_CHANGE_PCT"] > 0:
            strengths.append(t("report.tpl_str_growth", p=f"{row['MOM_CHANGE_PCT']:.1f}"))

        cautions: list[str] = []
        if row["pct_visiting"] < 30:
            cautions.append(t("report.tpl_cau_traffic"))
        if row["pct_income"] < 30:
            cautions.append(t("report.tpl_cau_income"))
        if row["MOM_CHANGE_PCT"] < -2:
            cautions.append(t("report.tpl_cau_decline", p=f"{row['MOM_CHANGE_PCT']:.1f}"))
        if row["pct_diversity"] < 30:
            cautions.append(t("report.tpl_cau_diversity"))

        _v_vit = f"{row['VITALITY_INDEX']:.1f}"
        _v_cat = f"{row['pct_category']:.0f}"
        _v_vis = f"{row['TOTAL_VISITING']:,.0f}"
        _v_sales = f"{row['TOTAL_CARD_SALES']:,.0f}"

        lines.append(f"### {rank}: {city} {district}")
        lines.append(f"**{t('report.tpl_score', v=f'{score:.1f}')}**\n")
        lines.append(f"- {t('report.tpl_vitality', v=_v_vit)}")
        lines.append(f"- {t('report.tpl_cat_pct', cat=cat_label_val, v=_v_cat)}")
        lines.append(f"- {t('report.tpl_visitors', v=_v_vis)}")
        lines.append(f"- {t('report.tpl_total_sales', v=_v_sales)}\n")

        if strengths:
            lines.append(f"**{t('report.tpl_strengths')}:** {' · '.join(strengths)}\n")
        if cautions:
            lines.append(f"**{t('report.tpl_cautions')}:** {' · '.join(cautions)}\n")
        lines.append("")

    best = top5.iloc[0]
    lines.append("---")
    lines.append(f"### {t('report.tpl_conclusion')}: {best['CITY_KOR_NAME']} {best['DISTRICT_KOR_NAME']}")
    lines.append(
        t("report.tpl_conclusion_text",
          city=best["CITY_KOR_NAME"], district=best["DISTRICT_KOR_NAME"],
          cat=cat_label_val, cat_p=f"{best['pct_category']:.0f}",
          vis_p=f"{best['pct_visiting']:.0f}", biz=business_type)
    )
    return "\n".join(lines)


# ── Main render ─────────────────────────────────────────────────────────────
def render(
    city_codes: tuple,
    city_code_to_name: dict,
    selected_month: str,
    dark_mode: bool = True,
) -> None:
    st.header(t("report.header"))
    st.markdown(
        f"<p style='color:#989ba2;font-size:14px;margin-top:-12px'>{t('report.intro')}</p>",
        unsafe_allow_html=True,
    )

    _CATS = categories()
    _presets = business_presets()

    # ── Business type selection ──────────────────────────────────────────────
    st.subheader(t("report.sub_business"))

    preset_labels = [p["label"] for p in _presets] + [t("preset.custom")]
    selected_preset = st.radio(
        t("report.radio_label"),
        preset_labels,
        horizontal=True,
        label_visibility="collapsed",
    )

    if selected_preset == t("preset.custom"):
        business_type = st.text_input(
            t("report.input_label"),
            placeholder=t("report.input_placeholder"),
        )
    else:
        idx = preset_labels.index(selected_preset)
        business_type = _presets[idx]["value"]

    if not business_type:
        st.info(t("report.info_pick"))
        return

    category_col = _classify_business(business_type)
    cat_label_val = category_label(category_col)

    st.markdown(
        f"<p style='font-size:14px;color:#989ba2;margin-top:4px'>"
        f"{t('report.mapped_cat')}<b style='color:#359efa'>{cat_label_val}</b></p>",
        unsafe_allow_html=True,
    )

    # ── Generate button ──────────────────────────────────────────────────────
    st.divider()

    if st.session_state.get("_report_business") != business_type:
        st.session_state.pop("_report_result", None)

    generate = st.button(t("report.generate"), type="primary", use_container_width=True)

    if generate:
        with st.spinner(t("report.generating")):
            df_all = data.load_vitality_data(city_codes)
            if df_all.empty:
                st.warning(t("common.no_data"))
                return

            df = df_all[df_all["STANDARD_YEAR_MONTH"] == selected_month].copy()
            if df.empty:
                st.warning(t("common.no_data_period"))
                return

            scored = _score_districts(df, category_col)
            top5 = scored.head(5).copy()
            top10 = scored.head(10).copy()

            ai_report = _generate_ai_report(business_type, category_col, top5)
            report_text = ai_report if ai_report else _template_report(business_type, category_col, top5)

            st.session_state["_report_result"] = {
                "business": business_type,
                "category": category_col,
                "scored": scored,
                "top5": top5,
                "top10": top10,
                "report_text": report_text,
                "ai_generated": ai_report is not None,
            }
            st.session_state["_report_business"] = business_type

    # ── Display results ──────────────────────────────────────────────────────
    result = st.session_state.get("_report_result")
    if not result:
        return

    top5 = result["top5"]
    top10 = result["top10"]
    scored = result["scored"]
    cat = result["category"]

    st.divider()

    # ── KPI cards ────────────────────────────────────────────────────────────
    best = top5.iloc[0]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(t("report.kpi_top1"), f"{best['CITY_KOR_NAME']} {best['DISTRICT_KOR_NAME']}")
    k2.metric(t("report.kpi_score"), f"{best['TOTAL_SCORE']:.1f}")
    k3.metric(f"{cat_label_val} {t('c.percentile')}", f"{best['pct_category']:.0f}")
    k4.metric(t("report.kpi_vitality"), f"{best['VITALITY_INDEX']:.1f}", f"{best['MOM_CHANGE_PCT']:+.1f}%")

    st.divider()

    # ── Top 10 bar chart ─────────────────────────────────────────────────────
    _region = t("c.region")
    _score = t("report.axis_score")

    st.subheader(t("report.top10"))

    bar_data = top10[["LABEL", "TOTAL_SCORE", "pct_category", "pct_visiting", "pct_income"]].copy()
    bar_chart = _apply_theme(
        alt.Chart(bar_data)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y("LABEL:N", title=_region, sort="-x"),
            x=alt.X("TOTAL_SCORE:Q", title=_score),
            color=alt.Color("TOTAL_SCORE:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=[
                alt.Tooltip("LABEL:N", title=_region),
                alt.Tooltip("TOTAL_SCORE:Q", title=_score, format=".1f"),
                alt.Tooltip("pct_category:Q", title=f"{cat_label_val} {t('c.percentile')}", format=".0f"),
                alt.Tooltip("pct_visiting:Q", title=f"{t('factor.foot_traffic')} {t('c.percentile')}", format=".0f"),
                alt.Tooltip("pct_income:Q", title=f"{t('factor.income')} {t('c.percentile')}", format=".0f"),
            ],
        )
        .properties(height=360),
        dark_mode,
    )
    st.altair_chart(bar_chart, use_container_width=True)

    st.divider()

    # ── Top 5 factor comparison ──────────────────────────────────────────────
    st.subheader(t("report.top5_compare"))

    _factor_labels = factors()
    _factor_labels["pct_category"] = f"{cat_label_val} {t('factor.cat_sales')}"

    _item = t("c.item")
    _pctl = t("c.percentile")

    compare_data = top5[["LABEL"] + list(_factor_labels.keys())].melt(
        id_vars=["LABEL"], var_name=_item, value_name=_pctl,
    )
    compare_data[_item] = compare_data[_item].map(_factor_labels)

    compare_chart = _apply_theme(
        alt.Chart(compare_data)
        .mark_bar()
        .encode(
            x=alt.X(f"{_item}:N", title=t("report.axis_factor"), axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{_pctl}:Q", title=t("report.axis_pct")),
            color=alt.Color("LABEL:N", title=_region),
            xOffset=alt.XOffset("LABEL:N"),
            tooltip=[
                alt.Tooltip("LABEL:N", title=_region),
                alt.Tooltip(f"{_item}:N"),
                alt.Tooltip(f"{_pctl}:Q", format=".1f"),
            ],
        )
        .properties(height=380),
        dark_mode,
    )
    st.altair_chart(compare_chart, use_container_width=True)

    st.divider()

    # ── Report text ──────────────────────────────────────────────────────────
    st.subheader(t("report.detail_header"))
    if result.get("ai_generated"):
        st.caption(t("report.ai_caption"))
    st.markdown(result["report_text"])

    st.divider()

    # ── Full ranking table ───────────────────────────────────────────────────
    st.subheader(t("report.ranking_header"))

    display = scored[[
        "CITY_KOR_NAME", "DISTRICT_KOR_NAME", "TOTAL_SCORE",
        "pct_category", "pct_visiting", "pct_income",
        "pct_population", "pct_growth", "pct_diversity",
        "VITALITY_INDEX", "MOM_CHANGE_PCT",
        "TOTAL_VISITING", "TOTAL_CARD_SALES", cat,
    ]].copy()
    display.index = range(1, len(display) + 1)

    _fl = factors()
    display.columns = [
        t("c.gu"), t("c.dong"), t("report.col_score"),
        f"{cat_label_val}", _fl["pct_visiting"], _fl["pct_income"],
        _fl["pct_population"], _fl["pct_growth"], _fl["pct_diversity"],
        t("report.col_vitality"), t("report.col_mom"),
        t("report.col_visitors"), t("report.col_total_sales"), f"{cat_label_val}(KRW)",
    ]
    st.dataframe(display, use_container_width=True, height=500)
