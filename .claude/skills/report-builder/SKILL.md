---
name: report-builder
description: |
  이 스킬은 "보고서 PDF 만들어 줘", "분석 보고서로 뽑아 줘", "PDF로 정리해 줘",
  "표랑 차트 넣어서 보고서 만들어 줘"처럼 데이터를 분석해 배포용 PDF 보고서를 만들라는
  요청에 사용한다. reportlab 문서 조립·한글 폰트 등록·표 스타일 같은 반복 작업은
  이 스킬이 가진 report_kit.py 가 대신 처리하므로, 그 내부 코드를 다시 설명하거나
  처음부터 새로 짜지 않는다.
allowed-tools: [Read, Write, Bash]
---

# report-builder

CSV 데이터를 분석해 표지·요약·표·차트가 들어간 PDF 보고서를 만드는 스킬.

## 이 스킬이 없으면 벌어지는 일

reportlab 은 PDF 를 코드로 조립하는 도구라 한글 폰트 등록, 표 스타일, 문서 조립까지
매번 30줄 넘는 배관 코드가 필요하다. 보고서마다 이 코드를 새로 쓰면 시간도 오래 걸리고
오타 하나로 한글이 깨진다. 이 스킬은 그 배관 코드를 `report_kit.py` 에 가둬 두고
**내용만** 채우면 되게 만든다.

## 쓰는 법

1. `report_kit.py` (이 스킬 폴더 안)을 임포트한다. 함수 이름만 알면 됨:
   - `styles()` — 제목·본문·표 글꼴 스타일 묶음 (호출 한 번으로 한글 폰트까지 등록됨)
   - `title_block(story, S, title, sub)` — 표지 제목과 부제
   - `heading(story, S, text)` / `body(story, S, text)` — 절 제목과 본문 문단
   - `kv_table(rows)` — "항목 - 값" 두 칸 표. `rows = [("총 거래금액", "5.76억원"), ...]`
   - `grid_table(header, body_rows, widths)` — 머리글 있는 일반 표
   - `chart_image(story, S, png_path, caption)` — 미리 저장한 차트 PNG 를 보고서에 붙임
   - `page_break(story)` — 새 쪽에서 시작
   - `save(story, out_path)` — 지금까지 담은 내용을 실제 PDF 파일로 씀

2. 차트가 필요하면 matplotlib 으로 그리고 `report_kit.save_chart(fig, path)` 로
   PNG 로 먼저 저장한 뒤 `chart_image()` 로 붙인다. (PDF 는 그림을 "붙이는" 방식이라
   차트가 먼저 파일로 있어야 함)

3. 표에 넣을 숫자는 pandas 로 직접 집계한다 (groupby, agg 등 — 이 부분은 이미 배운 문법
   그대로 씀). 이 스킬이 대신하는 것은 "그 숫자를 PDF 안에 예쁘게 앉히는 것"이지
   "숫자를 계산하는 것"이 아니다.

4. 완성된 `story` 목록을 `report_kit.save(story, "output/report/파일명.pdf")` 로 저장한다.

## 최소 예시

```python
import sys
sys.path.insert(0, ".claude/skills/report-builder")
import report_kit as rk

S = rk.styles()
story = []
rk.title_block(story, S, "핀테크 결제 데이터 분석 보고서", "분석 기간 2024-01 ~ 2024-12")
rk.heading(story, S, "1. 요약")
rk.body(story, S, "총 거래금액은 5.76억원이며 성공률은 92.4퍼센트입니다.")
rk.heading(story, S, "2. 전체 지표")
story.append(rk.kv_table([("거래 건수", "11,713건"), ("총 거래금액", "576,225,159원")]))
rk.save(story, "output/report/분석보고서.pdf")
```

## 스킬을 쓸 때와 안 쓸 때

| 상황 | 방식 |
|------|------|
| "보고서 PDF 만들어 줘" | 이 스킬로 report_kit 을 가져다 씀 |
| "마크다운으로 정리해 줘" | 이 스킬 필요 없음 (파일 쓰기만) |
| "PDF 레이아웃 자체를 바꾸고 싶어" | report_kit.py 함수를 확장 (드물게만) |

## 검수

만든 뒤에는 `output/report/` 안 PDF 파일 크기와 쪽 수를 확인하고, 표의 합계가
원본 CSV 집계와 같은지 한 번 대조한다. 지어낸 숫자가 들어가면 안 된다.
