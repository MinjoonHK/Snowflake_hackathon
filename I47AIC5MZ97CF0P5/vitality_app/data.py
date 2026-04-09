import streamlit as st

from vitality_app.session import get_session


@st.cache_data(ttl=3600)
def load_available_cities():
    session = get_session()
    return session.sql(
        """
        SELECT CITY_CODE, CITY_KOR_NAME, COUNT(DISTINCT DISTRICT_CODE) AS DISTRICT_CNT
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL
        GROUP BY CITY_CODE, CITY_KOR_NAME
        ORDER BY CITY_KOR_NAME
        """
    ).to_pandas()


@st.cache_data(ttl=600)
def load_vitality_data(city_codes: tuple):
    session = get_session()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    df = session.sql(
        f"""
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
        """
    ).to_pandas()
    return df


@st.cache_data(ttl=3600)
def load_visitor_data(city_codes: tuple):
    session = get_session()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    df = session.sql(
        f"""
        SELECT
            v.CITY_KOR_NAME, v.DISTRICT_KOR_NAME,
            v.CITY_CODE, v.DISTRICT_CODE,
            v.STANDARD_YEAR_MONTH,
            v.TOTAL_VISITING, v.TOTAL_POPULATION,
            v.TOTAL_CARD_SALES,
            v.SCORE_VISITING, v.SCORE_CONSUMPTION,
            v.VITALITY_INDEX,
            COALESCE(t.STATION_CNT, 0)     AS STATION_CNT,
            COALESCE(t.MIN_DISTANCE, 0)    AS MIN_DISTANCE,
            COALESCE(t.TOTAL_GET_ON, 0)    AS TOTAL_GET_ON,
            COALESCE(t.TOTAL_GET_OFF, 0)   AS TOTAL_GET_OFF,
            COALESCE(t.TOTAL_GET_ON, 0) + COALESCE(t.TOTAL_GET_OFF, 0) AS TOTAL_RIDERSHIP
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL v
        LEFT JOIN (
            SELECT
                LEFT(BJD_CODE, 8)                AS DISTRICT_CODE,
                COUNT(DISTINCT STATION_NAME)     AS STATION_CNT,
                MIN(DISTANCE)                    AS MIN_DISTANCE,
                SUM(MAX_GET_ON)                  AS TOTAL_GET_ON,
                SUM(MAX_GET_OFF)                 AS TOTAL_GET_OFF
            FROM (
                SELECT
                    BJD_CODE,
                    STATION_NAME,
                    MIN(DISTANCE)       AS DISTANCE,
                    MAX(COALESCE(GET_ON,  0)) AS MAX_GET_ON,
                    MAX(COALESCE(GET_OFF, 0)) AS MAX_GET_OFF
                FROM KOREA_REAL_ESTATE_APARTMENT_MARKET_INTELLIGENCE.HACKATHON_2026.APT_DANJI_AND_TRANSPORTATION_TRAIN_DISTANCE
                WHERE SD = '서울'
                GROUP BY BJD_CODE, STATION_NAME
            ) station_agg
            GROUP BY LEFT(BJD_CODE, 8)
        ) t ON v.DISTRICT_CODE = t.DISTRICT_CODE
        WHERE v.CITY_CODE IN ({codes_str})
        ORDER BY v.STANDARD_YEAR_MONTH, v.DISTRICT_CODE
        """
    ).to_pandas()
    return df


