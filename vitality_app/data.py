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
