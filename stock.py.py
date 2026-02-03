import streamlit as st
from finvizfinance.screener.overview import Overview
import pandas as pd

# 1. 앱 기본 설정 (핸드폰 브라우저 최적화)
st.set_page_config(page_title="미국주식 급등주 스캔", layout="wide")

st.title("🚀 오늘의 미국장 급등주 스캐너")
st.caption("실시간 Finviz 데이터를 바탕으로 급등주를 찾습니다.")

# 2. 사이드바 설정 (필터 조건 조정)
st.sidebar.header("🔍 검색 필터 설정")
min_change = st.sidebar.slider("최소 상승률 (%)", 0, 50, 5) # 5% 이상 상승 중인 종목
min_price = st.sidebar.number_input("최소 가격 ($)", value=1.0) # 동전주 제외 설정 가능

# 3. 데이터 가져오기 버튼
if st.button("지금 급등주 리스트 갱신하기"):
    with st.spinner('데이터 분석 중... 잠시만 기다려주세요!'):
        try:
            # Finviz에서 데이터 가져오기
            foverview = Overview()
            # 상승률 순(Change)으로 정렬하여 가져오기
            filters_dict = {'Price': f'Over {min_price}', 'Order': 'Change'}
            foverview.set_filter(filters_dict=filters_dict)
            df = foverview.screener_view()

            # 'Change' 문자열(예: '15.50%')을 숫자로 변환
            df['Change_Num'] = df['Change'].str.replace('%', '').astype(float)
            
            # 내가 설정한 상승률보다 높은 종목만 필터링
            result = df[df['Change_Num'] >= min_change]

            if not result.empty:
                st.success(f"✅ 총 {len(result)}개의 급등 종목을 발견했습니다!")
                
                # 보여줄 컬럼 선택
                display_df = result[['Ticker', 'Company', 'Sector', 'Price', 'Change', 'Volume']]
                
                # 화면에 표 그리기 (가득 차게)
                st.dataframe(
                    display_df.style.highlight_max(axis=0, subset=['Change']), 
                    use_container_width=True
                )
                
                st.info("💡 팁: 표 상단을 누르면 거래량순 등으로 다시 정렬할 수 있습니다.")
            else:
                st.warning("현재 조건에 맞는 급등 종목이 없습니다.")
                
        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")

st.divider()
st.caption("주의: 본 데이터는 투자 참고용이며, 모든 투자의 책임은 본인에게 있습니다.")