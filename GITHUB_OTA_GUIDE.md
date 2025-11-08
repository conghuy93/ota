# Hướng dẫn OTA qua GitHub Releases

## 🎯 Tổng quan

Thay vì host server riêng, bạn có thể sử dụng GitHub Releases để phân phối firmware. Khách hàng sẽ tự động tải firmware từ GitHub.

**Ưu điểm:**
- ✅ Miễn phí, không cần server riêng
- ✅ CDN nhanh, ổn định
- ✅ Dễ quản lý qua GitHub UI
- ✅ Tự động có versioning
- ✅ Khách tự cập nhật bằng link GitHub

---

## 📦 Bước 1: Tạo GitHub Repository

1. Tạo repo mới trên GitHub (public hoặc private)
2. Ví dụ: `https://github.com/username/firmware-releases`

---

## 🔑 Bước 2: Tạo GitHub Token

1. Vào: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Chọn quyền: `repo` (full control)
4. Copy token (chỉ hiện 1 lần!)

**Lưu token:**
```bash
# Windows
set GITHUB_TOKEN=your_token_here

# Linux/Mac
export GITHUB_TOKEN=your_token_here
```

---

## 📤 Bước 3: Upload Firmware lên GitHub

### Cách 1: Qua Script (Khuyến nghị)

```bash
python utils/github_upload.py firmware.bin v1.0.1 \
  -r username/repo-name \
  -t your_github_token \
  -d "Mô tả firmware này"
```

### Cách 2: Qua GitHub UI

1. Vào repo trên GitHub
2. Click "Releases" → "Create a new release"
3. Chọn tag mới (ví dụ: `v1.0.1`)
4. Upload file firmware
5. Thêm mô tả
6. Publish release

### Cách 3: Qua GitHub CLI

```bash
gh release create v1.0.1 firmware.bin \
  --title "Firmware v1.0.1" \
  --notes "Mô tả firmware"
```

---

## 🔗 Bước 4: Lấy Link cho Khách

Sau khi upload, bạn có 2 loại link:

### Link Release (Khuyến nghị)
```
https://github.com/username/repo-name/releases/latest
```

### Link Download trực tiếp
```
https://github.com/username/repo-name/releases/download/v1.0.1/firmware.bin
```

**Gửi link này cho khách hàng!**

---

## 💻 Bước 5: Code cho Khách hàng

### Python (Full)

```python
from client.github_ota_client import GitHubOTAClient

# Repo GitHub của bạn
REPO = "username/repo-name"  # ← Thay đổi repo của bạn
CURRENT_VERSION = "1.0.0"

client = GitHubOTAClient(repo=REPO)
client.set_current_version(CURRENT_VERSION)

def install_firmware(file_path):
    print(f"Cài đặt firmware: {file_path}")
    # Logic cài đặt của bạn

def progress_callback(downloaded, total):
    if total > 0:
        percent = (downloaded / total) * 100
        print(f"\rTiến trình: {percent:.1f}%", end="")

# Kiểm tra và cập nhật
result = client.update_firmware(
    install_callback=install_firmware,
    progress_callback=progress_callback
)

print(result)
```

### ESP32/ESP8266 (MicroPython)

```python
import urequests
import uhashlib

REPO = "username/repo-name"
CURRENT_VERSION = "1.0.0"

def check_github_update():
    # Lấy release mới nhất
    api_url = f"https://api.github.com/repos/{REPO}/releases/latest"
    response = urequests.get(api_url)
    release = response.json()
    
    tag = release["tag_name"]
    latest_version = tag.lstrip('vV')
    
    # So sánh version
    if compare_versions(latest_version, CURRENT_VERSION) > 0:
        # Tìm file firmware
        assets = release.get("assets", [])
        firmware_asset = None
        for asset in assets:
            if asset["name"].endswith(".bin"):
                firmware_asset = asset
                break
        
        if firmware_asset:
            # Tải firmware
            download_url = firmware_asset["browser_download_url"]
            firmware = urequests.get(download_url).content
            
            # Flash firmware
            # ... logic của bạn
            pass

def compare_versions(v1, v2):
    # Logic so sánh version
    pass
```

