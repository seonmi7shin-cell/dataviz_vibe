# data/01_핀테크결제_dirty.csv 원본에서 가맹점업종별 거래금액 합계를 구해
# 큰 순서로 가로 막대그래프를 그리는 스크립트. (정제 전 원본 파일을 그대로 사용)

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

# 환불·오류로 보이는 음수 거래금액이 섞여 있으면 합계가 실제보다 낮게 나와 순위·크기가
# 왜곡되므로 집계 전에 제외한다 (이상치 처리 지시에 따라 추가)
df = df[df["거래금액"] >= 0]

# 업종별 합계를 내고 오름차순으로 정렬. barh 는 위에서부터 그리므로
# 오름차순 정렬을 해야 화면에서 위쪽에 가장 큰 값이 온다 (큰 순서로 보이게 하는 핵심)
by_category = df.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=True)

print("업종별 거래금액 합계 (큰 순서):")
print(by_category.sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(by_category.index, by_category.values, color="#4C72B0")
ax.set_title("가맹점업종별 거래금액 합계 (큰 순서)")
ax.set_xlabel("거래금액 합계 (원)")
ax.set_ylabel("가맹점업종")

# 막대 끝에 실제 합계값을 표시. 천단위 구분기호를 넣어야 큰 금액이 한눈에 읽힘
for bar in bars:
    width = bar.get_width()
    ax.text(
        width,
        bar.get_y() + bar.get_height() / 2,
        f" {width:,.0f}",
        ha="left",
        va="center",
        fontsize=9,
    )

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "업종별_거래금액_가로막대.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")
