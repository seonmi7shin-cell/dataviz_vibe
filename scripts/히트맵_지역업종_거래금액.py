# data/핀테크_정제완료.csv 에서 지역×업종 교차 거래금액 합계를 히트맵으로 그리는 스크립트.
# 히트맵은 "하나의 측정값(거래금액)의 크기"를 보여주는 것이라 단일 색상(블루) 농도로 표현한다
# — 색이 여러 개면 정체성(범주) 인코딩과 혼동되므로 크기 인코딩엔 항상 한 가지 색만 쓴다.

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "핀테크_정제완료.csv"), encoding="utf-8-sig")

# 지역을 행, 업종을 열로 놓고 거래금액 합계를 교차 집계. 없는 조합은 0으로 채움
pivot = df.pivot_table(
    index="지역", columns="가맹점업종", values="거래금액", aggfunc="sum", fill_value=0
)

# "알수없음"은 실제 지역이 아니라 정제 단계에서 지역 결측(475건)을 채운 표시값이라
# 진짜 지역들과 순위 비교에 섞이지 않도록 분리해서 맨 아래에 따로 둔다.
unknown_label = "알수없음"
known = pivot.drop(index=unknown_label, errors="ignore")
known = known.sort_index(ascending=True)  # 지역 이름(문자열) 가나다 기준 오름차순 정렬
if unknown_label in pivot.index:
    pivot = pd.concat([known, pivot.loc[[unknown_label]]])
else:
    pivot = known

print("지역×업종 거래금액 합계 (교차표):")
print(pivot)

# dataviz 스킬의 검증된 순차(sequential) 블루 램프(references/palette.md 100~700 단계)를
# 그대로 이어 붙여 "값이 작으면 밝고 크면 진한" 단일 색조 그라데이션을 만든다
blue_ramp = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
cmap = LinearSegmentedColormap.from_list("blue_sequential", blue_ramp)

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(pivot.values, cmap=cmap, aspect="auto")

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_title("지역×업종 거래금액 합계 히트맵")

# 알수없음 행을 실제 지역과 시각적으로 분리하기 위해 구분선을 그음
if unknown_label in pivot.index:
    boundary = pivot.index.get_loc(unknown_label) - 0.5
    ax.axhline(boundary, color="black", linewidth=1.5)

cbar = fig.colorbar(im, ax=ax)
cbar.set_label("거래금액 합계 (원)")

# 칸마다 값을 적되, 배경이 진하면(값이 크면) 흰 글씨로 바꿔야 안 보이는 문제를 막음.
# 단위를 천원으로 줄여야 칸 안에 숫자가 겹치지 않고 들어간다
vmax = pivot.values.max()
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        value = pivot.values[i, j]
        text_color = "white" if value > vmax * 0.6 else "black"
        ax.text(j, i, f"{value/1e3:,.0f}", ha="center", va="center", color=text_color, fontsize=8)

plt.tight_layout()

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "지역업종_거래금액_히트맵.png")
plt.savefig(output_path, dpi=150)
print(f"저장 경로: {output_path}")
print("(칸 안 숫자 단위: 천원)")

# savefig 로 먼저 저장한 뒤에 show 를 호출해야 함 (순서를 바꾸면 show 이후 캔버스가
# 초기화되어 빈 파일이 저장될 수 있음)
plt.show()
