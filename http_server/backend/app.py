from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import subprocess
import webbrowser
import threading
import time
import os
import requests
from loguru import logger
from fastapi.responses import JSONResponse
from peewee import SqliteDatabase, Model, CharField

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

# 假设用内存模拟数据库
USER_INFO = {"nickname": "web用户"}

class Message(BaseModel):
    from_user: str
    text: str
    nickname: str = None

class BgSpriteUrl(BaseModel):
    url: str

# Peewee数据库初始化
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')
db = SqliteDatabase(DB_PATH)

class UserInfo(Model):
    nickname = CharField(null=False, unique=True)
    class Meta:
        database = db

# 启动时自动建表
with db:
    db.create_tables([UserInfo])

@app.get("/messages", response_model=List[Message])
def get_messages():
    return MESSAGES

@app.post("/send_message")
def send_message_from_web(msg: Message):
    """前端专用：只存储web用户消息，并转发到/messages供适配器轮询"""
    MESSAGES.append(msg)
    logger.info(f"[后端] 前端消息: {msg.from_user}: {msg.text}")
    # 自动转发到/messages（适配器路由）
    try:
        requests.post("http://127.0.0.1:8000/messages", json=msg.dict())
        logger.info("[后端] 已转发到/messages")
    except Exception as e:
        logger.error(f"[后端] 自动转发到/messages失败: {e}")
    return {"success": True}

@app.post("/messages")
def post_message(msg: Message):
    """适配器专用：只存储来自适配器的消息，不被前端直接调用"""
    MESSAGES.append(msg)
    return {"success": True}

@app.get("/background")
def get_background():
    return {"url": BACKGROUND_URL}

@app.post("/background")
def set_background(data: BgSpriteUrl):
    global BACKGROUND_URL
    BACKGROUND_URL = data.url
    return {"success": True}

@app.get("/sprite")
def get_sprite():
    return {"url": SPRITE_URL}

@app.post("/sprite")
def set_sprite(data: BgSpriteUrl):
    global SPRITE_URL
    SPRITE_URL = data.url
    return {"success": True}

@app.get("/get_nickname")
def get_nickname():
    user = UserInfo.select().first()
    return {"nickname": user.nickname if user else "web用户"}

@app.post("/set_nickname")
def set_nickname(data: dict = Body(...)):
    nickname = data.get("nickname", "web用户")
    user, created = UserInfo.get_or_create(nickname=nickname)
    if not created:
        user.nickname = nickname
        user.save()
    return JSONResponse({"success": True, "nickname": user.nickname})

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
