"""서울 3대 상업지구 자영업 상권분석 플랫폼 MCP 서버 — 창업 입지 추천 보고서를 Claude Code 등에서 사용 가능하게 노출"""
from __future__ import annotations

import json
import os
import sys
import logging

import numpy as np
import pandas as pd
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("vitality-mcp")

# ── MCP 서버 초기화 ──────────────────────────────────────────────────────────
mcp = FastMCP(
    "urban-vitality",
    instructions=(
        "「서울 3대 상업지구 자영업 상권분석 플랫폼」 MCP — 서울시 자영업 창업 입지 분석 도구입니다. "
        "업종(치킨집, 카페, 헬스장 등)을 알려주면 "
        "데이터 기반으로 최적의 동네를 추천하고 보고서를 생성합니다. "
        "백테스팅으로 추천 모델의 과거 적중률도 검증할 수 있습니다."
    ),
)

# ═══════════════════════════════════════════════════════════════════════════════
# 데이터 & 분석 로직 (report_tab.py / backtest_tab.py 에서 가져온 핵심 로직)
# ═══════════════════════════════════════════════════════════════════════════════

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

_CATEGORY_LABEL: dict[str, str] = {
    "FOOD_SALES": "음식",
    "COFFEE_SALES": "커피",
    "LEISURE_SALES": "여가",
    "ENTERTAINMENT_SALES": "엔터테인먼트",
    "FASHION_SALES": "패션",
    "SMALL_RETAIL_SALES": "소매",
}

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


def _classify_business(business: str) -> str:
    for keyword, category in _KEYWORD_TO_CATEGORY:
        if keyword in business:
            return category
    return "FOOD_SALES"


def _get_snowflake_session():
    """Snowflake 세션 생성 (Snowpark 환경이면 active session, 아니면 env 기반)"""
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        from snowflake.snowpark import Session
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        return Session.builder.configs({
            "account": os.environ["SF_ACCOUNT"],
            "user": os.environ["SF_USER"],
            "password": os.environ["SF_PASSWORD"],
            "warehouse": os.environ["SF_WAREHOUSE"],
            "database": "SPH_DATA",
            "schema": "GRANDATA",
        }).create()


_session = None


def _session_singleton():
    global _session
    if _session is None:
        _session = _get_snowflake_session()
    return _session


def _load_vitality_data(city_codes: tuple) -> pd.DataFrame:
    session = _session_singleton()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    return session.sql(f"""
        SELECT
            PROVINCE_KOR_NAME, CITY_KOR_NAME, DISTRICT_KOR_NAME,
            PROVINCE_CODE, CITY_CODE, DISTRICT_CODE,
            STANDARD_YEAR_MONTH,
            VITALITY_INDEX, PREV_VITALITY_INDEX, MOM_CHANGE_PCT,
            VITALITY_LEVEL, TREND_DIRECTION,
            SCORE_POPULATION, SCORE_VISITING, SCORE_CONSUMPTION,
            SCORE_DIVERSITY, SCORE_INCOME, SCORE_CREDIT,
            TOTAL_POPULATION, TOTAL_VISITING, TOTAL_CARD_SALES,
            CONSUMPTION_DIVERSITY, AVG_INCOME, AVG_CREDIT_SCORE,
            FOOD_SALES, COFFEE_SALES, ENTERTAINMENT_SALES,
            SMALL_RETAIL_SALES, FASHION_SALES, LEISURE_SALES
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL
        WHERE CITY_CODE IN ({codes_str})
        ORDER BY STANDARD_YEAR_MONTH, DISTRICT_CODE
    """).to_pandas()


def _load_city_codes() -> tuple[tuple, dict]:
    session = _session_singleton()
    df = session.sql("""
        SELECT CITY_CODE, CITY_KOR_NAME
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL
        GROUP BY CITY_CODE, CITY_KOR_NAME
        ORDER BY CITY_KOR_NAME
    """).to_pandas()
    codes = tuple(df["CITY_CODE"].tolist())
    name_map = df.set_index("CITY_CODE")["CITY_KOR_NAME"].to_dict()
    return codes, name_map


