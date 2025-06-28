@echo off
REM 一键启动前后端（Windows专用）
cd /d %~dp0
cd http_server/backend
start "FastAPI后端" cmd /k "uvicorn app:app --reload --port 8050"

REM 自动打开前端页面
start http://localhost:5173
