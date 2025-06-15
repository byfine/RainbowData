# 彩虹数据 (RainbowData) 生产环境部署指南

## 📋 部署概览

本指南将帮助您将彩虹数据项目从开发环境迁移到Ubuntu生产服务器。完整的部署包括：

- ✅ **Ubuntu服务器环境搭建**
- ✅ **Django后端应用部署**
- ✅ **Vue.js前端应用部署**
- ✅ **Nginx反向代理配置**
- ✅ **Systemd服务管理**
- ✅ **基础监控和日志**
- ✅ **安全配置和优化**

## 🎯 部署架构

```
[用户] → [Nginx] → [Gunicorn] → [Django应用]
                 ↓
           [Vue.js静态文件]
                 ↓
           [MySQL数据库] ← [Redis缓存] ← [Celery异步任务]
```

## 📋 系统要求

### 硬件要求
- **CPU**: 2核心或以上
- **内存**: 4GB RAM 或以上
- **存储**: 20GB 可用磁盘空间
- **网络**: 稳定的互联网连接

### 软件要求
- **操作系统**: Ubuntu 20.04 LTS 或更新版本
- **Python**: 3.8 或更新版本
- **Node.js**: 16.x 或更新版本
- **MySQL**: 8.0 或更新版本
- **Redis**: 6.x 或更新版本
- **Nginx**: 1.18 或更新版本

## 🚀 部署步骤

### 第一步：服务器环境搭建

1. **连接到服务器**
   ```bash
   ssh your-username@your-server-ip
   ```

2. **运行环境搭建脚本**
   ```bash
   # 上传脚本到服务器
   scp deploy/ubuntu_server_setup.sh your-username@your-server-ip:~/
   
   # 在服务器上执行
   chmod +x ubuntu_server_setup.sh
   ./ubuntu_server_setup.sh
   ```

3. **配置MySQL数据库**
   ```bash
   # 运行MySQL安全配置
   sudo mysql_secure_installation
   
   # 创建数据库和用户
   sudo mysql -u root -p
   ```
   
   ```sql
   CREATE DATABASE rainbow_data_prod CHARACTER SET utf8mb4;
   CREATE USER 'rainbowuser'@'localhost' IDENTIFIED BY 'your_strong_password';
   GRANT ALL PRIVILEGES ON rainbow_data_prod.* TO 'rainbowuser'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

### 第二步：项目代码上传

1. **使用Git克隆（推荐）**
   ```bash
   cd /var/www
   sudo git clone https://github.com/your-username/rainbow-data.git
   sudo chown -R rainbowdata:rainbowdata rainbow-data
   ```

2. **或使用SCP上传**
   ```bash
   # 从本地上传项目文件
   scp -r rainbow-data/ your-username@your-server-ip:/tmp/
   sudo mv /tmp/rainbow-data /var/www/
   sudo chown -R rainbowdata:rainbowdata /var/www/rainbow-data
   ```

### 第三步：应用部署

1. **运行部署脚本**
   ```bash
   cd /var/www/rainbow-data
   chmod +x deploy/deploy_application.sh
   ./deploy/deploy_application.sh
   ```

2. **配置环境变量**
   ```bash
   # 创建环境变量文件
   sudo tee /var/www/rainbow-data/backend/.env << EOF
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   DB_PASSWORD=your_database_password
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   EOF
   
   sudo chown rainbowdata:rainbowdata /var/www/rainbow-data/backend/.env
   sudo chmod 600 /var/www/rainbow-data/backend/.env
   ```

### 第四步：域名和SSL配置

1. **配置域名**
   ```bash
   # 编辑Nginx配置
   sudo nano /etc/nginx/sites-available/rainbow-data
   # 将 'your-domain.com' 替换为实际域名
   ```

2. **安装SSL证书（推荐Let's Encrypt）**
   ```bash
   # 安装Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # 获取SSL证书
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   
   # 设置自动续期
   sudo crontab -e
   # 添加：0 12 * * * /usr/bin/certbot renew --quiet
   ```

### 第五步：启动和验证

1. **启动所有服务**
   ```bash
   sudo systemctl start rainbow-data-gunicorn
   sudo systemctl enable rainbow-data-gunicorn
   sudo systemctl reload nginx
   ```

2. **验证部署**
   ```bash
   # 检查服务状态
   sudo systemctl status rainbow-data-gunicorn
   sudo systemctl status nginx
   sudo systemctl status mysql
   sudo systemctl status redis
   
   # 测试网站访问
   curl -I http://your-domain.com
   ```

## 🔧 配置说明

### Nginx配置要点

- **静态文件服务**: 直接由Nginx提供，提高性能
- **API代理**: 将API请求转发到Django应用
- **Gzip压缩**: 减少传输数据量
- **安全头**: 基础的安全配置

### Gunicorn配置要点

- **Worker数量**: CPU核心数 × 2 + 1
- **Worker类型**: sync（适合CPU密集型任务）
- **请求超时**: 120秒
- **预加载应用**: 提高性能

### Django生产配置

- **DEBUG**: 设为False
- **ALLOWED_HOSTS**: 配置允许的域名
- **数据库**: MySQL连接池配置
- **静态文件**: 使用collectstatic收集
- **日志**: 文件日志记录
- **安全**: HTTPS和安全头配置

## 📊 监控和维护

### 日志查看

```bash
# Django应用日志
sudo journalctl -u rainbow-data-gunicorn -f

