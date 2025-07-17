"""
API路由定义
"""
from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from typing import List

from backend.connection_manager import manager
from backend.schemas import (
    MessageRequest, MessageResponse, UrlRequest, UrlResponse,
    AvatarConfigRequest, AvatarConfigResponse, StandardResponse,
    ThemeRequest, ThemeResponse, ApiKeyRequest, ApiKeyResponse, ApiKeysResponse
)
from backend.services import ChatService, ConfigService, ThemeService, ApiKeyService, DatabaseService


# 创建路由器
api_router = APIRouter()


@api_router.get("/messages", response_model=List[MessageResponse])
async def get_messages(request: Request):
    """获取消息列表"""
    session_id = request.query_params.get('session_id', 'default')
    messages = ChatService.get_messages(session_id)
    return messages


@api_router.post("/send_message", response_model=StandardResponse)
async def send_message(message: MessageRequest, request: Request):
    """发送消息"""
    session_id = request.query_params.get('session_id', 'default')
    success = ChatService.send_message(message, session_id)

    if success:
        # 广播新消息
        await manager.broadcast(message.dict(), session_id)
    
    return StandardResponse(
        success=success,
        message="消息发送成功" if success else "消息发送失败"
    )


@api_router.get("/background", response_model=UrlResponse)
async def get_background():
    """获取背景配置"""
    url = ConfigService.get_background()
    return UrlResponse(url=url)


@api_router.post("/background", response_model=StandardResponse)
async def set_background(data: UrlRequest):
    """设置背景配置"""
    success = ConfigService.set_background(data.url)
    return StandardResponse(
        success=success,
        message="背景设置成功" if success else "背景设置失败"
    )


@api_router.get("/sprite", response_model=UrlResponse)
async def get_sprite():
    """获取立绘配置"""
    url = ConfigService.get_sprite()
    return UrlResponse(url=url)


@api_router.post("/sprite", response_model=StandardResponse)
async def set_sprite(data: UrlRequest):
    """设置立绘配置"""
    success = ConfigService.set_sprite(data.url)
    return StandardResponse(
        success=success,
        message="立绘设置成功" if success else "立绘设置失败"
    )


@api_router.get("/avatar_config", response_model=AvatarConfigResponse)
async def get_avatar_config():
    """获取头像配置"""
    config = ConfigService.get_avatar_config()
    return AvatarConfigResponse(**config)


@api_router.post("/avatar_config", response_model=StandardResponse)
async def set_avatar_config(data: AvatarConfigRequest):
    """设置头像配置"""
    success = ConfigService.set_avatar_config(data.user, data.bot)
    return StandardResponse(
        success=success,
        message="头像配置成功" if success else "头像配置失败"
    )


# 主题相关API
@api_router.get("/theme", response_model=ThemeResponse)
async def get_theme():
    """获取主题配置"""
    theme = ThemeService.get_theme()
    return ThemeResponse(theme=theme)


@api_router.post("/theme", response_model=StandardResponse)
async def set_theme(data: ThemeRequest):
    """设置主题配置"""
    success = ThemeService.set_theme(data.theme)
    return StandardResponse(
        success=success,
        message="主题设置成功" if success else "主题设置失败"
    )


# API密钥相关API
@api_router.get("/api_keys", response_model=ApiKeysResponse)
async def get_api_keys():
    """获取所有API密钥"""
    keys = ApiKeyService.get_all_api_keys()
    return ApiKeysResponse(keys=keys)


@api_router.post("/api_key", response_model=StandardResponse)
async def set_api_key(data: ApiKeyRequest):
    """设置API密钥"""
    success = ApiKeyService.set_api_key(data.key, data.value)
    return StandardResponse(
        success=success,
        message="API密钥设置成功" if success else "API密钥设置失败"
    )


# 数据库管理API
@api_router.post("/database/clear", response_model=StandardResponse)
async def clear_database():
    """清空数据"""
    success = DatabaseService.clear_data()
    return StandardResponse(
        success=success,
        message="数据清空成功" if success else "数据清空失败"
    )


@api_router.delete("/database", response_model=StandardResponse)
async def delete_database():
    """删除数据库"""
    success = DatabaseService.clear_database()
    return StandardResponse(
        success=success,
        message="数据库删除成功" if success else "数据库删除失败"
    )


@api_router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # 在这里，我们只是保持连接打开以接收广播
            # 客户端不需要通过这个WebSocket发送消息
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        print(f"Client #{session_id} disconnected")
