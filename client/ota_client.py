"""
OTA Client Library
Thư viện để thiết bị kiểm tra và tải firmware updates
"""
import requests
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Callable
import json

class OTAClient:
    """Client để tương tác với OTA Server"""
    
    def __init__(self, server_url: str, device_id: Optional[str] = None, 
                 api_key: Optional[str] = None, device_token: Optional[str] = None):
        """
        Khởi tạo OTA Client
        
        Args:
            server_url: URL của OTA server (ví dụ: http://192.168.1.100:8000)
            device_id: ID của thiết bị (tùy chọn)
            api_key: API key để authenticate (nếu server yêu cầu)
            device_token: Device token để authenticate (nếu server yêu cầu)
        """
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id
        self.api_key = api_key
        self.device_token = device_token
        self.current_version = "0.0.0"
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
    
    def get_headers(self):
        """Lấy headers với authentication"""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.device_token:
            headers["Authorization"] = f"Bearer {self.device_token}"
        return headers
    
    def set_current_version(self, version: str):
        """Thiết lập phiên bản hiện tại của thiết bị"""
        self.current_version = version
    
    def get_current_version(self) -> str:
        """Lấy phiên bản hiện tại"""
        return self.current_version
    
    def check_update(self) -> Dict:
        """
        Kiểm tra có firmware mới không
        
        Returns:
            Dict chứa thông tin update hoặc None nếu không có update
        """
        try:
            url = f"{self.server_url}/api/check-update"
            payload = {
                "current_version": self.current_version,
                "device_id": self.device_id
            }
            
            headers = self.get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi kiểm tra update: {e}")
            return {
                "update_available": False,
                "error": str(e)
            }
    
    def download_firmware(self, version: str, progress_callback: Optional[Callable] = None) -> Optional[Path]:
        """
        Tải firmware về
        
        Args:
            version: Phiên bản firmware cần tải
            progress_callback: Hàm callback để hiển thị tiến trình (bytes_downloaded, total_size)
        
        Returns:
            Path đến file đã tải về hoặc None nếu lỗi
        """
        try:
            url = f"{self.server_url}/api/download/{version}"
            headers = self.get_headers()
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Lấy tên file từ header hoặc URL
            filename = response.headers.get('content-disposition', '')
            if 'filename=' in filename:
                filename = filename.split('filename=')[1].strip('"')
            else:
                filename = f"firmware_{version}.bin"
            
            file_path = self.download_dir / filename
            
            # Tải file với progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            return file_path
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải firmware: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Xác minh checksum của file firmware
        
        Args:
            file_path: Đường dẫn đến file firmware
            expected_checksum: Checksum mong đợi (SHA256)
        
        Returns:
            True nếu checksum khớp, False nếu không
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            calculated_checksum = sha256_hash.hexdigest()
            return calculated_checksum.lower() == expected_checksum.lower()
        except Exception as e:
            print(f"Lỗi khi xác minh checksum: {e}")
            return False
    
    def update_firmware(self, 
                       install_callback: Optional[Callable] = None,
                       progress_callback: Optional[Callable] = None) -> Dict:
        """
        Kiểm tra và cập nhật firmware tự động
        
        Args:
            install_callback: Hàm callback để cài đặt firmware (nhận file_path)
            progress_callback: Hàm callback để hiển thị tiến trình tải
        
        Returns:
            Dict chứa kết quả update
        """
        # Kiểm tra update
        print(f"Đang kiểm tra update từ {self.server_url}...")
        update_info = self.check_update()
        
        if not update_info.get("update_available", False):
            print(f"Không có update mới. Phiên bản hiện tại: {self.current_version}")
            return {
                "success": False,
                "message": "Không có update mới",
                "current_version": self.current_version
            }
        
        firmware_info = update_info.get("firmware_info", {})
        latest_version = firmware_info.get("version")
        checksum = firmware_info.get("checksum")
        
        print(f"Tìm thấy firmware mới: {latest_version}")
        print(f"Mô tả: {firmware_info.get('description', 'N/A')}")
        
        # Tải firmware
        print(f"Đang tải firmware {latest_version}...")
        file_path = self.download_firmware(latest_version, progress_callback)
        
        if not file_path:
            return {
                "success": False,
                "message": "Lỗi khi tải firmware"
            }
        
        print(f"Đã tải firmware: {file_path}")
        
        # Xác minh checksum
        print("Đang xác minh checksum...")
        if not self.verify_checksum(file_path, checksum):
            print("Lỗi: Checksum không khớp! File có thể bị hỏng.")
            file_path.unlink()  # Xóa file không hợp lệ
            return {
                "success": False,
                "message": "Checksum không khớp"
            }
        
        print("Checksum hợp lệ!")
        
        # Cài đặt firmware
        if install_callback:
            print("Đang cài đặt firmware...")
            try:
                install_callback(file_path)
                print(f"Cài đặt thành công! Phiên bản mới: {latest_version}")
                
                # Cập nhật phiên bản hiện tại
                self.current_version = latest_version
                
                return {
                    "success": True,
                    "message": "Cập nhật firmware thành công",
                    "new_version": latest_version,
                    "file_path": str(file_path)
                }
            except Exception as e:
                print(f"Lỗi khi cài đặt firmware: {e}")
                return {
                    "success": False,
                    "message": f"Lỗi khi cài đặt: {str(e)}"
                }
        else:
            print(f"Firmware đã sẵn sàng tại: {file_path}")
            print("Lưu ý: Cần cài đặt firmware thủ công hoặc cung cấp install_callback")
            return {
                "success": True,
                "message": "Firmware đã tải về",
                "new_version": latest_version,
                "file_path": str(file_path),
                "needs_manual_install": True
            }
    
    def list_available_firmwares(self) -> Dict:
        """
        Lấy danh sách tất cả firmware có sẵn trên server
        """
        try:
            url = f"{self.server_url}/api/firmwares"
            headers = self.get_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy danh sách firmware: {e}")
            return {"firmwares": [], "error": str(e)}
    
    def register_device(self, device_name: Optional[str] = None, device_type: Optional[str] = None) -> Optional[str]:
        """
        Đăng ký device và nhận token
        Yêu cầu API key
        
        Returns:
            Device token hoặc None nếu lỗi
        """
        if not self.api_key:
            print("Lỗi: Cần API key để đăng ký device")
            return None
        
        try:
            url = f"{self.server_url}/api/auth/register"
            payload = {
                "device_id": self.device_id,
                "device_name": device_name,
                "device_type": device_type
            }
            headers = {"X-API-Key": self.api_key}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.device_token = data.get("token")
            print(f"Device registered! Token: {self.device_token[:20]}...")
            return self.device_token
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi đăng ký device: {e}")
            return None


# Ví dụ sử dụng
if __name__ == "__main__":
    # Khởi tạo client
    client = OTAClient(
        server_url="http://localhost:8000",
        device_id="device_001"
    )
    
    # Thiết lập phiên bản hiện tại
    client.set_current_version("1.0.0")
    
    # Callback để hiển thị tiến trình
    def progress_callback(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            print(f"\rTiến trình: {percent:.1f}% ({downloaded}/{total} bytes)", end="")
    
    # Callback để cài đặt firmware (ví dụ)
    def install_firmware(file_path):
        print(f"\nCài đặt firmware từ {file_path}...")
        # Ở đây bạn sẽ thực hiện logic cài đặt firmware thực tế
        # Ví dụ: copy file, flash vào thiết bị, v.v.
        pass
    
    # Thực hiện update
    result = client.update_firmware(
        install_callback=install_firmware,
        progress_callback=progress_callback
    )
    
    print(f"\nKết quả: {result}")

