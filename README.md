# MaiMbot WebUI Adapter

一个现代化的聊天机器人 Web 界面适配器，基于 **FastAPI** 后端和 **React** 前端构建。

## ✨ 特性

- 🎨 **现代化 UI 设计**：采用毛玻璃效果和渐变色彩
- 💬 **实时聊天界面**：支持文本和图片消息
- 🖼️ **自定义背景和立绘**：支持 URL 和本地文件上传
- 👤 **头像配置**：可自定义用户和机器人的名字和头像
- 📱 **响应式设计**：适配桌面端和移动端
- 🔄 **会话管理**：支持多会话切换
- 💾 **数据持久化**：使用 SQLite 数据库存储

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代 Python Web 框架
- **Peewee** - 轻量级 ORM
- **SQLite** - 嵌入式数据库
- **Loguru** - 日志管理
- **Uvicorn** - ASGI 服务器

### 前端
- **React 19** - 用户界面库
- **Vite** - 前端构建工具
- **CSS3** - 现代样式（支持毛玻璃效果、动画等）

## 📦 安装与运行

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 快速启动

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd MaiMbot-WEBui-adapter
   ```

2. **安装依赖**
   ```bash
   # 安装后端依赖
   cd http_server/backend
   pip install -r requirements.txt
   
   # 安装前端依赖
   cd ../
   npm install
   ```

3. **启动应用**
   ```bash
   # 方法1：使用启动脚本（推荐）
   ./start_app.bat  # Windows
   
   # 方法2：手动启动
   cd http_server
   python main.py
   ```

4. **访问应用**
   - 应用会自动打开浏览器
   - 默认地址：http://127.0.0.1:8050

## 🎯 核心功能

### 聊天功能
- 发送文本消息
- 发送图片（支持拖拽上传）
- 实时消息同步
- 消息历史记录

### 自定义配置
- **背景设置**：支持网络图片 URL 或本地文件上传
- **立绘设置**：支持角色立绘图片配置
- **头像配置**：分别设置用户和机器人的头像和名字

### 会话管理
- 多会话支持
- 会话切换
- 独立的消息历史

## 📁 项目结构

```
MaiMbot-WEBui-adapter/
├── http_server/                 # 主要应用目录
│   ├── backend/                 # 后端源码
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI 应用主文件
│   │   ├── config.py           # 配置管理
│   │   ├── models.py           # 数据模型
│   │   ├── schemas.py          # 数据验证模式
│   │   ├── services.py         # 业务逻辑层
│   │   ├── routes.py           # API 路由
│   │   ├── frontend_launcher.py # 前端启动器
│   │   └── requirements.txt    # Python 依赖
│   ├── src/                    # 前端源码
│   │   ├── components/         # React 组件
│   │   │   ├── ChatPanel.jsx   # 聊天面板
│   │   │   ├── SpritePanel.jsx # 立绘面板
│   │   │   ├── Background.jsx  # 背景组件
│   │   │   ├── Toolbar.jsx     # 工具栏
│   │   │   ├── Modal.jsx       # 模态框
│   │   │   ├── AvatarConfigModal.jsx # 头像配置
│   │   │   └── SessionSelector.jsx   # 会话选择器
│   │   ├── App.jsx             # 主应用组件
│   │   ├── App.css             # 样式文件
│   │   └── main.jsx            # 入口文件
│   ├── public/                 # 静态资源
│   │   └── server_config.json  # 服务器配置
│   ├── main.py                 # 应用启动脚本
│   ├── package.json            # 前端依赖配置
│   └── vite.config.js          # Vite 配置
├── adapter/                    # 适配器相关
├── start_app.bat              # Windows 启动脚本
└── README.md                  # 项目说明
```

## 🔧 配置说明

### 服务器配置
编辑 `http_server/public/server_config.json` 文件：
```json
{
  "host": "127.0.0.1",
  "port": 8050
}
```

### 数据库
- 数据库文件：`http_server/backend/chat.db`（自动创建）
- 支持的表：
  - `chat_messages`：聊天消息
  - `background_config`：背景配置
  - `sprite_config`：立绘配置
  - `avatar_config`：头像配置

## 🎨 界面预览

### 主界面
- 左侧：聊天面板，支持文本和图片消息
- 右侧：立绘显示面板
- 顶部：会话选择器和工具栏
- 背景：支持自定义背景图片

### 主要特色
- **毛玻璃效果**：现代化的视觉体验
- **渐变色彩**：美观的配色方案
- **动画效果**：流畅的交互动画
- **响应式布局**：适配不同屏幕尺寸

## 🔌 API 接口

### 消息相关
- `GET /messages` - 获取消息列表
- `POST /send_message` - 发送消息

### 配置相关
- `GET/POST /background` - 背景配置
- `GET/POST /sprite` - 立绘配置
- `GET/POST /avatar_config` - 头像配置

## 🤝 开发指南

### 后端开发
1. 模型定义在 `backend/models.py`
2. API 路由在 `backend/routes.py`
3. 业务逻辑在 `backend/services.py`

### 前端开发
1. 组件开发在 `src/components/`
2. 样式定义在 `src/App.css`
3. 使用 React Hooks 进行状态管理

### 启动开发环境
```bash
# 后端开发模式（自动重载）
cd http_server
python main.py

# 前端开发模式
cd http_server
npm run dev
```

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

如有问题或建议，请提交 Issue 或 Pull Request。