@st.cache_data(ttl=3600)
def load_migration_by_city(city_codes: tuple):
    """구별 전입/전출/순이동 월별 추이 (REGION_POPULATION_MOVEMENT, sgg 단위)"""
    session = get_session()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    return session.sql(
        f"""
        SELECT
            TO_CHAR(YYYYMMDD, 'YYYY-MM')  AS STANDARD_YEAR_MONTH,
            LEFT(BJD_CODE, 5)             AS CITY_CODE,
            SGG                           AS CITY_KOR_NAME,
            SUM(CASE WHEN MOVEMENT_TYPE = '전입'  THEN POPULATION ELSE 0 END) AS MOVE_IN,
            SUM(CASE WHEN MOVEMENT_TYPE = '전출'  THEN POPULATION ELSE 0 END) AS MOVE_OUT,
            SUM(CASE WHEN MOVEMENT_TYPE = '순이동' THEN POPULATION ELSE 0 END) AS NET_MOVEMENT
        FROM KOREA_REAL_ESTATE_APARTMENT_MARKET_INTELLIGENCE.HACKATHON_2026.REGION_POPULATION_MOVEMENT
        WHERE REGION_LEVEL = 'sgg'
          AND SD = '서울'
          AND LEFT(BJD_CODE, 5) IN ({codes_str})
        GROUP BY 1, 2, 3
        ORDER BY 2, 1
        """
    ).to_pandas()


@st.cache_data(ttl=3600)
def load_age_population_by_city(city_codes: tuple):
    """구별 연령대 인구 구성 (REGION_MOIS_POPULATION_GENDER_AGE_M_H, emd → sgg 집계)"""
    session = get_session()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    return session.sql(
        f"""
        SELECT
            TO_CHAR(YYYYMMDD, 'YYYY-MM') AS STANDARD_YEAR_MONTH,
            LEFT(BJD_CODE, 5)            AS CITY_CODE,
            SGG                          AS CITY_KOR_NAME,
            SUM(AGE_UNDER20) AS POP_UNDER20,
            SUM(AGE_20S)     AS POP_20S,
            SUM(AGE_30S)     AS POP_30S,
            SUM(AGE_40S)     AS POP_40S,
            SUM(AGE_50S)     AS POP_50S,
            SUM(AGE_60S)     AS POP_60S,
            SUM(AGE_OVER70)  AS POP_OVER70,
            SUM(TOTAL)       AS POP_TOTAL
        FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_GENDER_AGE_M_H
        WHERE SD = '서울'
          AND REGION_LEVEL = 'emd'
          AND LEFT(BJD_CODE, 5) IN ({codes_str})
        GROUP BY 1, 2, 3
        ORDER BY 2, 1
        """
    ).to_pandas()


@st.cache_data(ttl=3600)
def load_apt_price_by_city(city_codes: tuple):
    """구별 아파트 시세 (REGION_APT_RICHGO_MARKET_PRICE_M_H, sgg 단위)"""
    session = get_session()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    return session.sql(
        f"""
        SELECT
            TO_CHAR(YYYYMMDD, 'YYYY-MM')            AS STANDARD_YEAR_MONTH,
            LEFT(BJD_CODE, 5)                       AS CITY_CODE,
            SGG                                     AS CITY_KOR_NAME,
            AVG(MEME_PRICE_PER_SUPPLY_PYEONG)       AS AVG_MEME_PRICE,
            AVG(JEONSE_PRICE_PER_SUPPLY_PYEONG)     AS AVG_JEONSE_PRICE,
            MAX(TOTAL_HOUSEHOLDS)                   AS TOTAL_HOUSEHOLDS
        FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
        WHERE SD = '서울'
          AND REGION_LEVEL = 'sgg'
          AND LEFT(BJD_CODE, 5) IN ({codes_str})
        GROUP BY 1, 2, 3
        ORDER BY 2, 1
        """
    ).to_pandas()


@st.cache_data(ttl=3600)
def load_geo_data(city_codes: tuple):
    session = get_session()
    codes_str = ", ".join(f"'{c}'" for c in city_codes)
    geo_df = session.sql(
        f"""
        SELECT
            DISTRICT_KOR_NAME, DISTRICT_CODE, CITY_CODE,
            ST_ASGEOJSON(DISTRICT_GEOM) AS GEOJSON,
            ST_X(ST_CENTROID(DISTRICT_GEOM)) AS CENTER_LON,
            ST_Y(ST_CENTROID(DISTRICT_GEOM)) AS CENTER_LAT
        FROM SPH_DATA.GRANDATA.M_SCCO_MST
        WHERE CITY_CODE IN ({codes_str})
        """
    ).to_pandas()
    return geo_df