# Nginx访问日志
sudo tail -f /var/log/rainbow-data/nginx_access.log

# Nginx错误日志
sudo tail -f /var/log/rainbow-data/nginx_error.log

# Django应用日志
sudo tail -f /var/log/rainbow-data/django.log
```

### 性能监控

```bash
# 系统资源使用
htop

# 磁盘使用
df -h

# 网络连接
ss -tulpn

# 数据库状态
sudo systemctl status mysql
```

### 定期维护任务

1. **数据库备份**
   ```bash
   # 创建备份脚本
   sudo tee /usr/local/bin/backup-rainbow-data.sh << 'EOF'
   #!/bin/bash
   BACKUP_DIR="/var/backups/rainbow-data"
   DATE=$(date +%Y%m%d_%H%M%S)
   mkdir -p $BACKUP_DIR
   mysqldump -u rainbowuser -p rainbow_data_prod > $BACKUP_DIR/db_backup_$DATE.sql
   gzip $BACKUP_DIR/db_backup_$DATE.sql
   find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
   EOF
   
   sudo chmod +x /usr/local/bin/backup-rainbow-data.sh
   
   # 设置定时备份
   sudo crontab -e
   # 添加：0 2 * * * /usr/local/bin/backup-rainbow-data.sh
   ```

2. **日志清理**
   ```bash
   # 日志自动轮转已配置，定期检查
   sudo logrotate -d /etc/logrotate.d/rainbow-data
   ```

## 🔒 安全配置

### 防火墙配置

```bash
# UFW基础配置
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# 限制SSH访问（可选）
sudo ufw limit ssh
```

### 系统安全更新

```bash
# 自动安全更新
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 数据库安全

```bash
# MySQL安全配置检查
sudo mysql_secure_installation

# 定期更新密码
sudo mysql -u root -p
ALTER USER 'rainbowuser'@'localhost' IDENTIFIED BY 'new_strong_password';
FLUSH PRIVILEGES;
```

## ❌ 故障排除

### 常见问题及解决方案

1. **服务启动失败**
   ```bash
   # 查看详细错误信息
   sudo journalctl -u rainbow-data-gunicorn -n 50
   
   # 检查配置文件语法
   python /var/www/rainbow-data/backend/manage.py check --deploy
   ```

2. **Nginx配置错误**
   ```bash
   # 测试Nginx配置
   sudo nginx -t
   
   # 查看Nginx错误日志
   sudo tail -f /var/log/nginx/error.log
   ```

3. **数据库连接失败**
   ```bash
   # 检查MySQL服务状态
   sudo systemctl status mysql
   
   # 测试数据库连接
   mysql -u rainbowuser -p rainbow_data_prod
   ```

4. **静态文件404错误**
   ```bash
   # 重新收集静态文件
   cd /var/www/rainbow-data/backend
   source venv/bin/activate
   python manage.py collectstatic --noinput
   
   # 检查文件权限
   sudo chown -R rainbowdata:rainbowdata /var/www/rainbow-data/backend/static
   ```

5. **前端页面白屏**
   ```bash
   # 检查前端构建
   cd /var/www/rainbow-data/rainbow_data_frontend/rainbow-frontend
   npm run build
   
   # 复制构建文件
   sudo cp -r dist/* /var/www/rainbow-data/frontend/
   ```

### 性能优化

1. **数据库优化**
   ```sql
   -- 查看慢查询
   SHOW VARIABLES LIKE 'slow_query_log';
   SET GLOBAL slow_query_log = 'ON';
   
   -- 分析查询性能
   EXPLAIN SELECT * FROM lottery_lotteryresult ORDER BY draw_date DESC LIMIT 10;
   ```

2. **缓存配置**
   ```python
   # 在Django settings中添加Redis缓存
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

## 📚 参考资料

- [Django部署文档](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Gunicorn配置指南](https://docs.gunicorn.org/en/stable/configure.html)
- [Nginx配置最佳实践](https://nginx.org/en/docs/)
- [Ubuntu服务器配置指南](https://ubuntu.com/server/docs)

## 🆘 技术支持

如遇到部署问题，请：

1. 查看相关日志文件
2. 检查系统资源使用情况
3. 验证网络连接和防火墙设置
4. 确认所有服务正常运行

---

**文档版本**: v1.0  
**更新日期**: 2025年6月  
**适用版本**: 彩虹数据 v1.0 