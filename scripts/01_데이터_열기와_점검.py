# "처음 만난 데이터에서 보는 다섯 가지" 점검 절차를 그대로 따라 하는 스크립트.
# 그래프보다 점검이 먼저 — 분포·이상치·구조를 먼저 보는 게 EDA(탐색적 데이터 분석)의 기본이다.
# 1)크기 2)앞부분 3)타입 4)요약 5)범주, 이 다섯 가지를 한 번 실행으로 순서대로 출력한다.

import os
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

print("=" * 60)
print("1. 크기 — df.shape (행 수, 열 수)")
print("=" * 60)
print(df.shape)

print()
print("=" * 60)
print("2. 앞부분 — df.head() (컬럼과 값 모양 확인)")
print("=" * 60)
print(df.head())

print()
print("=" * 60)
print("3. 타입 — df.info() (숫자·문자 구분, 빈 값 확인)")
print("=" * 60)
df.info()
# 컬럼별 빈 값을 합쳐서 총 몇 칸이 비어있는지 한눈에 보이게 함
total_missing = df.isna().sum().sum()
print(f"\n빈 값 합계: {total_missing}건")

print()
print("=" * 60)
print("4. 요약 — df.describe() (평균과 최소·최대 범위)")
print("=" * 60)
print(df["거래금액"].describe())
# 최솟값이 0보다 작으면 음수 거래가 섞여 있다는 뜻이라 별도로 짚어줌
min_value = df["거래금액"].min()
if min_value < 0:
    print(f"\n주의: 최솟값이 {min_value:,.0f}원으로 0보다 작음 (음수 거래 존재)")

print()
print("=" * 60)
print("5. 범주 — value_counts(dropna=False) (항목별 개수, 쏠림과 표기 확인)")
print("=" * 60)
print(df["결제수단"].value_counts(dropna=False))
