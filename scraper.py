import os
import requests
from playwright.sync_api import sync_playwright

GAS_URL = os.environ.get("GAS_WEB_APP_URL")

def run(playwright):
    browser = playwright.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-setuid-sandbox']
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()

    # ĐOẠN MÃ GIÁN ĐIỆP (MONKEY PATCHING)
    # Tiêm vào trình duyệt trước khi tải trang để hứng dữ liệu đã được Coinglass giải mã
    page.add_init_script("""
        window.__STOLEN_DATA__ = null;
        let maxDataSize = 0;
        
        const originalParse = JSON.parse;
        JSON.parse = function(text, reviver) {
            const result = originalParse(text, reviver);
            try {
                // Dữ liệu Heatmap rất lớn. Ta sẽ bắt cục JSON nào to nhất được parse trên trang.
                if (text && text.length > 20000) { 
                    if (text.length > maxDataSize) {
                        maxDataSize = text.length;
                        window.__STOLEN_DATA__ = result; // Lén lưu trữ lại
                    }
                }
            } catch(e) {}
            return result;
        };
    """)

    print("1. Đang truy cập Coinglass và chờ trình duyệt tự động giải mã AES...")
    try:
        # Load trang và đợi 15 giây để script trên web tự chạy và vẽ biểu đồ
        page.goto("https://www.coinglass.com/pro/futures/LiquidationHeatMap", timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(15000) 
    except Exception as e:
        print(f"Cảnh báo tải trang: {e}")

    print("2. Đang thu thập dữ liệu từ 'Điệp viên'...")
    try:
        # Rút cục dữ liệu đã chộp được từ biến toàn cục của trình duyệt ra
        stolen_data = page.evaluate("() => window.__STOLEN_DATA__")
        
        if stolen_data:
            payload = {
                "status": "Thành công - Đã chộp được dữ liệu sau giải mã",
                "data_type": "Decrypted_Heatmap_Data",
                "data": stolen_data
            }
        else:
             payload = {
                "status": "Thất bại",
                "error_msg": "Không bắt được dữ liệu. Web có thể chưa giải mã xong hoặc bị lỗi hiển thị."
            }
    except Exception as e:
        payload = {
            "status": "Lỗi trích xuất",
            "error_msg": str(e)
        }

    print("3. Đang gửi dữ liệu thô về trạm GAS...")
    response = requests.post(GAS_URL, json=payload)
    print(f"Mã phản hồi từ GAS: {response.status_code}")
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
