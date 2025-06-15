"""
Celery configuration for rainbow_data project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# 设置默认的Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')

# 创建Celery应用实例
app = Celery('rainbow_data')

# 使用Django设置文件配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现Django应用中的tasks.py文件
app.autodiscover_tasks()

# Celery Beat调度器配置
app.conf.beat_schedule = {
    # 每天晚上21:30自动获取最新开奖数据
    'crawl-latest-data-daily': {
        'task': 'lottery.tasks.crawl_latest_data_simple',  # 使用存在的任务
        'schedule': crontab(hour=21, minute=30),
        'args': ['500彩票网'],  # 指定数据源
    },
    
    # 每天晚上22:00更新统计数据
    'update-statistics-daily': {
        'task': 'lottery.tasks.update_statistics',
        'schedule': crontab(hour=22, minute=0),
    },
    
    # 每周日凌晨2:00进行数据质量检查
    'data-quality-check-weekly': {
        'task': 'lottery.tasks.data_quality_check',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # 0表示周日
    },
    
    # 每小时检查数据源状态
    'check-data-sources-hourly': {
        'task': 'lottery.tasks.check_data_sources',
        'schedule': crontab(minute=0),  # 每小时整点执行
    },
    
    # 测试任务 - 每2分钟执行一次（用于调试）
    'test-task-every-2-minutes': {
        'task': 'lottery.tasks.test_simple_crawler_task',
        'schedule': crontab(minute='*/2'),  # 每2分钟执行一次
    },
}

# 任务执行超时配置
app.conf.timezone = 'Asia/Shanghai'

@app.task(bind=True)
def debug_task(self):
    """调试任务，用于测试Celery配置"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!' 