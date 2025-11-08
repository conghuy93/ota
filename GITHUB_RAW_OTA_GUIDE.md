# Hướng dẫn OTA qua GitHub Raw Files

Hệ thống OTA đơn giản sử dụng GitHub raw files - không cần server riêng!

## 🎯 Ưu điểm

- ✅ Miễn phí, không cần server
- ✅ Đơn giản, dễ setup
- ✅ Tự động qua GitHub
- ✅ CDN nhanh của GitHub

## 📁 Cấu trúc Repo

```
your-repo/
├── ota/
│   ├── firmware/
│   │   └── firmware.bin    # File firmware ESP32
│   └── version.json        # Version hiện tại
├── example/
│   └── esp32_ota_example.ino  # Code ESP32
└── README.md
```

## 🚀 Bước 1: Tạo Repo trên GitHub

1. Tạo repo mới trên GitHub (ví dụ: `ota`)
2. Clone về máy:
   ```bash
   git clone https://github.com/username/ota.git
   cd ota
   ```

## 📝 Bước 2: Tạo Cấu trúc

```bash
mkdir -p ota/firmware
```

Tạo file `ota/version.json`:
```json
{
  "version": 1
}
```

## 🔧 Bước 3: Build Firmware ESP32

1. Mở Arduino IDE
2. Mở file `example/esp32_ota_example.ino`
3. **Sửa cấu hình:**
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   
   String RAW_URL_VER = "https://raw.githubusercontent.com/USERNAME/REPO/main/ota/version.json";
   String RAW_URL_FW  = "https://raw.githubusercontent.com/USERNAME/REPO/main/ota/firmware/firmware.bin";
   ```
4. **Build và Export:**
   - Sketch → Export compiled binary
   - File `.bin` sẽ được tạo trong thư mục sketch

## 📤 Bước 4: Upload lên GitHub

### Cách 1: Qua Script (Khuyến nghị)

```bash
python utils/github_raw_upload.py firmware.bin \
  -r username/ota \
  -t your_github_token
```

Script sẽ:
- Upload `firmware.bin` lên `ota/firmware/firmware.bin`
- Tự động tăng version trong `version.json`

### Cách 2: Thủ công

1. Copy file `.bin` vào `ota/firmware/firmware.bin`
2. Commit và push:
   ```bash
   git add ota/
   git commit -m "Add firmware v1"
   git push
   ```

## 🔌 Bước 5: Nạp Code vào ESP32

1. **Lần đầu:** Nạp qua USB
   - Mở `example/esp32_ota_example.ino` trong Arduino IDE
   - Upload vào ESP32

2. **Từ lần sau:** ESP32 sẽ tự động OTA update!

## ✅ Bước 6: Test OTA Update

### Tạo Firmware mới:

1. **Sửa code ESP32** (ví dụ: thêm tính năng mới)
2. **Build và Export binary**
3. **Upload lên GitHub:**
   ```bash
   python utils/github_raw_upload.py new_firmware.bin -r username/ota
   ```
   Script tự động tăng version: `1 → 2`

4. **Khởi động lại ESP32:**
   - ESP32 sẽ check version
   - Thấy version online (2) > current (1)
   - Tự động download và flash firmware mới
   - Reboot với firmware mới

## 🔄 Workflow Hoàn chỉnh

```
Developer:
1. Sửa code ESP32
2. Build → Export binary
3. python utils/github_raw_upload.py firmware.bin -r username/ota
4. Done! (Version tự động tăng)

ESP32:
1. Check version mỗi 1 giờ (hoặc khi reboot)
2. So sánh: online_version > current_version?
3. Nếu có → Download firmware
4. Flash firmware
5. Reboot
```

## 📊 Links RAW

Sau khi upload, links sẽ là:

- **Version:**
  ```
  https://raw.githubusercontent.com/username/ota/main/ota/version.json
  ```

- **Firmware:**
  ```
  https://raw.githubusercontent.com/username/ota/main/ota/firmware/firmware.bin
  ```

Thay `username/ota` bằng repo của bạn.

## ⚙️ Cấu hình Nâng cao

### Thay đổi Check Interval

Trong `esp32_ota_example.ino`:
```cpp
int CHECK_INTERVAL = 3600000;  // 1 giờ (milliseconds)
// 1800000 = 30 phút
// 7200000 = 2 giờ
```

### Tắt Auto Update

```cpp
bool AUTO_UPDATE = false;  // Chỉ check, không tự động update
```

### Manual Update

Thêm button để trigger update thủ công:
```cpp
if (digitalRead(BUTTON_PIN) == LOW) {
  checkAndUpdate();
}
```

## 🤖 GitHub Actions (Tự động Build)

Nếu muốn tự động build khi push code:

1. Tạo file `.github/workflows/auto_build_upload.yml`
2. Workflow sẽ:
   - Build firmware khi push code
   - Tự động upload firmware.bin
   - Tự động tăng version
   - Commit và push

Xem file `github_raw_ota/.github/workflows/auto_build_upload.yml` để biết chi tiết.

## 🔐 Bảo mật

### Private Repository

Nếu repo là private, cần GitHub token để access:

1. Tạo Personal Access Token với quyền `repo`
2. Sử dụng token trong ESP32 (không khuyến nghị - token sẽ lộ)
3. Hoặc dùng GitHub Actions để build và public release

### Signed Firmware (Nâng cao)

Có thể thêm chữ ký số để verify firmware:
- Hash firmware và lưu trong version.json
- ESP32 verify hash trước khi flash

## 📋 Checklist

- [ ] Đã tạo GitHub repo
- [ ] Đã tạo cấu trúc `ota/`
- [ ] Đã build firmware và upload
- [ ] Đã sửa URLs trong code ESP32
- [ ] Đã nạp code vào ESP32 lần đầu
- [ ] Đã test OTA update
- [ ] (Tùy chọn) Đã setup GitHub Actions

## 🆘 Troubleshooting

### ESP32 không kết nối được

- Kiểm tra WiFi SSID/password đúng chưa
- Kiểm tra ESP32 có internet không
- Test ping GitHub từ ESP32

### Không tải được firmware

- Kiểm tra URL raw đúng chưa
- Kiểm tra file tồn tại trên GitHub
- Kiểm tra repo public (hoặc có token)

### Version không đúng

- Kiểm tra format JSON trong version.json
- Kiểm tra ESP32 parse JSON đúng chưa
- Serial monitor để debug

### Update thất bại

- Kiểm tra không gian flash đủ không
- Kiểm tra firmware size
- Kiểm tra kết nối mạng ổn định

## 📚 Tài liệu tham khảo

- ESP32 OTA: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ota.html
- ArduinoJson: https://arduinojson.org/
- GitHub Raw: https://raw.githubusercontent.com/

