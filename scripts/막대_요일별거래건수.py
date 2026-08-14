# data/핀테크_정제완료.csv 에서 요일별 거래 건수를 막대그래프로 그리는 스크립트.
# 거래일시 형식이 두 가지로 섞여 있어 format='mixed' 로 파싱한다.

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")
df["거래일시"] = pd.to_datetime(df["거래일시"], format="mixed")

# 요일은 크기가 아니라 월~일이라는 정해진 순서가 있는 항목이라, 건수 기준이 아니라
# 요일 순서 그대로 정렬해야 한 주의 흐름이 보인다 (건수순 정렬은 이 순서를 깨뜨림)
weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
weekday_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
df["요일"] = df["거래일시"].dt.weekday.map(weekday_map)

by_weekday = df["요일"].value_counts().reindex(weekday_order)

print("요일별 거래 건수:")
print(by_weekday)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(by_weekday.index, by_weekday.values, color="#2a78d6")  # 단일 계열이라 팔레트 기본 블루 하나만 사용
ax.set_title("요일별 거래 건수")
ax.set_xlabel("요일")
ax.set_ylabel("거래 건수")

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
output_path = os.path.join(output_dir, "요일별_거래건수_막대.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
