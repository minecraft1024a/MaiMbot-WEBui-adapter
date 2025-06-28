from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
import subprocess
import webbrowser
import threading
import time
import os
import requests
from loguru import logger
from fastapi.responses import JSONResponse
from peewee import SqliteDatabase, Model, CharField, TextField, DateTimeField
from datetime import datetime
import json
import logging

# lifespan事件和FastAPI实例
@asynccontextmanager
async def lifespan(app):
    def run_frontend():
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if not os.path.exists(os.path.join(frontend_dir, 'package.json')):
            print(f"未找到前端 package.json，前端未启动。路径: {frontend_dir}")
            return
        try:
            subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, shell=True)
        except Exception as e:
            print(f"启动前端失败: {e}")
        time.sleep(2.5)
        webbrowser.open_new_tab("http://localhost:5173")
    threading.Thread(target=run_frontend, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置uvicorn日志级别为info，输出所有请求日志
logging.basicConfig(level=logging.INFO)

# 内存存储（可替换为数据库）
MESSAGES = []
BACKGROUND_URL = ""
SPRITE_URL = ""

# Peewee数据库初始化
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')
db = SqliteDatabase(DB_PATH)

class ChatMessage(Model):
    from_user = CharField()
    text = TextField()
    type = CharField()
    image_b64 = TextField()
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = db

class BackgroundConfig(Model):
    key = CharField(primary_key=True)
    value = TextField()
    class Meta:
        database = db

class SpriteConfig(Model):
    key = CharField(primary_key=True)
    value = TextField()
    class Meta:
        database = db

# 启动时自动建表
with db:
    db.create_tables([ChatMessage, BackgroundConfig, SpriteConfig])

# 启动时从数据库加载背景
row = BackgroundConfig.get_or_none(BackgroundConfig.key == 'background_url')
if row:
    BACKGROUND_URL = row.value
else:
    BACKGROUND_URL = ""

# 启动时从数据库加载立绘
row = SpriteConfig.get_or_none(SpriteConfig.key == 'sprite_url')
if row:
    SPRITE_URL = row.value
else:
    SPRITE_URL = ""

class Message(BaseModel):
    from_user: str
    text: Optional[str] = ""
    type: Optional[str] = ""
    image_b64: Optional[str] = ""

class BgSpriteUrl(BaseModel):
    url: str

@app.get("/messages", response_model=List[Message])
def get_messages():
    # 查询所有消息，按时间排序
    msgs = ChatMessage.select().order_by(ChatMessage.created_at.asc())
    result = []
    for m in msgs:
        result.append({
            "from_user": m.from_user or "",
            "text": m.text or "",
            "type": m.type or "",
            "image_b64": m.image_b64 or ""
        })
    return result

@app.post("/send_message")
def send_message_from_web(msg: Message):
    ChatMessage.create(
        from_user=msg.from_user or "",
        text=msg.text or "",
        type=msg.type or "",
        image_b64=msg.image_b64 or ""
    )
    logger.info(f"[后端] 前端消息: {msg.from_user}: {msg.text if msg.text else '[图片]'}")
    return {"success": True}

@app.post("/messages")
def post_message(msg: Message):
    ChatMessage.create(
        from_user=msg.from_user or "",
        text=msg.text or "",
        type=msg.type or "",
        image_b64=msg.image_b64 or ""
    )
    return {"success": True}

@app.post("/background")
def set_background(data: BgSpriteUrl):
    global BACKGROUND_URL
    BACKGROUND_URL = data.url
    # 存储到数据库
    BackgroundConfig.insert(key='background_url', value=BACKGROUND_URL).on_conflict_replace().execute()
    return {"success": True}

@app.get("/background")
def get_background():
    # 如果是base64，直接返回
    if BACKGROUND_URL and BACKGROUND_URL.startswith("data:image/"):
        return {"url": BACKGROUND_URL}
    # 否则当作普通url
    return {"url": BACKGROUND_URL}

@app.post("/sprite")
def set_sprite(data: BgSpriteUrl):
    global SPRITE_URL
    SPRITE_URL = data.url
    # 存储到数据库
    SpriteConfig.insert(key='sprite_url', value=SPRITE_URL).on_conflict_replace().execute()
    return {"success": True}

@app.get("/sprite")
def get_sprite():
    if SPRITE_URL and SPRITE_URL.startswith("data:image/"):
        return {"url": SPRITE_URL}
    return {"url": SPRITE_URL}

# 读取host/port配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../public/server_config.json')
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
            HOST = config.get('host', '127.0.0.1')
            PORT = int(config.get('port', 8050))
        except Exception:
            HOST = '127.0.0.1'
            PORT = 8050
else:
    HOST = '127.0.0.1'
    PORT = 8050

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True, log_level="info")
