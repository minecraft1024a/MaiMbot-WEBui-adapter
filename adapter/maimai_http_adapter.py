import asyncio
import time
import requests
import yaml
from maim_message import (
    BaseMessageInfo, UserInfo, GroupInfo, MessageBase, Seg,
    Router, RouteConfig, TargetConfig
)
import os
from loguru import logger
import httpx
import sqlite3

# 读取配置
with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 兼容配置文件中 http_backend_url 结尾带/和不带/ 的情况
raw_backend = config.get('http_backend_url', 'http://127.0.0.1:8000')
if raw_backend.endswith('/'):
    HTTP_BACKEND = raw_backend[:-1]
else:
    HTTP_BACKEND = raw_backend

WS_URL = config.get('ws_url', 'ws://127.0.0.1:8000/ws')
POLL_INTERVAL = config.get('poll_interval', 2)
PLATFORM_ID = config.get('platform_id', 'maimai_http_adapter')

route_config = RouteConfig(
    route_config={
        PLATFORM_ID: TargetConfig(
            url=WS_URL,
            token=None
        )
    }
)

router = Router(route_config)

# 发送消息到http后端
async def send_to_backend(text, from_user="maimai", nickname=None, extra=None):
    try:
        payload = {"from_user": from_user, "text": text, "nickname": "web用户" }
        if extra:
            payload.update(extra)
        logger.info(f"[Adapter] 正在转发消息到后端: {payload}")
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{HTTP_BACKEND}/messages",
                json=payload,
                timeout=5
            )
    except Exception as e:
        logger.error(f"[Adapter] 发送到后端失败: {e}")

# 处理MaiBot Core下发的消息（下游到http后端）
def parse_maibot_message(message):
    """统一解析MaiBot Core消息，返回dict: {type, text, image_b64, nickname, from_user}"""
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
        parsed = parse_maibot_message(message)
        logger.info(f"[MaiBot] 收到消息: {parsed}")
        # 取 session_id，优先 extra 里的
        session_id = parsed.get('session_id') or 'default'
        extra = {'type': parsed['type']} if parsed['type'] == 'image' else {}
        if parsed['type'] == 'image' and parsed['image_b64']:
            extra['image_b64'] = parsed['image_b64']
        extra['session_id'] = session_id
        await send_to_backend(parsed['text'], from_user=parsed['from_user'], nickname=parsed['nickname'], extra=extra)
        logger.info(f"[Adapter] 正在转发MaiBot Core消息到后端: {parsed}")
    except Exception as e:
        logger.error(f"[Adapter] 处理MaiBot Core消息转发到后端时出错: {e}")

router.register_class_handler(handle_from_maibot)

# 连接原有 chat.db，增加 session_group 映射表
DB_PATH = os.path.join(os.path.dirname(__file__), '../http_server/backend/chat.db')
session_db = sqlite3.connect(DB_PATH)
session_db.execute('CREATE TABLE IF NOT EXISTS session_group (session_id TEXT PRIMARY KEY, group_id TEXT)')
session_db.commit()

def get_or_create_group_id(session_id):
    cur = session_db.execute('SELECT group_id FROM session_group WHERE session_id=?', (session_id,))
    row = cur.fetchone()
    if row:
        return row[0]
    group_id = session_id  # 你也可以用 uuid 或自增ID
    session_db.execute('INSERT INTO session_group (session_id, group_id) VALUES (?, ?)', (session_id, group_id))
    session_db.commit()
    return group_id

# 轮询http后端新消息并转发到MaiBot Core（http后端到下游）
async def poll_and_send():
    try:
        resp = requests.get(f"{HTTP_BACKEND}/messages")
        msgs = resp.json()
        last_len = len(msgs) if isinstance(msgs, list) else 0
    except Exception as e:
        logger.error(f"[Adapter] 启动时获取消息失败: {e}")
        last_len = 0
    while True:
        try:
            resp = requests.get(f"{HTTP_BACKEND}/messages")
            msgs = resp.json()
            if not isinstance(msgs, list):
                logger.warning(f"[Adapter] /messages 返回内容不是列表: {msgs}")
                await asyncio.sleep(POLL_INTERVAL)
                continue
            if last_len is None or last_len < 0 or last_len > len(msgs):
                last_len = 0
            for msg in msgs[last_len:]:
                # 跳过自己发出的消息，防止循环转发
                if (msg.get("nickname") == "maimai" ) or (msg.get("from_user") == "maimai" ):
                    continue
                session_id = msg.get("session_id", "default")
                group_id = get_or_create_group_id(session_id)
                user_info = UserInfo(platform=PLATFORM_ID, user_id=msg.get("from_user", "web"), user_nickname=msg.get("nickname") or "web用户")
                group_info = GroupInfo(platform=PLATFORM_ID, group_id=group_id, group_name=f"会话{group_id}")
                message_info = BaseMessageInfo(
                    platform=PLATFORM_ID,
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
            last_len = len(msgs)
        except Exception as e:
            logger.error(f"[Adapter] 轮询或转发消息出错: {e}")
        await asyncio.sleep(POLL_INTERVAL)

# 提供命令行发送消息到MaiBot Core
def send_message_to_maibot(text, user_id="cli"):
    user_info = UserInfo(platform=PLATFORM_ID, user_id=user_id)
    message_info = BaseMessageInfo(
        platform=PLATFORM_ID,
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
    router_task = asyncio.create_task(router.run())
    poll_task = asyncio.create_task(poll_and_send())
    await asyncio.gather(router_task, poll_task)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # 命令行发送消息到MaiBot Core
        send_message_to_maibot(' '.join(sys.argv[1:]))
    else:
        asyncio.run(main())
