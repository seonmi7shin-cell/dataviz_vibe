# 히스토그램_거래금액_20만원미만.py 와 데이터·구조는 동일하고, 색만 dataviz 팔레트의
# violet 슬롯(#4a3aa7)으로 바꾼 버전.

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")

under_200k = df[df["거래금액"] < 200000]["거래금액"]
print(f"전체 {len(df):,}건 중 20만원 미만 거래: {len(under_200k):,}건")

fig, ax = plt.subplots(figsize=(14, 7))
counts, bin_edges, patches = ax.hist(
    under_200k, bins=40, color="#4a3aa7", edgecolor="white"
)  # dataviz 팔레트의 violet 슬롯
ax.set_title("거래금액 분포 (20만원 미만) - 바이올렛")
ax.set_xlabel("거래금액 (원)")
ax.set_ylabel("건수")
ax.grid(axis="y", linestyle="--", alpha=0.4)

for count, patch in zip(counts, patches):
    if count > 0:
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            patch.get_height(),
            f"{int(count):,}",
            ha="center",
            va="bottom",
            fontsize=7,
            rotation=90,
        )

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "거래금액_히스토그램_20만원미만_바이올렛.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
