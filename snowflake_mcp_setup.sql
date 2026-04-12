-- ═══════════════════════════════════════════════════════════════════════════════
-- Urban Vitality — Snowflake Managed MCP Server
-- Snowflake Worksheet에 통째로 붙여넣고 "Run All" 하면 됩니다.
-- ═══════════════════════════════════════════════════════════════════════════════

USE DATABASE SPH_DATA;
USE SCHEMA GRANDATA;
USE WAREHOUSE COMPUTE_WH;


-- ─── 1. 업종 분류 UDF ────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION SPH_DATA.GRANDATA.CLASSIFY_BUSINESS(business_type VARCHAR)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
HANDLER = 'classify'
AS $$
def classify(business_type: str) -> str:
    m = [
        ("치킨","FOOD_SALES"),("고기","FOOD_SALES"),("삼겹살","FOOD_SALES"),
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
        ("꽃","SMALL_RETAIL_SALES"),
    ]
    for kw, cat in m:
        if kw in business_type:
            return cat
    return "FOOD_SALES"
$$;


-- ─── 2. 창업 입지 보고서 프로시저 ────────────────────────────────────────────
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
        if r["pc"]>=70: st.append(f"{lb} 매출 상위권 (백분위 {r['pc']:.0f})")
        if r["pv"]>=70: st.append(f"높은 유동인구 (백분위 {r['pv']:.0f})")
        if r["pi"]>=70: st.append(f"높은 소득 수준 (백분위 {r['pi']:.0f})")
        if r["pp"]>=70: st.append(f"풍부한 거주인구 (백분위 {r['pp']:.0f})")
        if r["MOM_CHANGE_PCT"]>0: st.append(f"성장세 (+{r['MOM_CHANGE_PCT']:.1f}%)")
        if r["pv"]<30: ca.append("유동인구 적음")
        if r["pi"]<30: ca.append("소득 수준 낮음")
        if r["MOM_CHANGE_PCT"]<-2: ca.append(f"활력 하락 ({r['MOM_CHANGE_PCT']:.1f}%)")
        if r["pd"]<30: ca.append("소비 다양성 낮음")
        L.append(f"## {i+1}위: {r['CITY_KOR_NAME']} {r['DISTRICT_KOR_NAME']}")
        L.append(f"**종합 점수: {r['TS']:.1f}점**\n")
        L.append(f"- 활력지수: {r['VITALITY_INDEX']:.1f}")
        L.append(f"- {lb} 매출 백분위: {r['pc']:.0f}")
        L.append(f"- 방문인구: {r['TOTAL_VISITING']:,.0f}명")
        L.append(f"- 총 카드매출: {r['TOTAL_CARD_SALES']:,.0f}원")
        L.append(f"- 전월 대비: {r['MOM_CHANGE_PCT']:+.1f}%\n")
        if st: L.append(f"**강점:** {' / '.join(st)}\n")
        if ca: L.append(f"**주의:** {' / '.join(ca)}\n")
    b=t5.iloc[0]
    L.append("---")
    L.append(f"## 최종 추천: {b['CITY_KOR_NAME']} {b['DISTRICT_KOR_NAME']}")
    L.append(f"{b['CITY_KOR_NAME']} {b['DISTRICT_KOR_NAME']}은(는) {lb} 매출 백분위 {b['pc']:.0f}, 방문인구 백분위 {b['pv']:.0f}으로 **{business_type}** 창업에 가장 유리한 입지로 분석됩니다.")
    L.append("\n\n---\n## 상위 10개 지역 요약\n")
    L.append("| 순위 | 지역 | 종합점수 | 업종매출 | 유동인구 | 소득수준 | 활력지수 |")
    L.append("|------|------|----------|----------|----------|----------|----------|")
    for i,r in t10.iterrows():
        L.append(f"| {i+1} | {r['CITY_KOR_NAME']} {r['DISTRICT_KOR_NAME']} | {r['TS']:.1f} | {r['pc']:.0f} | {r['pv']:.0f} | {r['pi']:.0f} | {r['VITALITY_INDEX']:.1f} |")
    L.append(f"\n> 기준월: {latest} | 카테고리: {lb} | 서울 {len(df)}개 법정동")
    return "\n".join(L)
$$;


-- ─── 3. 백테스트 프로시저 ────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE SPH_DATA.GRANDATA.STARTUP_BACKTEST(business_type VARCHAR, eval_months INT)
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

