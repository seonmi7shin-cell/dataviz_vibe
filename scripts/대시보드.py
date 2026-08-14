# 핀테크 결제 데이터(data/핀테크_정제완료.csv)를 지역·업종·결제수단·기간으로 필터링해서 보는
# Streamlit 대시보드. 왼쪽 사이드바에서 조건을 바꾸면 아래 지표·그래프·표가 전부 다시 그려진다.
# 이게 정적 이미지 대신 대시보드를 쓰는 이유 — 필터를 바꿀 때마다 코드를 다시 실행할 필요가 없다.
#
# 그래프는 matplotlib 정적 이미지 대신 Streamlit 내장 차트(st.bar_chart / st.line_chart)를 쓴다.
# 내장 차트는 마우스를 올리면 값이 뜨고 확대·범례 토글이 기본으로 되는데, 이건 Altair 라이브러리를
# 안에 감싸서 제공하는 기능이라 우리가 따로 마우스 이벤트를 코딩할 필요가 없다.

import os
import pandas as pd
import streamlit as st

# 스크립트가 scripts 폴더 안에 있으므로 상위 폴더로 이동해야 data/ 를 찾을 수 있음.
# 이 줄이 없으면 다른 폴더에서 실행할 때 FileNotFoundError 가 난다.
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

st.set_page_config(page_title="핀테크 결제 대시보드", layout="wide")


@st.cache_data
def load_data():
    # 매번 필터를 바꿀 때마다 CSV를 다시 읽으면 느려지므로, 원본 로딩 + 연월 계산까지 캐시해서
    # 앱이 켜져 있는 동안 딱 한 번만 실행한다.
    data = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")
    with_date = data.dropna(subset=["거래일시"]).copy()
    with_date["거래일시"] = pd.to_datetime(with_date["거래일시"], format="mixed")
    with_date["연월"] = with_date["거래일시"].dt.to_period("M").astype(str)
    return with_date


df = load_data()

st.title("핀테크 결제 데이터 대시보드")
st.caption("데이터: data/핀테크_정제완료.csv (정제 완료, 음수 거래금액 제외)")

# ---------- 왼쪽 사이드바: 필터 ----------
st.sidebar.header("필터")

region_options = sorted(df["지역"].unique())
category_options = sorted(df["가맹점업종"].unique())
payment_options = sorted(df["결제수단"].unique())
month_options = sorted(df["연월"].unique())

selected_regions = st.sidebar.multiselect("지역", region_options, default=region_options)
selected_categories = st.sidebar.multiselect("가맹점업종", category_options, default=category_options)
selected_payments = st.sidebar.multiselect("결제수단", payment_options, default=payment_options)

# select_slider 로 시작·끝 달을 양쪽에서 드래그해서 기간을 좁힐 수 있게 함
start_month, end_month = st.sidebar.select_slider(
    "기간 (연월)",
    options=month_options,
    value=(month_options[0], month_options[-1]),
)

# 아무것도 선택 안 하면 화면이 텅 비어 당황하기 쉬우므로, 그 경우엔 전체를 본 것처럼 처리한다
if not selected_regions:
    selected_regions = region_options
if not selected_categories:
    selected_categories = category_options
if not selected_payments:
    selected_payments = payment_options

filtered = df[
    df["지역"].isin(selected_regions)
    & df["가맹점업종"].isin(selected_categories)
    & df["결제수단"].isin(selected_payments)
    & df["연월"].between(start_month, end_month)
]

st.sidebar.caption(f"선택된 거래: {len(filtered):,}건 / 전체 {len(df):,}건")

# ---------- 상단 요약 지표 (총액·건수·평균·고객 수를 크게 강조) ----------
# delta 에 전체 대비 비중을 넣어야 "이 필터가 전체에서 얼마나 큰 부분을 보고 있는지" 바로 감이 온다
total_count, total_amount = len(df), df["거래금액"].sum()
filtered_count, filtered_amount = len(filtered), filtered["거래금액"].sum()
filtered_customers, total_customers = filtered["사용자ID"].nunique(), df["사용자ID"].nunique()

