import asyncio
import time
import requests
import tomllib
from maim_message import (
    BaseMessageInfo, UserInfo, GroupInfo, MessageBase, Seg,
    Router, RouteConfig, TargetConfig
)
import os
from loguru import logger
import httpx
import sqlite3
from typing import Dict, Any, Optional

class AdapterConfig:
    """适配器配置管理"""
    def __init__(self, config_path: str = 'config.toml'):
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'adapter': {
                'platform_id': 'maimai_http_adapter',
                'poll_interval': 2
            },
            'connection': {
                'ws_url': 'ws://127.0.0.1:8000/ws',
                'http_backend_url': 'http://127.0.0.1:8050'
            },
            'database': {
                'db_path': '../http_server/backend/chat.db'
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    @property
    def platform_id(self) -> str:
        return self._config['adapter']['platform_id']
    
    @property
    def poll_interval(self) -> int:
        return self._config['adapter']['poll_interval']
    
    @property
    def ws_url(self) -> str:
        return self._config['connection']['ws_url']
    
    @property
    def http_backend_url(self) -> str:
        url = self._config['connection']['http_backend_url']
        return url.rstrip('/') if url.endswith('/') else url
    
    @property
    def db_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), self._config['database']['db_path'])

# 初始化配置
config = AdapterConfig()

route_config = RouteConfig(
    route_config={
        config.platform_id: TargetConfig(
            url=config.ws_url,
            token=None
        )
    }
)

router = Router(route_config)

class MessageProcessor:
    """消息处理器"""
    
    @staticmethod
    async def send_to_backend(text: str, from_user: str = "maimai", 
                             nickname: Optional[str] = None, extra: Optional[Dict] = None):
        """发送消息到HTTP后端"""
        try:
            payload = {"from_user": from_user, "text": text, "nickname": nickname or "web用户"}
            if extra:
                payload.update(extra)
            logger.info(f"[Adapter] 正在转发消息到后端: {payload}")
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{config.http_backend_url}/messages",
                    json=payload,
                    timeout=5
                )
        except Exception as e:
            logger.error(f"[Adapter] 发送到后端失败: {e}")
    
    @staticmethod
    def parse_maibot_message(message) -> Dict[str, Any]:
        """统一解析MaiBot Core消息"""
        text = ''
        image_b64 = None
        msg_type = 'text'
        nickname = None
        from_user = 'maimai'
        session_id = None
        
        # dict结构
        if isinstance(message, dict):
            segments = message.get('message_segment', [])
            if isinstance(segments, dict):
                if segments.get('type') == 'text':
                    text += segments.get('data', '')
                elif segments.get('type') == 'image':
                    image_b64 = segments.get('data', '')
                    msg_type = 'image'
            elif isinstance(segments, list):
                for seg in segments:
                    if isinstance(seg, dict):
                        if seg.get('type') == 'text':
                            text += seg.get('data', '')
                        elif seg.get('type') == 'image':
                            image_b64 = seg.get('data', '')
                            msg_type = 'image'
        # MessageBase结构
        else:
            for seg in message.message_segment:
                if seg.type == 'text':
                    text += seg.data
                elif seg.type == 'image':
                    image_b64 = seg.data
                    msg_type = 'image'
            if hasattr(message, 'message_info') and hasattr(message.message_info, 'user_info'):
                nickname = "maimai"
                from_user = 'maimai'
        
        # 尝试从 message.extra 取 session_id
        if hasattr(message, 'extra') and isinstance(message.extra, dict):
            session_id = message.extra.get('session_id')
        
        return {
            'type': msg_type,
            'text': text,
            'image_b64': image_b64,
            'nickname': nickname,
            'from_user': from_user,
            'session_id': session_id
        }

async def handle_from_maibot(message: MessageBase):
    """处理MaiBot Core下发的消息，并转发到http后端"""
    try:
        parsed = MessageProcessor.parse_maibot_message(message)
        logger.info(f"[MaiBot] 收到消息: {parsed}")
        # 取 session_id，优先 extra 里的
        session_id = parsed.get('session_id') or 'default'
        extra = {'type': parsed['type']} if parsed['type'] == 'image' else {}
        if parsed['type'] == 'image' and parsed['image_b64']:
            extra['image_b64'] = parsed['image_b64']
        extra['session_id'] = session_id
        await MessageProcessor.send_to_backend(parsed['text'], from_user=parsed['from_user'], nickname=parsed['nickname'], extra=extra)
        logger.info(f"[Adapter] 正在转发MaiBot Core消息到后端: {parsed}")
    except Exception as e:
        logger.error(f"[Adapter] 处理MaiBot Core消息转发到后端时出错: {e}")

