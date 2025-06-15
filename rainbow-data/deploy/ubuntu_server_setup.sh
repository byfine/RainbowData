#!/bin/bash
# 彩虹数据 (RainbowData) Ubuntu服务器环境搭建脚本
# 用途：自动化安装和配置生产环境所需的所有组件
# 版本：v1.0
# 创建时间：2025年6月

set -e  # 遇到错误立即退出

echo "🚀 开始彩虹数据项目服务器环境搭建..."

# 7.1.1 系统基础配置
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

echo "🔧 安装基础工具..."
sudo apt install -y curl wget vim git htop tree unzip

echo "🔥 配置防火墙..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Django开发端口（可选）

# 7.1.2 Python环境安装
echo "🐍 安装Python环境..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y pkg-config default-libmysqlclient-dev

echo "✅ Python版本验证:"
python3 --version

# 7.1.3 MySQL数据库安装
echo "🗄️ 安装MySQL数据库..."
sudo apt install -y mysql-server

echo "⚙️ 配置MySQL服务..."
sudo systemctl start mysql
sudo systemctl enable mysql

echo "🔐 MySQL安全配置提示："
echo "请手动运行: sudo mysql_secure_installation"
echo "然后创建数据库和用户："
echo "CREATE DATABASE rainbow_data_prod CHARACTER SET utf8mb4;"
echo "CREATE USER 'rainbowuser'@'localhost' IDENTIFIED BY 'your_strong_password';"
echo "GRANT ALL PRIVILEGES ON rainbow_data_prod.* TO 'rainbowuser'@'localhost';"
echo "FLUSH PRIVILEGES;"

# 7.1.4 Redis安装配置（爬虫功能需要）
echo "🔴 安装Redis服务器..."
sudo apt install -y redis-server

echo "⚙️ 配置Redis服务..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

echo "✅ Redis连接测试:"
redis-cli ping

# 7.1.5 Nginx安装配置
echo "🌐 安装Nginx..."
sudo apt install -y nginx

echo "⚙️ 配置Nginx服务..."
sudo systemctl start nginx
sudo systemctl enable nginx

echo "🔥 配置防火墙允许Nginx..."
sudo ufw allow 'Nginx Full'

# Node.js安装（用于前端构建）
echo "📦 安装Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "✅ Node.js版本验证:"
node --version
npm --version

# 创建项目用户（可选）
echo "👤 创建项目用户 rainbowdata..."
if ! id "rainbowdata" &>/dev/null; then
    sudo useradd -m -s /bin/bash rainbowdata
    sudo usermod -aG sudo rainbowdata
    echo "用户 rainbowdata 创建完成"
else
    echo "用户 rainbowdata 已存在"
fi

# 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p /var/www/rainbow-data
sudo chown -R rainbowdata:rainbowdata /var/www/rainbow-data

# 创建日志目录
echo "📝 创建日志目录..."
sudo mkdir -p /var/log/rainbow-data
sudo chown -R rainbowdata:rainbowdata /var/log/rainbow-data

echo "🎉 Ubuntu服务器基础环境搭建完成！"
echo ""
echo "📋 下一步操作："
echo "1. 运行: sudo mysql_secure_installation"
echo "2. 配置MySQL数据库和用户"
echo "3. 上传项目代码到 /var/www/rainbow-data"
echo "4. 运行应用部署脚本"
echo ""
echo "🔧 验证安装结果:"
echo "- Python: $(python3 --version)"
echo "- MySQL: $(mysql --version | head -1)"
echo "- Redis: $(redis-server --version | head -1)"
echo "- Nginx: $(nginx -v 2>&1)"
echo "- Node.js: $(node --version)" 