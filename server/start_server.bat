@echo off
REM Script để khởi động OTA Server trên Windows

echo Đang khởi động OTA Server...
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

