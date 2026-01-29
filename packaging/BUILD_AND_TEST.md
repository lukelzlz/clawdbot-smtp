# Clawdbot SMTP Tool - 打包测试文档

## 开发者指南

此文档用于开发人员如何构建和测试Linux打包版本。

## 开发环境准备

```bash
# 进入项目目录
cd /root/clawd/clawdbot-smtp

# 安装开发依赖
pip install -r requirements.txt

# 确认工具已安装
pyinstaller --version
```

## 构建可执行文件

### 方式1: 使用build.sh脚本

```bash
cd packaging
./build.sh
```

这将创建 `dist/clawdbot-smtp` 可执行文件。

### 方式2: 手动使用PyInstaller

```bash
pyinstaller \
    --name="clawdbot-smtp" \
    --onefile \
    --add-data "email_cli/templates:email_cli/templates" \
    --hidden-import=jinja2 \
    --hidden-import=click \
    --hidden-import=dotenv \
    --hidden-import=colorama \
    --clean \
    email_cli/main.py
```

## 测试可执行文件

### 1. 基本功能测试

```bash
# 测试帮助命令
./dist/clawdbot-smtp --help

# 测试版本
./dist/clawdbot-smtp --version
```

### 2. 发送邮件测试

```bash
# 需要先创建测试配置
cat > /tmp/test_config.json << 'EOF'
{
  "accounts": {
    "test": {
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "imap_host": "imap.gmail.com",
      "imap_port": 993,
      "username": "your@gmail.com",
      "password": "your-app-password",
      "use_ssl": true
    }
  },
  "default_account": "test"
}
EOF

# 使用临时配置测试
EMAIL_CONFIG=/tmp/test_config.json ./dist/clawdbot-smtp send \
  --to yourself@example.com \
  --subject "Test" \
  --body "This is a test"
```

### 3. JSON输出测试

```bash
EMAIL_CONFIG=/tmp/test_config.json ./dist/clawdbot-smtp list \
  --limit 1 \
  --json | python -m json.tool
```

### 4. 模板测试

```bash
EMAIL_CONFIG=/tmp/test_config.json ./dist/clawdbot-smtp send \
  --to yourself@example.com \
  --subject "Template Test" \
  --template welcome \
  --context '{"name": "Test User", "company": "Test Corp"}'
```

## 创建发布包

### 创建tar.gz包

```bash
cd packaging
./release.sh 1.0.0
```

这将创建：
- `clawdbot-smtp-1.0.0-linux-x86_64.tar.gz`
- `clawdbot-smtp-1.0.0-linux-x86_64.tar.gz.sha256`

### 测试安装包

```bash
# 解压
tar -xzf clawdbot-smtp-1.0.0-linux-x86_64.tar.gz

# 检查内容
ls -la release/

# 模拟安装（使用--help检查脚本）
./release/install.sh --help
```

## 本地安装测试

### 1. 安装到系统

```bash
cd release
sudo ./install.sh
```

### 2. 验证安装

```bash
# 检查可执行文件
which clawdbot-smtp

# 检查版本
clawdbot-smtp --version

# 检查配置文件
ls -la /etc/clawdbot-smtp/

# 检查模板目录
ls -la /var/lib/clawdbot-smtp/templates/

# 检查文档
ls -la /usr/share/doc/clawdbot-smtp/
```

### 3. 功能测试（已安装版本）

```bash
# 编辑配置
sudo nano /etc/clawdbot-smtp/config.json

# 测试发送
clawdbot-smtp send --to yourself@example.com --subject "Test" --body "Test"

# 测试列出
clawdbot-smtp list --limit 1

# 测试JSON输出
clawdbot-smtp list --limit 1 --json
```

### 4. 测试卸载

```bash
sudo /var/lib/clawdbot-smtp/uninstall.sh
```

## 多架构构建（可选）

### 构建arm64版本

```bash
# 在arm64系统上
cd packaging
./build.sh

# 创建架构特定包
ARCH=arm64 ./release.sh 1.0.0
```

## 发布检查清单

发布前，确保完成以下检查：

- [ ] 可执行文件能够正常运行
- [ ] 所有基本命令（send, list, read, search, delete）都能工作
- [ ] JSON输出格式正确
- [ ] 模板系统正常工作
- [ ] 安装脚本能在干净的系统上成功运行
- [ ] 卸载脚本能正确清理文件
- [ ] 配置文件权限正确（600）
- [ ] 文档文件完整且正确
- [ ] SHA256校验和正确生成
- [ ] README中的安装说明准确

## 常见问题

### 1. PyInstaller找不到模块

```bash
# 明确指定隐藏导入
pyinstaller --hidden-import=模块名 ...
```

### 2. 模板文件没有包含

```bash
# 使用--add-data正确包含模板
pyinstaller --add-data "源路径:目标路径" ...
```

### 3. 权限问题

```bash
# 确保脚本有执行权限
chmod +x packaging/*.sh
```

### 4. 路径问题

测试时注意：
- 开发环境使用相对路径
- 打包后使用绝对路径
- 安装后使用系统路径

## 调试技巧

### 查看PyInstaller详细日志

```bash
pyinstaller --log-level DEBUG ...
```

### 测试时启用详细输出

```bash
# 设置环境变量
EMAIL_DEBUG=1 clawdbot-smtp list
```

### 检查打包内容

```bash
# 查看包含的文件
pyinstaller --log-level DEBUG email_cli/main.py 2>&1 | grep "adding"
```

## 发布流程

1. 更新版本号
2. 运行完整测试
3. 创建发布包
4. 在GitHub上创建Release
5. 上传tar.gz文件
6. 更新README中的下载链接
7. 通知用户

## 版本管理

使用语义化版本号：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的API更改
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的错误修复
