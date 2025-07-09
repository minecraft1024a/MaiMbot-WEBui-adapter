# 适配器重构迁移指南

## 主要变化

### 1. 配置文件格式变更
- **旧格式**: `config.yaml` (YAML格式)
- **新格式**: `config.toml` (TOML格式)

### 2. 配置文件结构重组
新的TOML配置文件结构更清晰：

```toml
[adapter]
platform_id = "maimai_http_adapter"
poll_interval = 2

[connection]
ws_url = "ws://127.0.0.1:8000/ws"
http_backend_url = "http://127.0.0.1:8050"

[database]
db_path = "../http_server/backend/chat.db"

[logging]
level = "INFO"
```

### 3. 代码结构重构

#### 新增类：
- `AdapterConfig`: 配置管理器，统一处理配置文件读取和默认值
- `MessageProcessor`: 消息处理器，负责消息解析和发送
- `DatabaseManager`: 数据库管理器，处理数据库连接和操作
- `MessagePoller`: 消息轮询器，负责轮询HTTP后端

#### 改进点：
1. **类型提示**: 添加了完整的类型注解
2. **错误处理**: 改进了异常处理和日志记录
3. **资源管理**: 改进了数据库连接管理，避免连接泄露
4. **代码组织**: 将功能按职责分离到不同的类中
5. **配置管理**: 统一的配置管理，支持默认值和错误恢复

### 4. 依赖变化
- **移除**: `pyyaml` (YAML解析)
- **新增**: `tomllib` (Python 3.11+ 内置，低版本需要 `tomli`)

### 5. 迁移步骤

1. **备份旧配置**:
   ```bash
   cp config.yaml config.yaml.bak
   ```

2. **创建新配置文件**:
   将 `config.yaml` 的内容转换为 `config.toml` 格式

3. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

4. **验证配置**:
   运行适配器确保配置正确加载

### 6. 向后兼容性
- 如果找不到 `config.toml` 文件，系统会使用默认配置
- 所有原有功能保持不变
- API接口保持兼容

### 7. 新功能
- 更好的错误处理和恢复能力
- 改进的日志记录
- 更安全的数据库连接管理
- 类型安全的代码结构

## 故障排除

### 常见问题：
1. **配置文件不存在**: 系统会自动使用默认配置并记录警告
2. **TOML解析错误**: 检查TOML语法是否正确
3. **数据库连接问题**: 确保数据库路径正确且有写入权限

### 回滚方案：
如果遇到问题，可以临时回到旧版本：
1. 恢复 `config.yaml` 文件
2. 使用备份的旧版本代码
3. 调试完成后再次尝试迁移
