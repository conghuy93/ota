"""
Cấu hình cho OTA Server
"""
import os
from pathlib import Path

# Cấu hình server
SERVER_HOST = os.getenv("OTA_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("OTA_SERVER_PORT", "8000"))

# Thư mục firmware
BASE_DIR = Path(__file__).parent.parent
FIRMWARE_DIR = BASE_DIR / "firmware"
FIRMWARE_DIR.mkdir(exist_ok=True)

# File metadata
METADATA_FILE = FIRMWARE_DIR / "metadata.json"

# Giới hạn kích thước file upload (MB)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024

# Cấu hình bảo mật (tùy chọn)
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "")

