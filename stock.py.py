import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. 자동 새로고침 (60초 주기)
st_autorefresh(interval=60000, key="datarefresh")

st.set_page_config(page_title="급등주 TOP 10", layout="wide")
st.title("🚀 미국장 급등주 TOP 10 스캐너")

# 사이드바 필터
st.sidebar.header("🔍 필터 설정")
price_options = {1.0: "Over $1", 5.0: "Over $5", 10.0: "Over $10", 20.0: "Over $20"}
selected_price = st.sidebar.selectbox("최소 가격 ($)", options=list(price_options.keys()), index=1)

volume_options = {"Over 500K": "Over 500K", "Over 1M": "Over 1M", "Over 2M": "Over 2M"}
selected_vol = st.sidebar.selectbox("최소 거래량", options=list(volume_options.keys()), index=0)

min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 10)

# 데이터 로딩 함수 (캐싱으로 속도 개선)
@st.cache_data(ttl=55)
def get_top_10(p_str, v_str, m_chg):
    try:
        foverview = Overview()
        # 서버 단계에서 필터링하여 데이터 양 축소
        foverview.set_filter(filters_dict={'Price': p_str, 'Current Volume': v_str})
        # 상승률순 정렬 요청
        df = foverview.screener_view(order='Change') 

        if df is not None and not df.empty:
            df['Change_Num'] = pd.to_numeric(df['Change'].str.replace('%', ''), errors='coerce')
            # 설정한 상승률 이상만 필터링 후 상위 10개 고정
            result = df[df['Change_Num'] >= m_chg].sort_values(by='Change_Num', ascending=False).head(10)
            return result
    except:
        return None
    return None

# 실행 및 출력
with st.spinner('상위 10개 종목 분석 중...'):
    res_df = get_top_10(price_options[selected_price], volume_options[selected_vol], min_change)

    if res_df is not None and not res_df.empty:
        st.success(f"🔥 실시간 급등 TOP {len(res_df)} (1분마다 자동 갱신)")
        
        # 핵심 컬럼만 추출하여 깔끔하게 표시
        display_cols = ['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']
        st.table(res_df[display_cols].reset_index(drop=True))
    else:
        st.warning("조건에 맞는 급등 종목이 없거나 데이터를 불러오는 중입니다.")

st.divider()
st.caption("Data: Finviz (15m delay) | 상위 10위 종목만 표시됩니다.")