def _score_districts(df: pd.DataFrame, category_col: str) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    if n == 0:
        return df
    weights = _SCORING_WEIGHTS.get(category_col, _SCORING_WEIGHTS["FOOD_SALES"])
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


def _build_report_text(business_type: str, category_col: str, top5: pd.DataFrame) -> str:
    cat_label = _CATEGORY_LABEL.get(category_col, "음식")
    lines: list[str] = []
    lines.append(f"# {business_type} 창업 추천 보고서\n")
    lines.append(f"> 분석 기준: {cat_label} 매출, 유동인구, 소득 수준, 성장세, 소비 다양성\n")

    for i, row in top5.iterrows():
        rank = i + 1
        city = row["CITY_KOR_NAME"]
        district = row["DISTRICT_KOR_NAME"]
        score = row["TOTAL_SCORE"]

        strengths: list[str] = []
        if row["pct_category"] >= 70:
            strengths.append(f"{cat_label} 매출 상위권 (백분위 {row['pct_category']:.0f})")
        if row["pct_visiting"] >= 70:
            strengths.append(f"높은 유동인구 (백분위 {row['pct_visiting']:.0f})")
        if row["pct_income"] >= 70:
            strengths.append(f"높은 소득 수준 (백분위 {row['pct_income']:.0f})")
        if row["pct_population"] >= 70:
            strengths.append(f"풍부한 거주인구 (백분위 {row['pct_population']:.0f})")
        if row["MOM_CHANGE_PCT"] > 0:
            strengths.append(f"성장세 (전월 대비 +{row['MOM_CHANGE_PCT']:.1f}%)")

        cautions: list[str] = []
        if row["pct_visiting"] < 30:
            cautions.append("유동인구가 적어 홍보·마케팅 전략 필요")
        if row["pct_income"] < 30:
            cautions.append("소득 수준이 낮아 가격 전략 중요")
        if row["MOM_CHANGE_PCT"] < -2:
            cautions.append(f"활력 하락 추세 ({row['MOM_CHANGE_PCT']:.1f}%)")
        if row["pct_diversity"] < 30:
            cautions.append("소비 다양성 낮음 — 업종 쏠림 위험")

        lines.append(f"## {rank}위: {city} {district}")
        lines.append(f"**종합 점수: {score:.1f}점**\n")
        lines.append(f"- 활력지수: {row['VITALITY_INDEX']:.1f}")
        lines.append(f"- {cat_label} 매출 백분위: {row['pct_category']:.0f}")
        lines.append(f"- 방문인구: {row['TOTAL_VISITING']:,.0f}명")
        lines.append(f"- 총 카드매출: {row['TOTAL_CARD_SALES']:,.0f}원")
        lines.append(f"- 전월 대비 변화: {row['MOM_CHANGE_PCT']:+.1f}%\n")

        if strengths:
            lines.append(f"**강점:** {' / '.join(strengths)}\n")
        if cautions:
            lines.append(f"**주의:** {' / '.join(cautions)}\n")

    best = top5.iloc[0]
    lines.append("---")
    lines.append(f"## 최종 추천: {best['CITY_KOR_NAME']} {best['DISTRICT_KOR_NAME']}")
    lines.append(
        f"{best['CITY_KOR_NAME']} {best['DISTRICT_KOR_NAME']}은(는) "
        f"{cat_label} 매출 백분위 {best['pct_category']:.0f}, "
        f"방문인구 백분위 {best['pct_visiting']:.0f}으로 "
        f"**{business_type}** 창업에 가장 유리한 입지로 분석됩니다."
    )
    return "\n".join(lines)


