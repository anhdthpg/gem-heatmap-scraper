import os
import requests

# Lấy URL ẩn từ Secret
GAS_URL = os.environ.get("GAS_WEB_APP_URL")

# Tạo một dữ liệu thử nghiệm giả lập
test_data = {
    "status": "Thử nghiệm kết nối thành công!",
    "message": "Đường ống từ GitHub về GAS đã thông suốt."
}

print("Đang gửi dữ liệu về GAS...")
response = requests.post(GAS_URL, json=test_data)

print(f"Mã trạng thái: {response.status_code}")
print(f"Phản hồi từ GAS: {response.text}")
