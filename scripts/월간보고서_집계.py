# data/핀테크_정제완료.csv 로 월간 보고서에 쓸 월별 요약(합계·건수·고객수·건당평균·전월대비 증감·1위업종)을
# 집계해서 output/월별_요약.csv 로 저장하고, 거래금액 추이를 라인차트로 그리는 스크립트.

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")
df["거래일시"] = pd.to_datetime(df["거래일시"], format="mixed")
df["연월"] = df["거래일시"].dt.to_period("M").astype(str)

by_month = df.groupby("연월").agg(
    거래금액_합계=("거래금액", "sum"),
    거래건수=("거래금액", "count"),
    고객수=("사용자ID", "nunique"),
).sort_index()
# 건당 평균은 반올림해야 소수점 아래 자리가 지저분하게 안 남는다
by_month["건당평균"] = (by_month["거래금액_합계"] / by_month["거래건수"]).round(0)
# 전월대비 증감률(%) — 첫 달은 비교할 전월이 없어 자동으로 빈 값(NaN)이 된다
by_month["전월대비증감(%)"] = (by_month["거래금액_합계"].pct_change() * 100).round(2)

# 그 달에 거래금액이 가장 큰 업종을 "1위업종"으로 붙여서, 달마다 어떤 업종이 견인했는지 바로 보이게 함
top_cat = df.groupby(["연월", "가맹점업종"])["거래금액"].sum().reset_index()
top_cat = top_cat.loc[top_cat.groupby("연월")["거래금액"].idxmax()].set_index("연월")["가맹점업종"]
by_month["1위업종"] = top_cat

output_path = os.path.join("output", "월별_요약.csv")
by_month.to_csv(output_path, encoding="utf-8-sig")
print(f"저장 경로: {output_path}")
print(by_month)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(by_month.index, by_month["거래금액_합계"], marker="o", color="#2a78d6", linewidth=2)
ax.set_title("월별 거래금액 합계 추이 (정제완료 데이터)")
ax.set_xlabel("연월")
ax.set_ylabel("거래금액 합계 (원)")
plt.xticks(rotation=45, ha="right")
ax.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()

chart_dir = os.path.join("output", "charts")
os.makedirs(chart_dir, exist_ok=True)
chart_path = os.path.join(chart_dir, "월별_거래금액_추이_정제완료.png")
plt.savefig(chart_path, dpi=150)
print(f"저장 경로: {chart_path}")

plt.show()
