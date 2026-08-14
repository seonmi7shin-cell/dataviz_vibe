# data/01_핀테크결제_dirty.csv 에서 거래금액 합계 상위 3개 업종을 골라, 각 업종의 월별
# 거래금액 추이를 한 그래프에 겹쳐 그리는 스크립트. (음수 거래금액은 제외하고 집계)

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

# 환불·오류로 보이는 음수 거래금액이 섞여 있으면 추이가 왜곡되므로 집계 전에 제외
df = df[df["거래금액"] >= 0]
df = df.dropna(subset=["거래일시"])
df["거래일시"] = pd.to_datetime(df["거래일시"], format="mixed")
df["연월"] = df["거래일시"].dt.to_period("M").astype(str)

# 업종별 총합에서 상위 3개를 골라야 "어떤 업종을 겹쳐 그릴지"가 정해진다
top3 = df.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=False).head(3).index.tolist()
print("상위 3개 업종:", top3)

pivot = (
    df[df["가맹점업종"].isin(top3)]
    .groupby(["연월", "가맹점업종"])["거래금액"]
    .sum()
    .unstack("가맹점업종")
    .sort_index()
    .reindex(columns=top3)  # 범례 순서를 합계 순위와 맞춤
)
print(pivot)

# 서로 다른 업종(정체성 구분)이라 dataviz 팔레트의 카테고리 색을 고정 순서로 사용
colors = ["#2a78d6", "#eb6834", "#1baf7a"]

fig, ax = plt.subplots(figsize=(11, 6))
for name, color in zip(top3, colors):
    ax.plot(pivot.index, pivot[name], marker="o", linewidth=2, color=color, label=name)

ax.set_title("업종별 거래금액 합계 상위 3개 - 월별 추이")
ax.set_xlabel("연월")
ax.set_ylabel("거래금액 합계 (원)")
plt.xticks(rotation=45, ha="right")
ax.legend(title="가맹점업종")  # 2개 이상의 계열이라 범례를 반드시 넣어야 함
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "업종상위3_월별추이_라인차트.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

plt.show()
