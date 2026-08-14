# Streamlit 대시보드(http://localhost:8501)를 Playwright 로 조작하면서 화면을 mp4(webm) 영상으로
# 녹화하는 스크립트. 헤드리스 브라우저는 원래 마우스 커서가 화면에 안 보이므로, 클릭할 때마다
# 어디를 눌렀는지 보이도록 가짜 커서 점 + 클릭 물결(ripple) 효과를 직접 그려 넣는다.
# 재생 속도는 그냥 실제 시간 그대로 녹화되는 1배속이고(별도 배속 조정 없음), 각 동작 사이에
# 충분한 대기시간을 둬서 실제 사람이 천천히 클릭하는 것처럼 보이게 한다.

import os
import time
from playwright.sync_api import sync_playwright

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

VIDEO_DIR = os.path.join("output", "ui_test", "video")
os.makedirs(VIDEO_DIR, exist_ok=True)

CURSOR_SETUP_JS = """
() => {
  const cursor = document.createElement('div');
  cursor.id = '__fake_cursor';
  cursor.style.cssText = `
    position:fixed; width:22px; height:22px; border-radius:50%;
    background:rgba(42,120,214,0.9); border:3px solid white;
    box-shadow:0 2px 8px rgba(0,0,0,0.45); pointer-events:none;
    z-index:999999; transform:translate(-50%,-50%);
    transition:left 0.5s cubic-bezier(.4,0,.2,1), top 0.5s cubic-bezier(.4,0,.2,1);
    left:-50px; top:-50px;
  `;
  document.body.appendChild(cursor);

  const style = document.createElement('style');
  style.textContent = `
    @keyframes __cursor_ripple {
      from { width:16px; height:16px; opacity:0.6; }
      to   { width:60px; height:60px; opacity:0; }
    }
  `;
  document.head.appendChild(style);
}
"""

MOVE_CURSOR_JS = """
([x, y]) => {
  const c = document.getElementById('__fake_cursor');
  if (c) { c.style.left = x + 'px'; c.style.top = y + 'px'; }
}
"""

CLICK_RIPPLE_JS = """
([x, y]) => {
  const ripple = document.createElement('div');
  ripple.style.cssText = `
    position:fixed; left:${x}px; top:${y}px; border-radius:50%;
    background:rgba(42,120,214,0.5); pointer-events:none; z-index:999998;
    transform:translate(-50%,-50%);
    animation:__cursor_ripple 0.6s ease-out forwards;
  `;
  document.body.appendChild(ripple);
  setTimeout(() => ripple.remove(), 700);
}
"""


def move_and_click(page, locator, label):
    # 대상 요소의 화면 좌표를 구해서 그 위치로 가짜 커서를 부드럽게 이동시킨 다음, 클릭 물결
    # 효과를 보여주고 나서 실제 클릭을 한다 — 이 순서를 지켜야 "커서가 옮겨가는 게 보인 다음
    # 클릭했다"는 자연스러운 흐름이 된다.
    box = locator.bounding_box()
    if box is None:
        print(f"[건너뜀] 요소를 찾지 못함: {label}")
        return
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    page.evaluate(MOVE_CURSOR_JS, [x, y])
    time.sleep(0.6)  # CSS transition(0.5초)이 끝날 때까지 기다림
    page.evaluate(CLICK_RIPPLE_JS, [x, y])
    time.sleep(0.3)
    locator.click()
    time.sleep(1.5)  # 클릭 후 화면이 다시 그려지는 걸 영상에 충분히 담기 위한 대기


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
    page.evaluate(CURSOR_SETUP_JS)
    time.sleep(1.5)

    for tab_name in ["개요", "업종별", "지역별", "월별 추이", "원본 데이터"]:
        tab = page.get_by_role("tab", name=tab_name)
        move_and_click(page, tab, f"{tab_name} 탭")

    # 지역 필터 콤보박스도 눌러보는 과정을 보여준 뒤 Escape 로 닫는다
    region_filter = page.get_by_text("지역", exact=True).first
    move_and_click(page, region_filter, "지역 필터")
    page.keyboard.press("Escape")
    time.sleep(1.0)

    context.close()  # 이 시점에 webm 파일이 최종 저장된다
    video_path = page.video.path()
    browser.close()

    print(f"영상 저장 경로: {video_path}")
