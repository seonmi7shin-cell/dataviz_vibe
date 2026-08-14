# 보고서에 첨부할 가맹점업종별 거래금액 합계 막대그래프를 PNG로 저장하는 스크립트.
# 화면에 띄우는 용도가 아니라 문서에 넣을 이미지 파일이 필요해서 이번엔 savefig 를 쓴다.

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")

by_category = df.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(by_category.index, by_category.values, color="#4C72B0")
ax.set_title("가맹점업종별 거래금액 합계")
ax.set_xlabel("가맹점업종")
ax.set_ylabel("거래금액 합계 (원)")
plt.xticks(rotation=45, ha="right")

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:,.0f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "가맹점업종_거래금액.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")
