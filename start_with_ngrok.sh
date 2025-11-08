#!/bin/bash

echo "========================================"
echo "  OTA Server với ngrok"
echo "========================================"
echo ""

# Kiểm tra ngrok
if ! command -v ngrok &> /dev/null; then
    echo "[ERROR] ngrok chưa được cài đặt!"
    echo ""
    echo "Cài đặt ngrok:"
    echo "  1. Download từ: https://ngrok.com/download"
    echo "  2. Hoặc dùng: brew install ngrok/ngrok/ngrok"
    echo "  3. Hoặc dùng: npm install -g ngrok"
    echo ""
    exit 1
fi

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python chưa được cài đặt!"
    exit 1
fi

echo "[1/3] Đang khởi động OTA Server..."
cd "$(dirname "$0")/server"
python3 main.py &
SERVER_PID=$!
cd ..

sleep 3

echo "[2/3] Đang khởi động ngrok..."
ngrok http 8000 &
NGROK_PID=$!

sleep 2

echo "[3/3] Đang mở ngrok dashboard..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:4040
elif command -v open &> /dev/null; then
    open http://localhost:4040
fi

echo ""
echo "========================================"
echo "  ✓ Đã khởi động thành công!"
echo "========================================"
echo ""
echo "Server local:  http://localhost:8000"
echo "Ngrok dashboard: http://localhost:4040"
echo ""
echo "Server PID: $SERVER_PID"
echo "Ngrok PID: $NGROK_PID"
echo ""
echo "Lấy URL công khai từ ngrok dashboard"
echo "và gửi cho khách hàng!"
echo ""
echo "Nhấn Ctrl+C để dừng..."
echo ""

# Mở Web UI
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000
elif command -v open &> /dev/null; then
    open http://localhost:8000
fi

# Đợi signal để dừng
trap "kill $SERVER_PID $NGROK_PID 2>/dev/null; exit" INT TERM
wait

