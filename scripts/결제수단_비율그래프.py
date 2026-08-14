# data/01_핀테크결제_dirty.csv 에서 결제수단별 건수와 비율을 가로 막대그래프로 그리는 스크립트.
# 공백 표기 문제(' 신용카드')는 집계 직전에만 strip() 으로 정리한다 (원본·정제완료 파일은 그대로 둠).

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

# 집계 직전에만 공백 제거. 결측은 "결측"이라는 항목으로 남겨서 전체 비율 100%가 맞게 함
payment = df["결제수단"].str.strip().fillna("결측")
counts = payment.value_counts().sort_values(ascending=True)  # barh 는 아래→위 순이라 오름차순 정렬해야 위쪽에 큰 값이 옴
percentages = counts / counts.sum() * 100

print("결제수단별 건수·비율:")
for name in counts.index[::-1]:
    print(f"{name}: {counts[name]:,}건 ({percentages[name]:.2f}%)")

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(counts.index, counts.values, color="#4C72B0")
ax.set_title("결제수단별 건수 및 비율")
ax.set_xlabel("건수")
ax.set_ylabel("결제수단")

# 막대 끝에 건수와 비율을 같이 표시 (소수점 둘째 자리, CLAUDE.md 비율 표기 규칙)
for bar, name in zip(bars, counts.index):
    width = bar.get_width()
    ax.text(
        width,
        bar.get_y() + bar.get_height() / 2,
        f" {width:,}건 ({percentages[name]:.2f}%)",
        ha="left",
        va="center",
        fontsize=9,
    )

ax.set_xlim(0, counts.max() * 1.2)  # 라벨 텍스트가 그래프 밖으로 잘리지 않게 여유를 둠
plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "결제수단별_건수_비율.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
