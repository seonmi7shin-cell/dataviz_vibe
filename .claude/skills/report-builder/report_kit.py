# -*- coding: utf-8 -*-
"""보고서 PDF 를 만드는 부품 모음 (report-builder 스킬 전용).

이 파일은 수강생이 읽거나 고치는 파일이 아닙니다. 폰트 등록, 표 스타일, 문서 조립처럼
매번 똑같이 반복되는 reportlab 배관 작업을 이 안에 가둬 두고, 내용(어떤 값을 넣을지)만
바깥에서 채우도록 만든 부품 모음입니다.

가져다 쓰는 쪽(스킬이 새로 쓰는 build_report.py)에서는 이 파일의 함수 이름만 알면 됩니다.
"""
import math
import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

NAVY = colors.HexColor("#1C1840")
TINT = colors.HexColor("#EEE9FC")
GREY = colors.HexColor("#6B7280")
PURPLE = "#6C3FE0"
PURPLE_C = colors.HexColor(PURPLE)

_fonts_ready = False


def register_korean_fonts():
    """한글 폰트를 PDF 에 등록. 보고서를 만들기 전 한 번만 호출하면 됨."""
    global _fonts_ready
    if _fonts_ready:
        return
    pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
    pdfmetrics.registerFont(TTFont("MalgunBd", "C:/Windows/Fonts/malgunbd.ttf"))
    _fonts_ready = True


def styles():
    register_korean_fonts()
    _b = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=_b["Title"], fontName="MalgunBd", fontSize=21,
                                textColor=NAVY, leading=27, spaceAfter=4),
        "sub": ParagraphStyle("s", parent=_b["Normal"], fontName="Malgun", fontSize=10,
                              textColor=GREY, alignment=TA_CENTER, spaceAfter=15),
        "h2": ParagraphStyle("h2", parent=_b["Heading2"], fontName="MalgunBd", fontSize=13.5,
                             textColor=PURPLE_C, spaceBefore=13, spaceAfter=7, leading=18),
        "body": ParagraphStyle("b", parent=_b["Normal"], fontName="Malgun", fontSize=10.2,
                               leading=16.5, spaceAfter=6),
        "cap": ParagraphStyle("c", parent=_b["Normal"], fontName="Malgun", fontSize=8.5,
                              textColor=GREY, alignment=TA_CENTER, spaceAfter=10),
    }


def title_block(story, S, title, sub):
    story.append(Paragraph(title, S["title"]))
    story.append(Paragraph(sub, S["sub"]))


def heading(story, S, text):
    story.append(Paragraph(text, S["h2"]))


def body(story, S, text):
    story.append(Paragraph(text, S["body"]))


def kv_table(rows):
    """'항목 - 값' 두 칸짜리 요약 표. rows = [(항목, 값), ...]"""
    t = Table([[k, v] for k, v in rows], colWidths=[58 * mm, 102 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Malgun"),
        ("FONTNAME", (0, 0), (0, -1), "MalgunBd"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), PURPLE_C),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, TINT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E7E3F2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def grid_table(header, body_rows, widths):
    """제목 줄이 있는 일반 표. header = 열 이름 목록, body_rows = 행 목록"""
    t = Table([header] + body_rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE_C),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "MalgunBd"),
        ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.2),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TINT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E7E3F2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    return t


def chart_image(story, S, path, caption, width=170 * mm):
    story.append(Image(path, width=width, height=width * 0.52))
    story.append(Paragraph(caption, S["cap"]))


def page_break(story):
    story.append(PageBreak())


def spacer(story, h=8):
    story.append(Spacer(1, h * mm))


def save(story, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            topMargin=18 * mm, bottomMargin=16 * mm,
                            leftMargin=20 * mm, rightMargin=20 * mm)
    doc.build(story)
    return out_path


def save_chart(fig, out_path):
    """matplotlib Figure 를 PDF 에 붙일 PNG 로 저장."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    return out_path
