import streamlit as st


def render(session, df, months: list, selected_cities: list, city_code_to_name: dict):
    st.header("🤖 AI 도시 분석 상담")
    st.markdown("도시 데이터에 대해 자연어로 질문하세요. Snowflake Cortex AI가 답변합니다.")

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

    system_prompt = f"""당신은 서울시 도시 활력 분석 전문 AI 컨설턴트입니다.
아래 데이터를 기반으로 질문에 답변하세요.

[데이터 기간]: 2021년 1월 ~ 2025년 12월
[분석 대상]: 서울시 {", ".join(selected_city_names)}의 법정동
[활력 지수]: 유동인구, 방문인구비율, 소비규모, 소비다양성, 소득수준, 신용건전성을 종합한 0~100 점수

[최신 월 활력 Top 5]:
{summary_top5}

[최신 월 활력 Bottom 5]:
{summary_bottom5}

답변 시:
- 구체적인 데이터 수치를 인용하세요
- 소상공인 창업, 지자체 정책, 부동산 투자 관점에서 실용적 인사이트를 제공하세요
- 한국어로 답변하세요
"""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("예: 서초구에서 카페 창업하기 좋은 동네는?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("분석 중..."):
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
                        st.error(f"Cortex AI 오류: {str(e2)}")
