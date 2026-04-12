-- STARTUP_REPORT 표시 형식 수정: 백분위 → 상위 X%
-- Snowflake Worksheet에 붙여넣고 실행

USE DATABASE SPH_DATA;
USE SCHEMA GRANDATA;
USE WAREHOUSE COMPUTE_WH;

CREATE OR REPLACE PROCEDURE SPH_DATA.GRANDATA.STARTUP_REPORT(business_type VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pandas', 'numpy')
HANDLER = 'main'
AS $$
import numpy as np, pandas as pd

CL = {"FOOD_SALES":"음식","COFFEE_SALES":"커피","LEISURE_SALES":"여가",
      "ENTERTAINMENT_SALES":"엔터테인먼트","FASHION_SALES":"패션","SMALL_RETAIL_SALES":"소매"}
W = {"FOOD_SALES":{"c":.30,"v":.25,"i":.15,"p":.15,"g":.10,"d":.05},
     "COFFEE_SALES":{"c":.25,"v":.30,"i":.15,"p":.10,"g":.15,"d":.05},
     "LEISURE_SALES":{"c":.30,"v":.15,"i":.20,"p":.20,"g":.10,"d":.05},
     "ENTERTAINMENT_SALES":{"c":.30,"v":.25,"i":.10,"p":.20,"g":.10,"d":.05},
     "FASHION_SALES":{"c":.25,"v":.30,"i":.20,"p":.10,"g":.10,"d":.05},
     "SMALL_RETAIL_SALES":{"c":.30,"v":.15,"i":.10,"p":.30,"g":.10,"d":.05}}
KW = [("치킨","FOOD_SALES"),("고기","FOOD_SALES"),("삼겹살","FOOD_SALES"),
      ("음식","FOOD_SALES"),("식당","FOOD_SALES"),("분식","FOOD_SALES"),
      ("피자","FOOD_SALES"),("국밥","FOOD_SALES"),("돈까스","FOOD_SALES"),
      ("떡볶이","FOOD_SALES"),("초밥","FOOD_SALES"),("중식","FOOD_SALES"),
      ("한식","FOOD_SALES"),("양식","FOOD_SALES"),("일식","FOOD_SALES"),
      ("족발","FOOD_SALES"),("보쌈","FOOD_SALES"),("곱창","FOOD_SALES"),
      ("해장","FOOD_SALES"),("밥","FOOD_SALES"),
      ("카페","COFFEE_SALES"),("커피","COFFEE_SALES"),("디저트","COFFEE_SALES"),
      ("베이커리","COFFEE_SALES"),("빵","COFFEE_SALES"),("케이크","COFFEE_SALES"),
      ("헬스","LEISURE_SALES"),("필라테스","LEISURE_SALES"),("요가","LEISURE_SALES"),
      ("수영","LEISURE_SALES"),("스포츠","LEISURE_SALES"),("당구","LEISURE_SALES"),
      ("볼링","LEISURE_SALES"),("짐","LEISURE_SALES"),("피트니스","LEISURE_SALES"),
      ("노래방","ENTERTAINMENT_SALES"),("PC방","ENTERTAINMENT_SALES"),
      ("게임","ENTERTAINMENT_SALES"),("오락","ENTERTAINMENT_SALES"),("방탈출","ENTERTAINMENT_SALES"),
      ("옷","FASHION_SALES"),("패션","FASHION_SALES"),("의류","FASHION_SALES"),
      ("신발","FASHION_SALES"),("액세서리","FASHION_SALES"),("미용","FASHION_SALES"),
      ("네일","FASHION_SALES"),("헤어","FASHION_SALES"),("뷰티","FASHION_SALES"),
      ("편의점","SMALL_RETAIL_SALES"),("마트","SMALL_RETAIL_SALES"),("소매","SMALL_RETAIL_SALES"),
      ("약국","SMALL_RETAIL_SALES"),("세탁","SMALL_RETAIL_SALES"),("문구","SMALL_RETAIL_SALES"),
      ("꽃","SMALL_RETAIL_SALES")]

def _cls(b):
    for k,c in KW:
        if k in b: return c
    return "FOOD_SALES"

def _top(pct):
    """백분위 → 상위 X% 변환. 백분위 84 → 상위 16%"""
    v = max(1, round(100 - pct))
    return f"상위 {v}%"

def _score(df, col):
    df=df.copy(); n=len(df)
    if n==0: return df
    w=W.get(col,W["FOOD_SALES"])
    df["MOM_CHANGE_PCT"]=df["MOM_CHANGE_PCT"].fillna(0)
    df["pc"]=df[col].rank(method="average")/n*100
    df["pv"]=df["SCORE_VISITING"].rank(method="average")/n*100
    df["pi"]=df["SCORE_INCOME"].rank(method="average")/n*100
    df["pp"]=df["SCORE_POPULATION"].rank(method="average")/n*100
    df["pd"]=df["SCORE_DIVERSITY"].rank(method="average")/n*100
    df["pg"]=df["MOM_CHANGE_PCT"].rank(method="average")/n*100
    df["TS"]=(df["pc"]*w["c"]+df["pv"]*w["v"]+df["pi"]*w["i"]+df["pp"]*w["p"]+df["pg"]*w["g"]+df["pd"]*w["d"]).round(1)
    df["LB"]=df["CITY_KOR_NAME"]+" "+df["DISTRICT_KOR_NAME"]
    return df.sort_values("TS",ascending=False).reset_index(drop=True)

def main(session, business_type):
    col=_cls(business_type); lb=CL.get(col,"음식")
    df_all=session.sql("""
        SELECT CITY_KOR_NAME,DISTRICT_KOR_NAME,CITY_CODE,DISTRICT_CODE,
               STANDARD_YEAR_MONTH,VITALITY_INDEX,MOM_CHANGE_PCT,
               SCORE_POPULATION,SCORE_VISITING,SCORE_CONSUMPTION,
               SCORE_DIVERSITY,SCORE_INCOME,SCORE_CREDIT,
               TOTAL_POPULATION,TOTAL_VISITING,TOTAL_CARD_SALES,
               CONSUMPTION_DIVERSITY,AVG_INCOME,AVG_CREDIT_SCORE,
               FOOD_SALES,COFFEE_SALES,ENTERTAINMENT_SALES,
               SMALL_RETAIL_SALES,FASHION_SALES,LEISURE_SALES
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL
        ORDER BY STANDARD_YEAR_MONTH,DISTRICT_CODE
    """).to_pandas()
    if df_all.empty: return "데이터가 없습니다."
    latest=df_all["STANDARD_YEAR_MONTH"].max()
    df=df_all[df_all["STANDARD_YEAR_MONTH"]==latest].copy()
    sc=_score(df,col); t5=sc.head(5); t10=sc.head(10)

    L=[f"# {business_type} 창업 추천 보고서\n",
       f"> 분석 기준: {lb} 매출, 유동인구, 소득 수준, 성장세, 소비 다양성\n"]
    for i,r in t5.iterrows():
        st,ca=[],[]
        if r["pc"]>=70: st.append(f"{lb} 매출 {_top(r['pc'])}")
        if r["pv"]>=70: st.append(f"유동인구 {_top(r['pv'])}")
        if r["pi"]>=70: st.append(f"소득 수준 {_top(r['pi'])}")
        if r["pp"]>=70: st.append(f"거주인구 {_top(r['pp'])}")
        if r["MOM_CHANGE_PCT"]>0: st.append(f"성장세 (+{r['MOM_CHANGE_PCT']:.1f}%)")
        if r["pv"]<30: ca.append("유동인구 적음")
        if r["pi"]<30: ca.append("소득 수준 낮음")
        if r["MOM_CHANGE_PCT"]<-2: ca.append(f"활력 하락 ({r['MOM_CHANGE_PCT']:.1f}%)")
        if r["pd"]<30: ca.append("소비 다양성 낮음")
        L.append(f"## {i+1}위: {r['CITY_KOR_NAME']} {r['DISTRICT_KOR_NAME']}")
        L.append(f"**종합 점수: {r['TS']:.1f}점**\n")
        L.append(f"- 활력지수: {r['VITALITY_INDEX']:.1f}")
        L.append(f"- {lb} 매출: {_top(r['pc'])}")
        L.append(f"- 유동인구: {_top(r['pv'])} ({r['TOTAL_VISITING']:,.0f}명)")
        L.append(f"- 소득수준: {_top(r['pi'])}")
        L.append(f"- 총 카드매출: {r['TOTAL_CARD_SALES']:,.0f}원")
        L.append(f"- 전월 대비: {r['MOM_CHANGE_PCT']:+.1f}%\n")
        if st: L.append(f"**강점:** {' / '.join(st)}\n")
        if ca: L.append(f"**주의:** {' / '.join(ca)}\n")
    b=t5.iloc[0]
    L.append("---")
    L.append(f"## 최종 추천: {b['CITY_KOR_NAME']} {b['DISTRICT_KOR_NAME']}")
    L.append(f"{b['CITY_KOR_NAME']} {b['DISTRICT_KOR_NAME']}은(는) {lb} 매출 {_top(b['pc'])}, 유동인구 {_top(b['pv'])}으로 **{business_type}** 창업에 가장 유리한 입지로 분석됩니다.")
    L.append("\n\n---\n## 상위 10개 지역 요약\n")
    L.append("| 순위 | 지역 | 종합점수 | 업종매출 | 유동인구 | 소득수준 | 활력지수 |")
    L.append("|------|------|----------|----------|----------|----------|----------|")
    for i,r in t10.iterrows():
        L.append(f"| {i+1} | {r['CITY_KOR_NAME']} {r['DISTRICT_KOR_NAME']} | {r['TS']:.1f} | {_top(r['pc'])} | {_top(r['pv'])} | {_top(r['pi'])} | {r['VITALITY_INDEX']:.1f} |")
    L.append(f"\n> 기준월: {latest} | 카테고리: {lb} | 서울 {len(df)}개 법정동")
    return "\n".join(L)
$$;
