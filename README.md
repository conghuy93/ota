# OTA Firmware Update System

Hệ thống OTA (Over-The-Air) để cập nhật firmware tự động cho các thiết bị IoT, ESP32, ESP8266, và các thiết bị nhúng khác.

## Tính năng

- ✅ Server API để quản lý và phân phối firmware
- ✅ Client library để thiết bị kiểm tra và tải firmware tự động
- ✅ Xác minh checksum (SHA256) để đảm bảo tính toàn vẹn
- ✅ So sánh phiên bản tự động
- ✅ Upload firmware qua API
- ✅ Hỗ trợ nhiều phiên bản firmware
- ✅ Progress tracking khi tải firmware

## Cấu trúc thư mục

```
otatoll/
├── server/                 # OTA Server
│   ├── main.py            # Server chính (FastAPI)
│   ├── config.py          # Cấu hình server
│   ├── start_server.sh    # Script khởi động (Linux/Mac)
│   └── start_server.bat   # Script khởi động (Windows)
├── client/                 # OTA Client
│   ├── ota_client.py      # Client library
│   ├── example_device.py   # Ví dụ sử dụng
│   └── config.py          # Cấu hình client
├── firmware/               # Thư mục lưu firmware (tự động tạo)
├── requirements.txt        # Python dependencies
└── README.md              # File này
```

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Khởi động Server

**Windows:**
```bash
cd server
start_server.bat
```

**Linux/Mac:**
```bash
cd server
chmod +x start_server.sh
./start_server.sh
```

**Hoặc chạy trực tiếp:**
```bash
cd server
python main.py
```

Server sẽ chạy tại: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Sử dụng

### Server API

#### 1. Upload Firmware

**Qua Web UI (Swagger):**
- Truy cập: `http://localhost:8000/docs`
- Chọn endpoint `/api/upload`
- Upload file firmware với các thông tin:
  - `file`: File firmware (.bin, .hex, v.v.)
  - `version`: Phiên bản (ví dụ: "1.0.1")
  - `description`: Mô tả (tùy chọn)

**Qua cURL:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@firmware.bin" \
  -F "version=1.0.1" \
  -F "description=Fix bug và cải thiện hiệu suất"
