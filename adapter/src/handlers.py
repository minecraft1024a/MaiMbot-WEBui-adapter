import time
from typing import Dict, Any, Optional
from loguru import logger
from maim_message import (
    BaseMessageInfo, UserInfo, GroupInfo, MessageBase, Seg
)
from .client import BackendClient
from .database import DatabaseManager
from .config import AdapterConfig

DEFAULT_USER = "maimai"
DEFAULT_NICKNAME = "web用户"
DEFAULT_SESSION_ID = "default"

def parse_maibot_message(message) -> Dict[str, Any]:
    """统一解析MaiBot Core消息"""
    text = ''
    image_b64 = None
    msg_type = 'text'
    nickname = DEFAULT_NICKNAME
    from_user = DEFAULT_USER
    session_id = None

    segments = []
    if isinstance(message, dict):
        segments = message.get('message_segment', [])
        if isinstance(segments, dict): # Handle single segment case
            segments = [segments]
    elif hasattr(message, 'message_segment'):
        segments = message.message_segment
        if hasattr(message, 'message_info') and hasattr(message.message_info, 'user_info'):
            nickname = DEFAULT_USER
            from_user = DEFAULT_USER

    for seg in segments:
        seg_dict = seg if isinstance(seg, dict) else seg.__dict__
        if seg_dict.get('type') == 'text':
            text += seg_dict.get('data', '')
        elif seg_dict.get('type') == 'image':
            image_b64 = seg_dict.get('data', '')
            msg_type = 'image'

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

async def handle_from_maibot(message: MessageBase, client: BackendClient):
    """处理MaiBot Core下发的消息，并转发到http后端"""
    try:
        parsed = parse_maibot_message(message)
        logger.info(f"[MaiBot] 收到消息: {parsed}")
        
        session_id = parsed.get('session_id') or DEFAULT_SESSION_ID
        
        payload = {
            "from_user": parsed['from_user'], 
            "text": parsed['text'], 
            "nickname": parsed['nickname'],
            "session_id": session_id
        }
        
        if parsed['type'] == 'image' and parsed['image_b64']:
            payload['type'] = 'image'
            payload['image_b64'] = parsed['image_b64']
        
        await client.send_message(payload)
        logger.info(f"[Adapter] 成功转发MaiBot Core消息到后端")
    except Exception as e:
        logger.error(f"[Adapter] 处理MaiBot Core消息转发到后端时出错: {e}", exc_info=True)

def create_maibot_message(msg: Dict[str, Any], config: AdapterConfig, db_manager: DatabaseManager) -> Optional[MessageBase]:
    """根据从后端获取的消息创建MaiBot消息对象"""
    if msg.get("from_user") == DEFAULT_USER:
        return None

    session_id = msg.get("session_id", DEFAULT_SESSION_ID)
    group_id = db_manager.get_or_create_group_id(session_id)
    
    user_info = UserInfo(
        platform=config.platform_id, 
        user_id=msg.get("from_user", "web"), 
        user_nickname=msg.get("nickname") or DEFAULT_NICKNAME
    )
    group_info = GroupInfo(
        platform=config.platform_id, 
        group_id=group_id, 
        group_name=f"会话{group_id}"
    )
    message_info = BaseMessageInfo(
        platform=config.platform_id,
        message_id=str(time.time()),
        time=time.time(),
        user_info=user_info,
        group_info=group_info,
        format_info={"content_format": ["text"], "accept_format": ["text", "image"]}
    )

    text_content = msg.get('text', '')
    msg_type = msg.get('type')
    image_b64 = msg.get('image_b64')

    if msg_type == 'image' and image_b64:
        seg = Seg("seglist", [Seg("image", image_b64)])
    elif msg_type == 'image' and text_content.startswith('/9j'): # 兼容旧格式
        seg = Seg("seglist", [Seg("image", text_content)])
    elif text_content:
        seg = Seg("seglist", [Seg("text", text_content)])
    else:
        logger.warning(f"[Adapter] 跳过内容为空的消息: {msg}")
        return None

    message = MessageBase(message_info=message_info, message_segment=seg)
    if not hasattr(message, 'extra'):
        message.extra = {}
    message.extra['session_id'] = session_id
    
    return message