def _score(df, col):
    df=df.copy(); n=len(df)
    if n==0: return df
    w=W.get(col,W["FOOD_SALES"])
    df["MOM_CHANGE_PCT"]=df["MOM_CHANGE_PCT"].fillna(0)
    df["pc"]=df[col].rank(method="average")/n*100
    df["pv"]=df["SCORE_VISITING"].rank(method="average")/n*100
    df["pi"]=df["SCORE_INCOME"].rank(method="average")/n*100
    df["pp"]=df["SCORE_POPULATION"].rank(method="average")/n*100
    df["pd_"]=df["SCORE_DIVERSITY"].rank(method="average")/n*100
    df["pg"]=df["MOM_CHANGE_PCT"].rank(method="average")/n*100
    df["TS"]=(df["pc"]*w["c"]+df["pv"]*w["v"]+df["pi"]*w["i"]+df["pp"]*w["p"]+df["pg"]*w["g"]+df["pd_"]*w["d"]).round(1)
    df["LB"]=df["CITY_KOR_NAME"]+" "+df["DISTRICT_KOR_NAME"]
    return df.sort_values("TS",ascending=False).reset_index(drop=True)

def main(session, business_type, eval_months):
    if eval_months not in (1,2,3,6): eval_months=3
    col=_cls(business_type); lb=CL.get(col,"음식")
    df_all=session.sql("""
        SELECT CITY_KOR_NAME,DISTRICT_KOR_NAME,CITY_CODE,DISTRICT_CODE,
               STANDARD_YEAR_MONTH,VITALITY_INDEX,MOM_CHANGE_PCT,
               SCORE_POPULATION,SCORE_VISITING,SCORE_CONSUMPTION,
               SCORE_DIVERSITY,SCORE_INCOME,SCORE_CREDIT,
               TOTAL_POPULATION,TOTAL_VISITING,TOTAL_CARD_SALES,
               FOOD_SALES,COFFEE_SALES,ENTERTAINMENT_SALES,
               SMALL_RETAIL_SALES,FASHION_SALES,LEISURE_SALES
        FROM SPH_DATA.GRANDATA.V_VITALITY_FINAL
        ORDER BY STANDARD_YEAR_MONTH,DISTRICT_CODE
    """).to_pandas()
    if df_all.empty: return "데이터가 없습니다."
    months=sorted(df_all["STANDARD_YEAR_MONTH"].unique())
    if len(months)<eval_months+2: return "데이터 기간이 부족합니다."

    res=[]
    for i in range(len(months)-eval_months):
        bm=months[i]; fm=months[i+1:i+1+eval_months]
        if not fm: continue
        db=df_all[df_all["STANDARD_YEAR_MONTH"]==bm].copy()
        if db.empty or len(db)<5: continue
        sc=_score(db,col)
        tc=sc.head(5)["DISTRICT_CODE"].tolist()
        tl=sc.head(5)["LB"].tolist()
        ac=sc["DISTRICT_CODE"].tolist()
        bs=db.set_index("DISTRICT_CODE")[col]
        df=df_all[(df_all["STANDARD_YEAR_MONTH"].isin(fm))&(df_all["DISTRICT_CODE"].isin(ac))]
        if df.empty: continue
        fa=df.groupby("DISTRICT_CODE")[col].mean()
        cm=bs.index.intersection(fa.index)
        if len(cm)<5: continue
        bc=bs.loc[cm].replace(0,np.nan)
        gr=((fa.loc[cm]-bc)/bc*100).dropna()
        if gr.empty: continue
        md=gr.median()
        ri=[c for c in tc if c in gr.index]
        if not ri: continue
        rg=gr.loc[ri]; h=int((rg>md).sum())
        res.append({"bm":bm,"ee":fm[-1],"ar":round(float(rg.mean()),2),
            "aa":round(float(gr.mean()),2),"h":h,"t":len(ri),
            "hr":round(h/len(ri)*100,1),
            "al":round(float(rg.mean())-float(gr.mean()),2),"lb":tl[:len(ri)]})

    if not res: return "백테스트 데이터 부족."
    th=sum(r["h"] for r in res); tr=sum(r["t"] for r in res)
    oh=th/tr*100; aa=sum(r["al"] for r in res)/len(res)
    wp=sum(1 for r in res if r["ar"]>r["aa"]); wr=wp/len(res)*100
    cf="높음" if oh>=65 else ("보통" if oh>=50 else "낮음")

    L=[f"# {business_type} 추천 모델 백테스트 결과\n",
       f"> 카테고리: {lb} | 평가: {eval_months}개월 | {len(res)}개 시점\n",
       "## 핵심 지표\n",
       f"- **전체 적중률**: {oh:.1f}%",
       f"- **평균 Alpha**: {aa:+.2f}%p",
       f"- **기간 승률**: {wr:.0f}% ({wp}/{len(res)})",
       f"- **신뢰도**: {cf}\n",
       "## 기간별 상세\n",
       "| 추천시점 | 평가종료 | 추천성장률 | 전체성장률 | Alpha | 적중 | 적중률 |",
       "|----------|----------|-----------|-----------|-------|------|--------|"]
    for r in res:
        L.append(f"| {r['bm']} | {r['ee']} | {r['ar']:+.2f}% | {r['aa']:+.2f}% | {r['al']:+.2f}%p | {r['h']}/{r['t']} | {r['hr']:.0f}% |")
    lt=res[-1]
    L.append(f"\n## 최근 백테스트 ({lt['bm']})\n")
    for i,x in enumerate(lt["lb"]): L.append(f"- {i+1}. {x}")
    L.append("\n## 결론\n")
    if oh>=55: L.append(f"**{business_type}** 모델은 적중률 {oh:.1f}%, Alpha {aa:+.2f}%p로 유의미합니다.")
    elif oh>=45: L.append(f"**{business_type}** 모델은 적중률 {oh:.1f}%로 랜덤 수준입니다.")
    else: L.append(f"**{business_type}** 모델은 적중률 {oh:.1f}%로 기대 미달입니다.")
    return "\n".join(L)
