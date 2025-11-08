# OTA Firmware Repository

Repository này chứa firmware cho OTA updates.

## Cấu trúc

```
ota/
├── firmware/
│   └── firmware.bin    # File firmware ESP32
├── version.json        # Version hiện tại
└── README.md          # File này
```

## Cách sử dụng

1. Build firmware từ Arduino IDE
2. Export compiled binary → `firmware.bin`
3. Upload `firmware.bin` vào `firmware/`
4. Tăng version trong `version.json`
5. Commit & Push
6. ESP32 sẽ tự động cập nhật

## Links RAW

- Version: `https://raw.githubusercontent.com/USERNAME/REPO/main/version.json`
- Firmware: `https://raw.githubusercontent.com/USERNAME/REPO/main/firmware/firmware.bin`

Thay `USERNAME` và `REPO` bằng thông tin repo của bạn.