```

**Qua Python:**
```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("firmware.bin", "rb")}
data = {
    "version": "1.0.1",
    "description": "Fix bug và cải thiện hiệu suất"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

#### 2. Kiểm tra Update

```bash
curl -X POST "http://localhost:8000/api/check-update" \
  -H "Content-Type: application/json" \
  -d '{"current_version": "1.0.0", "device_id": "device_001"}'
```

#### 3. Tải Firmware

```bash
curl -O "http://localhost:8000/api/download/1.0.1"
```

#### 4. Liệt kê Firmware

```bash
curl "http://localhost:8000/api/firmwares"
```

### Client (Thiết bị)

#### Cách 1: Sử dụng trực tiếp

```python
from client.ota_client import OTAClient

# Khởi tạo client
client = OTAClient(
    server_url="http://192.168.1.100:8000",
    device_id="ESP32_001"
)

# Thiết lập phiên bản hiện tại
client.set_current_version("1.0.0")

# Kiểm tra và cập nhật
def install_firmware(file_path):
    # Logic cài đặt firmware của bạn
    print(f"Cài đặt firmware từ: {file_path}")
    # Ví dụ: flash firmware vào thiết bị

result = client.update_firmware(install_callback=install_firmware)
print(result)
```

#### Cách 2: Sử dụng example

Chỉnh sửa `client/example_device.py`:
- `SERVER_URL`: URL của OTA server
- `DEVICE_ID`: ID của thiết bị
- `CURRENT_VERSION`: Phiên bản hiện tại
- Hàm `install_firmware()`: Logic cài đặt firmware

Sau đó chạy:
```bash
cd client
python example_device.py
```

## API Endpoints

### `GET /`
Thông tin server và danh sách endpoints

### `POST /api/check-update`
Kiểm tra có firmware mới không

**Request:**
```json
{
  "current_version": "1.0.0",
  "device_id": "device_001"
}
```

**Response:**
```json
{
  "update_available": true,
  "latest_version": "1.0.1",
  "current_version": "1.0.0",
  "firmware_info": {
    "version": "1.0.1",
    "size": 1234567,
    "checksum": "abc123...",
    "description": "...",
    "download_url": "/api/download/1.0.1"
  }
}
```

### `GET /api/download/{version}`
Tải firmware theo phiên bản

### `GET /api/firmwares`
Liệt kê tất cả firmware có sẵn

### `POST /api/upload`
Upload firmware mới

**Form Data:**
- `file`: File firmware
- `version`: Phiên bản (required)
- `description`: Mô tả (optional)

### `DELETE /api/firmware/{version}`
Xóa firmware theo phiên bản

## Cấu hình

### Server

Sửa file `server/config.py` hoặc set environment variables:
- `OTA_SERVER_HOST`: Host (mặc định: 0.0.0.0)
- `OTA_SERVER_PORT`: Port (mặc định: 8000)
- `MAX_UPLOAD_SIZE_MB`: Kích thước upload tối đa (MB)

### Client

Sửa file `client/config.py` hoặc set environment variables:
- `OTA_SERVER_URL`: URL của server
- `DEVICE_ID`: ID thiết bị
- `CURRENT_VERSION`: Phiên bản hiện tại
- `AUTO_CHECK_INTERVAL`: Khoảng thời gian tự động kiểm tra (giây)

## Bảo mật

Hiện tại hệ thống chưa có authentication. Để thêm bảo mật:

1. Thêm API key authentication
2. Sử dụng HTTPS thay vì HTTP
3. Thêm rate limiting
4. Thêm IP whitelist

## Ví dụ tích hợp với ESP32

```python
# Trên ESP32 (sử dụng MicroPython hoặc CircuitPython)
import urequests
import uhashlib

def check_and_update():
    server_url = "http://192.168.1.100:8000"
    current_version = "1.0.0"
    
    # Kiểm tra update
    response = urequests.post(
        f"{server_url}/api/check-update",
        json={"current_version": current_version}
    )
    data = response.json()
    
    if data.get("update_available"):
        # Tải firmware
        firmware_info = data["firmware_info"]
        download_url = f"{server_url}{firmware_info['download_url']}"
        firmware_data = urequests.get(download_url).content
        
        # Xác minh checksum
        checksum = uhashlib.sha256(firmware_data).hexdigest()
        if checksum == firmware_info["checksum"]:
            # Flash firmware
            # ... logic flash firmware ...
            pass
```

## Troubleshooting

### Server không khởi động được
- Kiểm tra port 8000 có bị chiếm không: `netstat -an | findstr 8000`
- Thử đổi port trong `config.py`

### Client không kết nối được server
- Kiểm tra URL server đúng chưa
- Kiểm tra firewall/network
- Thử ping server từ thiết bị

### Checksum không khớp
- File có thể bị hỏng khi tải
- Thử tải lại firmware
- Kiểm tra kết nối mạng

## OTA qua GitHub Releases (Khuyến nghị)

**Cách đơn giản nhất:** Sử dụng GitHub Releases thay vì server riêng!

### Ưu điểm:
- ✅ Miễn phí, không cần server
- ✅ CDN nhanh, ổn định
- ✅ Dễ quản lý qua GitHub UI
- ✅ Khách tự cập nhật bằng link GitHub

### Cách sử dụng:

1. **Tạo GitHub repo:**
   ```bash
   # Tạo repo mới trên GitHub
   ```

2. **Upload firmware:**
   ```bash
   python utils/github_upload.py firmware.bin v1.0.1 \
     -r username/repo-name \
     -t your_github_token
   ```

3. **Gửi link cho khách:**
   ```
   https://github.com/username/repo-name/releases/latest
   ```

4. **Khách sử dụng:**
   ```python
   from client.github_ota_client import GitHubOTAClient
   
   client = GitHubOTAClient(repo="username/repo-name")
   client.set_current_version("1.0.0")
   result = client.update_firmware(install_callback=install_firmware)
   ```

**Xem hướng dẫn chi tiết:** [GITHUB_OTA_GUIDE.md](GITHUB_OTA_GUIDE.md)

---

## Chia sẻ Server với Khách hàng

### Cách nhanh nhất: Sử dụng ngrok

1. **Cài đặt ngrok:**
   ```bash
   # Download từ https://ngrok.com/download
   # Hoặc: choco install ngrok
   ```

2. **Khởi động server với ngrok:**
   ```bash
   # Windows
   start_with_ngrok.bat
   
   # Linux/Mac
   chmod +x start_with_ngrok.sh
   ./start_with_ngrok.sh
   ```

3. **Lấy URL công khai:**
   - Mở http://localhost:4040 (ngrok dashboard)
   - Copy URL (ví dụ: `https://abc123.ngrok.io`)
   - Gửi URL này cho khách hàng

4. **Khách hàng sử dụng:**
   ```python
   from client.ota_client import OTAClient
   
   client = OTAClient(
       server_url="https://abc123.ngrok.io",  # URL bạn cung cấp
       device_id="device_001"
   )
   ```

Xem chi tiết trong [DEPLOYMENT.md](DEPLOYMENT.md)

## License

MIT License

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## Tác giả

Dựa trên repository: https://github.com/conghuy93/ota.git

