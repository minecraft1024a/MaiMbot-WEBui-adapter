#!/usr/bin/env python3
"""
MaiMbot WebUI Adapter - 启动脚本
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app, config

if __name__ == "__main__":
    import uvicorn
    print(f"🌟 启动 MaiMbot WebUI Adapter")
    print(f"🌐 服务器地址: http://{config.host}:{config.port}")
    print(f"📁 数据库路径: {config.database_url}")
    
    uvicorn.run(
        "backend.app:app",
        host=config.host,
        port=config.port,
        reload=True,
        log_level="info"
    )
