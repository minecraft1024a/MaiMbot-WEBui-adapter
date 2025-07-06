"""
数据模式定义 (Pydantic Models)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MessageRequest(BaseModel):
    """消息请求模型"""
    from_user: str = Field(..., description="发送者")
    text: Optional[str] = Field("", description="文本内容")
    type: Optional[str] = Field("text", description="消息类型")
    image_b64: Optional[str] = Field("", description="图片Base64数据")


class MessageResponse(BaseModel):
    """消息响应模型"""
    from_user: str
    text: str
    type: str
    image_b64: str


class UrlRequest(BaseModel):
    """URL请求模型"""
    url: str = Field(..., description="URL地址")


class UrlResponse(BaseModel):
    """URL响应模型"""
    url: str


class AvatarConfigRequest(BaseModel):
    """头像配置请求模型"""
    user: Dict[str, str] = Field(..., description="用户配置")
    bot: Dict[str, str] = Field(..., description="机器人配置")


class AvatarConfigResponse(BaseModel):
    """头像配置响应模型"""
    user: Dict[str, str]
    bot: Dict[str, str]


class StandardResponse(BaseModel):
    """标准响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: Optional[str] = Field(None, description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
