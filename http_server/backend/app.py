from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# 启动时自动建表
with db:
    db.create_tables([ChatMessage])

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

@app.get("/background")
def get_background():
    # 如果是base64，直接返回
    if BACKGROUND_URL and BACKGROUND_URL.startswith("data:image/"):
        return {"url": BACKGROUND_URL}
    # 否则当作普通url
    return {"url": BACKGROUND_URL}

@app.post("/background")
def set_background(data: BgSpriteUrl):
    global BACKGROUND_URL
    BACKGROUND_URL = data.url
    return {"success": True}

@app.get("/sprite")
def get_sprite():
    if SPRITE_URL and SPRITE_URL.startswith("data:image/"):
        return {"url": SPRITE_URL}
    return {"url": SPRITE_URL}

@app.post("/sprite")
def set_sprite(data: BgSpriteUrl):
    global SPRITE_URL
    SPRITE_URL = data.url
    return {"success": True}

@app.on_event("startup")
def open_frontend():
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
