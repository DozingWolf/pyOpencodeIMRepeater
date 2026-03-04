# IM Repeater 使用手册

> 飞书机器人 + OpenCode 远程操作指南

## 目录

1. [快速开始](#快速开始)
2. [飞书配置详解](#飞书配置详解)
3. [OpenCode 配置](#opencode-配置)
4. [命令使用指南](#命令使用指南)
5. [常见问题](#常见问题)

---

## 快速开始

### 前置条件

- ✅ Python 3.12+
- ✅ uv 包管理器
- ✅ 飞书开发者账号
- ✅ OpenCode 服务已运行

### 三步启动

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入配置

# 3. 启动服务
uv run python -m src.main
```

---

## 飞书配置详解

### 第一步：创建飞书应用

1. **访问飞书开放平台**
   - 打开 https://open.feishu.cn/
   - 登录您的飞书账号

2. **创建企业自建应用**
   - 点击「开发者后台」→「创建企业自建应用」
   - 填写应用名称：`OpenCode Bot`（可自定义）
   - 选择应用图标
   - 点击「创建」

### 第二步：配置应用权限

在应用详情页，进入「权限管理」→「申请权限」，添加以下权限：

#### 🔑 必需权限

| 权限名称 | 权限标识 | 用途 |
|---------|---------|------|
| 获取与更新用户信息 | `contact:user.base:readonly` | 获取用户基本信息 |
| 获取用户统一ID | `contact:user.id:readonly` | 识别用户身份 |
| 接收、发送单聊消息 | `im:message` | 接收和发送私聊消息 |
| 获取、上传、下载文件 | `drive:file` | 处理图片和文件消息 |

#### 📝 权限配置步骤

```
权限管理 → 申请权限 → 搜索权限名称 → 点击申请
```

**重要**：权限申请后需要等待管理员审批，或使用「可用性测试」功能临时启用。

### 第三步：配置事件订阅

1. **进入事件订阅页面**
   - 应用详情 → 「事件订阅」→「配置订阅方式」

2. **选择订阅方式**
   - ✅ 推荐：使用「长连接」模式（无需公网IP）
   - 或：使用「Webhook」模式（需要公网服务器）

#### 方式一：长连接模式（推荐）

```bash
# 本地启动后，在飞书开放平台：
# 事件订阅 → 配置订阅方式 → 长连接 → 添加订阅地址
# 输入：ws://your-server:8080/webhook/feishu
```

#### 方式二：Webhook 模式

```bash
# 1. 添加请求网址
# 事件订阅 → 配置订阅方式 → Webhook → 添加请求网址
# 输入：http://your-server:8080/webhook/feishu

# 2. 配置加密和验证
# - Encrypt Key: 用于消息加密（可选但推荐）
# - Verification Token: 用于验证请求来源
```

3. **订阅消息事件**
   - 在「添加事件」中搜索并添加：
     - ✅ `im.message.receive` - 接收消息事件
   - 点击「添加」

### 第四步：获取应用凭证

在应用详情页，进入「凭证与基础信息」：

```
┌─────────────────────────────────────┐
│ App ID:         cli_xxxxxxxxxxxx    │  ← 复制这个
│ App Secret:     xxxxxxxxxxxxxxxxxx  │  ← 复制这个
│ Encrypt Key:    xxxxxxxxxxxxxxxxxx  │  ← 复制这个（如果启用了加密）
│ Verification Token: xxxxxxxxxxxxxx  │  ← 复制这个
└─────────────────────────────────────┘
```

### 第五步：配置 .env 文件

编辑项目根目录下的 `.env` 文件：

```bash
# OpenCode API 配置
OPENCODE_API_URL=http://localhost:4096
OPENCODE_PASSWORD=your_opencode_password

# 飞书机器人配置（从上一步复制）
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxxxxxxx        # 可选，用于消息加密
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx   # 可选，用于验证请求

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# 数据库配置
DATABASE_PATH=data/sessions.db
```

### 第六步：发布应用

1. **提交审核**（如需）
   - 应用详情 → 「版本管理与发布」→「创建版本」
   - 填写版本说明，提交审核

2. **可用性测试**（开发阶段）
   - 应用详情 → 「可用性测试」→「添加测试用户」
   - 添加您自己的飞书账号为测试用户
   - **注意**：测试用户可以使用未审核的权限

---

## OpenCode 配置

### 启动 OpenCode 服务

确保 OpenCode 服务已经在运行：

```bash
# 检查 OpenCode 是否运行
curl http://localhost:4096/api/health

# 预期响应：
# {"status": "ok"}
```

### 获取 OpenCode 密码

如果 OpenCode 需要密码认证：

1. 查看 OpenCode 配置文件
2. 或在 OpenCode 启动日志中查找
3. 或咨询 OpenCode 管理员

---

## 命令使用指南

### 在飞书中使用

打开飞书，搜索您的机器人应用，发送私聊消息：

#### 基础命令

| 命令 | 示例 | 说明 |
|------|------|------|
| `/help` | `/help` | 查看所有命令 |
| `/new` | `/new 项目开发` | 创建新会话 |
| `/list` | `/list` | 列出所有会话 |
| `/switch` | `/switch 项目开发` | 切换到指定会话 |
| `/rename` | `/rename 新名称` | 重命名当前会话 |
| `/delete` | `/delete 项目开发` | 删除指定会话 |
| `/history` | `/history 20` | 查看最近20条消息 |
| `/export` | `/export` | 导出会话信息 |

#### 使用流程示例

```
用户: /new Python项目
机器人: ✅ Created new session: **Python项目**
      Session ID: `ses_abc123`
      
      You are now using this session.

用户: 帮我写一个快速排序算法
机器人: [OpenCode 的回复...]

用户: /list
机器人: 📋 **Your Sessions:**
      
      1. **Python项目** ✅
         ID: `ses_abc123`
         Created: 2026-03-04

用户: /switch Python项目
机器人: ✅ Switched to session: **Python项目**
      ID: `ses_abc123`
```

#### 直接发送消息

如果不使用命令，直接发送文本消息：

```
用户: 今天天气怎么样
机器人: [OpenCode 会理解并回复]
```

**注意**：
- 第一次发消息会自动创建默认会话
- 后续消息会继续在当前会话中对话
- 使用 `/new` 创建新会话以开始新的对话上下文

---

## 常见问题

### Q1: 飞书机器人收不到消息？

**检查清单**：
- [ ] 应用是否已发布或添加为测试用户
- [ ] 事件订阅是否正确配置
- [ ] 服务器是否可以从公网访问（Webhook模式）
- [ ] Encrypt Key 和 Verification Token 是否正确配置
- [ ] 查看服务器日志是否有错误

**调试方法**：
```bash
# 查看服务器日志
tail -f data/logs/im-repeater.log

# 测试 Webhook 是否可达
curl -X POST http://localhost:8080/webhook/feishu \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}'
```

### Q2: OpenCode 连接失败？

**检查清单**：
- [ ] OpenCode 服务是否运行
- [ ] `OPENCODE_API_URL` 是否正确
- [ ] `OPENCODE_PASSWORD` 是否正确（如需要）
- [ ] 网络是否可达

**调试方法**：
```bash
# 测试 OpenCode 连接
curl http://localhost:4096/api/sessions

# 检查环境变量
uv run python -c "from src.config import get_settings; s = get_settings(); print(s.opencode_api_url)"
```

### Q3: 如何查看日志？

```bash
# 实时查看日志
tail -f data/logs/im-repeater.log

# 查看最近100行
tail -100 data/logs/im-repeater.log

# 搜索错误
grep "ERROR" data/logs/im-repeater.log
```

### Q4: 数据库在哪里？

```
data/sessions.db
```

可以使用 SQLite 工具查看：

```bash
# 查看所有会话
sqlite3 data/sessions.db "SELECT * FROM sessions;"

# 查看表结构
sqlite3 data/sessions.db ".schema"
```

### Q5: 如何重置数据？

```bash
# 停止服务
# Ctrl+C 或 kill 进程

# 删除数据库（会清空所有会话）
rm data/sessions.db

# 重启服务
uv run python -m src.main
```

### Q6: 如何更新代码？

```bash
# 拉取最新代码
git pull

# 更新依赖
uv sync

# 重启服务
```

---

## 高级配置

### 自定义端口

编辑 `.env` 文件：

```bash
SERVER_PORT=9000
```

### 修改日志级别

在 `config/config.yaml` 中：

```yaml
logging:
  level: DEBUG  # INFO, WARNING, ERROR
```

### 配置多用户

系统自动支持多用户，每个飞书用户有独立的会话空间，互不干扰。

---

## 技术支持

- **GitHub Issues**: [项目地址]/issues
- **飞书开放平台文档**: https://open.feishu.cn/document
- **OpenCode 文档**: [OpenCode 项目文档]

---

## 许可证

MIT License

---

**祝您使用愉快！** 🎉
