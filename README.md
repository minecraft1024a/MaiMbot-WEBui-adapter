# MaiMbot-WEBui-adapter 使用说明

## 1. 环境准备

- 操作系统：Windows（推荐）
- 需要安装 [Node.js](https://nodejs.org/)（建议 16.x 及以上）
- 需要安装 [Python 3.8+](https://www.python.org/)（推荐 3.10+）
- 推荐使用 [Git](https://git-scm.com/) 进行代码管理

## 2. 克隆项目

```bash
git clone <你的仓库地址>
cd MaiMbot-WEBui-adapter
```

## 3. 安装依赖

### 前端依赖
```bash
cd http_server
npm install
```

### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

## 4. 启动服务

### 一键启动（推荐）

在项目根目录下运行：

```bash
./start_all.bat
```

前端启动后会自动打开浏览器，访问地址一般为：http://localhost:5173

## 5. 适配器配置与启动

1. 修改 `adapter/config.yaml`，配置你的后端 API 地址（如 `http_backend_url: http://127.0.0.1:8050`）。
2. 启动适配器：

```bash
cd adapter
python maimai_http_adapter.py
```

## 6. 使用说明

- 打开前端页面，输入消息即可与 MaiBot 进行对话。
- 支持发送文本和图片消息。
- 支持切换聊天背景和立绘图片。
- 聊天记录自动持久化，重启后依然可见。

## 7. 常见问题

- **端口冲突**：如 5173/8050 被占用，请修改 `vite.config.js` 和后端端口。
- **数据库报错**：如表结构变动，建议删除 `http_server/backend/chat.db` 重新生成。
- **依赖问题**：请确保 Node.js、Python 依赖均已安装。

## 8. 目录结构简述

```
MaiMbot-WEBui-adapter/
├── adapter/                # 适配器（与 MaiBot Core 通信）
├── http_server/
│   ├── backend/            # FastAPI 后端
│   ├── src/                # React 前端源码
│   ├── public/             # 前端静态资源
│   ├── package.json        # 前端依赖
│   └── ...
├── start_all.bat           # 一键启动脚本
└── README.md               # 使用说明
```

## 9. 联系与反馈

如有问题请在仓库 issue 区留言，或联系开发者。