def _run_backtest_core(
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
        rec_in_growth = [c for c in top_codes if c in growth.index]
        if not rec_in_growth:
            continue

        rec_growth = growth.loc[rec_in_growth]
        hits = int((rec_growth > median_growth).sum())

        results.append({
            "base_month": base_month,
            "eval_end": future_months[-1],
            "avg_growth_recommended": round(float(rec_growth.mean()), 2),
            "avg_growth_all": round(float(growth.mean()), 2),
            "median_growth_all": round(float(median_growth), 2),
            "hits": hits,
            "total": len(rec_in_growth),
            "hit_rate": round(hits / len(rec_in_growth) * 100, 1),
            "alpha": round(float(rec_growth.mean()) - float(growth.mean()), 2),
            "top_labels": top_labels[:len(rec_in_growth)],
        })

    return results if results else None


# ═══════════════════════════════════════════════════════════════════════════════
# MCP Tools
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def startup_report(business_type: str) -> str:
    """서울시에서 자영업 창업 최적 입지를 분석합니다.

    업종을 입력하면 유동인구, 소비 데이터, 소득 수준, 성장세 등을 종합 분석하여
    가장 유리한 동네 Top 5를 추천하고 근거를 설명하는 보고서를 생성합니다.

    예시 업종: 치킨집, 고깃집, 카페, 헬스장, 편의점, 옷가게, 노래방, 미용실, 피자집, 분식집,
    삼겹살집, 네일샵, 볼링장, 베이커리, 요가원, PC방 등

    Args:
        business_type: 창업하고 싶은 업종 (예: "치킨집", "카페", "헬스장")
    """
    logger.info(f"startup_report called: {business_type}")

    category_col = _classify_business(business_type)
    cat_label = _CATEGORY_LABEL.get(category_col, "음식")

    city_codes, _ = _load_city_codes()
    df_all = _load_vitality_data(city_codes)
    if df_all.empty:
        return "데이터가 없습니다. Snowflake 연결을 확인하세요."

    months = sorted(df_all["STANDARD_YEAR_MONTH"].unique())
    latest_month = months[-1]
    df = df_all[df_all["STANDARD_YEAR_MONTH"] == latest_month].copy()

    scored = _score_districts(df, category_col)
    top5 = scored.head(5).copy()
    top10 = scored.head(10).copy()

    report = _build_report_text(business_type, category_col, top5)

    # Top 10 요약 테이블 추가
    report += "\n\n---\n## 상위 10개 지역 요약\n\n"
    report += "| 순위 | 지역 | 종합점수 | 업종매출 | 유동인구 | 소득수준 | 활력지수 |\n"
    report += "|------|------|----------|----------|----------|----------|----------|\n"
    for i, row in top10.iterrows():
        report += (
            f"| {i+1} | {row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']} "
            f"| {row['TOTAL_SCORE']:.1f} "
            f"| {row['pct_category']:.0f} "
            f"| {row['pct_visiting']:.0f} "
            f"| {row['pct_income']:.0f} "
            f"| {row['VITALITY_INDEX']:.1f} |\n"
        )

    report += f"\n> 분석 기준월: {latest_month} | 소비 카테고리: {cat_label} | 서울 전체 {len(df)}개 법정동 대상"
    return report


@mcp.tool()
def startup_backtest(business_type: str, eval_months: int = 3) -> str:
    """창업 추천 모델의 과거 적중률을 백테스팅으로 검증합니다.

    과거 매월 시점에서 모델이 추천했을 지역이 실제로 이후 N개월간
    더 좋은 매출 성장을 보였는지 확인합니다.
    적중률이 50%를 넘으면 랜덤보다 나은 모델입니다.

    Args:
        business_type: 백테스트할 업종 (예: "치킨집", "카페")
        eval_months: 추천 후 성과 측정 기간 - 개월 수 (1, 2, 3, 또는 6). 기본값 3.
    """
    logger.info(f"startup_backtest called: {business_type}, eval={eval_months}m")

    if eval_months not in (1, 2, 3, 6):
        eval_months = 3

    category_col = _classify_business(business_type)
    cat_label = _CATEGORY_LABEL.get(category_col, "음식")

    city_codes, _ = _load_city_codes()
    df_all = _load_vitality_data(city_codes)
    if df_all.empty:
        return "데이터가 없습니다. Snowflake 연결을 확인하세요."

    results = _run_backtest_core(df_all, category_col, eval_months=eval_months)
    if results is None:
        return "백테스트를 실행하기에 데이터 기간이 부족합니다."

    total_hits = sum(r["hits"] for r in results)
    total_recs = sum(r["total"] for r in results)
    overall_hit_rate = total_hits / total_recs * 100
    avg_alpha = sum(r["alpha"] for r in results) / len(results)
    win_periods = sum(1 for r in results if r["avg_growth_recommended"] > r["avg_growth_all"])
    win_rate = win_periods / len(results) * 100

    if overall_hit_rate >= 65:
        confidence = "높음 ✅"
    elif overall_hit_rate >= 50:
        confidence = "보통 ⚠️"
    else:
        confidence = "낮음 ❌"

    lines: list[str] = []
    lines.append(f"# {business_type} 추천 모델 백테스트 결과\n")
    lines.append(f"> 소비 카테고리: {cat_label} | 평가 기간: 추천 후 {eval_months}개월 | 테스트 기간: {len(results)}개 시점\n")

    lines.append("## 핵심 지표\n")
    lines.append(f"- **전체 적중률**: {overall_hit_rate:.1f}% (추천 지역이 중앙값 상회한 비율)")
    lines.append(f"- **평균 초과 성장률 (Alpha)**: {avg_alpha:+.2f}%p (추천 vs 전체 평균)")
    lines.append(f"- **기간 승률**: {win_rate:.0f}% ({win_periods}/{len(results)}개 기간)")
    lines.append(f"- **모델 신뢰도**: {confidence}\n")

    lines.append("## 기간별 상세\n")
    lines.append("| 추천 시점 | 평가 종료 | 추천 성장률 | 전체 성장률 | Alpha | 적중 | 적중률 |")
    lines.append("|-----------|-----------|-------------|-------------|-------|------|--------|")
    for r in results:
        lines.append(
            f"| {r['base_month']} | {r['eval_end']} "
            f"| {r['avg_growth_recommended']:+.2f}% "
            f"| {r['avg_growth_all']:+.2f}% "
            f"| {r['alpha']:+.2f}%p "
            f"| {r['hits']}/{r['total']} "
            f"| {r['hit_rate']:.0f}% |"
        )

    # 최근 사례
    latest = results[-1]
    lines.append(f"\n## 최근 백테스트 상세 ({latest['base_month']} 추천)\n")
    for i, label in enumerate(latest["top_labels"]):
        lines.append(f"- {i+1}. {label}")

    # 결론
    lines.append("\n## 결론\n")
    if overall_hit_rate >= 55:
        lines.append(
            f"**{business_type}** 추천 모델은 적중률 **{overall_hit_rate:.1f}%**, "
            f"Alpha **{avg_alpha:+.2f}%p**로 유의미한 성과를 보였습니다. "
            f"모델 추천을 참고할 가치가 있습니다."
        )
    elif overall_hit_rate >= 45:
        lines.append(
            f"**{business_type}** 추천 모델은 적중률 **{overall_hit_rate:.1f}%**로 "
            f"랜덤 수준에 가깝습니다. 추천 결과를 참고하되 현장 조사와 병행하세요."
        )
    else:
        lines.append(
            f"**{business_type}** 추천 모델은 적중률 **{overall_hit_rate:.1f}%**로 "
            f"기대에 미치지 못합니다. 이 업종은 현재 데이터만으로 판단이 어려울 수 있습니다."
        )

    return "\n".join(lines)


@mcp.tool()
def list_business_types() -> str:
    """지원하는 업종 목록과 매핑된 소비 카테고리를 보여줍니다.

    어떤 업종을 분석할 수 있는지 확인할 때 사용합니다.
    """
    lines = ["# 지원 업종 목록\n"]
    lines.append("자유롭게 업종명을 입력할 수 있습니다. 아래는 대표 예시입니다.\n")

    by_cat: dict[str, list[str]] = {}
    for kw, cat in _KEYWORD_TO_CATEGORY:
        by_cat.setdefault(cat, []).append(kw)

    for cat, keywords in by_cat.items():
        label = _CATEGORY_LABEL.get(cat, cat)
        unique_kw = list(dict.fromkeys(keywords))  # dedup preserving order
        lines.append(f"## {label} 카테고리")
        lines.append(f"키워드: {', '.join(unique_kw)}\n")

    lines.append("---")
    lines.append("위 키워드가 업종명에 포함되면 해당 카테고리로 자동 매핑됩니다.")
    lines.append("매핑되지 않는 업종은 기본적으로 '음식' 카테고리로 분석됩니다.")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# 서버 실행
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    logger.info('서울 3대 상업지구 자영업 상권분석 플랫폼 MCP 서버 시작...')
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
