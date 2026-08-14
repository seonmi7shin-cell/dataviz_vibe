# data/01_핀테크결제_dirty.csv 원본에서 결제수단별 거래금액 비중을 도넛차트로 그리는 스크립트.
# 결제수단 표기의 앞뒤 공백은 집계 직전에만 strip() 으로 정리한다 (원본·정제완료 파일은 그대로 둠).

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

# 집계 직전에만 공백 제거. 결측은 "결측"이라는 항목으로 남겨서 전체 비중 100%가 맞게 함
df["결제수단_정리"] = df["결제수단"].str.strip().fillna("결측")
by_method = df.groupby("결제수단_정리")["거래금액"].sum().sort_values(ascending=False)
total = by_method.sum()

# 건수(거래 몇 건인지)는 금액과 별개로 집계해야 함 — sum()은 금액을 더한 값이라 건수와 다르다
count_by_method = df.groupby("결제수단_정리").size().reindex(by_method.index)
total_count = int(count_by_method.sum())

print("결제수단별 거래금액 비중:")
for name, value in by_method.items():
    print(f"{name}: {value:,.0f}원 ({value/total*100:.2f}%), {count_by_method[name]:,}건")

# 서로 다른 결제수단(정체성 구분)이라 카테고리 색을 고정 순서로 지정.
# dataviz 스킬의 검증된 팔레트(validate_palette.js 로 색약 구분·명도 통과 확인된 순서)를 그대로 사용
colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

# autopct 는 비율(%)만 넘겨주므로, 조각이 그려지는 순서(counts 리스트 순서)를 따라가며
# 건수를 하나씩 꺼내 같은 라벨에 같이 적어준다
counts_in_order = count_by_method.tolist()
wedge_position = {"i": 0}


def label_with_count(pct):
    i = wedge_position["i"]
    wedge_position["i"] += 1
    count = counts_in_order[i]
    return f"{pct:.2f}%\n({count:,}건)"


fig, ax = plt.subplots(figsize=(8, 8))
wedges, _, autotexts = ax.pie(
    by_method.values,
    labels=by_method.index,
    autopct=label_with_count,   # 비율과 건수를 함께 표시
    startangle=90,
    colors=colors[: len(by_method)],
    wedgeprops={"width": 0.4},  # width<1 로 가운데를 뚫어 도넛 모양을 만듦
    pctdistance=0.82,
)
ax.set_title("결제수단별 거래금액 비중")
ax.set_aspect("equal")

# 도넛 가운데 뚫린 공간에 전체 건수를 적어 전체 규모를 바로 보여줌
ax.text(0, 0, f"전체\n{total_count:,}건", ha="center", va="center", fontsize=14, fontweight="bold")

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "결제수단별_거래금액_도넛차트.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
