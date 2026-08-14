# data/01_핀테크결제_dirty.csv 원본에서 지역·결제수단·연령대별 거래금액 합계를
# 각각 큰 순서 가로 막대그래프로 그리는 스크립트. (정제 전 원본 파일 그대로 사용)

import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

plt.rcParams["font.family"] = "Malgun Gothic"   # 한글이 네모로 깨지지 않게
plt.rcParams["axes.unicode_minus"] = False      # 마이너스 기호 깨짐 방지

df = pd.read_csv(os.path.join("data", "01_핀테크결제_dirty.csv"), encoding="utf-8-sig")

output_dir = os.path.join("output", "charts")
os.makedirs(output_dir, exist_ok=True)


def draw_horizontal_bar(column, title, filename):
    # 오름차순으로 정렬해야 barh 에서 위쪽에 가장 큰 값이 오게 된다 (큰 순서로 보이게 하는 핵심)
    by_group = df.groupby(column)["거래금액"].sum().sort_values(ascending=True)

    print(f"{column}별 거래금액 합계 (큰 순서):")
    print(by_group.sort_values(ascending=False))
    print()

    # 지역은 카테고리가 17개라 그래프가 길어지므로 세로 크기를 값 개수에 맞춰 늘림
    fig_height = max(4, 0.4 * len(by_group))
    fig, ax = plt.subplots(figsize=(10, fig_height))
    bars = ax.barh(by_group.index, by_group.values, color="#4C72B0")
    ax.set_title(title)
    ax.set_xlabel("거래금액 합계 (원)")
    ax.set_ylabel(column)

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {width:,.0f}",
            ha="left",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"저장 경로: {output_path}")
    print()


draw_horizontal_bar("지역", "지역별 거래금액 합계 (큰 순서)", "지역별_거래금액_가로막대.png")
draw_horizontal_bar("결제수단", "결제수단별 거래금액 합계 (큰 순서)", "결제수단별_거래금액_가로막대.png")
draw_horizontal_bar("연령대", "연령대별 거래금액 합계 (큰 순서)", "연령대별_거래금액_가로막대.png")
