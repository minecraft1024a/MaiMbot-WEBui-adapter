@echo off
REM 一键启动前后端（Windows专用）
cd /d %~dp0
cd http_server/backend
pythpn app.py

REM 自动打开前端页面
