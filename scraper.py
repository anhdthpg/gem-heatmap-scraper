import os
import json
import requests
from playwright.sync_api import sync_playwright

GAS_URL = os.environ.get("GAS_WEB_APP_URL")

def run(playwright):
    # Bổ sung thêm các tham số để ngụy trang trình duyệt tốt hơn
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled', 
            '--no-sandbox', 
            '--disable-setuid-sandbox'
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()

    print("1. Đang truy cập Coinglass...")
    try:
        # Bắt buộc chỉ đợi tối đa 60 giây. Không đợi load 100% tài nguyên ảnh/video
        page.goto("https://www.coinglass.com/pro/futures/LiquidationHeatMap", timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(10000) # Đợi thêm 10s cho JS tự động giải mã
    except Exception as e:
        print(f"Cảnh báo: Tải trang chậm hoặc bị chặn - {e}")

    print("2. Đang kiểm tra trạng thái trang...")
    try:
        title = page.title()
        print(f"Tiêu đề trang hiện tại: {title}")
        
        # Nếu tiêu đề có chữ này, đích thị là bị Cloudflare chặn
        if "Just a moment" in title or "Cloudflare" in title:
            raise Exception("Bị hệ thống chống Bot (Cloudflare) chặn lại ở ngoài cửa.")
            
        next_data_text = page.locator("#__NEXT_DATA__").inner_text(timeout=5000)
        parsed_data = json.loads(next_data_text)
        
        payload = {
            "status": "Thành công",
            "data_length": len(next_data_text),
            "raw_data": parsed_data
        }
    except Exception as e:
        payload = {
            "status": "Thất bại",
            "error_msg": str(e),
            "page_title": page.title()
        }

    print("3. Đang gửi báo cáo về trạm GAS...")
    response = requests.post(GAS_URL, json=payload)
    print(f"Mã phản hồi từ GAS: {response.status_code}")
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