router.register_class_handler(handle_from_maibot)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_path = config.db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('CREATE TABLE IF NOT EXISTS session_group (session_id TEXT PRIMARY KEY, group_id TEXT)')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
    
    def get_or_create_group_id(self, session_id: str) -> str:
        """获取或创建群组ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.execute('SELECT group_id FROM session_group WHERE session_id=?', (session_id,))
            row = cur.fetchone()
            if row:
                conn.close()
                return row[0]
            group_id = session_id  # 你也可以用 uuid 或自增ID
            conn.execute('INSERT INTO session_group (session_id, group_id) VALUES (?, ?)', (session_id, group_id))
            conn.commit()
            conn.close()
            return group_id
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            return session_id

# 初始化数据库管理器
db_manager = DatabaseManager()

class MessagePoller:
    """消息轮询器"""
    
    def __init__(self):
        self.last_message_count = 0
    
    async def poll_and_send(self):
        """轮询http后端新消息并转发到MaiBot Core"""
        try:
            resp = requests.get(f"{config.http_backend_url}/messages")
            msgs = resp.json()
            self.last_message_count = len(msgs) if isinstance(msgs, list) else 0
        except Exception as e:
            logger.error(f"[Adapter] 启动时获取消息失败: {e}")
            self.last_message_count = 0
        
        while True:
            try:
                resp = requests.get(f"{config.http_backend_url}/messages")
                msgs = resp.json()
                if not isinstance(msgs, list):
                    logger.warning(f"[Adapter] /messages 返回内容不是列表: {msgs}")
                    await asyncio.sleep(config.poll_interval)
                    continue
                
                if self.last_message_count < 0 or self.last_message_count > len(msgs):
                    self.last_message_count = 0
                
                for msg in msgs[self.last_message_count:]:
                    # 跳过自己发出的消息，防止循环转发
                    if (msg.get("nickname") == "maimai") or (msg.get("from_user") == "maimai"):
                        continue
                    
                    session_id = msg.get("session_id", "default")
                    group_id = db_manager.get_or_create_group_id(session_id)
                    user_info = UserInfo(platform=config.platform_id, user_id=msg.get("from_user", "web"), user_nickname=msg.get("nickname") or "web用户")
                    group_info = GroupInfo(platform=config.platform_id, group_id=group_id, group_name=f"会话{group_id}")
                    message_info = BaseMessageInfo(
                        platform=config.platform_id,
                        message_id=str(time.time()),
                        time=time.time(),
                        user_info=user_info,
                        group_info=group_info,
                        format_info={"content_format": ["text"], "accept_format": ["text", "image"]}
                    )
                    
                    # 适配图片消息
                    if msg.get('type') == 'image' and msg.get('image_b64'):
                        seg = Seg("seglist", [Seg("image", msg["image_b64"])])
                    elif (msg.get('type') == 'image' or (msg.get('text') and msg.get('text', '').startswith('/9j'))) and msg.get('text'):
                        # 兼容type缺失但text为b64图片的情况
                        seg = Seg("seglist", [Seg("image", msg["text"])])
                    elif msg.get('type') == 'text' or msg.get('text'):
                        seg = Seg("seglist", [Seg("text", msg["text"])])
                    else:
                        if msg.get('type') or msg.get('text') == "":
                            # 兜底：空消息不转发
                            logger.warning(f"[Adapter] 跳过空消息: {msg}")
                            continue
                    
                    message = MessageBase(message_info=message_info, message_segment=seg)
                    # 在 message 对象中附加 session_id，便于下游回传
                    if not hasattr(message, 'extra'):
                        message.extra = {}
                    message.extra['session_id'] = session_id
                    await router.send_message(message)
                
                self.last_message_count = len(msgs)
            except Exception as e:
                logger.error(f"[Adapter] 轮询或转发消息出错: {e}")
            await asyncio.sleep(config.poll_interval)

# 初始化消息轮询器
poller = MessagePoller()

def send_message_to_maibot(text: str, user_id: str = "cli"):
    """提供命令行发送消息到MaiBot Core"""
    user_info = UserInfo(platform=config.platform_id, user_id=user_id)
    message_info = BaseMessageInfo(
        platform=config.platform_id,
        message_id=str(time.time()),
        time=time.time(),
        user_info=user_info,
        group_info=None,
        format_info={"content_format": ["text"], "accept_format": ["text", "image"]}
    )
    seg = Seg("seglist", [Seg("text", text)])
    message = MessageBase(message_info=message_info, message_segment=seg)
    asyncio.run(router.send_message(message))

async def main():
    """主函数"""
    router_task = asyncio.create_task(router.run())
    poll_task = asyncio.create_task(poller.poll_and_send())
    await asyncio.gather(router_task, poll_task)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # 命令行发送消息到MaiBot Core
        send_message_to_maibot(' '.join(sys.argv[1:]))
    else:
        asyncio.run(main())
