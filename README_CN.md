# Clawdbot SMTP Tool

📧 **独立的Linux邮件管理工具** - 深度集成Clawdbot，支持SMTP/IMAP、模板和定时任务。

## 快速安装

### 一键安装（推荐）

```bash
# 下载并安装
curl -sSL https://raw.githubusercontent.com/lukelzlz/clawdbot-smtp/main/packaging/install.sh | bash
```

### 手动安装

```bash
# 1. 下载最新版本
wget https://github.com/lukelzlz/clawdbot-smtp/releases/latest/download/clawdbot-smtp-linux-x86_64.tar.gz

# 2. 解压
tar -xzf clawdbot-smtp-linux-x86_64.tar.gz

# 3. 运行安装脚本
cd release
sudo ./install.sh
```

## 配置

安装后，编辑配置文件：

```bash
sudo nano /etc/clawdbot-smtp/config.json
```

### Gmail配置示例

```json
{
  "accounts": {
    "primary": {
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "imap_host": "imap.gmail.com",
      "imap_port": 993,
      "username": "your@gmail.com",
      "password": "your-app-password",
      "use_ssl": true
    }
  },
  "default_account": "primary"
}
```

**Gmail提示：** 必须启用两步验证并创建应用专用密码（不是你的账户密码）

### Outlook配置示例

```json
{
  "accounts": {
    "primary": {
      "smtp_host": "smtp.office365.com",
      "smtp_port": 587,
      "imap_host": "outlook.office365.com",
      "imap_port": 993,
      "username": "your@outlook.com",
      "password": "your-password",
      "use_ssl": true
    }
  },
  "default_account": "primary"
}
```

## 使用方法

### 发送邮件

```bash
# 简单文本邮件
clawdbot-smtp send --to user@example.com --subject "Hello" --body "这是一封测试邮件"

# 带附件的邮件
clawdbot-smtp send --to user@example.com --subject "报告" --body "请查收附件" --attach report.pdf

# 使用模板发送
clawdbot-smtp send --to user@example.com --subject "欢迎" --template welcome --context '{"name": "张三", "company": "我的公司"}'
```

### 管理邮件

```bash
# 列出收件箱邮件（前10封）
clawdbot-smtp list --limit 10

# 列出未读邮件
clawdbot-smtp list --unread

# 查看邮件详情
clawdbot-smtp read --id 123

# 搜索邮件
clawdbot-smtp search --query "FROM:boss@example.com  urgent"

# 删除邮件
clawdbot-smtp delete --id 123
```

### 文件夹管理

```bash
# 列出所有文件夹
clawdbot-smtp folders list

# 创建新文件夹
clawdbot-smtp folders create --name "重要邮件"
```

## 与Clawdbot集成

### 配置环境变量

```bash
# 编辑 /etc/clawdbot-smtp/config.json 或使用环境变量
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export IMAP_HOST=imap.gmail.com
export IMAP_PORT=993
export SMTP_USERNAME=your@gmail.com
export SMTP_PASSWORD=your-app-password
```

### 在Clawdbot中使用

```bash
# 检查邮件并获取JSON输出
clawdbot-smtp list --limit 5 --json

# 定时检查未读邮件
/var/lib/clawdbot-smtp/email_check.py 10 INBOX
```

### 设置定时任务（Cron）

```bash
# 每小时检查一次未读邮件并通知到Discord
0 * * * * /var/lib/clawdbot-smtp/email_check.py 10 INBOX | clawdbot message send --to discord --target YOUR_CHANNEL_ID

# 每天早上9点发送日报
0 9 * * * /usr/local/bin/clawdbot-smtp send --to manager@company.com --subject "日报" --template daily_report --context '{"date": "2024-01-29"}'
```

## 命令完整列表

```bash
# 查看帮助
clawdbot-smtp --help

# 发送邮件
clawdbot-smtp send --to EMAIL --subject SUBJECT [--body TEXT] [--html HTML] [--template NAME] [--context JSON] [--cc EMAIL] [--bcc EMAIL] [--attach FILE]

# 列出邮件
clawdbot-smtp list [--folder FOLDER] [--limit N] [--unread] [--json]

# 阅读邮件
clawdbot-smtp read --id ID [--folder FOLDER] [--json]

# 搜索邮件
clawdbot-smtp search --query QUERY [--limit N] [--json]

# 删除邮件
clawdbot-smtp delete --id ID [--folder FOLDER] [--yes]

# 文件夹管理
clawdbot-smtp folders list
clawdbot-smtp folders create --name NAME
```

## 自定义模板

编辑或添加模板到 `/var/lib/clawdbot-smtp/templates/`

**示例模板 (welcome.html):**
```html
<!DOCTYPE html>
<html>
<body>
  <h1>欢迎，{{ name }}！</h1>
  <p>感谢加入 {{ company }}。</p>
</body>
</html>
```

## 卸载

```bash
sudo /var/lib/clawdbot-smtp/uninstall.sh
```

## 文件位置

- **可执行文件：** `/usr/local/bin/clawdbot-smtp`
- **配置文件：** `/etc/clawdbot-smtp/config.json`
- **模板目录：** `/var/lib/clawdbot-smtp/templates/`
- **文档：** `/usr/share/doc/clawdbot-smtp/`

## 故障排除

### 认证失败

**Gmail:**
- 启用两步验证：https://myaccount.google.com/security
- 创建应用专用密码：https://myaccount.google.com/apppasswords
- 在配置中使用应用专用密码，不是账户密码

**Outlook:**
- 确保"允许不太安全的应用"已启用，或使用OAuth认证
- 检查邮箱是否启用了IMAP访问

### 连接问题

```bash
# 测试SMTP连接
clawdbot-smtp send --to 你的邮箱@example.com --subject "测试" --body "测试连接"

# 测试IMAP连接
clawdbot-smtp list --limit 1
```

### 权限问题

```bash
# 确保配置文件权限正确
sudo chmod 600 /etc/clawdbot-smtp/config.json
sudo chown root:root /etc/clawdbot-smtp/config.json
```

## 安全建议

1. ✅ 使用应用专用密码而非账户密码
2. ✅ 配置文件权限设置为600
3. ✅ 启用两步验证
4. ✅ 定期更新密码
5. ❌ 不要将配置文件提交到Git

## 系统要求

- **操作系统：** Linux (x86_64, arm64)
- **内存：** 最小 50MB
- **磁盘空间：** 最小 50MB

## 支持的邮箱服务

- ✅ Gmail
- ✅ Outlook/Office365
- ✅ Yahoo Mail
- ✅ 企业邮箱（Exchange）
- ✅ 自建SMTP/IMAP服务器

## 许可证

MIT License

## 获取帮助

- 📖 文档：`/usr/share/doc/clawdbot-smtp/`
- 🐛 问题反馈：https://github.com/lukelzlz/clawdbot-smtp/issues
- 💬 Clawdbot社区：https://discord.gg/clawd
