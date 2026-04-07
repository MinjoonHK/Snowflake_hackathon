import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
from snowflake.snowpark.context import get_active_session

# ============================================================
# 설정
# ============================================================
st.set_page_config(page_title="Urban Vitality Index", page_icon="🏙️", layout="wide")

@st.cache_resource
def get_session():
    return get_active_session()

session = get_session()

# ============================================================
# 데이터 로드
# ============================================================
@st.cache_data(ttl=3600)
def load_available_cities():
    """활력 데이터가 실제로 있는 구 목록만 동적으로 로드"""
    return session.sql("""
        SELECT CITY_CODE, CITY_KOR_NAME, COUNT(DISTINCT DISTRICT_CODE) AS DISTRICT_CNT
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL
        GROUP BY CITY_CODE, CITY_KOR_NAME
        ORDER BY CITY_KOR_NAME
    """).to_pandas()

@st.cache_data(ttl=600)
def load_vitality_data(city_codes: tuple):
    """선택된 구의 활력 데이터 로드"""
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    df = session.sql(f"""
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
    return df

@st.cache_data(ttl=3600)
def load_geo_data(city_codes: tuple):
    """선택된 구의 지오 데이터 로드"""
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    geo_df = session.sql(f"""
        SELECT
            DISTRICT_KOR_NAME, DISTRICT_CODE, CITY_CODE,
            ST_ASGEOJSON(DISTRICT_GEOM) AS GEOJSON,
            ST_X(ST_CENTROID(DISTRICT_GEOM)) AS CENTER_LON,
            ST_Y(ST_CENTROID(DISTRICT_GEOM)) AS CENTER_LAT
        FROM SPH_DATA.GRANDATA.M_SCCO_MST
        WHERE CITY_CODE IN ({codes_str})
    """).to_pandas()
    return geo_df

# ============================================================
# 사이드바
# ============================================================
st.sidebar.title("🏙️ Urban Vitality Index")
st.sidebar.markdown("서울 도시 활력 분석 플랫폼")
st.sidebar.divider()

city_df = load_available_cities()
city_code_to_name = city_df.set_index('CITY_CODE')['CITY_KOR_NAME'].to_dict()

selected_cities = st.sidebar.multiselect(
    "🏙️ 분석할 구 선택",
    options=city_df['CITY_CODE'].tolist(),
    default=city_df['CITY_CODE'].tolist(),
    format_func=lambda x: city_code_to_name.get(x, x)
)

if not selected_cities:
    st.warning("분석할 구를 하나 이상 선택하세요.")
    st.stop()

# 선택된 구 데이터 로드
df = load_vitality_data(tuple(selected_cities))
geo_df = load_geo_data(tuple(selected_cities))
months = sorted(df['STANDARD_YEAR_MONTH'].unique())

st.sidebar.divider()

selected_month = st.sidebar.select_slider(
    "📅 분석 기간",
    options=months,
    value=months[-1],
    format_func=lambda x: f"{x[:4]}년 {x[4:]}월"
)

st.sidebar.divider()
st.sidebar.subheader("⚖️ 지수 가중치 조정")
w_pop  = st.sidebar.slider("유동인구",      0, 100, 15, 5)
w_visit= st.sidebar.slider("방문인구 비율", 0, 100, 15, 5)
w_cons = st.sidebar.slider("소비 규모",     0, 100, 20, 5)
w_div  = st.sidebar.slider("소비 다양성",   0, 100, 10, 5)
w_inc  = st.sidebar.slider("소득 수준",     0, 100, 20, 5)
w_cred = st.sidebar.slider("신용 건전성",   0, 100, 20, 5)

total_w = w_pop + w_visit + w_cons + w_div + w_inc + w_cred
if total_w > 0:
    df['CUSTOM_INDEX'] = (
        df['SCORE_POPULATION']  * (w_pop   / total_w)
        + df['SCORE_VISITING']  * (w_visit / total_w)
        + df['SCORE_CONSUMPTION']*(w_cons  / total_w)
        + df['SCORE_DIVERSITY'] * (w_div   / total_w)
        + df['SCORE_INCOME']    * (w_inc   / total_w)
        + df['SCORE_CREDIT']    * (w_cred  / total_w)
    ).round(2)
else:
    df['CUSTOM_INDEX'] = df['VITALITY_INDEX']

# ============================================================
# 탭
# ============================================================
tab1, tab2, tab3 = st.tabs(["🗺️ 활력 지도", "📊 트렌드 분석", "🤖 AI 상담"])

# ============================================================
# 탭 1: 활력 지도
# ============================================================
with tab1:
    st.header("서울 법정동 활력 지도")
    df_month = df[df['STANDARD_YEAR_MONTH'] == selected_month].copy()

    if len(df_month) == 0:
        st.warning("선택한 기간에 데이터가 없습니다.")
    else:
        # KPI 카드 — 선택된 구 동적으로 렌더링
        kpi_cols = st.columns(len(selected_cities))
        for col, city_code in zip(kpi_cols, selected_cities):
            city_name = city_code_to_name.get(city_code, city_code)
            city_data = df_month[df_month['CITY_CODE'] == city_code]
            avg_idx  = city_data['CUSTOM_INDEX'].mean()
            rising   = len(city_data[city_data['TREND_DIRECTION'] == 'RISING'])
            declining= len(city_data[city_data['TREND_DIRECTION'] == 'DECLINING'])
            with col:
                st.metric(
                    label=f"📍 {city_name} 평균 활력",
                    value=f"{avg_idx:.1f}" if not pd.isna(avg_idx) else "N/A",
                    delta=f"↑{rising} ↓{declining} 개동"
                )

        st.divider()

        # pydeck 지도
        map_data = df_month.merge(
            geo_df[['DISTRICT_CODE', 'CENTER_LON', 'CENTER_LAT']],
            on='DISTRICT_CODE', how='inner'
        )

        vmin   = map_data['CUSTOM_INDEX'].min()
        vmax   = map_data['CUSTOM_INDEX'].max()
        vrange = max(vmax - vmin, 1)

        def vitality_color(val):
            ratio = (val - vmin) / vrange
            if ratio < 0.5:
                r, g, b = 220, int(60 + ratio * 2 * 180), 60
            else:
                r, g, b = int(220 - (ratio - 0.5) * 2 * 180), 220, 60
            return [r, g, b, 180]

        map_data['COLOR']  = map_data['CUSTOM_INDEX'].apply(vitality_color)
        map_data['RADIUS'] = ((map_data['CUSTOM_INDEX'] - vmin) / vrange * 300 + 100).astype(int)

        # 지도 중심을 선택된 데이터 평균 좌표로 자동 계산
        center_lat = map_data['CENTER_LAT'].mean()
        center_lon = map_data['CENTER_LON'].mean()

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position='[CENTER_LON, CENTER_LAT]',
            get_color='COLOR',
            get_radius='RADIUS',
            pickable=True,
            opacity=0.8,
        )

        view = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12, pitch=0
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip={
                "html": "<b>{DISTRICT_KOR_NAME}</b><br>"
                        "활력지수: {CUSTOM_INDEX}<br>"
                        "유동인구: {TOTAL_POPULATION}<br>"
                        "카드매출: {TOTAL_CARD_SALES}<br>"
                        "평균소득: {AVG_INCOME}",
                "style": {"backgroundColor": "steelblue", "color": "white", "fontSize": "13px"}
            },
            map_style="mapbox://styles/mapbox/light-v10"
        )

        st.pydeck_chart(deck, height=500)

        lcol1, lcol2, lcol3 = st.columns(3)
        lcol1.markdown("🔴 **낮은 활력**")
        lcol2.markdown("🟡 **중간 활력**")
        lcol3.markdown("🟢 **높은 활력**")

        st.divider()

        # 랭킹 테이블
        st.subheader("📋 법정동 활력 순위")
        ranking = df_month[[
            'CITY_KOR_NAME', 'DISTRICT_KOR_NAME', 'CUSTOM_INDEX',
            'VITALITY_LEVEL', 'TREND_DIRECTION', 'MOM_CHANGE_PCT',
            'TOTAL_POPULATION', 'TOTAL_CARD_SALES', 'AVG_INCOME'
        ]].copy()
        ranking.columns = ['구', '동', '활력지수', '등급', '추세', '전월비(%)',
                           '유동인구', '카드매출', '평균소득']
        ranking = ranking.sort_values('활력지수', ascending=False).reset_index(drop=True)
        ranking.index += 1
        st.dataframe(ranking, use_container_width=True, height=400)


# ============================================================
# 탭 2: 트렌드 분석
# ============================================================
with tab2:
    st.header("법정동 트렌드 분석")

    available_districts = df[['CITY_KOR_NAME', 'DISTRICT_KOR_NAME', 'DISTRICT_CODE']].drop_duplicates()
    available_districts['LABEL'] = available_districts['CITY_KOR_NAME'] + ' ' + available_districts['DISTRICT_KOR_NAME']
    district_options = available_districts.set_index('DISTRICT_CODE')['LABEL'].to_dict()

    selected_districts = st.multiselect(
        "비교할 법정동 선택 (최대 5개)",
        options=list(district_options.keys()),
        default=list(district_options.keys())[:3],
        format_func=lambda x: district_options.get(x, x),
        max_selections=5
    )

    if selected_districts:
        df_trend = df[df['DISTRICT_CODE'].isin(selected_districts)].copy()
        df_trend['LABEL'] = df_trend['CITY_KOR_NAME'] + ' ' + df_trend['DISTRICT_KOR_NAME']

        st.subheader("활력 지수 추이")
        chart_trend = alt.Chart(df_trend).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X('STANDARD_YEAR_MONTH:N', title='기간',
                    axis=alt.Axis(labelAngle=-45,
                                  values=df_trend['STANDARD_YEAR_MONTH'].unique()[::6].tolist())),
            y=alt.Y('CUSTOM_INDEX:Q', title='활력 지수', scale=alt.Scale(zero=False)),
            color=alt.Color('LABEL:N', title='법정동'),
            tooltip=['LABEL', 'STANDARD_YEAR_MONTH',
                     alt.Tooltip('CUSTOM_INDEX:Q', format='.1f')]
        ).properties(height=400).interactive()
        st.altair_chart(chart_trend, use_container_width=True)

        st.subheader("세부 지표 비교 (최신 월)")
        df_radar = df_trend[df_trend['STANDARD_YEAR_MONTH'] == selected_month].copy()

        if len(df_radar) > 0:
            radar_data = []
            for _, row in df_radar.iterrows():
                label = f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
                radar_data.extend([
                    {'법정동': label, '지표': '유동인구',   '점수': row['SCORE_POPULATION']},
                    {'법정동': label, '지표': '방문비율',   '점수': row['SCORE_VISITING']},
                    {'법정동': label, '지표': '소비규모',   '점수': row['SCORE_CONSUMPTION']},
                    {'법정동': label, '지표': '소비다양성', '점수': row['SCORE_DIVERSITY']},
                    {'법정동': label, '지표': '소득수준',   '점수': row['SCORE_INCOME']},
                    {'법정동': label, '지표': '신용건전성', '점수': row['SCORE_CREDIT']},
                ])
            df_radar_chart = pd.DataFrame(radar_data)

            chart_radar = alt.Chart(df_radar_chart).mark_bar(opacity=0.8).encode(
                x=alt.X('지표:N', title=None),
                y=alt.Y('점수:Q', title='점수 (0~100)', scale=alt.Scale(domain=[0, 100])),
                color=alt.Color('법정동:N'),
                xOffset='법정동:N',
                tooltip=['법정동', '지표', alt.Tooltip('점수:Q', format='.1f')]
            ).properties(height=400)
            st.altair_chart(chart_radar, use_container_width=True)

        st.subheader("업종별 카드 매출 구성")
        if len(df_radar) > 0:
            sales_data = []
            for _, row in df_radar.iterrows():
                label = f"{row['CITY_KOR_NAME']} {row['DISTRICT_KOR_NAME']}"
                total = max(
                    row['FOOD_SALES'] + row['COFFEE_SALES'] + row['ENTERTAINMENT_SALES']
                    + row['SMALL_RETAIL_SALES'] + row['FASHION_SALES'] + row['LEISURE_SALES'], 1
                )
                sales_data.extend([
                    {'동': label, '업종': '외식', '비율': round(row['FOOD_SALES']          / total * 100, 1)},
                    {'동': label, '업종': '커피', '비율': round(row['COFFEE_SALES']         / total * 100, 1)},
                    {'동': label, '업종': '엔터', '비율': round(row['ENTERTAINMENT_SALES']  / total * 100, 1)},
                    {'동': label, '업종': '소매', '비율': round(row['SMALL_RETAIL_SALES']   / total * 100, 1)},
                    {'동': label, '업종': '패션', '비율': round(row['FASHION_SALES']        / total * 100, 1)},
                    {'동': label, '업종': '레저', '비율': round(row['LEISURE_SALES']        / total * 100, 1)},
                ])
            df_sales = pd.DataFrame(sales_data)

            chart_sales = alt.Chart(df_sales).mark_bar().encode(
                x=alt.X('동:N', title=None),
                y=alt.Y('비율:Q', title='비율 (%)', stack='normalize'),
                color=alt.Color('업종:N', scale=alt.Scale(scheme='set2')),
                tooltip=['동', '업종', alt.Tooltip('비율:Q', format='.1f')]
            ).properties(height=400)
            st.altair_chart(chart_sales, use_container_width=True)
    else:
        st.info("비교할 법정동을 선택하세요.")


# ============================================================
# 탭 3: AI 상담
# ============================================================
with tab3:
    st.header("🤖 AI 도시 분석 상담")
    st.markdown("도시 데이터에 대해 자연어로 질문하세요. Snowflake Cortex AI가 답변합니다.")

    df_latest = df[df['STANDARD_YEAR_MONTH'] == months[-1]].copy()

    summary_top5 = df_latest.nlargest(5, 'CUSTOM_INDEX')[
        ['CITY_KOR_NAME', 'DISTRICT_KOR_NAME', 'CUSTOM_INDEX',
         'TREND_DIRECTION', 'TOTAL_POPULATION', 'TOTAL_CARD_SALES', 'AVG_INCOME']
    ].to_string(index=False)

    summary_bottom5 = df_latest.nsmallest(5, 'CUSTOM_INDEX')[
        ['CITY_KOR_NAME', 'DISTRICT_KOR_NAME', 'CUSTOM_INDEX',
         'TREND_DIRECTION', 'TOTAL_POPULATION', 'TOTAL_CARD_SALES', 'AVG_INCOME']
    ].to_string(index=False)

    selected_city_names = [city_code_to_name.get(c, c) for c in selected_cities]

    system_prompt = f"""당신은 서울시 도시 활력 분석 전문 AI 컨설턴트입니다.
아래 데이터를 기반으로 질문에 답변하세요.

[데이터 기간]: 2021년 1월 ~ 2025년 12월
[분석 대상]: 서울시 {', '.join(selected_city_names)}의 법정동
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

                    result = session.sql(f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'mistral-large2',
                            CONCAT('[SYSTEM] ', '{escaped_system}', ' [USER] ', '{escaped_prompt}')
                        ) AS RESPONSE
                    """).collect()

                    answer = result[0]['RESPONSE']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    error_msg = str(e)
                    try:
                        result = session.sql(f"""
                            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                                'snowflake-arctic',
                                CONCAT('[SYSTEM] ', '{escaped_system}', ' [USER] ', '{escaped_prompt}')
                            ) AS RESPONSE
                        """).collect()
                        answer = result[0]['RESPONSE']
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e2:
                        st.error(f"Cortex AI 오류: {str(e2)}")


# ============================================================
# 푸터
# ============================================================
st.sidebar.divider()
st.sidebar.caption("Built with Snowflake + Streamlit")
st.sidebar.caption("Data: SPH (SKT 유동인구, KCB 자산소득, 신한카드 소비)")