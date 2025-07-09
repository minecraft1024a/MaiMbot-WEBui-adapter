"""
MaiMbot WebUI Adapter - 主应用程序
一个基于 FastAPI 和 React 的聊天机器人 Web 界面适配器
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from loguru import logger

from backend.config import config
from backend.models import initialize_database
from backend.routes import api_router
from backend.frontend_launcher import FrontendLauncher


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 正在启动 MaiMbot WebUI Adapter...")
    
    # 初始化数据库
    initialize_database()
    logger.info("✅ 数据库初始化完成")
    
    # 启动前端服务
    frontend_launcher = FrontendLauncher()
    frontend_launcher.start_frontend()
    logger.info("✅ 前端服务启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("👋 MaiMbot WebUI Adapter 已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="MaiMbot WebUI Adapter",
        description="聊天机器人 Web 界面适配器",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌟 启动服务器: http://{config.host}:{config.port}")
    uvicorn.run(
        "app:app", 
        host=config.host, 
        port=config.port, 
        reload=True, 
        log_level="info"
    )
