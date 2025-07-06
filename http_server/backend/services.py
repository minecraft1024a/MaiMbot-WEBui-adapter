"""
业务服务层
"""
from typing import List, Optional, Dict, Any
from loguru import logger

from backend.models import (
    ChatMessage, BackgroundConfig, SpriteConfig, 
    AvatarConfig, db
)
from backend.schemas import MessageRequest, MessageResponse


class ChatService:
    """聊天服务"""
    
    @staticmethod
    def get_messages(session_id: str = 'default') -> List[MessageResponse]:
        """获取会话消息列表"""
        try:
            messages = (ChatMessage
                       .select()
                       .where(ChatMessage.session_id == session_id)
                       .order_by(ChatMessage.created_at.asc()))
            
            return [
                MessageResponse(
                    from_user=msg.from_user or "",
                    text=msg.text or "",
                    type=msg.type or "text",
                    image_b64=msg.image_b64 or ""
                )
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []
    
    @staticmethod
    def send_message(message: MessageRequest, session_id: str = 'default') -> bool:
        """发送消息"""
        try:
            ChatMessage.create(
                session_id=session_id,
                from_user=message.from_user,
                text=message.text or "",
                type=message.type or "text",
                image_b64=message.image_b64 or ""
            )
            
            content_info = message.text if message.text else '[图片]'
            logger.info(f"[聊天服务] 消息保存成功: {message.from_user}: {content_info} [session_id={session_id}]")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False


class ConfigService:
    """配置服务"""
    
    @staticmethod
    def get_background() -> str:
        """获取背景配置"""
        try:
            config = BackgroundConfig.get_or_none(BackgroundConfig.key == 'background_url')
            return config.value if config else ""
        except Exception as e:
            logger.error(f"获取背景配置失败: {e}")
            return ""
    
    @staticmethod
    def set_background(url: str) -> bool:
        """设置背景配置"""
        try:
            BackgroundConfig.insert(
                key='background_url', 
                value=url
            ).on_conflict_replace().execute()
            return True
        except Exception as e:
            logger.error(f"设置背景配置失败: {e}")
            return False
    
    @staticmethod
    def get_sprite() -> str:
        """获取立绘配置"""
        try:
            config = SpriteConfig.get_or_none(SpriteConfig.key == 'sprite_url')
            return config.value if config else ""
        except Exception as e:
            logger.error(f"获取立绘配置失败: {e}")
            return ""
    
    @staticmethod
    def set_sprite(url: str) -> bool:
        """设置立绘配置"""
        try:
            SpriteConfig.insert(
                key='sprite_url', 
                value=url
            ).on_conflict_replace().execute()
            return True
        except Exception as e:
            logger.error(f"设置立绘配置失败: {e}")
            return False
    
    @staticmethod
    def get_avatar_config() -> Dict[str, Dict[str, str]]:
        """获取头像配置"""
        try:
            user_config = AvatarConfig.get_or_none(AvatarConfig.key == 'user')
            bot_config = AvatarConfig.get_or_none(AvatarConfig.key == 'bot')
            
            return {
                "user": {
                    "name": user_config.name if user_config else '用户',
                    "avatar": user_config.avatar if user_config else ''
                },
                "bot": {
                    "name": bot_config.name if bot_config else '麦麦',
                    "avatar": bot_config.avatar if bot_config else ''
                }
            }
        except Exception as e:
            logger.error(f"获取头像配置失败: {e}")
            return {
                "user": {"name": "用户", "avatar": ""},
                "bot": {"name": "麦麦", "avatar": ""}
            }
    
    @staticmethod
    def set_avatar_config(user_config: Dict[str, str], bot_config: Dict[str, str]) -> bool:
        """设置头像配置"""
        try:
            # 保存用户配置
            AvatarConfig.insert(
                key='user',
                name=user_config.get('name', '用户'),
                avatar=user_config.get('avatar', '')
            ).on_conflict_replace().execute()
            
            # 保存机器人配置
            AvatarConfig.insert(
                key='bot',
                name=bot_config.get('name', '麦麦'),
                avatar=bot_config.get('avatar', '')
            ).on_conflict_replace().execute()
            
            return True
        except Exception as e:
            logger.error(f"设置头像配置失败: {e}")
            return False