### HTTP API (Bất kỳ ngôn ngữ nào)

```bash
# 1. Lấy release mới nhất
curl https://api.github.com/repos/username/repo-name/releases/latest

# 2. Tải firmware (từ response trên)
curl -L -O https://github.com/username/repo-name/releases/download/v1.0.1/firmware.bin
```

---

## 📋 Workflow Hoàn chỉnh

### Bạn (Developer):

1. **Build firmware:**
   ```bash
   # Build firmware của bạn
   ```

2. **Upload lên GitHub:**
   ```bash
   python utils/github_upload.py build/firmware.bin v1.0.2 \
     -r username/repo-name \
     -t $GITHUB_TOKEN \
     -d "Fix bug và cải thiện hiệu suất"
   ```

3. **Gửi thông tin cho khách:**
   ```
   🔔 Firmware mới đã có!
   
   📦 Repo: username/repo-name
   🔗 Link: https://github.com/username/repo-name/releases/latest
   📝 Version: v1.0.2
   
   Thiết bị sẽ tự động cập nhật khi chạy OTA client.
   ```

### Khách hàng:

1. **Cấu hình client:**
   ```python
   client = GitHubOTAClient(repo="username/repo-name")
   client.set_current_version("1.0.1")
   ```

2. **Chạy update:**
   ```python
   result = client.update_firmware(install_callback=install_firmware)
   ```

3. **Tự động tải và cài đặt firmware mới!**

---

## 🔧 Cấu hình Nâng cao

### Private Repository

Nếu repo là private, khách cần token:

```python
client = GitHubOTAClient(
    repo="username/private-repo",
    token="ghp_your_token_here"
)
```

### Chọn Release cụ thể

```python
# Lấy release theo tag
release = client.get_release_by_tag("v1.0.1")

# Tải firmware từ release đó
asset = client.find_firmware_asset(release)
file_path = client.download_firmware(asset["browser_download_url"])
```

### Liệt kê tất cả Releases

```python
releases = client.list_releases()
for release in releases:
    print(f"{release['tag_name']}: {release['name']}")
```

---

## 📊 So sánh: GitHub vs Server riêng

| Tính năng | GitHub Releases | Server riêng |
|-----------|----------------|--------------|
| Chi phí | Miễn phí | Cần hosting |
| Tốc độ | CDN nhanh | Phụ thuộc server |
| Quản lý | GitHub UI | Web UI riêng |
| Bảo mật | GitHub security | Tự quản lý |
| Versioning | Tự động | Tự quản lý |
| API | GitHub API | API riêng |

---

## ✅ Checklist

Trước khi gửi cho khách:

- [ ] Đã tạo GitHub repo
- [ ] Đã upload firmware test
- [ ] Đã test client có thể tải được
- [ ] Đã cung cấp repo name cho khách
- [ ] (Nếu private) Đã cung cấp token cho khách
- [ ] Đã cung cấp code mẫu

---

## 🆘 Troubleshooting

### Không tải được firmware

1. **Kiểm tra repo public:**
   - Nếu private, cần token
   - Test: `curl https://api.github.com/repos/username/repo/releases/latest`

2. **Kiểm tra file tồn tại:**
   - Vào GitHub Releases
   - Xem file có trong assets không

3. **Kiểm tra rate limit:**
   - GitHub API: 60 requests/hour (không auth)
   - Với auth: 5000 requests/hour

### Version không đúng

- Đảm bảo tag format: `v1.0.1` hoặc `1.0.1`
- Client tự động loại bỏ "v" prefix

---

## 📚 Tài liệu tham khảo

- GitHub Releases API: https://docs.github.com/en/rest/releases
- GitHub CLI: https://cli.github.com/
- Ví dụ code: `client/github_ota_client.py`

