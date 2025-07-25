@echo off
chcp 65001
echo 🚀 启动 MaiMbot WebUI Adapter
echo.
cd /d "%~dp0http_server"
python main.py
pause
