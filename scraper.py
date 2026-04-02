import os
import json
import requests
from playwright.sync_api import sync_playwright

GAS_URL = os.environ.get("GAS_WEB_APP_URL")

def run(playwright):
    # Khởi chạy trình duyệt ẩn với các cấu hình chống nhận diện bot
    browser = playwright.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    print("1. Đang truy cập Coinglass...")
    page.goto("https://www.coinglass.com/pro/futures/LiquidationHeatMap")
    
    # Đợi 15 giây để trang vượt qua tường lửa (nếu có) và tải xong dữ liệu
    page.wait_for_timeout(15000) 

    print("2. Đang trích xuất dữ liệu từ trình duyệt...")
    try:
        # Trang web Coinglass dùng framework Next.js, toàn bộ dữ liệu gốc (đã giải mã) 
        # thường được lưu trong thẻ script ẩn này. Ta sẽ rút nó ra.
        next_data_text = page.locator("#__NEXT_DATA__").inner_text()
        parsed_data = json.loads(next_data_text)
        
        payload = {
            "status": "Thành công",
            "data_length": len(next_data_text),
            "raw_data": parsed_data
        }
    except Exception as e:
        payload = {
            "status": "Lỗi trích xuất hoặc bị Cloudflare chặn",
            "error_msg": str(e)
        }

    print("3. Đang gửi về trạm GAS...")
    response = requests.post(GAS_URL, json=payload)
    print(f"Mã phản hồi từ GAS: {response.status_code}")
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
