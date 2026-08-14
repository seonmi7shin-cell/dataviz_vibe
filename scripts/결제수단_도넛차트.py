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

print("결제수단별 거래금액 비중:")
for name, value in by_method.items():
    print(f"{name}: {value:,.0f}원 ({value/total*100:.2f}%)")

# 서로 다른 결제수단(정체성 구분)이라 카테고리 색을 고정 순서로 지정.
# dataviz 스킬의 검증된 팔레트(validate_palette.js 로 색약 구분·명도 통과 확인된 순서)를 그대로 사용
colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

fig, ax = plt.subplots(figsize=(8, 8))
wedges, _, autotexts = ax.pie(
    by_method.values,
    labels=by_method.index,
    autopct="%.2f%%",   # 비율을 소수점 둘째 자리까지 표시
    startangle=90,
    colors=colors[: len(by_method)],
    wedgeprops={"width": 0.4},  # width<1 로 가운데를 뚫어 도넛 모양을 만듦
    pctdistance=0.82,
)
ax.set_title("결제수단별 거래금액 비중")
ax.set_aspect("equal")

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "결제수단별_거래금액_도넛차트.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
