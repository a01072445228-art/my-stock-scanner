import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. 설정 최상단 배치
st.set_page_config(page_title="급등주 TOP 10", layout="wide")

# 2. 자동 새로고침 (60초 주기)
st_autorefresh(interval=60000, key="datarefresh")

st.title("🚀 미국장 실시간 급등주 스캐너")

# 사이드바 필터 설정
st.sidebar.header("🔍 상세 필터 설정")

price_range = st.sidebar.slider(
    "가격 범위 설정 ($)", 
    0.0, 500.0, (1.0, 50.0), step=0.5
)
min_p, max_p = price_range

volume_options = {"Over 100K": "Over 100K", "Over 500K": "Over 500K", "Over 1M": "Over 1M"}
selected_vol = st.sidebar.selectbox("최소 거래량", options=list(volume_options.keys()), index=1)
min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 10)

@st.cache_data(ttl=55)
def get_custom_data(v_str, m_chg, p_min, p_max):
    try:
        foverview = Overview()
        # Finviz 자체 필터를 사용하여 서버 부하와 데이터 전송량 감소
        # 'Price': 'Under 50' 같은 방식 대신 Pandas 필터링 유지하되, 
        # 기본적인 거래량 조건은 서버 필터 활용
        foverview.set_filter(filters_dict={'Current Volume': v_str})
        df = foverview.screener_view(order='Change') 

        if df is not None and not df.empty:
            # 숫자 데이터 변환 (에러 방지용)
            df['Price'] = pd.to_numeric(df, errors='coerce')
            df['Change_Num'] = pd.to_numeric(df['Change'].str.replace('%', '', regex=False), errors='coerce')
            
            # 사용자 설정 필터링
            filtered_df = df[
                (df['Price'] >= p_min) & 
                (df['Price'] <= p_max) & 
                (df['Change_Num'] >= m_chg)
            ].copy()
            
            return filtered_df.sort_values(by='Change_Num', ascending=False).head(10)
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

# 실행부
with st.spinner(f'${min_p} ~ ${max_p} 종목 분석 중...'):
    res_df = get_custom_data(volume_options[selected_vol], min_change, min_p, max_p)

    if res_df is not None and not res_df.empty:
        st.success(f"🔥 {min_p}$ ~ {max_p}$ 범위 내 급등 TOP {len(res_df)}")
        
        # 가독성을 위한 열 선택 및 스타일링
        display_cols = ['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']
        st.dataframe(res_df[display_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("현재 조건에 맞는 종목이 없습니다. 필터를 조정해보세요.")

st.divider()
st.caption(f"💡 1분마다 자동 갱신됩니다. (현재 설정: {min_p}$ ~ {max_p}$ | {selected_vol})")








