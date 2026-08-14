# Streamlit 대시보드(http://localhost:8501)를 Playwright 로 조작하면서 화면을 mp4 영상으로
# 녹화하는 스크립트. record_video_dir 를 지정한 브라우저 컨텍스트를 새로 열어야 녹화가 시작되고,
# context.close() 를 호출해야 그 시점까지의 내용이 실제 mp4 파일로 저장(마무리)된다.

import os
import time
from playwright.sync_api import sync_playwright

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

VIDEO_DIR = os.path.join("output", "ui_test", "video")
os.makedirs(VIDEO_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        record_video_dir=VIDEO_DIR,
        record_video_size={"width": 1440, "height": 900},
    )
    page = context.new_page()

    page.goto("http://localhost:8501")
    page.wait_for_selector("text=핀테크 결제 데이터 대시보드", timeout=15000)
    time.sleep(1.5)  # 첫 렌더링이 끝나는 걸 화면에 담기 위한 최소 대기

    # 탭을 하나씩 눌러보며 각 화면을 영상에 담는다
    for tab_name in ["개요", "업종별", "지역별", "월별 추이", "원본 데이터"]:
        tab = page.get_by_role("tab", name=tab_name)
        tab.click()
        time.sleep(1.2)

    # 사이드바 필터도 조작해서 "화면이 다시 그려지는" 인터랙션까지 녹화에 담는다
    region_filter = page.get_by_text("지역", exact=True).first
    region_filter.click()
    time.sleep(0.8)
    page.keyboard.press("Escape")
    time.sleep(1.0)

    context.close()  # 이 시점에 mp4 파일이 최종 저장된다
    browser.close()

    video_path = page.video.path()
    print(f"영상 저장 경로: {video_path}")
