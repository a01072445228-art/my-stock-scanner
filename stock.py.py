import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd

st.set_page_config(page_title="급등주 스캐너", layout="wide")
st.title("🚀 오늘의 미국장 급등주 스캐너")

# 1. 필터 값 매핑용 딕셔너리 (오류 방지)
price_options = {
    1.0: "Over $1",
    2.0: "Over $2",
    5.0: "Over $5",
    10.0: "Over $10",
    20.0: "Over $20",
    50.0: "Over $50"
}

st.sidebar.header("필터 설정")
# 슬라이더 대신 선택 박스로 변경하여 오류 원천 차단
selected_price = st.sidebar.selectbox("최소 가격 선택 ($)", options=list(price_options.keys()), index=0)
min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 15)

if st.button("지금 급등주 찾기"):
    with st.spinner('전 종목 스캔 중...'):
        try:
            foverview = Overview()
            
            # 2. 필터 설정 (정해진 문자열 사용)
            # 'Price'에는 'Over $1' 같은 형식이 들어가야 함
            filters_dict = {
                'Price': price_options[selected_price], 
                'Order': 'Change'
            }
            
            foverview.set_filter(filters_dict=filters_dict)
            df = foverview.screener_view()

            if df is not None and not df.empty:
                # 상승률 문자열을 숫자로 변환하여 필터링
                df['Change_Num'] = df['Change'].str.replace('%', '').astype(float)
                result = df[df['Change_Num'] >= min_change]

                if not result.empty:
                    st.success(f"{len(result)}개의 종목을 찾았습니다!")
                    display_df = result[['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']]
                    # 소수점 정렬 및 하이라이트
                    st.dataframe(display_df.sort_values(by='Change_Num', ascending=False), use_container_width=True)
                else:
                    st.warning(f"상승률 {min_change}% 이상인 종목이 현재 없습니다.")
            else:
                st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")

        except Exception as e:
            st.error(f"알 수 없는 오류 발생: {e}")
            st.info("Tip: Finviz 사이트의 필터 양식이 변경되었을 수 있습니다.")

st.divider()
st.caption("주의: 핸드폰에서 보실 때는 '가로 모드'가 더 편합니다.")
