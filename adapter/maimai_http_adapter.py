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
async def send_to_backend(text, from_user="maimai", nickname=None):
    if not nickname:
        nickname = "web用户"
    try:
        logger.info(f"[Adapter] 正在转发消息到后端: from_user={from_user}, nickname={nickname}, text={text}")
        requests.post(
            f"{HTTP_BACKEND}/messages",
            json={"from_user": from_user, "text": text, "nickname": nickname}
        )
    except Exception as e:
        logger.error(f"[Adapter] 发送到后端失败: {e}")

# 处理MaiBot Core下发的消息（下游到http后端）
async def handle_from_maibot(message: MessageBase):
    print(f"[MaiBot] 收到消息: {message.message_segment}")
    text = ''
    nickname = None
    for seg in message.message_segment:
        if seg.type == 'text':
            text += seg.data
    # 优先取message_info.user_info.user_nickname
    if hasattr(message, 'message_info') and hasattr(message.message_info, 'user_info'):
        nickname = getattr(message.message_info.user_info, 'user_nickname', None)
    await send_to_backend(text, nickname=nickname)

router.register_class_handler(handle_from_maibot)

# 轮询http后端新消息并转发到MaiBot Core（http后端到下游）
async def poll_and_send():
    last_len = 0
    while True:
        try:
            resp = requests.get(f"{HTTP_BACKEND}/messages")
            msgs = resp.json()
            if not isinstance(msgs, list):
                print(f"[Adapter] /messages 返回内容不是列表: {msgs}")
                await asyncio.sleep(POLL_INTERVAL)
                continue
            if last_len is None or last_len < 0 or last_len > len(msgs):
                last_len = 0
            for msg in msgs[last_len:]:
                # 只回传非web用户的消息，防止回环
                if msg.get("from_user") == "web":
                    continue
                user_info = UserInfo(platform=PLATFORM_ID, user_id=msg.get("from_user", "web"), user_nickname=msg.get("nickname") or "web用户")
                message_info = BaseMessageInfo(
                    platform=PLATFORM_ID,
                    message_id=str(time.time()),
                    time=time.time(),
                    user_info=user_info,
                    group_info=None,
                    format_info={"content_format": ["text"], "accept_format": ["text", "image"]}
                )
                seg = Seg("seglist", [Seg("text", msg["text"])])
                message = MessageBase(message_info=message_info, message_segment=seg)
                await router.send_message(message)
            last_len = len(msgs)
        except Exception as e:
            print(f"[Adapter] 轮询或转发消息出错: {e}")
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
