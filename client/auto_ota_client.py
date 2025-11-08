"""
OTA Client tự động - Tự động kiểm tra và cập nhật firmware
Không cần khách tải, tự động chạy ở background
"""
import time
import threading
try:
    import schedule
except ImportError:
    print("Warning: schedule not installed. Install with: pip install schedule")
    schedule = None
from ota_client import OTAClient
from typing import Optional, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoOTAClient:
    """
    OTA Client tự động
    Tự động kiểm tra và cập nhật firmware định kỳ
    """
    
    def __init__(
        self,
        server_url: str,
        device_id: str,
        device_token: Optional[str] = None,
        check_interval_minutes: int = 60,
        auto_install: bool = True
    ):
        """
        Khởi tạo Auto OTA Client
        
        Args:
            server_url: URL của OTA server
            device_id: ID của thiết bị
            device_token: Device token (nếu server yêu cầu auth)
            check_interval_minutes: Khoảng thời gian kiểm tra (phút)
            auto_install: Tự động cài đặt firmware mới
        """
        self.server_url = server_url
        self.device_id = device_id
        self.device_token = device_token
        self.check_interval = check_interval_minutes
        self.auto_install = auto_install
        self.current_version = "0.0.0"
        self.is_running = False
        self.thread = None
        
        # Tạo OTA client
        self.client = OTAClient(server_url, device_id)
        if device_token:
            # Thêm token vào headers nếu cần
            self.client.token = device_token
    
    def set_current_version(self, version: str):
        """Thiết lập phiên bản hiện tại"""
        self.current_version = version
        self.client.set_current_version(version)
        logger.info(f"Current version set to: {version}")
    
    def set_install_callback(self, callback: Callable):
        """Thiết lập hàm cài đặt firmware"""
        self.install_callback = callback
    
    def set_progress_callback(self, callback: Callable):
        """Thiết lập hàm hiển thị tiến trình"""
        self.progress_callback = callback
    
    def check_and_update(self):
        """Kiểm tra và cập nhật firmware"""
        try:
            logger.info(f"Checking for updates... (Current: {self.current_version})")
            
            # Kiểm tra update
            update_info = self.client.check_update()
            
            if not update_info.get("update_available", False):
                logger.info("No update available")
                return False
            
            firmware_info = update_info.get("firmware_info", {})
            latest_version = firmware_info.get("version")
            
            logger.info(f"Update available! Latest: {latest_version}")
            
            if not self.auto_install:
                logger.info("Auto-install disabled. Update available but not installing.")
                return True
            
            # Tải và cài đặt
            logger.info("Downloading firmware...")
            file_path = self.client.download_firmware(
                latest_version,
                self.progress_callback if hasattr(self, 'progress_callback') else None
            )
            
            if not file_path:
                logger.error("Failed to download firmware")
                return False
            
            # Xác minh checksum
            expected_checksum = firmware_info.get("checksum")
            if expected_checksum:
                if not self.client.verify_checksum(file_path, expected_checksum):
                    logger.error("Checksum verification failed!")
                    return False
                logger.info("Checksum verified")
            
            # Cài đặt
            if hasattr(self, 'install_callback'):
                logger.info("Installing firmware...")
                try:
                    self.install_callback(file_path)
                    logger.info(f"Firmware installed successfully! New version: {latest_version}")
                    self.current_version = latest_version
                    self.client.set_current_version(latest_version)
                    return True
                except Exception as e:
                    logger.error(f"Installation failed: {e}")
                    return False
            else:
                logger.warning("No install callback set. Firmware downloaded but not installed.")
                return True
                
        except Exception as e:
            logger.error(f"Error during update check: {e}")
            return False
    
    def start(self):
        """Bắt đầu tự động kiểm tra"""
        if self.is_running:
            logger.warning("Auto OTA client is already running")
            return
        
        logger.info(f"Starting Auto OTA Client")
        logger.info(f"  Server: {self.server_url}")
        logger.info(f"  Device ID: {self.device_id}")
        logger.info(f"  Check interval: {self.check_interval} minutes")
        logger.info(f"  Auto install: {self.auto_install}")
        
        self.is_running = True
        
        # Lên lịch kiểm tra định kỳ
        if schedule:
            schedule.every(self.check_interval).minutes.do(self.check_and_update)
        
        # Chạy ngay lập tức
        self.check_and_update()
        
        # Chạy scheduler trong thread riêng
        def run_scheduler():
            while self.is_running:
                if schedule:
                    schedule.run_pending()
                time.sleep(1)
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Auto OTA Client started successfully")
    
    def stop(self):
        """Dừng tự động kiểm tra"""
        if not self.is_running:
            return
        
        logger.info("Stopping Auto OTA Client...")
        self.is_running = False
        if schedule:
            schedule.clear()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Auto OTA Client stopped")
    
    def force_check(self):
        """Kiểm tra ngay lập tức (không đợi lịch)"""
        logger.info("Force checking for updates...")
        return self.check_and_update()


# Ví dụ sử dụng
if __name__ == "__main__":
    # Cấu hình
    SERVER_URL = "http://localhost:8000"
    DEVICE_ID = "ESP32_001"
    DEVICE_TOKEN = None  # Thêm token nếu server yêu cầu auth
    
    # Khởi tạo client
    auto_client = AutoOTAClient(
        server_url=SERVER_URL,
        device_id=DEVICE_ID,
        device_token=DEVICE_TOKEN,
        check_interval_minutes=60,  # Kiểm tra mỗi 60 phút
        auto_install=True
    )
    
    # Thiết lập phiên bản hiện tại
    auto_client.set_current_version("1.0.0")
    
    # Hàm cài đặt firmware
    def install_firmware(file_path):
        print(f"\n[INSTALL] Cài đặt firmware từ: {file_path}")
        # Logic cài đặt của bạn
        # Ví dụ: flash firmware vào ESP32
        pass
    
    # Hàm hiển thị tiến trình
    def progress_callback(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            print(f"\rTiến trình: {percent:.1f}%", end="", flush=True)
    
    # Thiết lập callbacks
    auto_client.set_install_callback(install_firmware)
    auto_client.set_progress_callback(progress_callback)
    
    # Bắt đầu tự động kiểm tra
    auto_client.start()
    
    # Giữ chương trình chạy
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐang dừng...")
        auto_client.stop()

