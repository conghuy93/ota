"""
Cấu hình cho OTA Client
"""
import os

# URL của OTA Server
SERVER_URL = os.getenv("OTA_SERVER_URL", "http://localhost:8000")

# ID thiết bị
DEVICE_ID = os.getenv("DEVICE_ID", "device_001")

# Phiên bản hiện tại của thiết bị
CURRENT_VERSION = os.getenv("CURRENT_VERSION", "0.0.0")

# Thư mục tải firmware
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

# Timeout cho requests (giây)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Tự động kiểm tra update (giây)
AUTO_CHECK_INTERVAL = int(os.getenv("AUTO_CHECK_INTERVAL", "300"))  # 5 phút

