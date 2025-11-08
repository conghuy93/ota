# Hướng dẫn Gửi Firmware cho Khách hàng

## 🚀 Cách nhanh nhất (5 phút)

### Bước 1: Khởi động server với ngrok

**Windows:**
```bash
start_with_ngrok.bat
```

**Linux/Mac:**
```bash
chmod +x start_with_ngrok.sh
./start_with_ngrok.sh
```

### Bước 2: Lấy URL công khai

1. Mở trình duyệt: http://localhost:4040
2. Tìm dòng "Forwarding": `https://abc123.ngrok.io -> http://localhost:8000`
3. Copy URL: `https://abc123.ngrok.io`

### Bước 3: Upload firmware qua Web UI

1. Mở: http://localhost:8000
2. Kéo thả file firmware vào vùng upload
3. Nhập version (ví dụ: `1.0.1`)
4. Nhập mô tả (tùy chọn)
5. Click "Upload Firmware"

### Bước 4: Gửi thông tin cho khách

Gửi cho khách hàng:

```
🔧 OTA Server URL: https://abc123.ngrok.io

📋 Hướng dẫn sử dụng:

1. Cài đặt client library:
   pip install requests

2. Sử dụng code mẫu:
   (Gửi kèm file client/example_remote.py)

3. Cấu hình:
   - SERVER_URL = "https://abc123.ngrok.io"
   - DEVICE_ID = "device_cua_ban"
   - CURRENT_VERSION = "1.0.0"  # Phiên bản hiện tại

4. Chạy:
   python client/example_remote.py
```

---

## 📝 Code mẫu cho khách hàng

### Python (Full)

```python
from client.ota_client import OTAClient

# URL server bạn cung cấp
SERVER_URL = "https://abc123.ngrok.io"
DEVICE_ID = "device_001"
CURRENT_VERSION = "1.0.0"

client = OTAClient(SERVER_URL, DEVICE_ID)
client.set_current_version(CURRENT_VERSION)

def install_firmware(file_path):
    print(f"Cài đặt firmware: {file_path}")
    # Logic cài đặt của bạn

result = client.update_firmware(install_callback=install_firmware)
```

### ESP32/ESP8266 (MicroPython)

```python
import urequests
import uhashlib

SERVER_URL = "https://abc123.ngrok.io"
CURRENT_VERSION = "1.0.0"

def check_and_update():
    # Kiểm tra update
    response = urequests.post(
        f"{SERVER_URL}/api/check-update",
        json={"current_version": CURRENT_VERSION}
    )
    data = response.json()
    
    if data.get("update_available"):
        fw_info = data["firmware_info"]
        
        # Tải firmware
        firmware = urequests.get(
            f"{SERVER_URL}{fw_info['download_url']}"
        ).content
        
        # Xác minh checksum
        checksum = uhashlib.sha256(firmware).hexdigest()
        if checksum == fw_info["checksum"]:
            # Flash firmware
            # ... logic của bạn
            pass
```

### HTTP API (Bất kỳ ngôn ngữ nào)

```bash
# 1. Kiểm tra update
curl -X POST "https://abc123.ngrok.io/api/check-update" \
  -H "Content-Type: application/json" \
  -d '{"current_version": "1.0.0", "device_id": "device_001"}'

# 2. Tải firmware (nếu có update)
curl -O "https://abc123.ngrok.io/api/download/1.0.1"
```

---

## 🔒 Bảo mật (Tùy chọn)

### Thêm API Key

Sửa `server/main.py`:

```python
API_KEY = "your-secret-key-12345"

@app.post("/api/upload")
async def upload_firmware(
    file: UploadFile = File(...),
    version: str = None,
    description: str = None,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    # ... rest
```

Gửi API key cho khách:

```python
headers = {"X-API-Key": "your-secret-key-12345"}
response = requests.post(url, headers=headers, ...)
```

---

## 🌐 Deploy lên Cloud (Cho production)

### Heroku (Miễn phí)

```bash
# Tạo Procfile
echo "web: uvicorn server.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create ota-firmware-server
git push heroku main

# URL sẽ là: https://ota-firmware-server.herokuapp.com
```

### DigitalOcean / AWS

1. Tạo VPS/EC2
2. Cài Python, dependencies
3. Chạy server với systemd
4. Cấu hình firewall
5. (Tùy chọn) Thêm domain + SSL

Xem chi tiết trong [DEPLOYMENT.md](DEPLOYMENT.md)

---

## ✅ Checklist

Trước khi gửi cho khách:

- [ ] Server đã chạy và test thành công
- [ ] Đã có URL công khai (ngrok hoặc cloud)
- [ ] Đã upload firmware test
- [ ] Test client có thể kết nối được
- [ ] Đã cung cấp code mẫu cho khách
- [ ] (Tùy chọn) Đã thêm authentication
- [ ] (Tùy chọn) Đã cấu hình HTTPS

---

## 🆘 Troubleshooting

### Khách không kết nối được

1. **Kiểm tra server:**
   ```bash
   curl http://localhost:8000/api/firmwares
   ```

2. **Kiểm tra ngrok:**
   - Mở http://localhost:4040
   - Xem requests có đến không

3. **Kiểm tra URL:**
   - Test URL trong trình duyệt
   - Đảm bảo URL đúng (có https://)

### Ngrok URL thay đổi

- Đăng ký tài khoản ngrok miễn phí
- Cấu hình domain tĩnh
- Hoặc deploy lên cloud để có URL cố định

---

## 📞 Hỗ trợ

Nếu khách hàng gặp vấn đề:

1. Kiểm tra log server
2. Kiểm tra ngrok dashboard (nếu dùng ngrok)
3. Test API trực tiếp: `curl https://your-url/api/firmwares`
4. Kiểm tra firewall/network

