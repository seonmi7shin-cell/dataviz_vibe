# data/핀테크_정제완료.csv 에서 연령대별 거래금액 분포를 바이올린 플롯으로 그리는 스크립트.
# 박스플롯은 중앙값·사분위수만 보여주지만, 바이올린 플롯은 각 금액대에 몇 건이 몰려 있는지
# 폭(밀도)으로 보여줘서 "봉우리가 하나인지 여러 개인지"까지 확인할 수 있다.

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")

# 연령대는 크기 순서가 있는 항목(10대<20대<...)이라 나이 순서로 정렬해야 자연스럽게 읽힌다.
# "미상"은 나이 순서에 끼워 넣을 수 없으니 맨 뒤에 따로 둔다.
age_order = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
categories = [a for a in age_order if a in df["연령대"].unique()]
if "미상" in df["연령대"].unique():
    categories.append("미상")

data_by_age = [df.loc[df["연령대"] == age, "거래금액"] for age in categories]

# 박스플롯 때와 같은 이유로, 너무 큰 이상치(상위 1%)를 그릴 때만 빼서 밀도 모양이 눈에 잘 들어오게 한다.
# 원본 파일은 그대로 두고 이 그래프에 넣을 값만 거른다.
all_values = pd.concat(data_by_age)
upper_cutoff = all_values.quantile(0.99)
removed_count = sum((series > upper_cutoff).sum() for series in data_by_age)
data_by_age = [series[series <= upper_cutoff] for series in data_by_age]
print(f"바이올린 플롯 표시용으로 상위 1%({upper_cutoff:,.0f}원 초과) {removed_count}건을 제외함 (원본 파일은 그대로 둠)")

fig, ax = plt.subplots(figsize=(10, 7))
parts = ax.violinplot(data_by_age, showmedians=True, widths=0.8)

# violinplot 은 기본적으로 조각마다 색이 다르게 나오는데, 여기서는 전부 같은 측정값(거래금액)의
# 분포라 서로 다른 항목처럼 보이면 안 되므로 하나의 색(팔레트 기본 블루)으로 통일한다
for body in parts["bodies"]:
    body.set_facecolor("#2a78d6")
    body.set_edgecolor("#184f95")
    body.set_alpha(0.7)
parts["cmedians"].set_color("black")
parts["cmedians"].set_linewidth(2)

ax.set_xticks(range(1, len(categories) + 1))
ax.set_xticklabels(categories)
ax.set_title("연령대별 거래금액 분포 (바이올린 플롯)")
ax.set_xlabel("연령대")
ax.set_ylabel("거래금액 (원)")
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "연령대별_거래금액_바이올린플롯.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

for age, series in zip(categories, data_by_age):
    print(f"{age}: 중앙값 {series.median():,.0f}원, 건수 {len(series):,}건")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
