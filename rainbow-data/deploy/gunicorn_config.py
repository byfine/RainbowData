# 彩虹数据 (RainbowData) Gunicorn配置文件
# 文件位置：/var/www/rainbow-data/backend/gunicorn_config.py
# 用途：WSGI服务器配置，性能优化和日志管理
# 版本：v1.0

import multiprocessing
import os

# 7.2.2 Gunicorn基础配置
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 120
keepalive = 2

# 进程配置
user = "rainbowdata"
group = "rainbowdata"
tmp_upload_dir = None
daemon = False
pidfile = "/var/run/rainbow-data/gunicorn.pid"

# 日志配置
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "/var/log/rainbow-data/gunicorn_access.log"
errorlog = "/var/log/rainbow-data/gunicorn_error.log"
loglevel = "info"
access_log_datefmt = "[%Y-%m-%d %H:%M:%S %z]"
error_log_datefmt = "[%Y-%m-%d %H:%M:%S %z]"

# 性能优化
worker_tmp_dir = "/dev/shm"
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 安全配置
forwarded_allow_ips = "127.0.0.1"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# 启动时回调函数
def on_starting(server):
    """服务器启动时调用"""
    server.log.info("彩虹数据 Gunicorn服务器正在启动...")

def on_reload(server):
    """重新加载时调用"""
    server.log.info("彩虹数据 Gunicorn服务器正在重新加载...")

def when_ready(server):
    """服务器准备就绪时调用"""
    server.log.info("彩虹数据 Gunicorn服务器已准备就绪")

def on_exit(server):
    """服务器退出时调用"""
    server.log.info("彩虹数据 Gunicorn服务器正在关闭...")

# Worker进程配置
def post_fork(server, worker):
    """Worker进程创建后调用"""
    server.log.info("Worker进程 %s 已启动", worker.pid)

def pre_exec(server):
    """执行前调用"""
    server.log.info("服务器正在分叉...")

# 环境变量配置
raw_env = [
    'DJANGO_SETTINGS_MODULE=rainbow_data.settings.production',
    'PYTHONPATH=/var/www/rainbow-data/backend',
]

# 开发环境配置（仅用于测试）
if os.environ.get('DEBUG', 'False').lower() == 'true':
    workers = 1
    reload = True
    loglevel = "debug"
    raw_env = [
        'DJANGO_SETTINGS_MODULE=rainbow_data.settings.development',
        'PYTHONPATH=/var/www/rainbow-data/backend',
    ] 