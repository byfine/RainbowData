#!/usr/bin/env python
"""
手动测试Celery任务执行
"""

import os
import sys
import django
from pathlib import Path

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

def test_tasks():
    """测试各种任务"""
    print("🧪 开始手动任务测试...")
    print("=" * 50)
    
    # 导入任务
    from lottery.tasks import (
        test_simple_crawler_task,
        crawl_latest_data_simple,
        update_statistics,
        check_data_sources
    )
    
    # 测试1：简单爬虫任务
    print("\n1️⃣ 测试简单爬虫任务")
    try:
        result1 = test_simple_crawler_task.delay()
        print(f"任务提交成功，ID: {result1.id}")
        task_result1 = result1.get(timeout=15)
        print(f"✅ 结果: {task_result1}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试2：无参数爬虫任务
    print("\n2️⃣ 测试无参数爬虫任务")
    try:
        result2 = crawl_latest_data_simple.delay()
        print(f"任务提交成功，ID: {result2.id}")
        task_result2 = result2.get(timeout=15)
        print(f"✅ 结果: {task_result2}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试3：数据源检查任务
    print("\n3️⃣ 测试数据源检查任务")
    try:
        result3 = check_data_sources.delay()
        print(f"任务提交成功，ID: {result3.id}")
        task_result3 = result3.get(timeout=20)
        print(f"✅ 结果: {task_result3}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试4：统计更新任务
    print("\n4️⃣ 测试统计更新任务")
    try:
        result4 = update_statistics.delay()
        print(f"任务提交成功，ID: {result4.id}")
        task_result4 = result4.get(timeout=30)
        print(f"✅ 结果: {task_result4}")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 任务测试完成!")

def test_periodic_tasks():
    """测试周期性任务配置"""
    print("\n🕐 检查周期性任务...")
    
    try:
        from django_celery_beat.models import PeriodicTask
        
        tasks = PeriodicTask.objects.all()
        print(f"📋 数据库中的周期性任务: {tasks.count()} 个")
        
        for task in tasks:
            status = "✅ 启用" if task.enabled else "⚠️ 禁用"
            print(f"  - {task.name}: {task.task} ({status})")
            
    except Exception as e:
        print(f"❌ 检查周期性任务失败: {e}")

if __name__ == "__main__":
    print("🔍 Celery手动任务测试")
    print("时间:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 运行任务测试
    test_tasks()
    
    # 检查周期性任务
    test_periodic_tasks()
    
    print("\n💡 提示:")
    print("如果任务执行失败，请确保:")
    print("1. Redis服务正在运行")
    print("2. Celery Worker正在运行")
    print("3. 虚拟环境已激活") 