import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. 자동 새로고침 (60초 주기)
st_autorefresh(interval=60000, key="datarefresh")

st.set_page_config(page_title="급등주 TOP 10", layout="wide")
st.title("🚀 미국장 실시간 급등주 스캐너")

# 사이드바 필터 설정
st.sidebar.header("🔍 상세 필터 설정")

# [수정] 가격 범위 직접 설정 (슬라이더 또는 입력창)
price_range = st.sidebar.slider(
    "가격 범위 설정 ($)", 
    0.0, 500.0, (1.0, 50.0), step=0.5
)
min_p, max_p = price_range

# 거래량 필터 (서버 부하 감소용)
volume_options = {"Over 100K": "Over 100K", "Over 500K": "Over 500K", "Over 1M": "Over 1M"}
selected_vol = st.sidebar.selectbox("최소 거래량", options=list(volume_options.keys()), index=1)

# 상승률 필터
min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 10)

@st.cache_data(ttl=55)
def get_custom_data(v_str, m_chg, p_min, p_max):
    try:
        foverview = Overview()
        # 1차 필터링: 서버에서는 거래량 위주로 먼저 가져옴
        foverview.set_filter(filters_dict={'Current Volume': v_str})
        df = foverview.screener_view(order='Change') 

        if df is not None and not df.empty:
            # 데이터 숫자 변환
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['Change_Num'] = pd.to_numeric(df['Change'].str.replace('%', ''), errors='coerce')
            
            # [핵심] 사용자가 설정한 가격 범위 및 상승률로 정밀 필터링
            filtered_df = df[
                (df['Price'] >= p_min) & 
                (df['Price'] <= p_max) & 
                (df['Change_Num'] >= m_chg)
            ]
            
            # 상위 10개 추출
            return filtered_df.sort_values(by='Change_Num', ascending=False).head(10)
    except:
        return None
    return None

# 실행
with st.spinner(f'${min_p} ~ ${max_p} 범위 종목 분석 중...'):
    res_df = get_custom_data(volume_options[selected_vol], min_change, min_p, max_p)

    if res_df is not None and not res_df.empty:
        st.success(f"🔥 {min_p}$~{max_p}$ 범위 내 급등 TOP {len(res_df)}")
        
        display_cols = ['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']
        st.table(res_df[display_cols].reset_index(drop=True))
    else:
        st.warning("설정한 가격 범위 내에 조건에 맞는 종목이 없습니다.")

st.divider()
st.caption(f"현재 설정: {min_p}$ 이상 ~ {max_p}$ 이하 | 1분마다 자동 업데이트")







