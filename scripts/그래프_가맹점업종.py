# 정제 완료 데이터(data/핀테크_정제완료.csv)를 가맹점업종별로 그룹바이해서
# 거래금액 합계를 막대그래프로 그리는 스크립트.
# 파일로 저장하지 않고 plt.show() 로 화면에 창을 띄운다 (요청에 따라 이번만 예외).

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")

# 가맹점업종별 거래금액 합계를 냄. sort_values 로 큰 값부터 정렬해야 막대가 내림차순으로 보임
by_category = df.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=False)

print("가맹점업종별 거래금액 합계:")
print(by_category)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(by_category.index, by_category.values, color="#4C72B0")
ax.set_title("가맹점업종별 거래금액 합계")
ax.set_xlabel("가맹점업종")
ax.set_ylabel("거래금액 합계 (원)")
plt.xticks(rotation=45, ha="right")

# 막대 위에 실제 합계값을 표시. {:,.0f} 로 천단위 구분기호를 넣어야 큰 금액이 한눈에 읽힘
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
plt.show()
