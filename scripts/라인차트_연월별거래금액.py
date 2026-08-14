# data/01_핀테크결제_dirty.csv 원본에서 연월별 거래금액 합계 추이를 라인차트로 그리는 스크립트.
# (정제 전 원본 파일 그대로 사용. 거래일시 형식이 두 가지로 섞여 있어 format='mixed' 로 파싱)

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

# 거래일시가 없는 행은 월별로 묶을 수 없으므로 이 그래프에서만 임시로 제외 (원본 파일은 그대로 둠)
df = df.dropna(subset=["거래일시"])
df["거래일시"] = pd.to_datetime(df["거래일시"], format="mixed")
df["연월"] = df["거래일시"].dt.to_period("M").astype(str)

by_month = df.groupby("연월")["거래금액"].sum().sort_index()

print("연월별 거래금액 합계:")
print(by_month)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(by_month.index, by_month.values, marker="o", color="#4C72B0", linewidth=2)
ax.set_title("연월별 거래금액 합계 추이")
ax.set_xlabel("연월")
ax.set_ylabel("거래금액 합계 (원)")
plt.xticks(rotation=45, ha="right")

# 점마다 값을 다 찍으면 지저분해지므로 최댓값·최솟값 지점만 직접 라벨을 붙임
max_month = by_month.idxmax()
min_month = by_month.idxmin()
for month in (max_month, min_month):
    value = by_month[month]
    ax.annotate(
        f"{value:,.0f}",
        xy=(month, value),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=9,
    )

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "연월별_거래금액_라인차트.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")
