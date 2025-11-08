# Hướng dẫn nhanh

## Bước 1: Cài đặt

```bash
pip install -r requirements.txt
```

## Bước 2: Khởi động Server

```bash
cd server
python main.py
```

Server sẽ chạy tại: http://localhost:8000

## Bước 3: Upload Firmware

### Cách 1: Qua Web UI
1. Mở trình duyệt: http://localhost:8000/docs
2. Tìm endpoint `/api/upload`
3. Click "Try it out"
4. Chọn file firmware, nhập version và description
5. Click "Execute"

### Cách 2: Qua command line
```bash
python utils/upload_firmware.py firmware.bin 1.0.1 -d "Firmware mới"
```

## Bước 4: Kiểm tra Firmware có sẵn

```bash
python utils/list_firmwares.py
```

## Bước 5: Sử dụng trên thiết bị

### Python
```python
from client.ota_client import OTAClient

client = OTAClient("http://192.168.1.100:8000", "device_001")
client.set_current_version("1.0.0")

def install_firmware(file_path):
    # Logic cài đặt firmware của bạn
    print(f"Cài đặt: {file_path}")

result = client.update_firmware(install_callback=install_firmware)
```

### Command line
```bash
python utils/check_update.py 1.0.0 -s http://192.168.1.100:8000
```

## Ví dụ hoàn chỉnh

1. **Khởi động server:**
   ```bash
   cd server && python main.py
   ```

2. **Upload firmware:**
   ```bash
   python utils/upload_firmware.py my_firmware.bin 1.0.1 -d "Fix bugs"
   ```

3. **Kiểm tra từ thiết bị:**
   ```bash
   python utils/check_update.py 1.0.0
   ```

4. **Chạy client tự động:**
   ```bash
   cd client
   python example_device.py
   ```

## Lưu ý

- Thay đổi IP server trong client config nếu server chạy trên máy khác
- Đảm bảo firewall cho phép kết nối đến port 8000
- Firmware sẽ được lưu trong thư mục `firmware/`

