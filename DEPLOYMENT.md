# Hướng dẫn Deploy và Chia sẻ OTA Server

## Các cách để khách hàng truy cập server

### Cách 1: Sử dụng ngrok (Nhanh nhất - Khuyến nghị cho test)

**Ưu điểm:** Dễ setup, có URL công khai ngay
**Nhược điểm:** URL thay đổi mỗi lần restart (trừ khi dùng tài khoản trả phí)

#### Bước 1: Cài đặt ngrok
```bash
# Download từ https://ngrok.com/download
# Hoặc dùng chocolatey (Windows)
choco install ngrok

# Hoặc dùng npm
npm install -g ngrok
```

#### Bước 2: Khởi động OTA Server
```bash
cd server
python main.py
```

#### Bước 3: Chạy ngrok
```bash
ngrok http 8000
```

Bạn sẽ nhận được URL công khai, ví dụ:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Gửi URL này cho khách hàng!**

#### Bước 4: Cấu hình client của khách
```python
from client.ota_client import OTAClient

# Sử dụng URL ngrok
client = OTAClient(
    server_url="https://abc123.ngrok.io",
    device_id="device_001"
)
```

---

### Cách 2: Port Forwarding (Cho mạng nội bộ/LAN)

**Ưu điểm:** Miễn phí, ổn định
**Nhược điểm:** Cần cấu hình router, chỉ hoạt động trong mạng LAN

#### Bước 1: Tìm IP máy tính
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

Ví dụ: `192.168.1.100`

#### Bước 2: Cấu hình router (nếu cần truy cập từ internet)
- Vào router admin (thường là 192.168.1.1)
- Tìm "Port Forwarding" hoặc "Virtual Server"
- Forward port 8000 đến IP máy tính (192.168.1.100)

#### Bước 3: Khởi động server
```bash
cd server
python main.py
```

#### Bước 4: Gửi URL cho khách
- **Trong mạng LAN:** `http://192.168.1.100:8000`
- **Từ internet:** `http://<public-ip>:8000` (cần port forwarding)

---

### Cách 3: Deploy lên Cloud (Production)

#### Option A: Heroku
```bash
# Tạo Procfile
echo "web: uvicorn server.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create ota-firmware-server
git push heroku main
```

#### Option B: DigitalOcean / AWS / Azure
- Tạo VPS/EC2 instance
- Cài đặt Python và dependencies
- Chạy server với systemd service
- Cấu hình firewall (mở port 8000)

#### Option C: Docker
```bash
# Build image
docker build -t ota-server .

# Run
docker run -p 8000:8000 ota-server
```

---

## Script tự động với ngrok

Tạo script để tự động khởi động server + ngrok:

### Windows (start_with_ngrok.bat)
```batch
@echo off
echo Starting OTA Server with ngrok...

start "OTA Server" cmd /k "cd server && python main.py"
timeout /t 3
start "ngrok" cmd /k "ngrok http 8000"

echo.
echo Server đang chạy tại: http://localhost:8000
echo Kiểm tra ngrok dashboard: http://localhost:4040
echo.
pause
```

### Linux/Mac (start_with_ngrok.sh)
```bash
#!/bin/bash
echo "Starting OTA Server with ngrok..."

cd server
python main.py &
SERVER_PID=$!

sleep 3
ngrok http 8000 &
NGROK_PID=$!

echo "Server PID: $SERVER_PID"
echo "Ngrok PID: $NGROK_PID"
echo "Check ngrok dashboard: http://localhost:4040"
echo "Press Ctrl+C to stop"

wait
```

---

## Bảo mật

### 1. Thêm Authentication (Khuyến nghị cho production)

Sửa `server/main.py` để thêm API key:

```python
from fastapi import Header, HTTPException

API_KEY = "your-secret-key-here"

@app.post("/api/upload")
async def upload_firmware(
    file: UploadFile = File(...),
    version: str = None,
    description: str = None,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    # ... rest of code
```

### 2. Sử dụng HTTPS

- Với ngrok: Tự động có HTTPS
- Với cloud: Cấu hình SSL certificate (Let's Encrypt)
- Với reverse proxy: Sử dụng nginx với SSL

### 3. Rate Limiting

Thêm rate limiting để tránh abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/check-update")
@limiter.limit("10/minute")
async def check_update(...):
    # ...
```

---

## Hướng dẫn cho khách hàng

### Cách 1: Sử dụng Client Library

```python
from client.ota_client import OTAClient

# URL server bạn cung cấp
SERVER_URL = "https://abc123.ngrok.io"  # hoặc IP của bạn

client = OTAClient(SERVER_URL, device_id="device_001")
client.set_current_version("1.0.0")

def install_firmware(file_path):
    # Logic cài đặt firmware của bạn
    print(f"Cài đặt firmware: {file_path}")
    # Flash firmware vào thiết bị...

# Kiểm tra và cập nhật
result = client.update_firmware(install_callback=install_firmware)
```

### Cách 2: Sử dụng API trực tiếp

```python
import requests

SERVER_URL = "https://abc123.ngrok.io"

# Kiểm tra update
response = requests.post(
    f"{SERVER_URL}/api/check-update",
    json={"current_version": "1.0.0", "device_id": "device_001"}
)
data = response.json()

if data.get("update_available"):
    # Tải firmware
    fw_info = data["firmware_info"]
    download_url = f"{SERVER_URL}{fw_info['download_url']}"
    firmware = requests.get(download_url).content
    
    # Xác minh checksum
    import hashlib
    checksum = hashlib.sha256(firmware).hexdigest()
    if checksum == fw_info["checksum"]:
        # Cài đặt firmware
        # ...
```

### Cách 3: ESP32/ESP8266 (MicroPython)

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
        firmware_data = urequests.get(
            f"{SERVER_URL}{fw_info['download_url']}"
        ).content
        
        # Xác minh checksum
        checksum = uhashlib.sha256(firmware_data).hexdigest()
        if checksum == fw_info["checksum"]:
            # Flash firmware
            # ... logic flash firmware của bạn
            pass
```

---

## Checklist trước khi gửi cho khách

- [ ] Server đã chạy và test thành công
- [ ] Có URL/IP công khai (ngrok hoặc cloud)
- [ ] Đã upload firmware test
- [ ] Test client có thể kết nối và tải được
- [ ] Đã cung cấp hướng dẫn cho khách
- [ ] (Tùy chọn) Đã thêm authentication
- [ ] (Tùy chọn) Đã cấu hình HTTPS

---

## Troubleshooting

### Khách không kết nối được
1. Kiểm tra server có đang chạy không
2. Kiểm tra firewall (port 8000)
3. Kiểm tra URL/IP đúng chưa
4. Test từ trình duyệt: `http://your-url/api/firmwares`

### Ngrok URL thay đổi
- Đăng ký tài khoản ngrok miễn phí
- Cấu hình domain tĩnh: `ngrok config add-authtoken <token>`
- Sử dụng: `ngrok http 8000 --domain=your-domain.ngrok.io`

### Lỗi CORS
- Đã cấu hình CORS trong server
- Nếu vẫn lỗi, kiểm tra lại middleware CORS

