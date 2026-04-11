import streamlit as st

from vitality_app.i18n import t

# Add AI tab translations
_AI_MESSAGES = {
    "ai.header": {"ko": "🤖 AI 도시 분석 상담", "en": "🤖 AI urban analysis assistant"},
    "ai.desc": {
        "ko": "도시 데이터에 대해 자연어로 질문하세요. Snowflake Cortex AI가 답변합니다.",
        "en": "Ask questions about urban data in natural language. Snowflake Cortex AI will answer.",
    },
    "ai.system_prompt": {
        "ko": (
            "당신은 서울시 도시 활력 분석 전문 AI 컨설턴트입니다.\n"
            "아래 데이터를 기반으로 질문에 답변하세요.\n\n"
            "[데이터 기간]: 2021년 1월 ~ 2025년 12월\n"
            "[분석 대상]: 서울시 {cities}의 법정동\n"
            "[활력 지수]: 유동인구, 방문인구비율, 소비규모, 소비다양성, 소득수준, 신용건전성을 종합한 0~100 점수\n\n"
            "[최신 월 활력 Top 5]:\n{top5}\n\n"
            "[최신 월 활력 Bottom 5]:\n{bottom5}\n\n"
            "답변 시:\n"
            "- 구체적인 데이터 수치를 인용하세요\n"
            "- 소상공인 창업, 지자체 정책, 부동산 투자 관점에서 실용적 인사이트를 제공하세요\n"
            "- 한국어로 답변하세요"
        ),
        "en": (
            "You are an AI consultant specializing in Seoul urban vitality analysis.\n"
            "Answer questions based on the data below.\n\n"
            "[Data period]: Jan 2021 – Dec 2025\n"
            "[Scope]: Seoul districts in {cities}\n"
            "[Vitality index]: 0–100 composite of foot traffic, visit ratio, spending, diversity, income, credit health\n\n"
            "[Latest month Top 5]:\n{top5}\n\n"
            "[Latest month Bottom 5]:\n{bottom5}\n\n"
            "Guidelines:\n"
            "- Cite specific data figures\n"
            "- Provide practical insights for small business startups, local policy, and real estate\n"
            "- Answer in English"
        ),
    },
    "ai.placeholder": {
        "ko": "예: 서초구에서 카페 창업하기 좋은 동네는?",
        "en": "e.g., Which neighborhoods in Seocho are best for opening a café?",
    },
    "ai.analyzing": {"ko": "분석 중...", "en": "Analyzing..."},
    "ai.error": {"ko": "Cortex AI 오류: {err}", "en": "Cortex AI error: {err}"},
}

# Register AI messages into the i18n system
from vitality_app.i18n import MESSAGES
MESSAGES.update(_AI_MESSAGES)


def render(session, df, months: list, selected_cities: list, city_code_to_name: dict):
    st.header(t("ai.header"))
    st.markdown(t("ai.desc"))

    df_latest = df[df["STANDARD_YEAR_MONTH"] == months[-1]].copy()

    summary_top5 = df_latest.nlargest(5, "CUSTOM_INDEX")[
        [
            "CITY_KOR_NAME",
            "DISTRICT_KOR_NAME",
            "CUSTOM_INDEX",
            "TREND_DIRECTION",
            "TOTAL_POPULATION",
            "TOTAL_CARD_SALES",
            "AVG_INCOME",
        ]
    ].to_string(index=False)

    summary_bottom5 = df_latest.nsmallest(5, "CUSTOM_INDEX")[
        [
            "CITY_KOR_NAME",
            "DISTRICT_KOR_NAME",
            "CUSTOM_INDEX",
            "TREND_DIRECTION",
            "TOTAL_POPULATION",
            "TOTAL_CARD_SALES",
            "AVG_INCOME",
        ]
    ].to_string(index=False)

    selected_city_names = [city_code_to_name.get(c, c) for c in selected_cities]

    system_prompt = t(
        "ai.system_prompt",
        cities=", ".join(selected_city_names),
        top5=summary_top5,
        bottom5=summary_bottom5,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(t("ai.placeholder")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t("ai.analyzing")):
                try:
                    escaped_system = system_prompt.replace("'", "\\'").replace("\n", "\\n")
                    escaped_prompt = prompt.replace("'", "\\'")

                    result = session.sql(
                        f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'mistral-large2',
                            CONCAT('[SYSTEM] ', '{escaped_system}', ' [USER] ', '{escaped_prompt}')
                        ) AS RESPONSE
                        """
                    ).collect()

                    answer = result[0]["RESPONSE"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception:
                    try:
                        result = session.sql(
                            f"""
                            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                                'snowflake-arctic',
                                CONCAT('[SYSTEM] ', '{escaped_system}', ' [USER] ', '{escaped_prompt}')
                            ) AS RESPONSE
                            """
                        ).collect()
                        answer = result[0]["RESPONSE"]
                        st.markdown(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                    except Exception as e2:
                        st.error(t("ai.error", err=str(e2)))
