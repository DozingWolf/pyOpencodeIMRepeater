# IM Repeater 使用手册

> 飞书机器人 + OpenCode 远程操作完整配置指南

---

## 📋 目录

1. [快速开始](#-快速开始)
2. [飞书开放平台配置（详细图文）](#-飞书开放平台配置详细图文)
3. [OpenCode 配置](#opencode-配置)
4. [命令使用指南](#-命令使用指南)
5. [常见问题 FAQ](#-常见问题-faq)

---

## 🚀 快速开始

### 前置条件

- ✅ Python 3.12 或更高版本
- ✅ uv 包管理器 ([安装指南](https://docs.astral.sh/uv/))
- ✅ 飞书开发者账号
- ✅ OpenCode 服务已运行

### 三步启动

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入飞书和 OpenCode 配置

# 3. 启动服务
uv run python -m src.main
```

服务将在 `http://0.0.0.0:8080` 启动。

---

## 🔧 飞书开放平台配置（详细图文）

### 第一步：登录飞书开放平台

1. 访问 **https://open.feishu.cn/**
2. 使用飞书账号登录（个人或企业账号均可）

### 第二步：创建企业自建应用

1. 点击顶部导航栏的 **「开发者后台」**
2. 点击 **「创建企业自建应用」** 按钮
3. 填写应用信息：
   - **应用名称**: `OpenCode Bot` （或您喜欢的名称）
   - **应用描述**: `通过飞书远程操作 OpenCode`
   - **应用图标**: 上传一个机器人图标（可选）

### 第三步：配置权限（重要！）

进入应用后，点击左侧菜单 **「权限管理」** → **「权限配置」**

#### 必需权限：

| 权限分类 | 权限名称 | 用途 |
|---------|---------|------|
| 🔹 消息 | `im:message` | 接收消息 |
| 🔹 消息 | `im:message:send_as_bot` | 以应用身份发消息 |
| 🔹 消息 | `im:resource` | 获取图片、文件等资源 |

#### 如何配置：

1. 在权限列表中搜索 `im:message`
2. 点击权限名称右侧的 **「添加」** 按钮
3. 重复以上步骤，添加所有必需权限

**⚠️ 注意**: 不需要申请「通讯录」权限，因为我们只处理私聊消息

### 第四步：配置事件订阅

点击左侧菜单 **「事件订阅」**

#### 方式一：Webhook 模式（推荐，需公网 IP）

1. 选择 **「配置订阅方式」** → **「Webhook」**
2. 填写配置：

```
请求网址: http://你的公网IP:8080/webhook/feishu
Encrypt Key: （点击"随机生成"按钮）
Verification Token: （点击"随机生成"按钮）
```

3. **添加事件**：
   - 搜索 `im.message.receive`
   - 点击 **「添加」** 按钮

4. 点击 **「保存」** 按钮

**⚠️ Webhook 模式要求**：
- 您的服务器必须有公网 IP 或域名
- 端口 8080 必须对外开放
- 如果使用内网，需要使用内网穿透工具（如 ngrok）

#### 方式二：长连接模式（推荐，适合开发测试）

1. 选择 **「配置订阅方式」** → **「长连接」**
2. 下载飞书开放平台提供的 SDK
3. 不需要公网 IP，适合本地开发

**本项目的代码主要支持 Webhook 模式**

### 第五步：获取应用凭证

点击左侧菜单 **「凭证与基础信息」**

您将看到以下信息（需要复制到 `.env` 文件）：

```
┌──────────────────────────────────────────┐
│ App ID:         cli_xxxxxxxxxxxxx        │  ← FEISHU_APP_ID
│ App Secret:     xxxxxxxxxxxxxxxxxxxx    │  ← FEISHU_APP_SECRET
│ Encrypt Key:    xxxxxxxxxxxxxxxxxxxx    │  ← FEISHU_ENCRYPT_KEY（Webhook模式）
│ Verification Token: xxxxxxxxxxxxxxx    │  ← FEISHU_VERIFICATION_TOKEN（Webhook模式）
└──────────────────────────────────────────┘
```

### 第六步：配置 .env 文件

编辑项目根目录下的 `.env` 文件：

```bash
# ========================================
# OpenCode API 配置
# ========================================
OPENCODE_API_URL=http://localhost:4096
OPENCODE_PASSWORD=your_opencode_password_here

# ========================================
# 飞书机器人配置（从第五步复制）
# ========================================
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxxxxxxx        # Webhook 模式需要
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx   # Webhook 模式需要

# ========================================
# 服务器配置
# ========================================
SERVER_HOST=0.0.0.0              # 监听所有网络接口
SERVER_PORT=8080                 # 服务端口

# ========================================
# 数据库配置
# ========================================
DATABASE_PATH=data/sessions.db   # 数据库文件路径
```

### 第七步：发布应用

#### 开发/测试阶段：使用可用性测试

1. 点击左侧菜单 **「可用性测试」**
2. 点击 **「添加测试用户」**
3. 搜索并添加您的飞书账号
4. **测试用户可以立即使用应用，无需审核**

#### 生产环境：发布应用

1. 点击左侧菜单 **「版本管理与发布」**
2. 点击 **「创建版本」**
3. 填写版本说明（如："v1.0.0 - 初始版本"）
4. 点击 **「保存」**
5. 点击 **「申请发布」**，等待审核
6. 审核通过后，全企业用户都可以使用

### 第八步：测试机器人

1. 打开飞书手机应用或桌面客户端
2. 在搜索栏搜索您的机器人名称（如 "OpenCode Bot"）
3. 发送一条消息测试：
   ```
   /help
   ```
4. 如果收到帮助信息，恭喜！配置成功！🎉

---

## 🔌 OpenCode 配置

### 检查 OpenCode 服务状态

```bash
# 检查 OpenCode 是否运行
curl http://localhost:4096/api/health

# 预期响应：
# {"status": "ok"} 或 {"status": "healthy"}
```

### 获取 OpenCode 密码

如果 OpenCode 需要密码认证：

1. 查看 OpenCode 的配置文件
2. 或查看 OpenCode 启动日志
3. 或咨询 OpenCode 管理员

将密码配置到 `.env` 文件：

```bash
OPENCODE_PASSWORD=your_actual_password
```

---

## 📖 命令使用指南

### 在飞书中使用

打开飞书，搜索您的机器人应用，发送私聊消息：

#### 🆕 基础命令

| 命令 | 示例 | 说明 |
|------|------|------|
| `/help` | `/help` | 显示所有可用命令 |
| `/help <命令>` | `/help new` | 显示特定命令的详细帮助 |
| `/new [名称]` | `/new 项目开发` | 创建新会话 |
| `/list` | `/list` | 列出所有会话 |
| `/switch <会话>` | `/switch 项目开发` | 切换到指定会话 |
| `/delete <会话>` | `/delete 旧会话` | 删除会话 |
| `/rename <新名称>` | `/rename 重点工作` | 重命名当前会话 |
| `/history [数量]` | `/history 20` | 查看最近20条历史记录 |
| `/export` | `/export` | 导出当前会话信息为 JSON |

#### 💡 使用示例

```
用户: /help
机器人: 📖 可用命令：
       • /new - 创建新会话
       • /list - 列出所有会话
       ...
       使用 /help <命令> 查看详细信息

用户: /new 网站重构
机器人: ✅ 创建新会话: **网站重构**
       会话 ID: `ses_abc123`
       
       您现在正在使用此会话。

用户: 写一个 Python 的 Hello World 程序
机器人: [OpenCode 的回复...]

用户: /list
机器人: 📋 **您的会话：**
       
       1. **网站重构** ✅
          ID: `ses_abc123`
          创建时间: 2026-03-03
       
       2. **默认会话**
          ID: `ses_def456`
          创建时间: 2026-03-02

用户: /switch 默认会话
机器人: ✅ 切换到会话: **默认会话**
       ID: `ses_def456`

用户: /export
机器人: 📦 **会话导出**
       
       ```json
       {
         "session": {
           "id": 2,
           "opencode_session_id": "ses_def456",
           "name": "默认会话",
           "created_at": "2026-03-02T10:30:00",
           "updated_at": "2026-03-03T15:20:00",
           "is_active": true
         },
         "exported_at": "2026-03-03T16:00:00",
         "user_id": "ou_xxx"
       }
       ```
       
       💡 复制上面的 JSON 保存会话信息。
```

#### 📌 会话管理技巧

1. **为不同项目创建独立会话**
   ```
   /new 前端开发
   /new 后端 API
   /new 文档编写
   ```

2. **快速切换会话**
   ```
   /switch 前端    # 支持模糊匹配
   /switch 后端
   ```

3. **清理旧会话**
   ```
   /list                    # 先查看
   /delete 已完成的项目      # 再删除
   ```

---

## ❓ 常见问题 FAQ

### Q1: 飞书机器人收不到消息？

#### 检查清单：

- [ ] 应用是否已添加为测试用户或已发布
- [ ] 事件订阅是否正确配置（`im.message.receive`）
- [ ] 服务器是否可以从公网访问（Webhook模式）
- [ ] Encrypt Key 和 Verification Token 是否正确配置
- [ ] 查看服务器日志是否有错误

#### 调试方法：

```bash
# 1. 查看服务器日志
tail -f data/logs/im-repeater.log

# 2. 测试 Webhook 是否可达（从外部网络）
curl -X POST http://你的公网IP:8080/webhook/feishu \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}'

# 3. 检查飞书应用配置
# 在飞书开放平台查看「事件订阅」状态是否为"已启用"
```

#### 如果使用内网：

使用内网穿透工具：

```bash
# 使用 ngrok（示例）
ngrok http 8080

# 将 ngrok 提供的 HTTPS 地址配置到飞书 Webhook
# 例如: https://abc123.ngrok.io/webhook/feishu
```

### Q2: OpenCode 连接失败？

#### 检查清单：

- [ ] OpenCode 服务是否正在运行
- [ ] `OPENCODE_API_URL` 是否正确（检查端口）
- [ ] `OPENCODE_PASSWORD` 是否正确（如需要）
- [ ] 网络是否可达

#### 调试方法：

```bash
# 1. 测试 OpenCode 连接
curl http://localhost:4096/api/sessions

# 2. 检查环境变量是否加载
uv run python -c "from src.config import get_settings; s = get_settings(); print(f'OpenCode URL: {s.opencode_api_url}')"

# 3. 查看 OpenCode 日志
# 查看 OpenCode 项目的日志输出
```

### Q3: 如何查看日志？

```bash
# 实时查看日志（推荐）
tail -f data/logs/im-repeater.log

# 查看最近100行
tail -100 data/logs/im-repeater.log

# 搜索错误日志
grep "ERROR" data/logs/im-repeater.log
grep "Exception" data/logs/im-repeater.log

# 搜索特定用户的操作
grep "user_id_xxx" data/logs/im-repeater.log
```

### Q4: 数据库文件在哪里？

```
位置: data/sessions.db
```

#### 查看数据库内容：

```bash
# 查看所有会话
sqlite3 data/sessions.db "SELECT id, name, user_id, created_at FROM sessions;"

# 查看表结构
sqlite3 data/sessions.db ".schema"

# 导出为 CSV
sqlite3 data/sessions.db -csv "SELECT * FROM sessions;" > sessions.csv
```

### Q5: 如何重置所有数据？

```bash
# 1. 停止服务（Ctrl+C）

# 2. 删除数据库（⚠️ 会清空所有会话！）
rm data/sessions.db

# 3. 删除日志（可选）
rm -rf data/logs/

# 4. 重启服务（会自动创建新的数据库）
uv run python -m src.main
```

### Q6: 如何更新到最新版本？

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
uv sync

# 3. 检查配置变化
git diff HEAD~1 .env.example

# 4. 重启服务
uv run python -m src.main
```

### Q7: 支持哪些消息类型？

| 消息类型 | 支持状态 | 说明 |
|---------|---------|------|
| ✅ 文本消息 | 完全支持 | 可以正常收发 |
| ⚠️ 图片消息 | 部分支持 | 可以接收，但处理需要配置飞书文件下载 API |
| ⚠️ 文件消息 | 部分支持 | 可以接收，但处理需要配置飞书文件下载 API |
| ❌ 群消息 | 不支持 | 仅处理私聊消息 |
| ❌ 富文本 | 不支持 | 按纯文本处理 |

### Q8: 多人可以同时使用吗？

**可以！** 系统自动支持多用户，每个飞书用户有独立的会话空间，互不干扰。

```
用户 A 的会话:
  - 项目讨论
  - 日常开发

用户 B 的会话:
  - API 设计
  - 文档编写

互不影响 ✅
```

### Q9: 如何在服务器上部署？

#### 使用 systemd（推荐）：

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/im-repeater.service
```

```ini
[Unit]
Description=IM Repeater - Feishu Bot for OpenCode
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/pyOpencodeIMRepeater
ExecStart=/path/to/.venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 2. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable im-repeater
sudo systemctl start im-repeater

# 3. 查看状态
sudo systemctl status im-repeater

# 4. 查看日志
sudo journalctl -u im-repeater -f
```

### Q10: 端口被占用怎么办？

```bash
# 1. 查看端口占用
lsof -i:8080

# 2. 修改端口（编辑 .env）
SERVER_PORT=9000

# 3. 或停止占用端口的进程
kill -9 <PID>
```

---

## 🔐 安全建议

1. **不要将 .env 文件提交到 Git**
   ```bash
   # 确保 .gitignore 包含
   .env
   data/
   ```

2. **定期更换飞书应用密钥**
   - 在飞书开放平台重新生成 App Secret
   - 更新 .env 文件
   - 重启服务

3. **限制测试用户数量**
   - 仅添加必要的测试用户
   - 生产环境发布前移除测试用户

4. **监控日志**
   ```bash
   # 定期检查异常访问
   grep "WARNING\|ERROR" data/logs/im-repeater.log
   ```

---

## 📚 相关链接

- **飞书开放平台**: https://open.feishu.cn/
- **飞书开放平台文档**: https://open.feishu.cn/document
- **uv 包管理器**: https://docs.astral.sh/uv/
- **FastAPI 文档**: https://fastapi.tiangolo.com/

---

## 📄 许可证

MIT License

---

**祝您使用愉快！如有问题，请提交 Issue。** 🎉
