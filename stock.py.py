import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="실시간 급등주 TOP 10", layout="wide")

# 1. 자동 새로고침 설정 (1분마다 실행)
# 60 * 1000ms = 60초
count = st_autorefresh(interval=60000, key="fscannercounter")

st.title("🚀 실시간 미국장 급등주 TOP 10")
st.caption(f"🔄 1분마다 자동 갱신 중... (현재 갱신 횟수: {count})")

# 2. 데이터 로딩 함수 (캐싱 적용으로 속도 극대화)
@st.cache_data(ttl=55) # 자동 새로고침 주기보다 살짝 짧게 설정
def get_top_10_movers(price_str, vol_str, min_chg):
    try:
        foverview = Overview()
        # [핵심] 서버에 필터와 정렬을 동시에 전달하여 전송 데이터 최소화
        filters_dict = {'Price': price_str, 'Current Volume': vol_str}
        foverview.set_filter(filters_dict=filters_dict)
        
        # 상승률순으로 정렬된 전체 데이터를 가져옴
        df = foverview.screener_view(order='Change')
        
        if df is not None and not df.empty:
            # 숫자 변환 및 필터링
            df['Change_Num'] = pd.to_numeric(df['Change'].str.replace('%', ''), errors='coerce')
            result = df[df['Change_Num'] >= min_chg]
            
            # 최종 상위 10개만 리턴
            return result.sort_values(by='Change_Num', ascending=False).head(10)
        return None
    except:
        return None

# 사이드바 설정
st.sidebar.header("⚙️ 필터 고정")
price_options = {1.0: "Over $1", 5.0: "Over $5", 10.0: "Over $10"}
selected_price = st.sidebar.selectbox("최소 가격 ($)", options=list(price_options.keys()), index=1)

volume_options = {"Over 500K": "Over 500K", "Over 1M": "Over 1M"}
selected_vol = st.sidebar.selectbox("최소 거래량", options=list(volume_options.keys()), index=0)

min_change = st.sidebar.slider("최소 상승률 (%)", 5, 50, 10)

# 3. 메인 로직 실행
with st.spinner('최신 급등주 데이터 로딩 중...'):
    top_10_df = get_top_10_movers(price_options[selected_price], volume_options[selected_vol], min_change)

    if top_10_df is not None and not top_10_df.empty:
        # 가독성을 위한 메트릭 표시
        col1, col2 = st.columns(2)
        col1.metric("현재 1위", top_10_df.iloc[0]['Ticker'], f"{top_10_df.iloc[0]['Change']}")
        col2.metric("TOP 10 평균 상승률", f"{top_10_df['Change_Num'].mean():.2f}%")
        
        # 테이블 출력 (Index 제외하고 깔끔하게)
        display_cols = ['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']
        st.table(top_10_df[display_cols].reset_index(drop=True))
    else:
        st.info("현재 조건에 맞는 급등 종목이 없습니다. 시장이 열려 있는지 확인하세요.")

st.divider()
st.caption("제공: Finviz (15분 지연) | 자동으로 데이터를 새로고침하므로 버튼을 누를 필요가 없습니다.")



