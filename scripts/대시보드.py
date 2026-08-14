# 핀테크 결제 데이터(data/핀테크_정제완료.csv)를 지역·업종으로 필터링해서 보는 Streamlit 대시보드.
# 왼쪽 사이드바에서 지역·업종을 고르면 그 조건에 맞는 데이터로 모든 표·그래프가 다시 그려진다.
# 이게 정적 이미지 대신 대시보드를 쓰는 이유 — 필터를 바꿀 때마다 코드를 다시 실행할 필요가 없다.

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# 스크립트가 scripts 폴더 안에 있으므로 상위 폴더로 이동해야 data/ 를 찾을 수 있음.
# 이 줄이 없으면 다른 폴더에서 실행할 때 FileNotFoundError 가 난다.
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

st.set_page_config(page_title="핀테크 결제 대시보드", layout="wide")


@st.cache_data
def load_data():
    # 매번 필터를 바꿀 때마다 CSV를 다시 읽으면 느려지므로, 원본 로딩만 캐시해서 한 번만 읽는다.
    return pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")


df = load_data()

st.title("핀테크 결제 데이터 대시보드")
st.caption("데이터: data/핀테크_정제완료.csv (정제 완료, 음수 거래금액 제외)")

# ---------- 왼쪽 사이드바: 지역·업종 필터 ----------
st.sidebar.header("필터")

# 정렬된 목록에서 고르게 해야 사이드바 리스트가 뒤죽박죽 안 보인다
region_options = sorted(df["지역"].unique())
category_options = sorted(df["가맹점업종"].unique())

selected_regions = st.sidebar.multiselect("지역", region_options, default=region_options)
selected_categories = st.sidebar.multiselect("가맹점업종", category_options, default=category_options)

# 아무것도 선택 안 하면 화면이 텅 비어 당황하기 쉬우므로, 그 경우엔 전체를 본 것처럼 처리한다
if not selected_regions:
    selected_regions = region_options
if not selected_categories:
    selected_categories = category_options

filtered = df[df["지역"].isin(selected_regions) & df["가맹점업종"].isin(selected_categories)]

# ---------- 상단 요약 지표 ----------
col1, col2, col3 = st.columns(3)
col1.metric("거래 건수", f"{len(filtered):,}건")
col2.metric("거래금액 합계", f"{filtered['거래금액'].sum():,.0f}원")
col3.metric(
    "건당 평균 금액",
    f"{filtered['거래금액'].mean():,.0f}원" if len(filtered) else "0원",
)

st.divider()

# ---------- 업종별 거래금액 합계 (가로 막대) ----------
st.subheader("업종별 거래금액 합계")
by_category = filtered.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=True)

if len(by_category):
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.barh(by_category.index, by_category.values, color="#2a78d6")  # 단일 계열이라 팔레트 기본 블루 사용
    ax1.set_xlabel("거래금액 합계 (원)")
    for i, v in enumerate(by_category.values):
        ax1.text(v, i, f" {v:,.0f}", va="center", fontsize=8)
    st.pyplot(fig1)
else:
    st.info("선택한 조건에 해당하는 데이터가 없습니다.")

# ---------- 지역별 거래금액 합계 (가로 막대) ----------
st.subheader("지역별 거래금액 합계")
by_region = filtered.groupby("지역")["거래금액"].sum().sort_values(ascending=True)

if len(by_region):
    fig2, ax2 = plt.subplots(figsize=(8, max(4, 0.35 * len(by_region))))
    ax2.barh(by_region.index, by_region.values, color="#2a78d6")
    ax2.set_xlabel("거래금액 합계 (원)")
    for i, v in enumerate(by_region.values):
        ax2.text(v, i, f" {v:,.0f}", va="center", fontsize=8)
    st.pyplot(fig2)
else:
    st.info("선택한 조건에 해당하는 데이터가 없습니다.")

# ---------- 연월별 거래금액 추이 ----------
st.subheader("연월별 거래금액 합계 추이")
monthly_df = filtered.dropna(subset=["거래일시"]).copy()
if len(monthly_df):
    monthly_df["거래일시"] = pd.to_datetime(monthly_df["거래일시"], format="mixed")
    monthly_df["연월"] = monthly_df["거래일시"].dt.to_period("M").astype(str)
    by_month = monthly_df.groupby("연월")["거래금액"].sum().sort_index()

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(by_month.index, by_month.values, marker="o", color="#2a78d6", linewidth=2)
    ax3.set_ylabel("거래금액 합계 (원)")
    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig3)
else:
    st.info("선택한 조건에 해당하는 데이터가 없습니다.")

# ---------- 원본 데이터 표 ----------
st.subheader("필터링된 데이터")
st.dataframe(filtered, use_container_width=True)
