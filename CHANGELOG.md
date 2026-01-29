# 更新日志

## v1.1.0 - 配置文件消息预设功能

### 新功能

#### 1. 消息预设 (Message Presets)
- 从配置文件读取预定义的邮件模板
- 支持Jinja2变量替换
- 快速发送常用邮件类型
- 可通过 `--preset` 参数使用

#### 2. 收件人组 (Recipient Groups)
- 在配置文件中定义收件人组
- 发送邮件时使用组名
- 第一个收件人作为TO，其他作为CC

#### 3. 上下文变量渲染
- 支持 `--context` 参数传递JSON数据
- 可替换主题和正文中的变量
- 支持Jinja2模板语法

#### 4. 默认设置
- `default_cc`: 默认抄送列表
- `default_bcc`: 默认密送列表

### 新命令

```bash
# 列出所有预设
clawdbot-smtp presets list

# 查看预设详情
clawdbot-smtp presets show --name welcome

# 列出所有收件人组
clawdbot-smtp recipients list
```

### 使用示例

```bash
# 使用预设发送邮件
clawdbot-smtp send \
  --to user@example.com \
  --preset welcome \
  --context '{"name": "张三", "company": "公司名"}'

# 发送到收件人组
clawdbot-smtp send --to team --subject "通知" --body "内容"

# 组合使用
clawdbot-smtp send \
  --to team \
  --preset meeting_reminder \
  --context '{"meeting_title": "周会", "date": "2024-01-30"}'
```

### 配置文件结构

```json
{
  "message_presets": {
    "welcome": {
      "subject": "Welcome to {{ company }}!",
      "body": "Hi {{ name }}..."
    }
  },
  "recipients": {
    "team": ["alice@company.com", "bob@company.com"]
  },
  "settings": {
    "default_cc": [],
    "default_bcc": []
  }
}
```

### 文档更新

- 新增 `packaging/PRESETS_GUIDE.md` - 预设和收件人组使用指南
- 更新 `config.example.json` - 包含预设和收件人组示例
- 更新 `email_cli/config.py` - 添加预设和收件人组读取功能
- 更新 `email_cli/main.py` - 支持预设、组和上下文变量

---

## v1.0.0 - 初始版本

### 核心功能
- SMTP邮件发送（支持附件、HTML、纯文本）
- IMAP邮件管理（列表、阅读、搜索、删除）
- Jinja2模板系统
- 多账户支持
- JSON输出格式
- Linux打包支持
- Clawdbot深度集成

### 安装方式
- 一键安装脚本
- 独立可执行文件
- Python包安装
