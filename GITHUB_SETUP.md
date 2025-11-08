# Hướng dẫn Push Code lên GitHub cho OTA

## 🚀 Cách Nhanh (3 bước)

### Bước 1: Tạo Repo trên GitHub

1. Vào: https://github.com/new
2. Tên repo: `ota` (hoặc tên bạn muốn)
3. Chọn **Public** hoặc **Private**
4. **KHÔNG** tích các tùy chọn:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
5. Click **"Create repository"**

### Bước 2: Setup Local Repository

```bash
# Chạy script setup
setup_ota_repo.bat
```

Script sẽ:
- Init git (nếu chưa có)
- Tạo cấu trúc `ota/`
- Add và commit files

### Bước 3: Push lên GitHub

```bash
# Chạy script push
push_to_github.bat
```

Hoặc thủ công:
```bash
git remote add origin https://github.com/USERNAME/ota.git
git branch -M main
git push -u origin main
```

## 📁 Cấu trúc Repo

Sau khi push, repo sẽ có cấu trúc:

```
ota/
├── ota/
│   ├── firmware/
│   │   └── firmware.bin    # Upload firmware vào đây
│   ├── version.json        # Version hiện tại
│   └── README.md
├── server/                 # OTA Server
├── client/                 # OTA Client
├── example/                # Code ESP32
├── utils/                  # Scripts
└── README.md
```

## 🔗 URLs cho OTA

Sau khi push, URLs sẽ là:

- **Version:**
  ```
  https://raw.githubusercontent.com/USERNAME/ota/main/ota/version.json
  ```

- **Firmware:**
  ```
  https://raw.githubusercontent.com/USERNAME/ota/main/ota/firmware/firmware.bin
  ```

Thay `USERNAME` và `ota` bằng thông tin repo của bạn.

## 📝 Workflow Hoàn chỉnh

### Lần đầu:

1. **Tạo repo trên GitHub**
2. **Setup local:**
   ```bash
   setup_ota_repo.bat
   ```
3. **Push code:**
   ```bash
   push_to_github.bat
   ```

### Cập nhật Firmware:

1. **Build firmware** từ Arduino IDE → Export binary
2. **Upload lên GitHub:**
   ```bash
   python utils/github_raw_upload.py firmware.bin -r USERNAME/ota
   ```
3. **ESP32 tự động update!**

## 🔐 Authentication

Nếu repo là **Private**, cần GitHub token:

```bash
# Set token
set_github_token.bat

# Hoặc set environment variable
set GITHUB_TOKEN=your_token_here
```

## ✅ Checklist

- [ ] Đã tạo repo trên GitHub
- [ ] Đã chạy `setup_ota_repo.bat`
- [ ] Đã chạy `push_to_github.bat`
- [ ] Đã test URLs raw
- [ ] Đã upload firmware test
- [ ] ESP32 có thể download được

## 🆘 Troubleshooting

### Push bị từ chối

- Kiểm tra repo đã tạo chưa
- Kiểm tra URL remote đúng chưa
- Thử: `git push -u origin main --force` (cẩn thận!)

### Không tìm thấy remote

```bash
git remote add origin https://github.com/USERNAME/ota.git
git remote -v  # Kiểm tra
```

### Lỗi authentication

- Tạo Personal Access Token: https://github.com/settings/tokens
- Set token: `set_github_token.bat`
- Hoặc dùng: `git push https://TOKEN@github.com/USERNAME/ota.git`

## 📚 Xem thêm

- Quick Start: [QUICKSTART_GITHUB_RAW.md](QUICKSTART_GITHUB_RAW.md)
- Chi tiết: [GITHUB_RAW_OTA_GUIDE.md](GITHUB_RAW_OTA_GUIDE.md)

