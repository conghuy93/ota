# Hướng dẫn Bảo mật OTA và Tự động Cập nhật

## 🔒 Bảo mật OTA

### 1. Authentication System

Hệ thống hỗ trợ 2 loại authentication:

#### API Key (Cho Developer/Admin)
- Dùng để upload firmware, quản lý
- Tạo API key:
  ```bash
  curl -X POST "http://localhost:8000/api/auth/generate-key?name=my-key"
  ```

#### Device Token (Cho Thiết bị)
- JWT token cho từng device
- Đăng ký device:
  ```bash
  curl -X POST "http://localhost:8000/api/auth/register" \
    -H "X-API-Key: your_api_key" \
    -H "Content-Type: application/json" \
    -d '{"device_id": "ESP32_001", "device_name": "Device 1"}'
  ```

### 2. Bảo vệ API Endpoints

Tất cả API endpoints đã được bảo vệ:

- `/api/check-update` - Yêu cầu API key hoặc device token
- `/api/download/{version}` - Yêu cầu API key hoặc device token
- `/api/firmwares` - Yêu cầu API key hoặc device token
- `/api/upload` - Chỉ API key (admin)
- `/api/firmware/{version}` - Chỉ API key (admin)

### 3. Sử dụng Authentication trong Client

```python
from client.ota_client import OTAClient

# Với API key
client = OTAClient(
    server_url="http://localhost:8000",
    device_id="ESP32_001",
    api_key="your_api_key_here"
)

# Hoặc với device token
client = OTAClient(
    server_url="http://localhost:8000",
    device_id="ESP32_001",
    device_token="your_device_token_here"
)
```

---

## 🤖 Tự động Cập nhật (Không cần khách tải)

### Auto OTA Client

Client tự động kiểm tra và cập nhật firmware định kỳ:

```python
from client.auto_ota_client import AutoOTAClient

# Khởi tạo
auto_client = AutoOTAClient(
    server_url="http://localhost:8000",
    device_id="ESP32_001",
    device_token="your_device_token",  # Nếu server yêu cầu auth
    check_interval_minutes=60,  # Kiểm tra mỗi 60 phút
    auto_install=True  # Tự động cài đặt
)

# Thiết lập phiên bản hiện tại
auto_client.set_current_version("1.0.0")

# Hàm cài đặt firmware
def install_firmware(file_path):
    print(f"Cài đặt firmware: {file_path}")
    # Logic flash firmware của bạn
    # Ví dụ ESP32:
    #   import esptool
    #   esptool.write_flash(0x1000, file_path)

# Thiết lập callbacks
auto_client.set_install_callback(install_firmware)

# Bắt đầu tự động kiểm tra
auto_client.start()

# Giữ chương trình chạy
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    auto_client.stop()
```

### Tính năng:

- ✅ Tự động kiểm tra định kỳ (có thể cấu hình)
- ✅ Tự động tải và cài đặt firmware mới
- ✅ Chạy ở background, không cần can thiệp
- ✅ Xác minh checksum tự động
- ✅ Logging đầy đủ

---

## 📋 Workflow Hoàn chỉnh

### Bước 1: Tạo API Key (Developer)

```bash
# Tạo API key đầu tiên (có thể cần admin)
curl -X POST "http://localhost:8000/api/auth/generate-key?name=admin-key"
```

Response:
```json
{
  "api_key": "abc123...",
  "name": "admin-key",
  "message": "API key generated. Save it securely!"
}
```

### Bước 2: Đăng ký Device

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_001",
    "device_name": "Living Room Sensor",
    "device_type": "ESP32"
  }'
```

Response:
```json
{
  "device_id": "ESP32_001",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "Device registered successfully"
}
```

### Bước 3: Upload Firmware (Developer)

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "X-API-Key: your_api_key" \
  -F "file=@firmware.bin" \
  -F "version=1.0.1" \
  -F "description=Fix bugs"
```

### Bước 4: Device Tự động Cập nhật

Device chạy Auto OTA Client sẽ tự động:
1. Kiểm tra firmware mới mỗi 60 phút (hoặc interval bạn set)
2. Tải firmware nếu có version mới
3. Xác minh checksum
4. Tự động flash firmware
5. Khởi động lại với firmware mới

---

## 🔐 Bảo mật Nâng cao

### 1. Sử dụng HTTPS

Luôn sử dụng HTTPS trong production:

```python
# Server
uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

# Client
client = OTAClient(server_url="https://your-server.com")
```

### 2. Rotate API Keys

Định kỳ thay đổi API keys:

```python
# Tạo key mới
# Cập nhật tất cả devices
# Xóa key cũ
```

### 3. Rate Limiting

Thêm rate limiting để tránh abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/check-update")
@limiter.limit("10/minute")
async def check_update(...):
    ...
```

### 4. Device Whitelist

Chỉ cho phép devices đã đăng ký:

```python
# Trong auth.py
ALLOWED_DEVICES = ["ESP32_001", "ESP32_002"]

def verify_device_token(token):
    device_id = decode_token(token)
    if device_id not in ALLOWED_DEVICES:
        raise HTTPException(401, "Device not authorized")
    return device_id
```

---

## 📱 Ví dụ: ESP32 Auto OTA

```python
# main.py trên ESP32
from client.auto_ota_client import AutoOTAClient
import esptool

SERVER_URL = "https://your-server.com"
DEVICE_ID = "ESP32_001"
DEVICE_TOKEN = "your_token_here"

def flash_firmware(file_path):
    """Flash firmware vào ESP32"""
    esptool.write_flash(
        address=0x1000,
        filename=str(file_path),
        port="/dev/ttyUSB0"
    )

auto_client = AutoOTAClient(
    server_url=SERVER_URL,
    device_id=DEVICE_ID,
    device_token=DEVICE_TOKEN,
    check_interval_minutes=60,
    auto_install=True
)

auto_client.set_current_version("1.0.0")
auto_client.set_install_callback(flash_firmware)
auto_client.start()

# Main loop của ESP32
while True:
    # Code chính của bạn
    pass
```

---

## ✅ Checklist Bảo mật

- [ ] Đã tạo API keys và lưu an toàn
- [ ] Đã đăng ký tất cả devices
- [ ] Đã cấu hình HTTPS (production)
- [ ] Đã test authentication
- [ ] Đã test auto update
- [ ] Đã backup API keys và tokens
- [ ] Đã cấu hình rate limiting (nếu cần)
- [ ] Đã test với device thật

---

## 🆘 Troubleshooting

### Lỗi 401 Unauthorized

- Kiểm tra API key/device token đúng chưa
- Kiểm tra header format: `X-API-Key: your_key` hoặc `Authorization: Bearer your_token`
- Kiểm tra token chưa hết hạn

### Device không tự động cập nhật

- Kiểm tra Auto OTA Client đã start chưa
- Kiểm tra check_interval
- Kiểm tra auto_install = True
- Kiểm tra install_callback đã set chưa
- Xem logs để debug

### Token hết hạn

- Device token mặc định hết hạn sau 30 ngày
- Đăng ký lại device để nhận token mới
- Hoặc tăng expires_hours trong `generate_device_token()`

