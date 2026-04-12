"""UI strings for ko / en. Locale lives in st.session_state["locale"]."""
from __future__ import annotations

import streamlit as st

MESSAGES: dict[str, dict[str, str]] = {
    # ── Navigation ──────────────────────────────────────────────────────────
    "nav.visitor": {
        "ko": "🚇 구경꾼 동네",
        "en": "🚇 Visitor hotspots",
    },
    "nav.consumer": {
        "ko": "📈 전입×소비",
        "en": "📈 Migration × spend",
    },
    "nav.asset": {
        "ko": "🏠 자산×소비",
        "en": "🏠 Assets × spend",
    },
    "nav.report": {
        "ko": "📊 창업 보고서",
        "en": "📊 Startup report",
    },
    "nav.backtest": {
        "ko": "🔬 백테스팅",
        "en": "🔬 Backtesting",
    },
    "nav.diagnostic": {
        "ko": "🔧 모델 진단",
        "en": "🔧 Model diagnostics",
    },

    # ── Sidebar ─────────────────────────────────────────────────────────────
    "sidebar.title": {
        "ko": "### 🏙️ 서울 3대 상업지구 자영업 상권분석 플랫폼",
        "en": "### 🏙️ Seoul 3 major commercial districts — SME retail trade-area analytics",
    },
    "sidebar.tagline": {
        "ko": "유동·소비·자산 데이터 기반 자영업 입지·상권 인사이트",
        "en": "Foot traffic, spend, and asset data for SME location and trade-area insight",
    },

    # ── Footer ──────────────────────────────────────────────────────────────
    "footer.built": {
        "ko": "Built with Snowflake + Streamlit",
        "en": "Built with Snowflake + Streamlit",
    },
    "footer.data": {
        "ko": "Data: SPH (SKT 유동인구, KCB 자산소득, 신한카드 소비)",
        "en": "Data: SPH (SKT foot traffic, KCB assets, Shinhan card spend)",
    },

    # ── Common ──────────────────────────────────────────────────────────────
    "common.no_data": {
        "ko": "데이터가 없습니다.",
        "en": "No data available.",
    },
    "common.no_data_period": {
        "ko": "선택한 기간에 데이터가 없습니다.",
        "en": "No data for the selected period.",
    },

    # ── Shared chart / data labels ──────────────────────────────────────────
    "c.period": {"ko": "기간", "en": "Period"},
    "c.score": {"ko": "점수", "en": "Score"},
    "c.district": {"ko": "법정동", "en": "District"},
    "c.dong": {"ko": "동", "en": "Dong"},
    "c.gu": {"ko": "구", "en": "Gu"},
    "c.type": {"ko": "유형", "en": "Type"},
    "c.category": {"ko": "업종", "en": "Category"},
    "c.value": {"ko": "값", "en": "Value"},
    "c.ratio_pct": {"ko": "비율 (%)", "en": "Ratio (%)"},
    "c.series": {"ko": "구분", "en": "Series"},
    "c.percentile": {"ko": "백분위", "en": "Percentile"},
    "c.item": {"ko": "항목", "en": "Item"},
    "c.region": {"ko": "지역", "en": "Area"},
    "c.model": {"ko": "모델", "en": "Model"},
    "c.factor": {"ko": "팩터", "en": "Factor"},
    "c.weight": {"ko": "가중치", "en": "Weight"},
    "c.correlation": {"ko": "상관계수", "en": "Correlation"},
    "c.direction": {"ko": "방향", "en": "Direction"},
    "c.display_val": {"ko": "표시값", "en": "Display"},
    "c.n_months": {"ko": "{n}개월", "en": "{n}mo"},

    # ── Categories ──────────────────────────────────────────────────────────
    "cat.coffee": {"ko": "커피", "en": "Coffee"},
    "cat.entertainment": {"ko": "엔터테인먼트", "en": "Entertainment"},
    "cat.food": {"ko": "음식", "en": "Food"},
    "cat.fashion": {"ko": "패션", "en": "Fashion"},
    "cat.leisure": {"ko": "여가", "en": "Leisure"},
    "cat.retail": {"ko": "소매", "en": "Retail"},
    # Short labels for trend tab
    "cat_s.food": {"ko": "외식", "en": "Dining"},
    "cat_s.coffee": {"ko": "커피", "en": "Coffee"},
    "cat_s.entertainment": {"ko": "엔터", "en": "Entertain."},
    "cat_s.retail": {"ko": "소매", "en": "Retail"},
    "cat_s.fashion": {"ko": "패션", "en": "Fashion"},
    "cat_s.leisure": {"ko": "레저", "en": "Leisure"},

    # ── Scoring factors ─────────────────────────────────────────────────────
    "factor.cat_sales": {"ko": "업종 매출", "en": "Category sales"},
    "factor.foot_traffic": {"ko": "유동인구", "en": "Foot traffic"},
    "factor.income": {"ko": "소득수준", "en": "Income level"},
    "factor.population": {"ko": "거주인구", "en": "Residents"},
    "factor.growth": {"ko": "성장세", "en": "Growth"},
    "factor.diversity": {"ko": "소비다양성", "en": "Spend diversity"},

    # ── Quadrant names ──────────────────────────────────────────────────────
    "quad.spectator": {"ko": "구경꾼 동네", "en": "Spectator zone"},
    "quad.active": {"ko": "활성 상권", "en": "Active market"},
    "quad.local": {"ko": "지역 소비", "en": "Local spending"},
    "quad.stagnant": {"ko": "침체 동네", "en": "Stagnant zone"},

    # ── Business presets ────────────────────────────────────────────────────
    "preset.chicken": {"ko": "🍗 치킨집", "en": "🍗 Fried chicken"},
    "preset.meat": {"ko": "🥩 고깃집", "en": "🥩 BBQ restaurant"},
    "preset.cafe": {"ko": "☕ 카페", "en": "☕ Café"},
    "preset.gym": {"ko": "💪 헬스장", "en": "💪 Gym"},
    "preset.convenience": {"ko": "🏪 편의점", "en": "🏪 Convenience store"},
    "preset.clothing": {"ko": "👗 옷가게", "en": "👗 Clothing store"},
    "preset.karaoke": {"ko": "🎤 노래방", "en": "🎤 Karaoke"},
    "preset.salon": {"ko": "💇 미용실", "en": "💇 Hair salon"},
    "preset.pizza": {"ko": "🍕 피자집", "en": "🍕 Pizza shop"},
    "preset.snack": {"ko": "🍜 분식집", "en": "🍜 Snack bar"},
    "preset.custom": {"ko": "✏️ 직접 입력", "en": "✏️ Custom input"},

    # ── Map tab ─────────────────────────────────────────────────────────────
    "map.header": {"ko": "서울 법정동 활력 지도", "en": "Seoul district vitality map"},
    "map.avg_vitality": {"ko": "{name} 평균 활력", "en": "{name} avg vitality"},
    "map.delta": {"ko": "↑{up} ↓{down} 개동", "en": "↑{up} ↓{down} districts"},
    "map.tooltip_vitality": {"ko": "활력지수", "en": "Vitality"},
    "map.tooltip_population": {"ko": "유동인구", "en": "Foot traffic"},
    "map.tooltip_sales": {"ko": "카드매출", "en": "Card sales"},
    "map.tooltip_income": {"ko": "평균소득", "en": "Avg income"},
    "map.legend_low": {"ko": "● 낮은 활력", "en": "● Low vitality"},
    "map.legend_mid": {"ko": "● 중간 활력", "en": "● Mid vitality"},
    "map.legend_high": {"ko": "● 높은 활력", "en": "● High vitality"},
    "map.ranking": {"ko": "법정동 활력 순위", "en": "District vitality ranking"},
    "map.col_vitality": {"ko": "활력지수", "en": "Vitality"},
    "map.col_grade": {"ko": "등급", "en": "Grade"},
    "map.col_trend": {"ko": "추세", "en": "Trend"},
    "map.col_mom": {"ko": "전월비(%)", "en": "MoM(%)"},
    "map.col_population": {"ko": "유동인구", "en": "Foot traffic"},
    "map.col_sales": {"ko": "카드매출", "en": "Card sales"},
    "map.col_income": {"ko": "평균소득", "en": "Avg income"},

    # ── Trend tab ───────────────────────────────────────────────────────────
    "trend.header": {"ko": "법정동 트렌드 분석", "en": "District trend analysis"},
    "trend.select": {
        "ko": "비교할 법정동 선택 (최대 5개)",
        "en": "Select districts to compare (max 5)",
    },
    "trend.select_prompt": {
        "ko": "비교할 법정동을 선택하세요.",
        "en": "Please select districts to compare.",
    },
    "trend.vitality_trend": {"ko": "활력 지수 추이", "en": "Vitality index trend"},
    "trend.vitality_index": {"ko": "활력 지수", "en": "Vitality index"},
    "trend.detail_compare": {
        "ko": "세부 지표 비교 (최신 월)",
        "en": "Detailed metrics (latest month)",
    },
    "trend.m_population": {"ko": "유동인구", "en": "Foot traffic"},
    "trend.m_visiting": {"ko": "방문비율", "en": "Visit ratio"},
    "trend.m_consumption": {"ko": "소비규모", "en": "Spending"},
    "trend.m_diversity": {"ko": "소비다양성", "en": "Diversity"},
    "trend.m_income": {"ko": "소득수준", "en": "Income"},
    "trend.m_credit": {"ko": "신용건전성", "en": "Credit health"},
    "trend.score_axis": {"ko": "점수 (0~100)", "en": "Score (0~100)"},
    "trend.sales_header": {"ko": "업종별 카드 매출 구성", "en": "Card sales by category"},

    # ── Visitor tab ─────────────────────────────────────────────────────────
    "visitor.header": {
        "ko": "구경꾼 동네 분석",
        "en": "Visitor-dominant neighborhoods",
    },
    "visitor.intro": {
        "ko": (
            "방문인구는 많지만 카드 소비가 낮은 "
            "'통과 동네'를 탐지합니다. "
            "지하철 승하차 데이터로 진짜 통과 동네 "
            "여부를 검증합니다."
        ),
        "en": (
            "Detects pass-through areas with high foot traffic but low card spend. "
            "Subway ridership validates true pass-through patterns."
        ),
    },
    "visitor.kpi_spectator": {"ko": "구경꾼 동네 수", "en": "Spectator zones"},
    "visitor.kpi_spectator_total": {
        "ko": "전체 {total}개 동 중",
        "en": "out of {total} districts",
    },
    "visitor.kpi_passthrough": {"ko": "통과 동네 확정", "en": "Confirmed pass-through"},
    "visitor.kpi_passthrough_desc": {
        "ko": "지하철 승하차 상위 50%",
        "en": "Top 50% subway ridership",
    },
    "visitor.kpi_visit_pct": {"ko": "방문 백분위 기준", "en": "Visit pctl cutoff"},
    "visitor.kpi_spend_pct": {"ko": "소비 백분위 기준", "en": "Spend pctl cutoff"},
    "visitor.kpi_median_quadrant": {
        "ko": "중앙값 기준 사분면",
        "en": "Median-based quadrant",
    },
    "visitor.quad_header": {
        "ko": "방문 vs 소비 사분면 분석",
        "en": "Visit vs spend quadrant analysis",
    },
    "visitor.axis_visit_pct": {"ko": "방문 백분위", "en": "Visit percentile"},
    "visitor.axis_spend_pct": {"ko": "소비 백분위", "en": "Spend percentile"},
    "visitor.legend_subway": {"ko": "지하철 승하차", "en": "Subway ridership"},
    "visitor.tooltip_ridership": {"ko": "지하철 승하차", "en": "Subway ridership"},
    "visitor.tooltip_station": {"ko": "인근 역 수", "en": "Nearby stations"},
    "visitor.caption_scatter": {
        "ko": "점 크기 = 지하철 총 승하차 수 | 기준선: 백분위 50 (중앙값)",
        "en": "Dot size = total subway ridership | Baseline: percentile 50 (median)",
    },
    "visitor.list_header": {"ko": "구경꾼 동네 상세 목록", "en": "Spectator zone details"},
    "visitor.no_spectator": {
        "ko": "이번 달 구경꾼 동네로 분류된 법정동이 없습니다.",
        "en": "No districts classified as spectator zones this month.",
    },
    "visitor.col_pct_gap": {"ko": "백분위_갭", "en": "Pctl_gap"},
    "visitor.passthrough_yes": {"ko": "✅ 통과 동네", "en": "✅ Pass-through"},
    "visitor.passthrough_no": {"ko": "△ 주의", "en": "△ Caution"},
    "visitor.col_visit_pct": {"ko": "방문백분위", "en": "Visit pctl"},
    "visitor.col_spend_pct": {"ko": "소비백분위", "en": "Spend pctl"},
    "visitor.col_gap": {"ko": "갭", "en": "Gap"},
    "visitor.col_visitors": {"ko": "방문인구", "en": "Visitors"},
    "visitor.col_sales": {"ko": "카드매출", "en": "Card sales"},
    "visitor.col_stations": {"ko": "인근역수", "en": "Stations"},
    "visitor.col_distance": {"ko": "최근역거리(m)", "en": "Nearest stn(m)"},
    "visitor.col_ridership": {"ko": "지하철승하차", "en": "Ridership"},
    "visitor.col_passthrough": {"ko": "통과동네", "en": "Pass-through"},
    "visitor.subway_header": {
        "ko": "지하철 승하차 vs 카드 소비",
        "en": "Subway ridership vs card spend",
    },
    "visitor.subway_desc": {
        "ko": "승하차↑ + 소비↓ → 진짜 통과 동네 | 버블 색상 = 동네 유형",
        "en": "Ridership↑ + Spend↓ → True pass-through | Bubble color = zone type",
    },
    "visitor.axis_ridership": {"ko": "지하철 총 승하차수", "en": "Total subway ridership"},
    "visitor.axis_card_sales": {"ko": "카드 총 매출", "en": "Total card sales"},
    "visitor.tooltip_card_sales": {"ko": "카드 매출", "en": "Card sales"},
    "visitor.no_subway": {
        "ko": "지하철 데이터가 있는 법정동이 없습니다.",
        "en": "No districts with subway data.",
    },
    "visitor.trend_header": {
        "ko": "구경꾼 동네 방문·소비 추이",
        "en": "Spectator zone visit & spend trends",
    },
    "visitor.select_spectator": {
        "ko": "구경꾼 동네 선택 (최대 5개)",
        "en": "Select spectator zones (max 5)",
    },
    "visitor.visit_score": {"ko": "방문 점수", "en": "Visit score"},
    "visitor.spend_score": {"ko": "소비 점수", "en": "Spend score"},
    "visitor.caption_trend": {
        "ko": "실선 = 방문 점수 / 점선 = 소비 점수 — 격차가 클수록 통과 동네 성격이 강함",
        "en": "Solid = visit score / Dashed = spend score — larger gap = stronger pass-through",
    },

    # ── Consumer tab ────────────────────────────────────────────────────────
    "consumer.header": {
        "ko": "전입 인구 × 업종 소비 연관 분석",
        "en": "Migration × category spending",
    },
    "consumer.intro": {
        "ko": (
            "20~30대 전입 증가 이후 어떤 업종 매출이 "
            "따라 오르는지 Lag 상관 분석으로 추적합니다."
        ),
        "en": (
            "Uses lagged correlation to see which category sales rise after inflows of "
            "residents in their 20s–30s."
        ),
    },
    "consumer.spinner": {
        "ko": "전입·인구 데이터 로딩 중…",
        "en": "Loading migration and population data…",
    },
    "consumer.select_gu": {"ko": "분석할 구 선택", "en": "Select district to analyze"},
    "consumer.kpi_move_in": {"ko": "{name} 전입인구", "en": "{name} in-migration"},
    "consumer.kpi_move_in_delta": {
        "ko": "{pct}% vs 전월",
        "en": "{pct}% vs last month",
    },
    "consumer.kpi_net": {"ko": "순이동 (전입−전출)", "en": "Net movement (in−out)"},
    "consumer.kpi_net_desc": {"ko": "양수 = 순유입", "en": "Positive = net inflow"},
    "consumer.kpi_young": {"ko": "20-30대 인구 비중", "en": "Age 20-30s ratio"},
    "consumer.kpi_young_desc": {"ko": "전체 대비", "en": "of total"},
    "consumer.kpi_best_cat": {
        "ko": "1개월 후 최상관 업종",
        "en": "Best correlated category (1mo lag)",
    },
    "consumer.mig_header": {
        "ko": "{name} 전입·전출·순이동 추이",
        "en": "{name} in/out/net migration trend",
    },
    "consumer.mig_count": {"ko": "인구수", "en": "Population"},
    "consumer.mig_in": {"ko": "전입", "en": "In-migration"},
    "consumer.mig_out": {"ko": "전출", "en": "Out-migration"},
    "consumer.mig_net": {"ko": "순이동", "en": "Net movement"},
    "consumer.pop_axis": {"ko": "인구 (명)", "en": "Population"},
    "consumer.norm_header": {
        "ko": "전입 증가 → 업종 매출 시계열 비교",
        "en": "In-migration increase → category sales comparison",
    },
    "consumer.norm_desc": {
        "ko": (
            "각 지표를 0~100으로 정규화해 추세 방향과 피크 시점을 비교합니다. "
            "전입 피크 이후 매출이 뒤따라 오르면 인과 신호입니다."
        ),
        "en": (
            "Normalized 0~100 to compare trend direction and peak timing. "
            "If sales follow an in-migration peak, it signals causality."
        ),
    },
    "consumer.select_cats": {
        "ko": "비교할 업종 선택 (최대 3개)",
        "en": "Select categories to compare (max 3)",
    },
    "consumer.norm_axis": {"ko": "정규화 지수 (0~100)", "en": "Normalized index (0~100)"},
    "consumer.move_in_label": {"ko": "전입인구", "en": "In-migration"},
    "consumer.caption_norm": {
        "ko": "0~100 정규화 — 추세 방향과 피크 시점만 비교하세요 (절댓값 아님)",
        "en": "0~100 normalized — compare trend direction and peaks only (not absolute values)",
    },
    "consumer.lag_header": {
        "ko": "전입 증가 후 N개월 업종 매출 상관계수 (Lag 분석)",
        "en": "Lag correlation: in-migration → category sales after N months",
    },
    "consumer.lag_desc": {
        "ko": (
            "Lag = N개월: 전입이 증가한 달로부터 N개월 뒤 업종 매출과의 상관계수. "
            "<b style='color:#359efa'>파란색</b> = 양의 상관 (전입↑ → 매출↑), "
            "<b style='color:#ff5252'>빨간색</b> = 음의 상관."
        ),
        "en": (
            "Lag = N months: correlation between in-migration and category sales N months later. "
            "<b style='color:#359efa'>Blue</b> = positive (migration↑ → sales↑), "
            "<b style='color:#ff5252'>Red</b> = negative."
        ),
    },
    "consumer.lag_x_axis": {"ko": "전입 후 경과 개월", "en": "Months after in-migration"},
    "consumer.lag_corr_r": {"ko": "상관계수 r", "en": "Correlation r"},
    "consumer.lag_tooltip_months": {"ko": "경과 개월", "en": "Months elapsed"},
    "consumer.lag_caption": {
        "ko": "|r| > 0.5 강한 상관  |  |r| > 0.3 유의미  |  |r| < 0.1 무상관",
        "en": "|r| > 0.5 strong  |  |r| > 0.3 significant  |  |r| < 0.1 no correlation",
    },
    "consumer.lag_no_data": {
        "ko": "상관계수 계산에 충분한 데이터가 없습니다 (최소 8개월 필요).",
        "en": "Not enough data for correlation (minimum 8 months required).",
    },
    "consumer.age_header": {
        "ko": "{name} 연령대별 인구 비중 추이",
        "en": "{name} age group population trend",
    },
    "consumer.age_desc": {
        "ko": "20-30대 비중 상승 시기와 전입 증가 시기가 겹치면 청년 유입 시그널입니다.",
        "en": "Overlapping rise in 20-30s ratio and in-migration signals youth inflow.",
    },
    "consumer.age_20_30": {"ko": "20-30대 비중(%)", "en": "20-30s ratio(%)"},
    "consumer.age_40_50": {"ko": "40-50대 비중(%)", "en": "40-50s ratio(%)"},
    "consumer.age_60_plus": {"ko": "60대 이상 비중(%)", "en": "60+ ratio(%)"},
    "consumer.age_group": {"ko": "연령대", "en": "Age group"},
    "consumer.age_ratio": {"ko": "비중(%)", "en": "Ratio(%)"},
    "consumer.pop_ratio_axis": {"ko": "인구 비중 (%)", "en": "Population ratio (%)"},
    "consumer.caption_age": {
        "ko": "데이터 출처: 행정안전부 주민등록 인구통계",
        "en": "Source: MOIS resident registration statistics",
    },
    "consumer.no_age_data": {
        "ko": "연령대 인구 데이터가 없습니다.",
        "en": "No age-group population data available.",
    },

    # ── Asset tab ───────────────────────────────────────────────────────────
    "asset.header": {
        "ko": "자산 수준 × 소비 성향 분석",
        "en": "Assets × spending behavior",
    },
    "asset.intro_html": {
        "ko": (
            "아파트 시세(자산 수준 proxy)와 연령 구조가 "
            "업종별 소비 패턴에 어떻게 반영되는지 "
            "분석합니다. 데이터 가용 구: "
            "<b style='color:#ffffff'>중구 · 영등포구 · 서초구</b>"
        ),
        "en": (
            "How apartment prices (asset proxy) and age mix relate to category spending. "
            "Available districts: <b style='color:#ffffff'>Jung · Yeongdeungpo · Seocho</b>"
        ),
    },
    "asset.spinner": {"ko": "데이터 로딩 중…", "en": "Loading data…"},
    "asset.section1": {
        "ko": "구별 자산·소비 현황 ({month})",
        "en": "District asset & spending overview ({month})",
    },
    "asset.kpi_meme": {"ko": "매매가/평 (만원)", "en": "Sale price/pyeong (10K KRW)"},
    "asset.kpi_jeonse": {"ko": "전세가/평 (만원)", "en": "Deposit/pyeong (10K KRW)"},
    "asset.kpi_ratio": {"ko": "전세가율", "en": "Deposit ratio"},
    "asset.kpi_young": {"ko": "20-30대 비중", "en": "20-30s ratio"},
    "asset.kpi_top_cat": {"ko": "주요 소비 업종", "en": "Top spending category"},
    "asset.bubble_header": {
        "ko": "아파트 시세 × 업종 소비 비중 (버블 차트)",
        "en": "Apt. price × category spend share (bubble)",
    },
    "asset.bubble_desc": {
        "ko": "X축: 매매가/평(만원) · Y축: 선택 업종 소비 비중 · 버블 크기: 총 카드 매출",
        "en": "X: Sale price/pyeong · Y: Selected category share · Bubble: Total card sales",
    },
    "asset.select_cat": {"ko": "비교 업종", "en": "Compare category"},
    "asset.axis_meme": {
        "ko": "아파트 매매가/평 (만원)",
        "en": "Apt sale price/pyeong (10K KRW)",
    },
    "asset.spend_share": {"ko": "소비 비중 (%)", "en": "Spend share (%)"},
    "asset.tooltip_meme": {"ko": "매매가/평(만원)", "en": "Sale/pyeong(10K)"},
    "asset.tooltip_share": {"ko": "소비 비중(%)", "en": "Spend share(%)"},
    "asset.tooltip_total_sales": {"ko": "총 카드매출", "en": "Total card sales"},
    "asset.age_header": {"ko": "구별 연령 구조 비교", "en": "District age structure"},
    "asset.age_under20": {"ko": "20세 미만", "en": "Under 20"},
    "asset.age_20s": {"ko": "20대", "en": "20s"},
    "asset.age_30s": {"ko": "30대", "en": "30s"},
    "asset.age_40s": {"ko": "40대", "en": "40s"},
    "asset.age_50s": {"ko": "50대", "en": "50s"},
    "asset.age_60s": {"ko": "60대", "en": "60s"},
    "asset.age_over70": {"ko": "70대 이상", "en": "70+"},
    "asset.age_axis": {"ko": "연령대", "en": "Age group"},
    "asset.pop_ratio_axis": {"ko": "인구 비중 (%)", "en": "Population ratio (%)"},
    "asset.comp_header": {
        "ko": "구별 업종 소비 구성 비교 (정규화)",
        "en": "District category spend comparison (normalized)",
    },
    "asset.comp_desc": {
        "ko": (
            "동일 시점, 각 구의 총 카드 매출 기준 업종 비중. "
            "자산 수준에 따라 소비 구성이 어떻게 달라지는지 확인합니다."
        ),
        "en": (
            "Same period, category share by total card sales per district. "
            "Shows how spending composition varies by asset level."
        ),
    },
    "asset.ts_header": {
        "ko": "아파트 시세 × 소비 추이 비교 (정규화)",
        "en": "Apt price × spending trend (normalized)",
    },
    "asset.ts_desc": {
        "ko": (
            "각 지표를 0~100으로 정규화. "
            "매매가 상승/하락이 소비 패턴 변화와 동행하는지 확인합니다."
        ),
        "en": (
            "Normalized 0~100. "
            "Checks whether price changes track spending pattern changes."
        ),
    },
    "asset.select_gu": {"ko": "구 선택", "en": "Select district"},
    "asset.meme_label": {"ko": "매매가/평", "en": "Sale price/pyeong"},
    "asset.norm_axis": {"ko": "정규화 지수 (0~100)", "en": "Normalized index (0~100)"},
    "asset.caption_norm": {
        "ko": "0~100 정규화 — 절대값이 아닌 추세 방향을 비교합니다",
        "en": "0~100 normalized — compare trend direction, not absolute values",
    },
    "asset.no_ts_data": {
        "ko": "시계열 데이터가 충분하지 않습니다.",
        "en": "Not enough time-series data.",
    },
    "asset.source": {
        "ko": "데이터 출처: 리치고 아파트 시세 · 행정안전부 주민등록 인구통계 · SPH/GRANDATA 소비 데이터",
        "en": "Sources: Richgo apt prices · MOIS resident stats · SPH/GRANDATA spend data",
    },
    "asset.col_meme": {"ko": "매매가_평당", "en": "Sale_pyeong"},
    "asset.col_share": {"ko": "소비비중", "en": "Share"},
    "asset.col_total": {"ko": "총매출", "en": "TotalSales"},
    "asset.col_share_pct": {"ko": "소비비중(%)", "en": "Share(%)"},

    # ── Report tab ──────────────────────────────────────────────────────────
    "report.header": {"ko": "창업 추천 보고서", "en": "Startup location report"},
    "report.intro": {
        "ko": (
            "자영업 업종을 입력하면 데이터 기반으로 "
            "최적의 창업 입지를 분석하고 보고서를 "
            "생성합니다."
        ),
        "en": "Enter a business type to score districts and generate a data-driven location report.",
    },
    "report.sub_business": {"ko": "업종 선택", "en": "Business type"},
    "report.info_pick": {
        "ko": "업종을 선택하거나 입력해주세요.",
        "en": "Select or enter a business type.",
    },
    "report.radio_label": {"ko": "추천 업종", "en": "Recommended types"},
    "report.input_label": {
        "ko": "창업하고 싶은 업종을 입력하세요",
        "en": "Enter the business type you want to start",
    },
    "report.input_placeholder": {
        "ko": "예: 삼겹살집, 네일샵, 볼링장 ...",
        "en": "e.g., BBQ, nail salon, bowling alley ...",
    },
    "report.mapped_cat": {
        "ko": "📂 매핑된 소비 카테고리: ",
        "en": "📂 Mapped spending category: ",
    },
    "report.generate": {"ko": "📊 보고서 생성", "en": "📊 Generate report"},
    "report.generating": {
        "ko": "데이터 분석 및 보고서 생성 중…",
        "en": "Analyzing data and generating report…",
    },
    "report.kpi_top1": {"ko": "🏆 1위 추천 지역", "en": "🏆 #1 recommended area"},
    "report.kpi_score": {"ko": "종합 점수", "en": "Overall score"},
    "report.kpi_vitality": {"ko": "활력지수", "en": "Vitality index"},
    "report.top10": {"ko": "상위 10개 추천 지역", "en": "Top 10 recommended areas"},
    "report.axis_score": {"ko": "종합 점수", "en": "Overall score"},
    "report.top5_compare": {
        "ko": "상위 5개 지역 항목별 비교",
        "en": "Top 5 areas by factor comparison",
    },
    "report.axis_factor": {"ko": "평가 항목", "en": "Factor"},
    "report.axis_pct": {"ko": "백분위 점수 (0~100)", "en": "Percentile score (0~100)"},
    "report.detail_header": {"ko": "📋 상세 분석 보고서", "en": "📋 Detailed analysis report"},
    "report.ai_caption": {
        "ko": "Snowflake Cortex AI로 생성된 보고서입니다.",
        "en": "Report generated by Snowflake Cortex AI.",
    },
    "report.ranking_header": {"ko": "전체 지역 랭킹 데이터", "en": "Full area ranking data"},
    "report.col_score": {"ko": "종합점수", "en": "Score"},
    "report.col_vitality": {"ko": "활력지수", "en": "Vitality"},
    "report.col_mom": {"ko": "전월대비(%)", "en": "MoM(%)"},
    "report.col_visitors": {"ko": "방문인구수", "en": "Visitors"},
    "report.col_total_sales": {"ko": "총카드매출", "en": "Total sales"},
    # Template report
    "report.tpl_title": {
        "ko": "{biz} 창업 추천 보고서",
        "en": "{biz} startup location report",
    },
    "report.tpl_basis": {
        "ko": "분석 기준: {cat} 매출, 유동인구, 소득 수준, 성장세, 소비 다양성",
        "en": "Basis: {cat} sales, foot traffic, income, growth, spend diversity",
    },
    "report.tpl_score": {"ko": "종합 점수: {v}점", "en": "Overall score: {v}"},
    "report.tpl_vitality": {"ko": "활력지수: {v}", "en": "Vitality index: {v}"},
    "report.tpl_cat_pct": {
        "ko": "{cat} 매출: 상위 {v}%",
        "en": "{cat} sales: top {v}%",
    },
    "report.tpl_visitors": {"ko": "방문인구: {v}명", "en": "Visitors: {v}"},
    "report.tpl_total_sales": {"ko": "총 카드매출: {v}원", "en": "Total card sales: {v} KRW"},
    "report.tpl_str_cat": {
        "ko": "**{cat} 매출 상위 {p}%**",
        "en": "**Top {p}% in {cat} sales**",
    },
    "report.tpl_str_traffic": {
        "ko": "**유동인구 상위 {p}%**",
        "en": "**Top {p}% foot traffic**",
    },
    "report.tpl_str_income": {
        "ko": "**소득 수준 상위 {p}%**",
        "en": "**Top {p}% income level**",
    },
    "report.tpl_str_population": {
        "ko": "**거주인구 상위 {p}%**",
        "en": "**Top {p}% residential population**",
    },
    "report.tpl_str_growth": {
        "ko": "**성장세** (전월 대비 +{p}%)",
        "en": "**Growth trend** (+{p}% MoM)",
    },
    "report.tpl_cau_traffic": {
        "ko": "유동인구가 적어 홍보·마케팅 전략 필요",
        "en": "Low foot traffic — marketing strategy needed",
    },
    "report.tpl_cau_income": {
        "ko": "소득 수준이 낮아 가격 전략 중요",
        "en": "Low income level — pricing strategy important",
    },
    "report.tpl_cau_decline": {
        "ko": "활력 하락 추세 ({p}%)",
        "en": "Vitality declining ({p}%)",
    },
    "report.tpl_cau_diversity": {
        "ko": "소비 다양성 낮음 — 업종 쏠림 위험",
        "en": "Low spend diversity — category concentration risk",
    },
    "report.tpl_strengths": {"ko": "강점", "en": "Strengths"},
    "report.tpl_cautions": {"ko": "주의", "en": "Cautions"},
    "report.tpl_conclusion": {"ko": "최종 추천", "en": "Final recommendation"},
    "report.tpl_conclusion_text": {
        "ko": (
            "{city} {district}은(는) "
            "{cat} 매출 상위 {cat_p}%, "
            "방문인구 상위 {vis_p}%로 "
            "**{biz}** 창업에 가장 유리한 입지로 분석됩니다."
        ),
        "en": (
            "{city} {district} ranks in the "
            "top {cat_p}% for {cat} sales and "
            "top {vis_p}% for visitors, making it "
            "the strongest location for a **{biz}** startup."
        ),
    },
    # Cortex prompt
    "report.cortex_system": {
        "ko": "당신은 서울시 자영업 창업 전문 컨설턴트입니다.",
        "en": "You are a startup location consultant specializing in Seoul small business.",
    },
    "report.cortex_instruction": {
        "ko": (
            "아래 데이터 분석 결과를 바탕으로 '{biz}' 창업 최적 입지를 추천하는 보고서를 작성하세요."
        ),
        "en": (
            "Based on the data analysis below, write a report recommending the best locations "
            "for opening a '{biz}' business."
        ),
    },
    "report.cortex_category": {"ko": "관련 소비 카테고리", "en": "Related spending category"},
    "report.cortex_top5": {
        "ko": "상위 5개 추천 지역 (데이터 분석 기반)",
        "en": "Top 5 recommended areas (data-driven)",
    },
    "report.cortex_guidelines": {
        "ko": (
            "## 보고서 작성 지침:\n"
            "1. 각 추천 지역에 대해 해당 업종에 왜 적합한지 구체적으로 설명\n"
            "2. 수치를 인용하여 근거 제시\n"
            "3. 각 지역의 강점과 주의할 점을 균형 있게 분석\n"
            "4. 업종 특성(타겟 고객층, 입지 요건)과 지역 데이터를 연결\n"
            "5. 최종 1순위 추천과 그 이유를 결론으로 제시\n"
            "6. 한국어 마크다운 형식으로 작성\n"
        ),
        "en": (
            "## Report guidelines:\n"
            "1. Explain specifically why each area suits this business type\n"
            "2. Cite data to support every claim\n"
            "3. Analyze strengths and risks for each area in a balanced way\n"
            "4. Link business characteristics (target customers, location needs) with area data\n"
            "5. Provide a clear #1 recommendation with reasoning as conclusion\n"
            "6. Write in English markdown format\n"
        ),
    },
    "report.cortex_write": {"ko": "보고서를 작성하세요:", "en": "Write the report:"},
    "report.cortex_rank": {"ko": "위", "en": ""},
    "report.cortex_score_label": {"ko": "종합점수", "en": "Overall score"},
    "report.cortex_cat_pct": {"ko": "업종({cat}) 매출 백분위", "en": "{cat} sales percentile"},
    "report.cortex_visit_pct": {"ko": "방문인구 백분위", "en": "Visitor percentile"},
    "report.cortex_income_pct": {"ko": "소득수준 백분위", "en": "Income percentile"},
    "report.cortex_pop_pct": {"ko": "거주인구 백분위", "en": "Resident percentile"},
    "report.cortex_growth_pct": {"ko": "성장세 백분위", "en": "Growth percentile"},
    "report.cortex_diversity_pct": {"ko": "소비다양성 백분위", "en": "Diversity percentile"},
    "report.cortex_vitality": {"ko": "활력지수", "en": "Vitality index"},
    "report.cortex_mom": {"ko": "전월대비 변화", "en": "MoM change"},
    "report.cortex_total_sales": {"ko": "총 카드매출", "en": "Total card sales"},
    "report.cortex_visitors": {"ko": "방문인구수", "en": "Visitors"},

    # ── Backtest tab ────────────────────────────────────────────────────────
    "backtest.header": {"ko": "백테스팅", "en": "Backtesting"},
    "backtest.intro": {
        "ko": (
            "추천 모델을 과거 데이터에 적용해 실제로 "
            "추천 지역이 더 좋은 성과를 내는지 "
            "검증합니다. 적중률이 50%를 넘으면 "
            "랜덤보다 나은 모델입니다."
        ),
        "en": (
            "Tests whether recommended districts historically outperformed. "
            "A hit rate above 50% beats random choice."
        ),
    },
    "backtest.sub_settings": {"ko": "백테스트 설정", "en": "Backtest settings"},
    "backtest.warn_insufficient_history": {
        "ko": "백테스트를 실행하기에 데이터 기간이 부족합니다.",
        "en": "Not enough history in the data to run this backtest.",
    },
    "backtest.select_business": {"ko": "업종 선택", "en": "Select business"},
    "backtest.eval_period": {
        "ko": "평가 기간 (추천 후 N개월 성과 측정)",
        "en": "Evaluation period (N months after recommendation)",
    },
    "backtest.desc": {
        "ko": (
            "매월 <b style='color:#359efa'>{cat}</b> 매출 기준 상위 5개 지역을 추천했다고 가정하고, "
            "추천 후 {n}개월간 해당 지역의 실제 매출 성장률이 전체 중앙값을 넘었는지 확인합니다."
        ),
        "en": (
            "Assumes top 5 areas by <b style='color:#359efa'>{cat}</b> sales each month, "
            "then checks whether actual growth over {n} months beat the overall median."
        ),
    },
    "backtest.run": {"ko": "🔬 백테스트 실행", "en": "🔬 Run backtest"},
    "backtest.running": {
        "ko": "전체 기간 백테스트 실행 중…",
        "en": "Running full-period backtest…",
    },
    "backtest.kpi_hit_rate": {"ko": "전체 적중률", "en": "Overall hit rate"},
    "backtest.kpi_hit_desc": {
        "ko": "추천 지역이 중앙값 상회",
        "en": "Recommended areas beat median",
    },
    "backtest.kpi_alpha": {"ko": "평균 초과 성장률", "en": "Avg excess growth"},
    "backtest.kpi_alpha_desc": {
        "ko": "추천 vs 전체 평균",
        "en": "Recommended vs overall avg",
    },
    "backtest.kpi_win_rate": {"ko": "기간 승률", "en": "Period win rate"},
    "backtest.kpi_win_desc": {
        "ko": "{w}/{t}개 기간",
        "en": "{w}/{t} periods",
    },
    "backtest.kpi_confidence": {"ko": "모델 신뢰도", "en": "Model confidence"},
    "backtest.conf_high": {"ko": "높음", "en": "High"},
    "backtest.conf_mid": {"ko": "보통", "en": "Moderate"},
    "backtest.conf_low": {"ko": "낮음", "en": "Low"},
    "backtest.hit_trend": {"ko": "월별 적중률 추이", "en": "Monthly hit rate trend"},
    "backtest.hit_trend_desc": {
        "ko": "50% 기준선(= 랜덤 수준) 위에 있으면 모델이 유효합니다.",
        "en": "Above the 50% baseline (= random) means the model is valid.",
    },
    "backtest.axis_rec_time": {"ko": "추천 시점", "en": "Recommendation time"},
    "backtest.axis_hit_rate": {"ko": "적중률 (%)", "en": "Hit rate (%)"},
    "backtest.random_baseline": {"ko": "랜덤 기준 50%", "en": "Random baseline 50%"},
    "backtest.growth_header": {
        "ko": "추천 지역 vs 전체 평균 성장률",
        "en": "Recommended vs overall avg growth rate",
    },
    "backtest.growth_desc": {
        "ko": "파란색(추천)이 회색(전체)보다 높으면 모델이 더 좋은 지역을 골라낸 것입니다.",
        "en": "Blue (recommended) above gray (overall) means the model picked better areas.",
    },
    "backtest.growth_rec": {"ko": "추천 지역", "en": "Recommended"},
    "backtest.growth_all": {"ko": "전체 평균", "en": "Overall avg"},
    "backtest.alpha_header": {
        "ko": "누적 초과 성장률 (Alpha)",
        "en": "Cumulative excess growth (Alpha)",
    },
    "backtest.alpha_desc": {
        "ko": (
            "추천 지역이 전체 평균 대비 얼마나 더 성장했는지 누적합니다. "
            "우상향이면 모델이 지속적으로 좋은 지역을 골라내고 있다는 뜻입니다."
        ),
        "en": (
            "Cumulates how much recommended areas outgrew the average. "
            "An upward trend means the model consistently picks better areas."
        ),
    },
    "backtest.alpha_axis": {
        "ko": "누적 초과 성장률 (%p)",
        "en": "Cumulative excess growth (%p)",
    },
    "backtest.alpha_tooltip": {"ko": "해당 기간 Alpha", "en": "Period Alpha"},
    "backtest.case_header": {
        "ko": "최근 백테스트 상세 사례",
        "en": "Latest backtest case details",
    },
    "backtest.case_desc": {
        "ko": (
            "<b style='color:#ffffff'>{base}</b>에 모델이 추천한 지역들의 "
            "<b style='color:#ffffff'>{end}</b>까지 실제 성과입니다."
        ),
        "en": (
            "Actual performance of model-recommended areas from "
            "<b style='color:#ffffff'>{base}</b> through "
            "<b style='color:#ffffff'>{end}</b>."
        ),
    },
    "backtest.col_rec_area": {"ko": "추천 지역", "en": "Recommended area"},
    "backtest.col_actual_growth": {"ko": "실제 성장률(%)", "en": "Actual growth(%)"},
    "backtest.col_median": {"ko": "전체 중앙값(%)", "en": "Overall median(%)"},
    "backtest.col_verdict": {"ko": "판정", "en": "Verdict"},
    "backtest.hit": {"ko": "✅ 적중", "en": "✅ Hit"},
    "backtest.miss": {"ko": "❌ 미적중", "en": "❌ Miss"},
    "backtest.chart_rec_growth": {"ko": "추천 지역 성장률", "en": "Recommended growth"},
    "backtest.chart_baseline": {"ko": "기준선 (중앙값)", "en": "Baseline (median)"},
    "backtest.chart_median_label": {"ko": "전체 중앙값", "en": "Overall median"},
    "backtest.full_result": {
        "ko": "전체 기간 백테스트 결과",
        "en": "Full backtest results",
    },
    "backtest.col_rec_time": {"ko": "추천 시점", "en": "Rec. time"},
    "backtest.col_eval_end": {"ko": "평가 종료", "en": "Eval end"},
    "backtest.col_rec_growth": {"ko": "추천 성장률(%)", "en": "Rec. growth(%)"},
    "backtest.col_all_growth": {"ko": "전체 성장률(%)", "en": "Avg growth(%)"},
    "backtest.col_alpha": {"ko": "Alpha(%p)", "en": "Alpha(%p)"},
    "backtest.col_hits": {"ko": "적중", "en": "Hits"},
    "backtest.col_recs": {"ko": "추천수", "en": "Recs"},
    "backtest.col_hit_rate": {"ko": "적중률(%)", "en": "Hit rate(%)"},
    "backtest.verdict_good": {
        "ko": (
            "**{biz}** 추천 모델은 과거 {n}개 기간에 걸쳐 "
            "**적중률 {hr}%**, 평균 초과 성장률 **{alpha}%p**를 기록했습니다. "
            "랜덤(50%) 대비 유의미한 성과로, 모델 추천을 참고할 가치가 있습니다."
        ),
        "en": (
            "The **{biz}** recommendation model achieved "
            "**{hr}% hit rate** and **{alpha}%p** avg excess growth over {n} periods. "
            "Significantly beats random (50%), worth consulting."
        ),
    },
    "backtest.verdict_mid": {
        "ko": (
            "**{biz}** 추천 모델은 적중률 **{hr}%**로 "
            "랜덤 수준에 가깝습니다. 추천 결과를 참고하되, 현장 조사와 병행하시기를 권합니다."
        ),
        "en": (
            "The **{biz}** model has a **{hr}%** hit rate, "
            "close to random. Use recommendations as reference alongside field research."
        ),
    },
    "backtest.verdict_bad": {
        "ko": (
            "**{biz}** 추천 모델은 적중률 **{hr}%**로 "
            "랜덤보다 낮은 성과를 보였습니다. 이 업종은 현재 데이터만으로 입지를 판단하기 어려울 수 있습니다."
        ),
        "en": (
            "The **{biz}** model has a **{hr}%** hit rate, below random. "
            "Current data may not be sufficient to judge location for this type."
        ),
    },
    "backtest.verdict_header": {"ko": "백테스트 결론", "en": "Backtest conclusion"},

    # ── Diagnostic tab ──────────────────────────────────────────────────────
    "diagnostic.header": {
        "ko": "모델 진단 & 최적화",
        "en": "Model diagnostics & optimization",
    },
    "diagnostic.intro": {
        "ko": (
            "추천 모델이 왜 부정확한지 원인을 "
            "분석하고, 데이터 기반으로 가중치를 "
            "재조정합니다."
        ),
        "en": (
            "Analyzes why the recommendation model is inaccurate "
            "and recalibrates weights using historical data."
        ),
    },
    "diagnostic.select_business": {"ko": "업종 선택", "en": "Select business"},
    "diagnostic.eval_period": {"ko": "평가 기간 (개월)", "en": "Evaluation period (months)"},
    "diagnostic.run": {"ko": "🔍 진단 실행", "en": "🔍 Run diagnostics"},
    "diagnostic.analyzing": {
        "ko": "팩터 예측력 분석 중…",
        "en": "Analyzing factor predictiveness…",
    },
    "diagnostic.no_data": {"ko": "데이터가 없습니다.", "en": "No data available."},
    "diagnostic.insufficient": {
        "ko": "분석에 필요한 데이터 기간이 부족합니다.",
        "en": "Insufficient data period for analysis.",
    },
    "diagnostic.optimizing": {
        "ko": "최적 가중치 탐색 중 (그리드서치)… 잠시 기다려주세요",
        "en": "Finding optimal weights (grid search)… please wait",
    },
    "diagnostic.s1_header": {
        "ko": "1. 문제 진단: 각 팩터의 실제 예측력",
        "en": "1. Diagnosis: factor predictiveness",
    },
    "diagnostic.s1_desc": {
        "ko": (
            "각 팩터 백분위와 미래 매출 성장률 간의 상관계수입니다. "
            "<b style='color:#7de12f'>양수</b> = 높을수록 미래 성장↑ | "
            "<b style='color:#ff5252'>음수</b> = 높을수록 오히려 성장↓ (포화 신호)"
        ),
        "en": (
            "Correlation between each factor percentile and future sales growth. "
            "<b style='color:#7de12f'>Positive</b> = higher → more growth | "
            "<b style='color:#ff5252'>Negative</b> = higher → less growth (saturation)"
        ),
    },
    "diagnostic.avg_corr": {"ko": "평균 상관계수", "en": "Avg correlation"},
    "diagnostic.corr_axis": {
        "ko": "미래 성장률과의 상관계수",
        "en": "Correlation with future growth",
    },
    "diagnostic.dir_positive": {"ko": "양(+) 예측력", "en": "Positive(+)"},
    "diagnostic.dir_negative": {"ko": "음(-) 역예측", "en": "Negative(−) inverse"},
    "diagnostic.neg_title": {"ko": "⚠️ 역예측 팩터 발견", "en": "⚠️ Inverse-prediction factors found"},
    "diagnostic.neg_text": {
        "ko": (
            "이 팩터가 높은 지역은 오히려 미래 성장률이 낮습니다. "
            "경쟁 포화 또는 이미 피크를 지난 지역일 수 있습니다."
        ),
        "en": (
            "Areas high in this factor actually have lower future growth. "
            "Could indicate market saturation or post-peak areas."
        ),
    },
    "diagnostic.pos_title": {"ko": "✅ 유효한 팩터", "en": "✅ Valid factors"},
    "diagnostic.pos_text": {
        "ko": "이 팩터는 실제로 미래 성장을 예측하는 데 유효합니다.",
        "en": "These factors effectively predict future growth.",
    },
    "diagnostic.s2_header": {
        "ko": "2. 기간별 팩터 예측력 히트맵",
        "en": "2. Factor predictiveness heatmap",
    },
    "diagnostic.s2_desc": {
        "ko": (
            "팩터의 예측력이 시간에 따라 안정적인지 확인합니다. "
            "색이 일관되면 신뢰할 수 있는 팩터입니다."
        ),
        "en": (
            "Checks whether factor predictiveness is stable over time. "
            "Consistent colors indicate reliable factors."
        ),
    },
    "diagnostic.s3_header": {
        "ko": "3. 가중치 최적화 결과",
        "en": "3. Weight optimization results",
    },
    "diagnostic.opt_failed": {
        "ko": "최적화에 실패했습니다. 데이터가 부족할 수 있습니다.",
        "en": "Optimization failed. Data may be insufficient.",
    },
    "diagnostic.kpi_current": {"ko": "현재 모델 적중률", "en": "Current model hit rate"},
    "diagnostic.kpi_current_desc": {"ko": "기존 가중치", "en": "Existing weights"},
    "diagnostic.kpi_optimized": {
        "ko": "최적화 모델 적중률",
        "en": "Optimized model hit rate",
    },
    "diagnostic.kpi_improvement": {
        "ko": "{v}%p 개선",
        "en": "{v}%p improvement",
    },
    "diagnostic.trust_label": {"ko": "최적화 후 신뢰도", "en": "Post-optimization confidence"},
    "diagnostic.trust_valid": {"ko": "유효", "en": "Valid"},
    "diagnostic.trust_moderate": {"ko": "보통", "en": "Moderate"},
    "diagnostic.model_current": {"ko": "현재 모델", "en": "Current model"},
    "diagnostic.model_optimized": {"ko": "최적화 모델", "en": "Optimized model"},
    "diagnostic.weight_axis": {"ko": "가중치 (%)", "en": "Weight (%)"},
    "diagnostic.s4_header": {"ko": "4. 최적 가중치 상세", "en": "4. Optimal weight details"},
    "diagnostic.col_current": {"ko": "현재", "en": "Current"},
    "diagnostic.col_optimized": {"ko": "최적화", "en": "Optimized"},
    "diagnostic.col_change": {"ko": "변화", "en": "Change"},
    "diagnostic.s5_header": {
        "ko": "5. 최적화 가중치 적용",
        "en": "5. Apply optimized weights",
    },
    "diagnostic.apply_good": {
        "ko": (
            "최적화 가중치를 적용하면 백테스트 적중률이 "
            "**{curr}% → {best}%** (+{imp}%p)로 개선됩니다."
        ),
        "en": (
            "Applying optimized weights improves backtest hit rate "
            "from **{curr}% → {best}%** (+{imp}%p)."
        ),
    },
    "diagnostic.apply_bad": {
        "ko": (
            "이 업종은 현재 데이터의 팩터만으로는 미래 성장을 예측하기 어렵습니다. "
            "최적화 후에도 적중률이 **{best}%**에 머물러, "
            "추가 데이터(경쟁 밀도, 임대료 등)가 필요할 수 있습니다."
        ),
        "en": (
            "This category is hard to predict with current factors alone. "
            "Even after optimization, hit rate stays at **{best}%** — "
            "additional data (competition, rent) may be needed."
        ),
    },
    "diagnostic.apply_btn": {
        "ko": "✅ 최적화 가중치를 보고서 탭에 적용",
        "en": "✅ Apply optimized weights to report tab",
    },
    "diagnostic.apply_success": {
        "ko": (
            "적용 완료! '📊 창업 보고서' 탭에서 최적화 가중치로 분석됩니다. "
            "(적중률 {curr}% → {best}%)"
        ),
        "en": (
            "Applied! The '📊 Startup report' tab now uses optimized weights. "
            "(Hit rate {curr}% → {best}%)"
        ),
    },
    "diagnostic.s6_header": {"ko": "6. 해석 가이드", "en": "6. Interpretation guide"},
    "diagnostic.interp_saturated": {
        "ko": "이미 높은 곳은 포화 상태. 가중치를 낮추거나 역방향으로 사용해야 합니다.",
        "en": "Already high areas are saturated. Reduce weight or use inversely.",
    },
    "diagnostic.interp_useless": {
        "ko": "예측력 없음. 가중치를 최소화해야 합니다.",
        "en": "No predictive power. Minimize weight.",
    },
    "diagnostic.interp_valid": {
        "ko": "유효한 예측 팩터. 가중치를 높여야 합니다.",
        "en": "Valid predictive factor. Increase weight.",
    },
}


