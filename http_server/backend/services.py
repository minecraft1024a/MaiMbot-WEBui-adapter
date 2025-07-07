"""
业务服务层
"""
from typing import List, Optional, Dict, Any
from loguru import logger

from backend.models import (
    ChatMessage, BackgroundConfig, SpriteConfig, 
    AvatarConfig, ThemeConfig, ApiKeyConfig, db
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


class ThemeService:
    """主题服务"""
    
    @staticmethod
    def get_theme() -> str:
        """获取主题配置"""
        try:
            config = ThemeConfig.get_or_none(ThemeConfig.key == 'theme')
            return config.value if config else 'auto'
        except Exception as e:
            logger.error(f"获取主题配置失败: {e}")
            return 'auto'
    
    @staticmethod
    def set_theme(theme: str) -> bool:
        """设置主题配置"""
        try:
            ThemeConfig.insert(
                key='theme',
                value=theme
            ).on_conflict_replace().execute()
            logger.info(f"主题设置成功: {theme}")
            return True
        except Exception as e:
            logger.error(f"设置主题配置失败: {e}")
            return False


class ApiKeyService:
    """API密钥服务"""
    
    @staticmethod
    def get_api_key(key: str) -> str:
        """获取API密钥"""
        try:
            config = ApiKeyConfig.get_or_none(ApiKeyConfig.key == key)
            return config.value if config else ''
        except Exception as e:
            logger.error(f"获取API密钥失败: {e}")
            return ''
    
    @staticmethod
    def set_api_key(key: str, value: str) -> bool:
        """设置API密钥"""
        try:
            ApiKeyConfig.insert(
                key=key,
                value=value
            ).on_conflict_replace().execute()
            logger.info(f"API密钥设置成功: {key}")
            return True
        except Exception as e:
            logger.error(f"设置API密钥失败: {e}")
            return False
    
    @staticmethod
    def get_all_api_keys() -> List[Dict[str, str]]:
        """获取所有API密钥"""
        try:
            configs = ApiKeyConfig.select()
            return [{"key": config.key, "value": config.value} for config in configs]
        except Exception as e:
            logger.error(f"获取所有API密钥失败: {e}")
            return []


class DatabaseService:
    """数据库服务"""
    
    @staticmethod
    def clear_data() -> bool:
        """清空数据"""
        try:
            # 清空所有表的数据，但保留表结构
            ChatMessage.delete().execute()
            BackgroundConfig.delete().execute()
            SpriteConfig.delete().execute()
            AvatarConfig.delete().execute()
            ThemeConfig.delete().execute()
            ApiKeyConfig.delete().execute()
            
            logger.info("数据清空成功")
            return True
        except Exception as e:
            logger.error(f"数据清空失败: {e}")
            return False
    
    @staticmethod
    def clear_database() -> bool:
        """删除数据库文件"""
        try:
            import os
            from backend.config import config
            
            # 关闭数据库连接
            db.close()
            
            # 删除数据库文件
            if os.path.exists(config.database_url):
                os.remove(config.database_url)
                logger.info(f"数据库文件删除成功: {config.database_url}")
            
            # 重新初始化数据库
            from backend.models import initialize_database
            initialize_database()
            
            logger.info("数据库重新初始化成功")
            return True
        except Exception as e:
            logger.error(f"删除数据库文件失败: {e}")
            return False
