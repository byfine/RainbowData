# 彩虹数据 (RainbowData) 部署文件说明

## 📋 概述

本目录包含彩虹数据项目的完整生产环境部署配置和自动化脚本。通过这些文件，您可以快速将项目从开发环境迁移到Ubuntu生产服务器。

## 📁 文件结构

```
deploy/
├── README.md                    # 本说明文件
├── ubuntu_server_setup.sh      # Ubuntu服务器环境搭建脚本
├── deploy_application.sh       # 应用部署脚本
├── build_frontend.sh           # 前端构建脚本
├── check_deployment.sh         # 部署状态检查脚本
├── nginx_config.conf           # Nginx配置文件
├── gunicorn_config.py          # Gunicorn WSGI服务器配置
├── systemd_services.txt        # Systemd服务配置文件
├── deployment_guide.md         # 详细部署指南
└── frontend_dist/              # 前端构建输出目录（自动生成）
```

## 🚀 快速部署流程

### 第一步：服务器环境准备

1. **上传环境搭建脚本到服务器**
   ```bash
   scp deploy/ubuntu_server_setup.sh your-username@your-server-ip:~/
   ```

2. **在服务器上运行环境搭建**
   ```bash
   ssh your-username@your-server-ip
   chmod +x ubuntu_server_setup.sh
   ./ubuntu_server_setup.sh
   ```

3. **配置MySQL数据库**
   ```bash
   sudo mysql_secure_installation
   sudo mysql -u root -p
   ```
   ```sql
   CREATE DATABASE rainbow_data_prod CHARACTER SET utf8mb4;
   CREATE USER 'rainbowuser'@'localhost' IDENTIFIED BY 'your_strong_password';
   GRANT ALL PRIVILEGES ON rainbow_data_prod.* TO 'rainbowuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

### 第二步：本地前端构建

```bash
# 在本地项目目录执行
chmod +x deploy/build_frontend.sh
./deploy/build_frontend.sh
```

### 第三步：项目代码上传

```bash
# 方法一：Git克隆（推荐）
ssh your-username@your-server-ip
cd /var/www
sudo git clone https://github.com/your-username/rainbow-data.git
sudo chown -R rainbowdata:rainbowdata rainbow-data

# 方法二：直接上传
scp -r . your-username@your-server-ip:/tmp/rainbow-data/
ssh your-username@your-server-ip
sudo mv /tmp/rainbow-data /var/www/
sudo chown -R rainbowdata:rainbowdata /var/www/rainbow-data
```

### 第四步：应用部署

```bash
# 在服务器上执行
cd /var/www/rainbow-data
chmod +x deploy/deploy_application.sh
./deploy/deploy_application.sh
```

### 第五步：部署验证

```bash
# 检查部署状态
chmod +x deploy/check_deployment.sh
./deploy/check_deployment.sh
```

## 📄 文件详细说明

### 🔧 核心脚本

#### `ubuntu_server_setup.sh`
**用途**: 自动化安装Ubuntu服务器所需的所有基础组件
- 系统更新和基础工具安装
- Python 3.8+ 环境配置
- MySQL 8.0+ 数据库安装
- Redis 缓存服务安装
- Nginx Web服务器安装
- Node.js 前端构建环境
- 用户和目录初始化

#### `deploy_application.sh`
**用途**: 自动化部署Django后端和Vue.js前端应用
- Python虚拟环境创建
- 依赖包安装
- 数据库迁移执行
- 静态文件收集
- 前端应用构建
- Nginx配置部署
- Systemd服务配置

#### `build_frontend.sh`
**用途**: 在本地构建Vue.js前端应用
- Node.js环境检查
- 依赖包安装
- 生产环境构建
- 构建文件验证
- 部署准备

#### `check_deployment.sh`
**用途**: 全面检查生产环境部署状态
- 系统服务状态检查
- 应用服务状态检查
- 网络和端口监听检查
- 文件和权限检查
- 数据库连接检查
- HTTP服务检查
- 性能状态监控

### ⚙️ 配置文件

#### `nginx_config.conf`
**用途**: Nginx Web服务器配置
- 前端静态文件服务
- 后端API反向代理
- Gzip压缩优化
- 安全头配置
- SSL/HTTPS支持（可选）
- 日志配置

#### `gunicorn_config.py`
**用途**: Gunicorn WSGI服务器配置
- Worker进程配置
- 性能优化设置
- 日志配置
- 安全配置
- 环境变量管理

#### `systemd_services.txt`
**用途**: Linux系统服务配置模板
- Django Gunicorn服务
- Celery Worker服务（爬虫功能）
- Celery Beat定时任务服务
- 服务依赖关系配置
- 自动重启配置

### 📚 文档

#### `deployment_guide.md`
**用途**: 详细的部署指南文档
- 系统要求说明
- 分步骤部署指南
- 配置说明
- 监控和维护指南
- 故障排除方案
- 性能优化建议

## 🎯 部署架构

```
Internet → Nginx (Port 80/443) → Gunicorn (Port 8000) → Django App
    ↓
Vue.js Static Files (Nginx)
    ↓
MySQL Database ← Redis Cache ← Celery Tasks
```

## 🔒 安全配置

### 必须配置项
1. **修改默认密码**: 数据库、系统用户
2. **配置防火墙**: UFW基础规则
3. **SSL证书**: Let's Encrypt推荐
4. **环境变量**: 敏感信息不要硬编码

### 推荐配置项
1. **自动安全更新**: unattended-upgrades
2. **SSH密钥登录**: 禁用密码登录
3. **定期备份**: 数据库和文件备份
4. **日志监控**: 错误日志监控

## 📊 监控和维护

### 服务管理命令
```bash
# 查看服务状态
sudo systemctl status rainbow-data-gunicorn
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis

# 重启服务
sudo systemctl restart rainbow-data-gunicorn
sudo systemctl reload nginx

# 查看日志
sudo journalctl -u rainbow-data-gunicorn -f
sudo tail -f /var/log/rainbow-data/nginx_access.log
```

### 备份建议
```bash
# 数据库备份
mysqldump -u rainbowuser -p rainbow_data_prod > backup_$(date +%Y%m%d).sql

# 文件备份
tar -czf backup_files_$(date +%Y%m%d).tar.gz /var/www/rainbow-data
```

## ❌ 常见问题

### 部署失败
1. 检查系统环境是否满足要求
2. 确认所有依赖包已正确安装
3. 查看详细错误日志

### 服务无法启动
1. 检查配置文件语法
2. 确认文件权限正确
3. 查看systemd服务日志

### 网站无法访问
1. 确认Nginx配置正确
2. 检查防火墙设置
3. 验证DNS解析

## 🆘 技术支持

如果遇到部署问题：

1. 首先运行 `check_deployment.sh` 脚本诊断
2. 查看相关服务日志文件
3. 参考 `deployment_guide.md` 详细文档
4. 检查系统资源使用情况

## 📚 相关文档

- [Django 部署文档](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Nginx 配置指南](https://nginx.org/en/docs/)
- [Ubuntu 服务器文档](https://ubuntu.com/server/docs)
- [Let's Encrypt SSL证书](https://letsencrypt.org/getting-started/)

---

**文档版本**: v1.0  
**更新日期**: 2025年6月  
**适用版本**: 彩虹数据 v1.0 