# st.metric 기본 글자 크기가 작아 눈에 잘 안 띄어서, 값 부분만 훨씬 큰 폰트로 직접 꾸민다.
# 카드 4개를 나란히 두면 "총액 · 건수 · 평균 · 고객 수"를 한눈에 비교하기 쉽다.
st.markdown(
    """
    <style>
    .kpi-card { background: #f9f9f7; border: 1px solid #e1e0d9; border-radius: 8px;
                padding: 16px 20px; text-align: center; }
    .kpi-label { font-size: 14px; color: #52514e; margin-bottom: 6px; }
    .kpi-value { font-size: 34px; font-weight: 700; color: #0b0b0b; line-height: 1.1; }
    .kpi-delta { font-size: 12px; color: #256abf; margin-top: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(column, label, value, delta=None):
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    column.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


col1, col2, col3, col4 = st.columns(4)
kpi_card(
    col1, "거래금액 합계", f"{filtered_amount:,.0f}원",
    f"전체의 {filtered_amount / total_amount * 100:.1f}%" if total_amount else None,
)
kpi_card(
    col2, "거래 건수", f"{filtered_count:,}건",
    f"전체의 {filtered_count / total_count * 100:.1f}%" if total_count else None,
)
kpi_card(
    col3, "건당 평균 금액",
    f"{filtered['거래금액'].mean():,.0f}원" if filtered_count else "0원",
)
kpi_card(
    col4, "고객 수", f"{filtered_customers:,}명",
    f"전체의 {filtered_customers / total_customers * 100:.1f}%" if total_customers else None,
)

st.divider()

# ---------- 탭으로 구성: 한 화면에 다 몰아넣지 않고 필요한 것만 눌러서 보게 함 ----------
tab_overview, tab_category, tab_region, tab_trend, tab_raw = st.tabs(
    ["개요", "업종별", "지역별", "월별 추이", "원본 데이터"]
)

with tab_overview:
    st.subheader("업종별 거래금액 비중 상위 5")
    top5 = filtered.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=False).head(5)
    if len(top5):
        # st.bar_chart 는 마우스를 올리면 값이 뜨는 인터랙티브 차트라 정적 이미지보다 바로 값을 확인하기 좋다
        st.bar_chart(top5)
    else:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")

    st.subheader("결제수단별 건수")
    payment_counts = filtered["결제수단"].value_counts()
    if len(payment_counts):
        st.bar_chart(payment_counts)

with tab_category:
    st.subheader("업종별 거래금액 합계")
    by_category = filtered.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=False)
    if len(by_category):
        st.bar_chart(by_category)
        st.dataframe(
            by_category.rename("거래금액 합계(원)").reset_index(),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")

with tab_region:
    st.subheader("지역별 거래금액 합계")
    by_region = filtered.groupby("지역")["거래금액"].sum().sort_values(ascending=False)
    if len(by_region):
        st.bar_chart(by_region)
        st.dataframe(
            by_region.rename("거래금액 합계(원)").reset_index(),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")

with tab_trend:
    st.subheader("연월별 거래금액 합계 추이")
    by_month = filtered.groupby("연월")["거래금액"].sum().sort_index()
    if len(by_month):
        st.line_chart(by_month)
    else:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")

with tab_raw:
    st.subheader("필터링된 원본 데이터")
    # 표를 기본으로 접어두면(expander) 처음 화면이 덜 복잡해 보이고, 필요할 때만 펼쳐서 본다
    with st.expander(f"{len(filtered):,}행 보기 / 접기", expanded=False):
        st.dataframe(filtered, width="stretch")

    # 필터링한 결과를 그대로 CSV 로 내려받을 수 있어야 대시보드 밖에서도 이어서 분석할 수 있다
    st.download_button(
        "필터링된 데이터 CSV로 다운로드",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="핀테크_필터링결과.csv",
        mime="text/csv",
    )
