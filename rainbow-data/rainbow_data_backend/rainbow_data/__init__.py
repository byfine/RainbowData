"""
确保Celery应用在Django启动时被加载
"""

# 导入Celery应用，确保Django项目启动时Celery也会启动
from .celery import app as celery_app

__all__ = ('celery_app',)
