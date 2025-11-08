# Quick Start - GitHub Raw OTA

Hướng dẫn nhanh để setup OTA qua GitHub Raw Files.

## ⚡ 5 Phút Setup

### 1. Tạo Repo trên GitHub

```bash
# Tạo repo mới trên GitHub (ví dụ: "ota")
# Clone về máy
git clone https://github.com/username/ota.git
cd ota
```

### 2. Setup Cấu trúc

```bash
# Chạy script setup
python utils/setup_github_raw_ota.py

# Hoặc tạo thủ công
mkdir -p ota/firmware
echo '{"version": 1}' > ota/version.json
```

### 3. Build Firmware ESP32

1. Mở `example/esp32_ota_example.ino` trong Arduino IDE
2. **Sửa cấu hình:**
   ```cpp
   const char* ssid = "YOUR_WIFI";
   const char* password = "YOUR_PASSWORD";
   
   String RAW_URL_VER = "https://raw.githubusercontent.com/USERNAME/REPO/main/ota/version.json";
   String RAW_URL_FW  = "https://raw.githubusercontent.com/USERNAME/REPO/main/ota/firmware/firmware.bin";
   ```
3. **Export binary:**
   - Sketch → Export compiled binary
   - File `.bin` sẽ được tạo

### 4. Upload lên GitHub

```bash
# Cách 1: Qua script (tự động tăng version)
python utils/github_raw_upload.py firmware.bin \
  -r username/ota \
  -t your_github_token

# Cách 2: Thủ công
cp firmware.bin ota/firmware/firmware.bin
git add ota/
git commit -m "Add firmware v1"
git push
```

### 5. Nạp vào ESP32

- **Lần đầu:** Upload `esp32_ota_example.ino` qua USB
- **Từ lần sau:** ESP32 tự động OTA!

## 🔄 Update Firmware

```bash
# 1. Sửa code ESP32
# 2. Build → Export binary
# 3. Upload (tự động tăng version)
python utils/github_raw_upload.py new_firmware.bin -r username/ota -t token

# 4. ESP32 tự động update khi reboot hoặc sau 1 giờ
```

## 📋 Checklist

- [ ] Đã tạo GitHub repo
- [ ] Đã setup cấu trúc `ota/`
- [ ] Đã sửa URLs trong code ESP32
- [ ] Đã build và upload firmware
- [ ] Đã nạp code vào ESP32
- [ ] Đã test OTA update

## 🔗 Links

Sau khi setup, links sẽ là:
- Version: `https://raw.githubusercontent.com/username/ota/main/ota/version.json`
- Firmware: `https://raw.githubusercontent.com/username/ota/main/ota/firmware/firmware.bin`

## 📚 Xem thêm

- Chi tiết: [GITHUB_RAW_OTA_GUIDE.md](GITHUB_RAW_OTA_GUIDE.md)
- Code ESP32: [example/esp32_ota_example.ino](example/esp32_ota_example.ino)

