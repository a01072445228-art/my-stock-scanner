import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd

st.set_page_config(page_title="급등주 스캐너", layout="wide")
st.title("🚀 오늘의 미국장 급등주 스캐너")

price_options = {
    1.0: "Over $1",
    2.0: "Over $2",
    5.0: "Over $5",
    10.0: "Over $10",
    20.0: "Over $20",
    50.0: "Over $50"
}

st.sidebar.header("필터 설정")
selected_price = st.sidebar.selectbox("최소 가격 선택 ($)", options=list(price_options.keys()), index=0)
min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 15)

if st.button("지금 급등주 찾기"):
    with st.spinner('전 종목 스캔 중...'):
        try:
            foverview = Overview()
            
            # [수정 포인트 1] filters_dict에서 'Order'를 제거합니다.
            filters_dict = {
                'Price': price_options[selected_price]
            }
            
            foverview.set_filter(filters_dict=filters_dict)
            
            # [수정 포인트 2] 정렬(order)은 screener_view 호출 시 인자로 전달합니다.
            # 기본값은 'Ticker'이며, 상승률순 정렬을 원하면 'Change'를 입력합니다.
            df = foverview.screener_view(order='Change') 

            if df is not None and not df.empty:
                # 'Change' 컬럼의 % 기호를 제거하고 숫자로 변환
                df['Change_Num'] = df['Change'].str.replace('%', '', regex=False).astype(float)
                result = df[df['Change_Num'] >= min_change]

                if not result.empty:
                    st.success(f"{len(result)}개의 종목을 찾았습니다!")
                    display_df = result[['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume', 'Relative Volume']]
                    # 결과 내에서 다시 한번 높은 순서대로 정렬하여 출력
                    st.dataframe(display_df.sort_values(by='Change_Num', ascending=False), use_container_width=True)
                else:
                    st.warning(f"상승률 {min_change}% 이상인 종목이 현재 없습니다.")
            else:
                st.error("데이터를 불러오지 못했습니다.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

st.divider()
st.caption("데이터 제공: Finviz (실시간이 아니며 약 15분 지연될 수 있습니다.)")

