"""
API路由定义
"""
from fastapi import APIRouter, Request, HTTPException
from typing import List

from backend.schemas import (
    MessageRequest, MessageResponse, UrlRequest, UrlResponse,
    AvatarConfigRequest, AvatarConfigResponse, StandardResponse
)
from backend.services import ChatService, ConfigService


# 创建路由器
api_router = APIRouter()


@api_router.get("/messages", response_model=List[MessageResponse])
async def get_messages(request: Request):
    """获取消息列表"""
    session_id = request.query_params.get('session_id', 'default')
    messages = ChatService.get_messages(session_id)
    return messages


@api_router.post("/messages", response_model=StandardResponse)
@api_router.post("/send_message", response_model=StandardResponse)
async def send_message(message: MessageRequest, request: Request):
    """发送消息"""
    session_id = request.query_params.get('session_id', 'default')
    success = ChatService.send_message(message, session_id)
    
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
