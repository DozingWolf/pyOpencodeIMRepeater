# OpenCode IM Repeater

OpenCode IM 中继器,通过飞书机器人远程操作 OpenCode,让用户能够像使用 OpenCode 一样通过 IM 软件发送指令并获取反馈。

## 功能特性

- 飞书机器人消息接收与处理
- 会话管理 (创建、切换、删除、重命名)
- OpenCode API 集成与流式响应
- 图片和文件消息处理
- 多用户会话隔离

## 先决条件

- Python 3.12+
- uv 包管理器 ([安装指南](https://docs.astral.sh/uv/))
- 飞书开放平台应用 (获取 App ID 和 Secret)
- OpenCode 服务 (默认 http://localhost:4096)

## 安装

### 1. 克隆仓库

```bash
git clone <repository-url>
cd pyOpencodeIMRepeater
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置

#### 方式一: 环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,填入你的配置
```

#### 方式二: YAML 配置文件

编辑 `config/config.yaml`:

```yaml
# OpenCode API 配置
opencode_api_url: "http://localhost:4096"
opencode_password: ""

# 飞书机器人配置
feishu_app_id: ""
feishu_app_secret: ""
feishu_encrypt_key: ""
feishu_verification_token: ""

# 服务器配置
server_host: "0.0.0.0"
server_port: 8080

# 数据库配置
database_path: "data/sessions.db"
```

**配置优先级**: 环境变量 > .env 文件 > YAML 配置 > 默认值

## 运行

```bash
uv run python -m src.main
```

服务将在 `http://0.0.0.0:8080` 启动。

## 斜杠命令

通过飞书发送以下命令来管理会话:

| 命令 | 用法 | 描述 |
|------|------|------|
| `/new` | `/new [名称]` | 创建新会话 |
| `/list` | `/list` | 列出所有会话 |
| `/switch` | `/switch <ID或名称>` | 切换到指定会话 |
| `/delete` | `/delete <ID或名称>` | 删除会话 |
| `/rename` | `/rename <新名称>` | 重命名当前会话 |
| `/history` | `/history [数量]` | 查看对话历史 |
| `/export` | `/export` | 导出当前会话信息 |
| `/help` | `/help [命令]` | 显示帮助信息 |

### 使用示例

```
/new 项目讨论        # 创建名为"项目讨论"的新会话
/list                # 列出所有会话
/switch 项目讨论     # 切换到"项目讨论"会话
/rename 新项目       # 重命名当前会话为"新项目"
/history 20          # 显示最近20条消息
/help switch         # 查看 /switch 命令详细用法
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/health` | GET | 健康检查 |
| `/webhook/feishu` | POST | 飞书消息回调 |
| `/admin/cleanup` | POST | 清理过期会话 |

### 端点详情

#### `GET /`

返回服务基本信息。

```json
{
  "message": "OpenCode IM Repeater",
  "status": "running"
}
```

#### `GET /health`

健康检查端点。

```json
{
  "status": "healthy"
}
```

#### `POST /webhook/feishu`

接收飞书消息事件。仅处理私聊消息,忽略群消息。

#### `POST /admin/cleanup?days=30`

清理指定天数未更新的会话。

```json
{
  "deleted": 5,
  "message": "Cleaned up 5 sessions"
}
```

## 项目结构

```
pyOpencodeIMRepeater/
├── config/
│   └── config.yaml       # YAML 配置文件
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理
│   ├── commands/
│   │   ├── __init__.py
│   │   └── handler.py    # 斜杠命令处理
│   ├── feishu/
│   │   ├── __init__.py
│   │   └── client.py     # 飞书 API 客户端
│   ├── opencode/
│   │   ├── __init__.py
│   │   └── client.py     # OpenCode API 客户端
│   ├── services/
│   │   ├── __init__.py
│   │   ├── media_handler.py  # 图片/文件处理
│   │   └── streaming.py      # 流式响应处理
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py       # SQLite 数据库
│   │   └── session_manager.py # 会话管理
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py  # 错误处理中间件
│   └── utils/
│       └── __init__.py
├── tests/                # 测试代码
├── data/                 # 数据库文件目录
├── pyproject.toml        # 项目配置
└── .env.example          # 环境变量模板
```

## 开发与测试

### 运行测试

```bash
uv run pytest
```

### 代码检查

```bash
# Ruff linting
uv run ruff check src/

# Type checking
uv run mypy src/
```

### 测试覆盖率

```bash
uv run pytest --cov=src tests/
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENCODE_API_URL` | OpenCode API 地址 | `http://localhost:4096` |
| `OPENCODE_PASSWORD` | OpenCode 认证密码 | - |
| `FEISHU_APP_ID` | 飞书应用 ID | - |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | - |
| `FEISHU_ENCRYPT_KEY` | 飞书消息加密密钥 | - |
| `FEISHU_VERIFICATION_TOKEN` | 飞书验证令牌 | - |
| `SERVER_HOST` | 服务绑定地址 | `0.0.0.0` |
| `SERVER_PORT` | 服务绑定端口 | `8080` |
| `DATABASE_PATH` | SQLite 数据库路径 | `data/sessions.db` |

## 许可证

MIT
