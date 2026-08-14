# data/핀테크_정제완료.csv 에서 연령대별 거래금액 분포를 박스플롯으로 그리는 스크립트.
# 박스플롯은 평균 하나가 아니라 중앙값·사분위수·이상치까지 한번에 보여주는 게 목적이라
# 막대그래프(합계 비교)와는 다른 질문(퍼져있는 정도, 이상치 존재)에 답한다.

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")

# 연령대는 크기 순서가 있는 항목(10대<20대<...)이라 값 기준이 아니라 나이 순서로 정렬해야
# 자연스럽게 읽힌다. "미상"은 나이 순서에 끼워 넣을 수 없으니 맨 뒤에 따로 둔다.
age_order = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
categories = [a for a in age_order if a in df["연령대"].unique()]
if "미상" in df["연령대"].unique():
    categories.append("미상")

data_by_age = [df.loc[df["연령대"] == age, "거래금액"] for age in categories]

# 박스플롯을 그릴 때만 너무 큰 이상치를 빼서 박스(사분위 범위)가 눈에 잘 보이게 한다.
# 전체 데이터 기준 상위 1% 값을 잘라내는 것으로, data/핀테크_정제완료.csv 파일 자체는 그대로 두고
# 이 그래프에서 화면에 그릴 값만 걸러낸다.
all_values = pd.concat(data_by_age)
upper_cutoff = all_values.quantile(0.99)
removed_count = sum((series > upper_cutoff).sum() for series in data_by_age)
data_by_age = [series[series <= upper_cutoff] for series in data_by_age]
print(f"박스플롯 표시용으로 상위 1%({upper_cutoff:,.0f}원 초과) {removed_count}건을 제외함 (원본 파일은 그대로 둠)")

fig, ax = plt.subplots(figsize=(10, 7))
box = ax.boxplot(
    data_by_age,
    tick_labels=categories,
    patch_artist=True,
    widths=0.5,  # 박스를 넓게 그려야 눈에 잘 들어옴 (기본값 0.5보다 더 조밀했던 문제 보완)
    boxprops=dict(facecolor="#2a78d6", alpha=0.7, linewidth=1.5),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5),
    medianprops=dict(color="black", linewidth=2),
    flierprops=dict(marker="o", markersize=4, markerfacecolor="#e34948", alpha=0.5, markeredgewidth=0),  # 이상치는 팔레트의 red 슬롯
)
ax.set_title("연령대별 거래금액 분포")
ax.set_xlabel("연령대")
ax.set_ylabel("거래금액 (원)")
ax.grid(axis="y", linestyle="--", alpha=0.4)  # 가로 눈금선을 넣어야 박스 높이 차이가 눈에 잘 들어옴

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "연령대별_거래금액_박스플롯.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

for age, series in zip(categories, data_by_age):
    print(
        f"{age}: 중앙값 {series.median():,.0f}원, Q1 {series.quantile(0.25):,.0f}원, "
        f"Q3 {series.quantile(0.75):,.0f}원, 최댓값 {series.max():,.0f}원"
    )

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
