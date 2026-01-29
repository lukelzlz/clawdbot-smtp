# Clawdbot SMTP Tool - Linux打包版本说明

## 概述

这是一个独立的Linux邮件管理工具，已打包成可执行文件，无需Python环境即可运行。深度集成Clawdbot，支持SMTP发送、IMAP管理、模板系统和定时任务。

## 安装方式

### 方式1: 一键安装（最简单）

```bash
curl -sSL https://raw.githubusercontent.com/lukelzlz/clawdbot-smtp/main/packaging/install.sh | bash
```

### 方式2: 手动安装

```bash
# 下载
wget https://github.com/lukelzlz/clawdbot-smtp/releases/latest/download/clawdbot-smtp-linux-x86_64.tar.gz

# 解压
tar -xzf clawdbot-smtp-linux-x86_64.tar.gz

# 安装
cd release
sudo ./install.sh
```

## 安装后的文件结构

```
/usr/local/bin/clawdbot-smtp           # 主程序可执行文件
/etc/clawdbot-smtp/
  └── config.json                      # 配置文件
/var/lib/clawdbot-smtp/
  ├── templates/                       # 邮件模板目录
  │   └── welcome.html
  └── email_check.py                   # 邮件检查脚本
/usr/share/doc/clawdbot-smtp/
  ├── README.md                        # 英文文档
  ├── README_CN.md                     # 中文文档
  ├── INTEGRATION.md                   # 集成文档
  └── LICENSE                          # 许可证
```

## 配置

### 1. 编辑配置文件

```bash
sudo nano /etc/clawdbot-smtp/config.json
```

### 2. 配置示例

**Gmail配置（需要应用专用密码）：**
```json
{
  "accounts": {
    "primary": {
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "imap_host": "imap.gmail.com",
      "imap_port": 993,
      "username": "your@gmail.com",
      "password": "xxxx xxxx xxxx xxxx",  # 应用专用密码，不是账户密码
      "use_ssl": true
    }
  },
  "default_account": "primary"
}
```

**获取Gmail应用专用密码：**
1. 访问 https://myaccount.google.com/security
2. 启用两步验证
3. 访问 https://myaccount.google.com/apppasswords
4. 创建新应用专用密码
5. 复制密码到配置文件

**Outlook配置：**
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

### 3. 设置权限

```bash
sudo chmod 600 /etc/clawdbot-smtp/config.json
sudo chown root:root /etc/clawdbot-smtp/config.json
```

## 基本使用

### 发送邮件

```bash
# 简单邮件
clawdbot-smtp send --to user@example.com --subject "Hello" --body "测试邮件"

# 带附件
clawdbot-smtp send --to user@example.com --subject "报告" --body "请查收" --attach report.pdf

# 使用模板
clawdbot-smtp send --to user@example.com --subject "欢迎" --template welcome --context '{"name": "张三", "company": "公司名"}'
```

### 管理邮件

```bash
# 列出邮件（前10封）
clawdbot-smtp list --limit 10

# 只看未读邮件
clawdbot-smtp list --unread

# 查看邮件详情
clawdbot-smtp read --id 123

# 搜索邮件
clawdbot-smtp search --query "FROM:boss@example.com"

# 删除邮件
clawdbot-smtp delete --id 123 --yes
```

### 文件夹管理

```bash
# 列出所有文件夹
clawdbot-smtp folders list

# 创建新文件夹
clawdbot-smtp folders create --name "重要邮件"
```

## 与Clawdbot集成

### 1. 配置环境变量（可选）

如果不想使用配置文件，可以设置环境变量：

```bash
# 添加到 ~/.bashrc 或 /etc/environment
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export IMAP_HOST=imap.gmail.com
export IMAP_PORT=993
export SMTP_USERNAME=your@gmail.com
export SMTP_PASSWORD=your-app-password
```

### 2. 在Clawdbot中使用

```bash
# 检查邮件（JSON格式输出，便于Clawdbot解析）
clawdbot-smtp list --limit 5 --json

# 检查未读邮件
clawdbot-smtp list --unread --json
```

### 3. 定时检查邮件（Cron）