def t(key: str, **kwargs: str | float | int) -> str:
    loc = st.session_state.get("locale", "ko")
    row = MESSAGES.get(key, {})
    text = row.get(loc) or row.get("ko") or key
    return text.format(**kwargs) if kwargs else text


def nav_label(tab_key: str) -> str:
    return t(f"nav.{tab_key}")


# ── Helper dicts (call at render-time so locale is current) ─────────────


def categories() -> dict[str, str]:
    """Column name → translated label for spending categories."""
    return {
        "COFFEE_SALES": t("cat.coffee"),
        "ENTERTAINMENT_SALES": t("cat.entertainment"),
        "FOOD_SALES": t("cat.food"),
        "FASHION_SALES": t("cat.fashion"),
        "LEISURE_SALES": t("cat.leisure"),
        "SMALL_RETAIL_SALES": t("cat.retail"),
    }


def category_label(col: str) -> str:
    return categories().get(col, t("cat.food"))


def categories_short() -> dict[str, str]:
    """Short category labels for compact charts."""
    return {
        "FOOD_SALES": t("cat_s.food"),
        "COFFEE_SALES": t("cat_s.coffee"),
        "ENTERTAINMENT_SALES": t("cat_s.entertainment"),
        "SMALL_RETAIL_SALES": t("cat_s.retail"),
        "FASHION_SALES": t("cat_s.fashion"),
        "LEISURE_SALES": t("cat_s.leisure"),
    }


def factors() -> dict[str, str]:
    """pct_col → translated label for scoring factors."""
    return {
        "pct_category": t("factor.cat_sales"),
        "pct_visiting": t("factor.foot_traffic"),
        "pct_income": t("factor.income"),
        "pct_population": t("factor.population"),
        "pct_growth": t("factor.growth"),
        "pct_diversity": t("factor.diversity"),
    }


def quadrants() -> dict[str, str]:
    """Internal key → translated quadrant name."""
    return {
        "spectator": t("quad.spectator"),
        "active": t("quad.active"),
        "local": t("quad.local"),
        "stagnant": t("quad.stagnant"),
    }


def business_presets() -> list[dict]:
    """Return translated business preset list. Values stay Korean for classification."""
    _keys = [
        ("preset.chicken", "치킨집"),
        ("preset.meat", "고깃집"),
        ("preset.cafe", "카페"),
        ("preset.gym", "헬스장"),
        ("preset.convenience", "편의점"),
        ("preset.clothing", "옷가게"),
        ("preset.karaoke", "노래방"),
        ("preset.salon", "미용실"),
        ("preset.pizza", "피자집"),
        ("preset.snack", "분식집"),
    ]
    return [{"label": t(k), "value": v} for k, v in _keys]
