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

# [변경] 슬라이더 대신 직접 숫자 입력(Number Input) 사용
st.sidebar.subheader("가격 범위 ($)")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_p = st.number_input("최소 가격", min_value=0.0, max_value=2000.0, value=1.0, step=0.5)
with col2:
    max_p = st.number_input("최대 가격", min_value=0.0, max_value=2000.0, value=50.0, step=0.5)

# 거래량 및 상승률 설정
volume_options = {"Over 100K": "Over 100K", "Over 500K": "Over 500K", "Over 1M": "Over 1M"}
selected_vol = st.sidebar.selectbox("최소 거래량", options=list(volume_options.keys()), index=1)
min_change = st.sidebar.number_input("최소 상승률 (%)", min_value=0, max_value=100, value=10, step=1)

@st.cache_data(ttl=55)
def get_custom_data(v_str, m_chg, p_min, p_max):
    try:
        foverview = Overview()
        # 기본적인 거래량 필터 적용
        foverview.set_filter(filters_dict={'Current Volume': v_str})
        df = foverview.screener_view(order='Change') 

        if df is not None and not df.empty:
            # 숫자 데이터로 변환
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            df['Change_Num'] = pd.to_numeric(df['Change'].str.replace('%', '', regex=False), errors='coerce')
            
            # 입력된 가격/상승률로 필터링
            filtered_df = df[
                (df['Price'] >= p_min) & 
                (df['Price'] <= p_max) & 
                (df['Change_Num'] >= m_chg)
            ].copy()
            
            return filtered_df.sort_values(by='Change_Num', ascending=False).head(10)
    except Exception as e:
        return None
    return None

# 실행부
with st.spinner('데이터를 분석 중입니다...'):
    res_df = get_custom_data(volume_options[selected_vol], min_change, min_p, max_p)

    if res_df is not None and not res_df.empty:
        st.success(f"🔥 {min_p}$ ~ {max_p}$ 범위 내 급등 TOP {len(res_df)}")
        
        display_cols = ['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']
        # 표를 더 깔끔하게 보기 위해 데이터프레임 사용
        st.dataframe(
            res_df[display_cols].reset_index(drop=True), 
            use_container_width=True,
            column_config={
                "Price": st.column_config.Number_Column(format="$%.2f"),
                "Change": st.column_config.Text_Column("상승률")
            }
        )
    else:
        st.warning(f"{min_p}$ ~ {max_p}$ 조건에 맞는 종목이 없습니다. 가격이나 상승률을 낮춰보세요.")

st.divider()
st.caption(f"💡 현재 기준: {min_p}$ ~ {max_p}$ | {selected_vol} 이상 | {min_change}% 상승")









