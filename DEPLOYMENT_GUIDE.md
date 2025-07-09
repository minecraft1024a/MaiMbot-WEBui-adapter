# 🚀 MaiMbot WebUI Adapter 快速部署指南

## 📋 系统要求

- **Python**: 3.8+ 
- **Node.js**: 16+ 
- **操作系统**: Windows/Linux/macOS

## ⚡ 一键启动

### Windows用户
```bash
# 双击运行
start_app.bat

# 或使用命令行
./start_app.bat
```

### Linux/macOS用户
```bash
cd http_server
python main.py
```

## 🔧 手动部署

### 1. 安装Python依赖
```bash
cd http_server/backend
pip install -r requirements.txt
```

### 2. 安装Node.js依赖
```bash
cd http_server
npm install
```

### 3. 启动应用
```bash
# 在http_server目录下
python main.py
```

## 🌐 访问地址

- **主应用**: http://localhost:5173
- **API文档**: http://127.0.0.1:8050/docs
- **后端服务**: http://127.0.0.1:8050

## 🛠️ 开发模式

### 后端开发
```bash
cd http_server/backend
uvicorn app:app --reload --port 8050
```

### 前端开发
```bash
cd http_server
npm run dev
```

## 📁 重要文件说明

- `main.py`: 主启动文件，同时启动前后端
- `backend/app.py`: FastAPI应用入口
- `backend/config.py`: 配置文件
- `src/App.jsx`: React主组件
- `package.json`: 前端依赖配置
- `requirements.txt`: Python依赖配置

## 🐛 常见问题

### 问题1: 端口被占用
```bash
# 查看端口占用
netstat -ano | findstr :8050
netstat -ano | findstr :5173

# 杀死进程
taskkill /PID <进程ID> /F
```

### 问题2: Python依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3: Node.js依赖安装失败
```bash
# 清理npm缓存
npm cache clean --force

# 使用国内镜像
npm install --registry https://registry.npmmirror.com
```

## 🔒 安全配置

### 生产环境部署
1. 修改默认端口和密钥
2. 启用HTTPS
3. 配置防火墙规则
4. 设置环境变量

```bash
# 设置环境变量
export ENVIRONMENT=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=your-database-url
```

## 📊 监控和日志

- 日志文件位置: `backend/logs/`
- 数据库文件: `backend/chat.db`
- 配置文件: `backend/config.yaml`

## 🔄 版本更新

```bash
# 1. 备份数据
cp backend/chat.db backup/
cp backend/config.yaml backup/

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
pip install -r backend/requirements.txt
npm install

# 4. 重启服务
python main.py
```

## 📞 技术支持

如遇到问题，请检查：
1. Python和Node.js版本是否满足要求
2. 依赖是否正确安装
3. 端口是否被占用
4. 防火墙和网络配置

---

**提示**: 首次启动可能需要几分钟来安装依赖和初始化数据库，请耐心等待。