$$;


-- ─── 4. 업종 목록 함수 ──────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION SPH_DATA.GRANDATA.LIST_BUSINESS_TYPES()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
SELECT '# 지원 업종 목록

## 음식: 치킨, 고기, 삼겹살, 음식, 식당, 분식, 피자, 국밥, 돈까스, 떡볶이, 초밥, 중식, 한식, 양식, 일식, 족발, 보쌈, 곱창
## 커피: 카페, 커피, 디저트, 베이커리, 빵, 케이크
## 여가: 헬스, 필라테스, 요가, 수영, 스포츠, 당구, 볼링, 짐, 피트니스
## 엔터테인먼트: 노래방, PC방, 게임, 오락, 방탈출
## 패션: 옷, 패션, 의류, 신발, 액세서리, 미용, 네일, 헤어, 뷰티
## 소매: 편의점, 마트, 소매, 약국, 세탁, 문구, 꽃

키워드가 업종명에 포함되면 자동 매핑됩니다. 매핑 안 되면 음식으로 분석합니다.'
$$;


-- ─── 5. MCP Server 생성 ─────────────────────────────────────────────────────
CREATE OR REPLACE MCP SERVER SPH_DATA.GRANDATA.URBAN_VITALITY_MCP
  FROM SPECIFICATION $$
tools:
  - name: startup_report
    title: 창업 입지 보고서
    type: GENERIC
    identifier: SPH_DATA.GRANDATA.STARTUP_REPORT
    description: >
      서울시 자영업 창업 최적 입지를 분석합니다.
      업종을 입력하면 유동인구, 소비, 소득, 성장세를 종합 분석하여
      Top 5 동네를 추천하는 보고서를 생성합니다.
      예시: 치킨집, 카페, 헬스장, 편의점, 노래방, 미용실
    config:
      type: procedure
      warehouse: COMPUTE_WH
      input_schema:
        type: object
        properties:
          business_type:
            type: string
            description: 창업하고 싶은 업종 (예 치킨집, 카페, 헬스장)
        required:
          - business_type

  - name: startup_backtest
    title: 추천 모델 백테스트
    type: GENERIC
    identifier: SPH_DATA.GRANDATA.STARTUP_BACKTEST
    description: >
      창업 추천 모델의 과거 적중률을 백테스팅으로 검증합니다.
      추천 지역이 실제로 더 좋은 매출 성장을 보였는지 확인합니다.
    config:
      type: procedure
      warehouse: COMPUTE_WH
      input_schema:
        type: object
        properties:
          business_type:
            type: string
            description: 백테스트할 업종 (예 치킨집, 카페)
          eval_months:
            type: integer
            description: 추천 후 성과 측정 기간 (1, 2, 3, 6). 기본값 3.
            default: 3
        required:
          - business_type

  - name: list_business_types
    title: 지원 업종 목록
    type: GENERIC
    identifier: SPH_DATA.GRANDATA.LIST_BUSINESS_TYPES
    description: 분석 가능한 업종 목록과 카테고리 매핑을 보여줍니다.
    config:
      type: function
      warehouse: COMPUTE_WH
      input_schema:
        type: object
        properties: {}
$$;


-- ─── 6. 확인 ────────────────────────────────────────────────────────────────
SHOW MCP SERVERS IN SCHEMA SPH_DATA.GRANDATA;
DESCRIBE MCP SERVER SPH_DATA.GRANDATA.URBAN_VITALITY_MCP;


-- ─── 7. (선택) 개별 테스트 ──────────────────────────────────────────────────
-- CALL SPH_DATA.GRANDATA.STARTUP_REPORT('치킨집');
-- CALL SPH_DATA.GRANDATA.STARTUP_BACKTEST('카페', 3);
-- SELECT SPH_DATA.GRANDATA.LIST_BUSINESS_TYPES();
