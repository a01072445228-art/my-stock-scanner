import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd

st.set_page_config(page_title="급등주 TOP 10 스캐너", layout="wide")
st.title("🚀 미국장 급등주 TOP 10 스캐너")

# 사이드바 설정
st.sidebar.header("🔍 필터 설정")

# 1. 가격 필터
price_options = {1.0: "Over $1", 5.0: "Over $5", 10.0: "Over $10", 20.0: "Over $20"}
selected_price = st.sidebar.selectbox("최소 가격 ($)", options=list(price_options.keys()), index=1)

# 2. 거래량 필터 (추가)
# Finviz 라이브러리 규격에 맞는 옵션들입니다.
volume_options = {
    "Any": "Any",
    "Over 100K": "Over 100K",
    "Over 500K": "Over 500K",
    "Over 1M": "Over 1M",
    "Over 2M": "Over 2M"
}
selected_vol = st.sidebar.selectbox("최소 거래량", options=list(volume_options.keys()), index=2) # 기본 500K

# 3. 상승률 필터
min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 15)

if st.button("지금 급등주 찾기"):
    with st.spinner('Finviz 서버에서 상위 종목 분석 중...'):
        try:
            foverview = Overview()
            
            # 필터 딕셔너리 구성
            filters_dict = {
                'Price': price_options[selected_price],
                'Current Volume': volume_options[selected_vol]
            }
            
            foverview.set_filter(filters_dict=filters_dict)
            
            # 상승률(Change) 순으로 정렬하여 데이터 호출
            df = foverview.screener_view(order='Change') 

            if df is not None and not df.empty:
                # 'Change' 컬럼 숫자 변환 (% 제거)
                df['Change_Num'] = pd.to_numeric(df['Change'].str.replace('%', ''), errors='coerce')
                
                # 사용자가 설정한 최소 상승률로 필터링
                result = df[df['Change_Num'] >= min_change].copy()

                if not result.empty:
                    # 상위 10개 추출 (내림차순 정렬 후 head(10))
                    top_10 = result.sort_values(by='Change_Num', ascending=False).head(10)
                    
                    st.success(f"🔥 조건에 맞는 상위 {len(top_10)}개 종목을 찾았습니다.")
                    
                    # 출력할 컬럼 지정
                    display_cols = ['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']
                    
                    # 테이블 출력
                    st.table(top_10[display_cols]) # TOP 10은 table로 보는 것이 더 깔끔합니다.
                else:
                    st.warning(f"설정한 조건(상승률 {min_change}% 이상)을 만족하는 종목이 없습니다.")
            else:
                st.error("Finviz에서 데이터를 가져오지 못했습니다. 잠시 후 다시 시도해주세요.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

st.divider()
st.caption("데이터 제공: [Finviz Official](https://finviz.com) | 15분 지연 데이터")


