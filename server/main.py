"""
OTA Firmware Update Server
Server để quản lý và phân phối firmware updates qua OTA
"""
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Header
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import hashlib
from pathlib import Path
from typing import Optional, List
import uvicorn
from config import FIRMWARE_DIR, METADATA_FILE, SERVER_HOST, SERVER_PORT, MAX_UPLOAD_SIZE
from auth import (
    require_api_key, require_device_token, require_auth,
    generate_api_key, generate_device_token,
    load_api_keys, load_device_tokens
)

app = FastAPI(title="OTA Firmware Update Server")

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FirmwareInfo(BaseModel):
    version: str
    filename: str
    size: int
    checksum: str
    description: Optional[str] = None
    release_date: Optional[str] = None

class UpdateCheck(BaseModel):
    current_version: str
    device_id: Optional[str] = None

class DeviceRegistration(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None

def load_metadata():
    """Load metadata từ file"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"firmwares": []}

def save_metadata(metadata):
    """Lưu metadata vào file"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def calculate_checksum(file_path: Path) -> str:
    """Tính checksum SHA256 của file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def compare_versions(v1: str, v2: str) -> int:
    """So sánh 2 phiên bản, trả về 1 nếu v1 > v2, -1 nếu v1 < v2, 0 nếu bằng"""
    v1_parts = [int(x) for x in v1.split('.')]
    v2_parts = [int(x) for x in v2.split('.')]
    
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    for i in range(max_len):
        if v1_parts[i] > v2_parts[i]:
            return 1
        elif v1_parts[i] < v2_parts[i]:
            return -1
    return 0

@app.get("/", response_class=HTMLResponse)
async def root():
    """Trang chủ - Web UI"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>OTA Server</title></head>
        <body>
            <h1>OTA Firmware Update Server</h1>
            <p>Web UI đang được tải...</p>
            <p><a href="/api/docs">API Documentation</a></p>
        </body>
    </html>
    """

@app.get("/api")
async def api_root():
    """API root"""
    return {
        "message": "OTA Firmware Update Server",
        "version": "1.0.0",
        "endpoints": {
            "check_update": "/api/check-update",
            "download": "/api/download/{version}",
            "list_firmwares": "/api/firmwares",
            "upload": "/api/upload",
            "github_info": "/api/github-info"
        },
        "web_ui": "/"
    }

@app.get("/api/github-info")
async def github_info():
    """
    Lấy thông tin GitHub repo (nếu có)
    Cấu hình trong config hoặc environment variable
    """
    github_repo = os.getenv("GITHUB_REPO", "")
    github_tag = os.getenv("GITHUB_TAG", "latest")
    
    if not github_repo:
        return {
            "enabled": False,
            "message": "GitHub repo chưa được cấu hình"
        }
    
    return {
        "enabled": True,
        "repo": github_repo,
        "latest_release_url": f"https://github.com/{github_repo}/releases/latest",
        "releases_url": f"https://github.com/{github_repo}/releases",
        "api_url": f"https://api.github.com/repos/{github_repo}/releases/latest"
    }

@app.post("/api/auth/register")
async def register_device(device: DeviceRegistration, api_key: str = Depends(require_api_key)):
    """
    Đăng ký device và nhận token
    Yêu cầu API key để đăng ký
    """
    token = generate_device_token(device.device_id)
    return {
        "device_id": device.device_id,
        "token": token,
        "message": "Device registered successfully"
    }

@app.post("/api/auth/generate-key")
async def create_api_key(name: str = "default"):
    """
    Tạo API key mới (cần authentication hiện tại hoặc admin)
    """
    key = generate_api_key(name)
    return {
        "api_key": key,
        "name": name,
        "message": "API key generated. Save it securely!"
    }

@app.get("/api/auth/keys")
async def list_api_keys(api_key: str = Depends(require_api_key)):
    """Liệt kê API keys (chỉ hiện tên, không hiện key)"""
    keys = load_api_keys()
    return {
        "keys": [
            {"name": info.get("name"), "created_at": info.get("created_at")}
            for key, info in keys.items()
        ]
    }

@app.post("/api/check-update")
async def check_update(
    update_check: UpdateCheck,
    auth_info: dict = Depends(require_auth)
):
    """
    Kiểm tra có firmware mới không
    Yêu cầu authentication (API key hoặc device token)
    """
    metadata = load_metadata()
    firmwares = metadata.get("firmwares", [])
    
    if not firmwares:
        return {
            "update_available": False,
            "message": "Không có firmware nào trong hệ thống"
        }
    
    # Lấy firmware mới nhất (sắp xếp theo version)
    latest_firmware = max(firmwares, key=lambda x: tuple(map(int, x["version"].split('.'))))
    
    if not latest_firmware:
        return {
            "update_available": False,
            "message": "Không tìm thấy firmware"
        }
    
    # So sánh phiên bản
    current = update_check.current_version
    latest = latest_firmware["version"]
    
    if compare_versions(latest, current) > 0:
        return {
            "update_available": True,
            "latest_version": latest,
            "current_version": current,
            "firmware_info": {
                "version": latest_firmware["version"],
                "size": latest_firmware["size"],
                "checksum": latest_firmware["checksum"],
                "description": latest_firmware.get("description", ""),
                "release_date": latest_firmware.get("release_date", ""),
                "download_url": f"/api/download/{latest}"
            }
        }
    else:
        return {
            "update_available": False,
            "current_version": current,
            "latest_version": latest,
            "message": "Đã sử dụng phiên bản mới nhất"
        }

@app.get("/api/download/{version}")
async def download_firmware(
    version: str,
    auth_info: dict = Depends(require_auth)
):
    """
    Tải firmware theo phiên bản
    Yêu cầu authentication (API key hoặc device token)
    """
    metadata = load_metadata()
    firmwares = metadata.get("firmwares", [])
    
    firmware = next((f for f in firmwares if f["version"] == version), None)
    
    if not firmware:
        raise HTTPException(status_code=404, detail="Không tìm thấy firmware")
    
    file_path = FIRMWARE_DIR / firmware["filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File firmware không tồn tại")
    
    return FileResponse(
        path=file_path,
        filename=firmware["filename"],
        media_type="application/octet-stream"
    )

@app.get("/api/firmwares")
async def list_firmwares(auth_info: dict = Depends(require_auth)):
    """
    Liệt kê tất cả firmware có sẵn
    Yêu cầu authentication
    """
    metadata = load_metadata()
    return {
        "firmwares": metadata.get("firmwares", []),
        "count": len(metadata.get("firmwares", []))
    }

@app.post("/api/upload")
async def upload_firmware(
    file: UploadFile = File(...),
    version: str = None,
    description: str = None,
    api_key: str = Depends(require_api_key)
):
    """
    Upload firmware mới lên server
    Yêu cầu API key (chỉ admin/developer)
    """
    if not version:
        raise HTTPException(status_code=400, detail="Thiếu tham số version")
    
    # Kiểm tra kích thước file
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File quá lớn. Kích thước tối đa: {MAX_UPLOAD_SIZE / 1024 / 1024:.1f} MB"
        )
    
    # Lưu file
    file_path = FIRMWARE_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Tính checksum và size
    checksum = calculate_checksum(file_path)
    size = file_path.stat().st_size
    
    # Cập nhật metadata
    metadata = load_metadata()
    firmwares = metadata.get("firmwares", [])
    
    # Kiểm tra xem version đã tồn tại chưa
    existing = next((f for f in firmwares if f["version"] == version), None)
    if existing:
        # Xóa file cũ nếu có
        old_file = FIRMWARE_DIR / existing["filename"]
        if old_file.exists() and old_file != file_path:
            old_file.unlink()
        # Cập nhật thông tin
        existing.update({
            "filename": file.filename,
            "size": size,
            "checksum": checksum,
            "description": description or existing.get("description", ""),
        })
    else:
        # Thêm firmware mới
        from datetime import datetime
        firmwares.append({
            "version": version,
            "filename": file.filename,
            "size": size,
            "checksum": checksum,
            "description": description or "",
            "release_date": datetime.now().isoformat()
        })
    
    metadata["firmwares"] = firmwares
    save_metadata(metadata)
    
    return {
        "message": "Upload firmware thành công",
        "firmware_info": {
            "version": version,
            "filename": file.filename,
            "size": size,
            "checksum": checksum
        }
    }

@app.delete("/api/firmware/{version}")
async def delete_firmware(
    version: str,
    api_key: str = Depends(require_api_key)
):
    """
    Xóa firmware theo phiên bản
    Yêu cầu API key (chỉ admin/developer)
    """
    metadata = load_metadata()
    firmwares = metadata.get("firmwares", [])
    
    firmware = next((f for f in firmwares if f["version"] == version), None)
    
    if not firmware:
        raise HTTPException(status_code=404, detail="Không tìm thấy firmware")
    
    # Xóa file
    file_path = FIRMWARE_DIR / firmware["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Xóa khỏi metadata
    firmwares = [f for f in firmwares if f["version"] != version]
    metadata["firmwares"] = firmwares
    save_metadata(metadata)
    
    return {"message": f"Đã xóa firmware version {version}"}

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

