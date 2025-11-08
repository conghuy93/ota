"""
Script tự động flash firmware vào ESP32 qua Serial Port
Sử dụng esptool để flash firmware
"""
import subprocess
import sys
import argparse
from pathlib import Path
import time

def flash_firmware(port: str, firmware_path: str, baud: int = 921600, 
                   flash_mode: str = "dio", flash_freq: str = "80m",
                   flash_size: str = "4MB", address: str = "0x1000"):
    """
    Flash firmware vào ESP32
    
    Args:
        port: Serial port (ví dụ: COM31, /dev/ttyUSB0)
        firmware_path: Đường dẫn đến file firmware.bin
        baud: Baud rate (mặc định: 921600)
        flash_mode: Flash mode (dio, qio, dout, qout)
        flash_freq: Flash frequency (80m, 40m, 26m, 20m)
        flash_size: Flash size (4MB, 8MB, 16MB)
        address: Flash address (mặc định: 0x1000 cho ESP32)
    """
    firmware_path = Path(firmware_path)
    
    if not firmware_path.exists():
        print(f"❌ File firmware không tồn tại: {firmware_path}")
        return False
    
    print("=" * 60)
    print("ESP32 Firmware Flasher")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Firmware: {firmware_path}")
    print(f"Size: {firmware_path.stat().st_size:,} bytes")
    print(f"Baud: {baud}")
    print("=" * 60)
    
    # Kiểm tra esptool
    try:
        result = subprocess.run(["esptool.py", "--version"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ esptool.py không tìm thấy!")
            print("\nCài đặt esptool:")
            print("  pip install esptool")
            return False
    except FileNotFoundError:
        print("❌ esptool.py không tìm thấy!")
        print("\nCài đặt esptool:")
        print("  pip install esptool")
        return False
    
    # Lệnh flash
    cmd = [
        "esptool.py",
        "--chip", "esp32",
        "--port", port,
        "--baud", str(baud),
        "--before", "default_reset",
        "--after", "hard_reset",
        "write_flash",
        "-z",
        "--flash_mode", flash_mode,
        "--flash_freq", flash_freq,
        "--flash_size", flash_size,
        address,
        str(firmware_path)
    ]
    
    print(f"\n📤 Đang flash firmware...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        # Chạy esptool
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Hiển thị output real-time
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ Flash firmware thành công!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ Flash firmware thất bại!")
            print("=" * 60)
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã hủy bởi người dùng")
        return False
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        return False

def erase_flash(port: str, baud: int = 921600):
    """Xóa toàn bộ flash"""
    print(f"🗑️  Đang xóa flash trên {port}...")
    
    cmd = [
        "esptool.py",
        "--chip", "esp32",
        "--port", port,
        "--baud", str(baud),
        "erase_flash"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Xóa flash thành công!")
            return True
        else:
            print("❌ Xóa flash thất bại!")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def get_chip_info(port: str, baud: int = 115200):
    """Lấy thông tin chip"""
    print(f"📊 Đang lấy thông tin chip trên {port}...")
    
    cmd = [
        "esptool.py",
        "--chip", "auto",
        "--port", port,
        "--baud", str(baud),
        "chip_id"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Flash firmware vào ESP32 qua Serial Port'
    )
    parser.add_argument('firmware', help='Đường dẫn đến file firmware.bin')
    parser.add_argument('-p', '--port', default='COM31',
                       help='Serial port (default: COM31)')
    parser.add_argument('-b', '--baud', type=int, default=921600,
                       help='Baud rate (default: 921600)')
    parser.add_argument('--flash-mode', default='dio',
                       choices=['dio', 'qio', 'dout', 'qout'],
                       help='Flash mode (default: dio)')
    parser.add_argument('--flash-freq', default='80m',
                       choices=['80m', '40m', '26m', '20m'],
                       help='Flash frequency (default: 80m)')
    parser.add_argument('--flash-size', default='4MB',
                       choices=['4MB', '8MB', '16MB'],
                       help='Flash size (default: 4MB)')
    parser.add_argument('--address', default='0x1000',
                       help='Flash address (default: 0x1000)')
    parser.add_argument('--erase', action='store_true',
                       help='Xóa flash trước khi flash')
    parser.add_argument('--info', action='store_true',
                       help='Chỉ hiển thị thông tin chip')
    
    args = parser.parse_args()
    
    if args.info:
        get_chip_info(args.port, args.baud)
        return
    
    if args.erase:
        if not erase_flash(args.port, args.baud):
            sys.exit(1)
        time.sleep(2)
    
    success = flash_firmware(
        port=args.port,
        firmware_path=args.firmware,
        baud=args.baud,
        flash_mode=args.flash_mode,
        flash_freq=args.flash_freq,
        flash_size=args.flash_size,
        address=args.address
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

