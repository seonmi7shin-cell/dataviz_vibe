# 핀테크 결제 데이터(data/01_핀테크결제_dirty.csv)를 정해진 순서대로 정제해서
# data/핀테크_정제완료.csv 로 저장하는 스크립트.
# 순서를 바꾸면 남는 행 수가 달라지므로 CLAUDE.md에 정해둔 순서를 그대로 따른다:
#   1) 범주 컬럼 결측 채우기  2) 거래일시·거래금액 결측 행 삭제  3) 완전 중복 제거
#   4) 음수 거래금액 제거 (이상치 처리 지시에 따라 추가된 단계, 반드시 3단계 이후)

import os
import pandas as pd

# 스크립트가 scripts 폴더 안에 있으므로 상위 폴더로 이동해야 data/ 를 찾을 수 있음.
# 이 줄이 없으면 다른 폴더에서 실행할 때 FileNotFoundError 가 난다.
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

INPUT_PATH = os.path.join("data", "01_핀테크결제_dirty.csv")
OUTPUT_PATH = os.path.join("data", "핀테크_정제완료.csv")

df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
before = len(df)
print(f"원본 행 수: {before}")

# 1단계: 범주 컬럼 결측 채우기 (행은 지우지 않음)
# 결제수단·지역은 카테고리 수가 많고 "어떤 값인지 모른다"는 뜻으로 알수없음 처리,
# 연령대만 관례상 미상으로 구분해 표기한다.
df["결제수단"] = df["결제수단"].fillna("알수없음")
df["지역"] = df["지역"].fillna("알수없음")
df["연령대"] = df["연령대"].fillna("미상")
print(f"1단계 완료 (결측 채움, 행 수 변화 없음): {len(df)}행")

# 2단계: 거래일시·거래금액 결측 행 삭제
# 금액이 없으면 합계에 넣을 수 없고, 날짜가 없으면 월별로 묶을 수 없어 분석 자체가 불가능하다.
step2_before = len(df)
df = df.dropna(subset=["거래일시", "거래금액"])
print(f"2단계 완료 (거래일시·거래금액 결측 행 삭제): {step2_before}행 -> {len(df)}행 ({step2_before - len(df)}행 삭제)")

# 3단계: 완전 중복 제거 (반드시 마지막 단계)
# 모든 컬럼 값이 같은 행만 제거 대상이며, 먼저 나온 행을 남긴다.
# 1·2단계보다 먼저 하면 결측 처리 전/후 값이 달라 중복 판정 기준이 흔들리므로 순서를 지켜야 한다.
step3_before = len(df)
df = df.drop_duplicates(keep="first")
print(f"3단계 완료 (완전 중복 제거): {step3_before}행 -> {len(df)}행 ({step3_before - len(df)}행 삭제)")

# 4단계: 음수 거래금액 제거
# 환불·오류로 보이는 음수 거래가 섞여 있으면 합계·평균이 실제보다 낮게 나와 모든 집계·그래프가
# 왜곡된다. 이상치 처리는 원래 별도 지시가 있을 때만 하는데, 이번에 지시가 있어 추가한다.
step4_before = len(df)
df = df[df["거래금액"] >= 0]
print(f"4단계 완료 (음수 거래금액 제거): {step4_before}행 -> {len(df)}행 ({step4_before - len(df)}행 삭제)")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print()
print(f"최종 행 수: {len(df)} (원본 {before}행에서 {before - len(df)}행 감소)")
print(f"저장 경로: {OUTPUT_PATH}")