```bash
# 编辑crontab
crontab -e

# 每小时检查一次未读邮件并发送通知到Discord
0 * * * * /var/lib/clawdbot-smtp/email_check.py 10 INBOX | clawdbot message send --to discord --target YOUR_CHANNEL_ID

# 每天早上9点发送日报
0 9 * * * /usr/local/bin/clawdbot-smtp send --to manager@company.com --subject "日报" --template daily_report --context '{"date": "2024-01-29"}'
```

## 自定义模板

### 添加新模板

```bash
# 1. 创建模板文件
sudo nano /var/lib/clawdbot-smtp/templates/my_template.html

# 2. 编写模板内容（使用Jinja2语法）
<!DOCTYPE html>
<html>
<body>
  <h1>你好，{{ name }}！</h1>
  <p>{{ message }}</p>
  <p>日期：{{ date }}</p>
</body>
</html>

# 3. 使用模板
clawdbot-smtp send --to user@example.com --subject "测试" --template my_template --context '{"name": "用户", "message": "这是一条消息", "date": "2024-01-29"}'
```

## 常见问题

### 1. 认证失败

**Gmail:**
- 确保已启用两步验证
- 使用应用专用密码，不是账户密码
- 检查是否已启用IMAP访问

**Outlook:**
- 确保"允许不太安全的应用"已启用
- 检查Outlook设置中是否启用了IMAP

### 2. 连接超时

```bash
# 测试连接
clawdbot-smtp send --to 你的邮箱@example.com --subject "测试" --body "测试连接"

# 检查防火墙设置
sudo ufw status
```

### 3. 权限问题

```bash
# 修复配置文件权限
sudo chmod 600 /etc/clawdbot-smtp/config.json
sudo chown root:root /etc/clawdbot-smtp/config.json

# 修复可执行文件权限
sudo chmod +x /usr/local/bin/clawdbot-smtp
```

### 4. 找不到命令

```bash
# 确保已正确安装
which clawdbot-smtp

# 如果没有输出，重新安装
sudo /var/lib/clawdbot-smtp/uninstall.sh
# 然后重新运行安装脚本
```

## 更新到最新版本

```bash
# 1. 备份配置
sudo cp /etc/clawdbot-smtp/config.json /tmp/config.json.backup

# 2. 下载最新版本
wget https://github.com/lukelzlz/clawdbot-smtp/releases/latest/download/clawdbot-smtp-linux-x86_64.tar.gz

# 3. 解压并安装
tar -xzf clawdbot-smtp-linux-x86_64.tar.gz
cd release
sudo ./install.sh

# 4. 恢复配置（如果需要）
sudo cp /tmp/config.json.backup /etc/clawdbot-smtp/config.json
```

## 卸载

```bash
sudo /var/lib/clawdbot-smtp/uninstall.sh
```

卸载时，脚本会询问是否删除配置文件和数据目录。

## 系统要求

- **操作系统：** Linux (x86_64, arm64)
- **最小内存：** 50MB
- **最小磁盘空间：** 50MB
- **网络：** 需要访问SMTP/IMAP服务器

## 安全建议

1. ✅ 使用应用专用密码而非账户密码
2. ✅ 配置文件权限设置为600
3. ✅ 启用邮箱的两步验证
4. ✅ 定期更新密码
5. ❌ 不要将配置文件提交到版本控制
6. ❌ 不要在脚本中硬编码密码

## 支持的邮箱服务

- ✅ Gmail（需要应用专用密码）
- ✅ Outlook/Office365
- ✅ Yahoo Mail
- ✅ 企业邮箱（Exchange）
- ✅ 自建SMTP/IMAP服务器

## 获取帮助

- 📖 文档：`/usr/share/doc/clawdbot-smtp/`
- 🐛 问题反馈：https://github.com/lukelzlz/clawdbot-smtp/issues
- 💬 Clawdbot社区：https://discord.gg/clawd
- 📚 官方文档：https://docs.clawd.bot

## 快速参考

```bash
# 查看帮助
clawdbot-smtp --help

# 发送邮件
clawdbot-smtp send --to EMAIL --subject SUBJECT --body BODY

# 列出邮件
clawdbot-smtp list --limit N

# 搜索邮件
clawdbot-smtp search --query QUERY

# JSON输出（供程序使用）
clawdbot-smtp list --json

# 检查未读邮件（用于定时任务）
/var/lib/clawdbot-smtp/email_check.py N FOLDER
```
