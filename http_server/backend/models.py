"""
数据库模型定义
"""
from peewee import (
    SqliteDatabase, Model, CharField, TextField, 
    DateTimeField, PrimaryKeyField
)
from datetime import datetime
from backend.config import config


# 数据库连接
db = SqliteDatabase(config.database_url)


class BaseModel(Model):
    """基础模型类"""
    class Meta:
        database = db


class ChatMessage(BaseModel):
    """聊天消息模型"""
    id = PrimaryKeyField()
    session_id = CharField(default='default', help_text='会话ID')
    from_user = CharField(help_text='发送者')
    text = TextField(default='', help_text='文本内容')
    type = CharField(default='text', help_text='消息类型')
    image_b64 = TextField(default='', help_text='图片Base64数据')
    created_at = DateTimeField(default=datetime.now, help_text='创建时间')
    
    class Meta:
        table_name = 'chat_messages'
        indexes = (
            (('session_id', 'created_at'), False),
        )


class BackgroundConfig(BaseModel):
    """背景配置模型"""
    key = CharField(primary_key=True)
    value = TextField(help_text='背景URL或Base64数据')
    
    class Meta:
        table_name = 'background_config'


class SpriteConfig(BaseModel):
    """立绘配置模型"""
    key = CharField(primary_key=True)
    value = TextField(help_text='立绘URL或Base64数据')
    
    class Meta:
        table_name = 'sprite_config'


class AvatarConfig(BaseModel):
    """头像配置模型"""
    key = CharField(primary_key=True, help_text='user或bot')
    name = CharField(help_text='显示名称')
    avatar = TextField(default='', help_text='头像URL或Base64数据')
    
    class Meta:
        table_name = 'avatar_config'


class ThemeConfig(BaseModel):
    """主题配置模型"""
    key = CharField(primary_key=True, default='theme')
    value = CharField(default='auto', help_text='主题设置: light, dark, auto')
    
    class Meta:
        table_name = 'theme_config'


class ApiKeyConfig(BaseModel):
    """API密钥配置模型"""
    key = CharField(primary_key=True, help_text='密钥名称')
    value = TextField(help_text='密钥值')
    
    class Meta:
        table_name = 'api_key_config'


def initialize_database():
    """初始化数据库"""
    with db:
        db.create_tables([
            ChatMessage, 
            BackgroundConfig, 
            SpriteConfig, 
            AvatarConfig,
            ThemeConfig,
            ApiKeyConfig
        ], safe=True)


# 所有模型类
__all__ = [
    'db',
    'ChatMessage',
    'BackgroundConfig', 
    'SpriteConfig',
    'AvatarConfig',
    'ThemeConfig',
    'ApiKeyConfig',
    'initialize_database'
]
