# data/핀테크_정제완료.csv 에서 20만원 미만 거래만 골라 거래금액 분포를 히스토그램(40칸)으로 그리는 스크립트.

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
    under_200k, bins=40, color="#2a78d6", edgecolor="white"
)  # 단일 계열 분포라 팔레트 기본 블루 하나만 사용
ax.set_title("거래금액 분포 (20만원 미만)")
ax.set_xlabel("거래금액 (원)")
ax.set_ylabel("건수")
ax.grid(axis="y", linestyle="--", alpha=0.4)

# 칸마다 건수를 적어야 막대 높이를 눈대중으로 읽지 않고 정확한 값을 바로 확인할 수 있다.
# 0건인 칸까지 숫자를 찍으면 지저분해지므로 1건 이상인 칸에만 표시한다.
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
output_path = os.path.join(output_dir, "거래금액_히스토그램_20만원미만.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
