# 지금까지 만든 그래프들의 근거가 되는 집계 결과를 output 폴더에 CSV로 남기는 스크립트.
# CLAUDE.md 규칙상 표는 output 폴더에 CSV(encoding=utf-8-sig)로 저장해야 하는데, 그동안은
# md/docx 문서 안에만 표로 넣고 CSV로는 안 뽑아뒀어서 이번에 따로 뽑는다.
# 음수 거래금액(25건)은 이상치 처리 지시에 따라 전부 제외하고 집계한다.

import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")
df = df[df["거래금액"] >= 0]

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


def save(frame, name):
    path = os.path.join(output_dir, name)
    frame.to_csv(path, encoding="utf-8-sig")
    print(f"저장: {path} ({len(frame)}행)")


# 1. 업종별 거래금액 합계
by_category = df.groupby("가맹점업종")["거래금액"].sum().sort_values(ascending=False)
by_category.name = "거래금액_합계"
save(by_category, "업종별_거래금액_합계.csv")

# 2. 지역별 거래금액 합계
# groupby 는 결측을 기본적으로 조용히 빼버려서 전체 합계가 안 맞게 되므로, 알수없음으로
# 채워서 결측 건수도 표에 같이 남긴다 (CLAUDE.md: 결측이 있어도 컬럼을 분석에서 빼지 않음)
by_region = df["지역"].fillna("알수없음")
by_region = df.groupby(by_region)["거래금액"].sum().sort_values(ascending=False)
by_region.name = "거래금액_합계"
by_region.index.name = "지역"
save(by_region, "지역별_거래금액_합계.csv")

# 3. 결제수단별 거래금액 합계·건수·비중 (공백 표기 문제는 집계 직전에만 정리)
df["결제수단_정리"] = df["결제수단"].str.strip().fillna("결측")
by_payment_sum = df.groupby("결제수단_정리")["거래금액"].sum().sort_values(ascending=False)
by_payment_count = df.groupby("결제수단_정리").size().reindex(by_payment_sum.index)
by_payment = pd.DataFrame({
    "거래금액_합계": by_payment_sum,
    "건수": by_payment_count,
    "비중(%)": (by_payment_sum / by_payment_sum.sum() * 100).round(2),
})
save(by_payment, "결제수단별_거래금액_합계.csv")

# 4. 연령대별 거래금액 합계 (결측은 미상으로 채워서 합계에 포함)
by_age = df["연령대"].fillna("미상")
by_age = df.groupby(by_age)["거래금액"].sum().sort_values(ascending=False)
by_age.name = "거래금액_합계"
by_age.index.name = "연령대"
save(by_age, "연령대별_거래금액_합계.csv")

# 5. 연월별 거래금액 합계 추이
month_df = df.dropna(subset=["거래일시"]).copy()
month_df["거래일시"] = pd.to_datetime(month_df["거래일시"], format="mixed")
month_df["연월"] = month_df["거래일시"].dt.to_period("M").astype(str)
by_month = month_df.groupby("연월")["거래금액"].sum().sort_index()
by_month.name = "거래금액_합계"
save(by_month, "연월별_거래금액_합계.csv")
