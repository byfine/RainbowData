#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

from lottery.models import CrawlLog
from django.utils import timezone

print("🔧 清理卡住的Celery任务")
print("=" * 40)

# 查找长时间运行的任务（超过10分钟）
stuck_time = timezone.now() - timedelta(minutes=10)
stuck_tasks = CrawlLog.objects.filter(
    status='running',
    created_at__lt=stuck_time
)

print(f"发现 {stuck_tasks.count()} 个卡住的任务")

for task in stuck_tasks:
    print(f"  - {task.task_id[:12]}... (创建于: {task.created_at})")
    
    # 将任务标记为失败
    task.status = 'failed'
    task.end_time = timezone.now()
    task.error_message = '任务超时，自动标记为失败'
    
    if task.start_time:
        duration = (timezone.now() - task.start_time).total_seconds()
        task.duration_seconds = int(duration)
    
    task.save()
    print(f"    ✅ 已标记为失败")

print("✅ 清理完成") 