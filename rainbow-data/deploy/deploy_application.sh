#!/bin/bash
# 彩虹数据 (RainbowData) 应用部署脚本
# 用途：自动化部署Django后端和Vue.js前端应用
# 版本：v1.0
# 创建时间：2025年6月

set -e  # 遇到错误立即退出

echo "🚀 开始彩虹数据应用部署..."

# 配置变量
PROJECT_NAME="rainbow-data"
PROJECT_DIR="/var/www/rainbow-data"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="/var/log/rainbow-data"
PID_DIR="/var/run/rainbow-data"
USER="rainbowdata"
GROUP="rainbowdata"

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  此脚本不应以root用户运行，请使用普通用户"
   exit 1
fi

# 7.2.1 项目文件准备
echo "📁 准备项目目录..."
sudo mkdir -p $PROJECT_DIR
sudo mkdir -p $BACKEND_DIR
sudo mkdir -p $FRONTEND_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p $PID_DIR
sudo chown -R $USER:$GROUP $PROJECT_DIR
sudo chown -R $USER:$GROUP $LOG_DIR
sudo chown -R $USER:$GROUP $PID_DIR

# 检查Git仓库是否存在
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "📥 克隆项目代码..."
    # 请替换为您的实际Git仓库地址
    # git clone https://github.com/your-username/rainbow-data.git $PROJECT_DIR
    echo "⚠️  请手动克隆项目代码到 $PROJECT_DIR"
    echo "或者从本地复制项目文件到服务器"
    read -p "项目代码是否已准备就绪？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 请先准备项目代码"
        exit 1
    fi
fi

# 7.2.2 Django后端部署
echo "🐍 配置Django后端..."

# 进入后端目录（假设后端代码在rainbow_data_backend目录）
cd $PROJECT_DIR
if [ -d "rainbow_data_backend" ]; then
    echo "📦 复制后端代码..."
    cp -r rainbow_data_backend/* $BACKEND_DIR/
fi

cd $BACKEND_DIR

# 创建Python虚拟环境
echo "🔧 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖包
echo "📦 安装Python依赖包..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn  # 添加Gunicorn
else
    echo "⚠️  未找到requirements.txt文件"
fi

# 创建生产环境配置文件
echo "⚙️  配置生产环境设置..."
if [ ! -f "rainbow_data/settings/production.py" ]; then
    mkdir -p rainbow_data/settings
    cat > rainbow_data/settings/production.py << 'EOF'
from .base import *
import os

# 生产环境配置
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'localhost', '127.0.0.1']

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rainbow_data_prod',
        'USER': 'rainbowuser',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_database_password'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 安全配置
SECURE_SSL_REDIRECT = False  # 使用HTTPS时设为True
SECURE_HSTS_SECONDS = 31536000  # 使用HTTPS时启用
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/rainbow-data/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Celery配置（爬虫功能）
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
EOF
    echo "✅ 生产环境配置文件已创建"
fi

# 数据库迁移
echo "🗄️  执行数据库迁移..."
python manage.py migrate

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

# 创建超级用户（可选）
echo "👤 创建超级用户..."
read -p "是否创建Django超级用户？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# 7.2.3 Vue.js前端部署
echo "🖥️  构建Vue.js前端..."

# 进入前端目录
cd $PROJECT_DIR
if [ -d "rainbow_data_frontend/rainbow-frontend" ]; then
    echo "📦 构建前端应用..."
    cd rainbow_data_frontend/rainbow-frontend
    
    # 安装前端依赖
    npm install
    
    # 构建生产版本
    npm run build
    
    # 复制构建文件到部署目录
    cp -r dist/* $FRONTEND_DIR/
    echo "✅ 前端构建完成"
else
    echo "⚠️  未找到前端项目目录"
fi

# 7.2.4 配置Nginx
echo "🌐 配置Nginx..."
sudo cp $PROJECT_DIR/deploy/nginx_config.conf /etc/nginx/sites-available/rainbow-data

# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/rainbow-data /etc/nginx/sites-enabled/

# 删除默认站点
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
sudo nginx -t

# 重载Nginx配置
sudo systemctl reload nginx

# 7.2.5 配置Systemd服务
echo "⚙️  配置系统服务..."

# 复制服务文件
sudo tee /etc/systemd/system/rainbow-data-gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=彩虹数据 Django Gunicorn服务
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=notify
User=rainbowdata
Group=rainbowdata
WorkingDirectory=/var/www/rainbow-data/backend
ExecStart=/var/www/rainbow-data/backend/venv/bin/gunicorn rainbow_data.wsgi:application -c /var/www/rainbow-data/deploy/gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=3
Environment=DJANGO_SETTINGS_MODULE=rainbow_data.settings.production
Environment=PYTHONPATH=/var/www/rainbow-data/backend
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rainbow-data-gunicorn

[Install]
WantedBy=multi-user.target
EOF

# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
echo "🔄 启动应用服务..."
sudo systemctl start rainbow-data-gunicorn
sudo systemctl enable rainbow-data-gunicorn

# 检查服务状态
echo "✅ 检查服务状态..."
sleep 3
sudo systemctl status rainbow-data-gunicorn --no-pager

# 7.3 基础监控配置
echo "📊 配置基础监控..."

# 创建日志轮转配置
sudo tee /etc/logrotate.d/rainbow-data > /dev/null << 'EOF'
/var/log/rainbow-data/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 rainbowdata rainbowdata
    postrotate
        systemctl reload rainbow-data-gunicorn > /dev/null 2>&1 || true
    endscript
}
EOF

echo "🎉 彩虹数据应用部署完成！"
echo ""
echo "📋 部署摘要："
echo "- 项目目录: $PROJECT_DIR"
echo "- 后端目录: $BACKEND_DIR"
echo "- 前端目录: $FRONTEND_DIR"
echo "- 日志目录: $LOG_DIR"
echo ""
echo "🔧 验证部署结果："
echo "1. 检查服务状态: sudo systemctl status rainbow-data-gunicorn"
echo "2. 查看应用日志: sudo journalctl -u rainbow-data-gunicorn -f"
echo "3. 访问网站: http://your-domain.com"
echo "4. 访问API文档: http://your-domain.com/api/docs/"
echo "5. 访问Django Admin: http://your-domain.com/admin/"
echo ""
echo "🚨 重要提醒："
echo "1. 修改域名配置: $PROJECT_DIR/deploy/nginx_config.conf"
echo "2. 设置数据库密码环境变量"
echo "3. 配置SSL证书（生产环境推荐）"
echo "4. 设置防火墙规则"
echo "5. 配置定期备份" 