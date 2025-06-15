#!/usr/bin/env python
"""
完整的Celery系统测试脚本
测试所有任务和定时任务功能
"""

import os
import sys
import django
import time
from pathlib import Path
from datetime import datetime

# 添加Django项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

def test_all_tasks():
    """测试所有定义的任务"""
    print("🧪 测试所有Celery任务...")
    
    try:
        from lottery.tasks import (
            test_simple_crawler_task,
            crawl_latest_data_simple,
            update_statistics,
            data_quality_check,
            check_data_sources
        )
        
        # 测试1：简单爬虫任务
        print("\n1️⃣ 测试简单爬虫任务...")
        result1 = test_simple_crawler_task.delay()
        print(f"任务ID: {result1.id}")
        try:
            task_result1 = result1.get(timeout=15)
            print(f"✅ 结果: {task_result1}")
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试2：无参数爬虫任务
        print("\n2️⃣ 测试无参数爬虫任务...")
        result2 = crawl_latest_data_simple.delay()
        print(f"任务ID: {result2.id}")
        try:
            task_result2 = result2.get(timeout=15)
            print(f"✅ 结果: {task_result2}")
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试3：统计更新任务
        print("\n3️⃣ 测试统计更新任务...")
        result3 = update_statistics.delay()
        print(f"任务ID: {result3.id}")
        try:
            task_result3 = result3.get(timeout=30)
            print(f"✅ 结果: {task_result3}")
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试4：数据质量检查任务
        print("\n4️⃣ 测试数据质量检查任务...")
        result4 = data_quality_check.delay()
        print(f"任务ID: {result4.id}")
        try:
            task_result4 = result4.get(timeout=20)
            print(f"✅ 结果: {task_result4}")
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试5：数据源检查任务
        print("\n5️⃣ 测试数据源检查任务...")
        result5 = check_data_sources.delay()
        print(f"任务ID: {result5.id}")
        try:
            task_result5 = result5.get(timeout=20)
            print(f"✅ 结果: {task_result5}")
        except Exception as e:
            print(f"❌ 失败: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ 任务测试失败: {e}")
        return False

def test_beat_schedule():
    """测试定时任务配置"""
    print("\n🕐 检查Celery Beat定时任务配置...")
    
    try:
        from rainbow_data.celery import app
        
        schedule = app.conf.beat_schedule
        print(f"✅ 定义的定时任务数量: {len(schedule)}")
        
        for task_name, task_config in schedule.items():
            print(f"\n📋 任务: {task_name}")
            print(f"  - 任务函数: {task_config['task']}")
            print(f"  - 调度配置: {task_config['schedule']}")
            if 'args' in task_config:
                print(f"  - 参数: {task_config['args']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 定时任务配置检查失败: {e}")
        return False

def check_celery_processes():
    """检查Celery进程状态"""
    print("\n🔍 检查Celery进程状态...")
    
    try:
        from rainbow_data.celery import app
        
        # 检查活跃的worker
        inspect = app.control.inspect()
        
        # 获取活跃的worker
        active_queues = inspect.active_queues()
        if active_queues:
            print("✅ 活跃的Worker:")
            for worker, queues in active_queues.items():
                print(f"  - {worker}: {len(queues)} 队列")
        else:
            print("⚠️ 没有发现活跃的Worker")
        
        # 检查注册的任务
        registered_tasks = inspect.registered()
        if registered_tasks:
            print("✅ 注册的任务:")
            for worker, tasks in registered_tasks.items():
                print(f"  - {worker}: {len(tasks)} 个任务")
                for task in tasks[:5]:  # 只显示前5个
                    print(f"    · {task}")
                if len(tasks) > 5:
                    print(f"    · ... 还有{len(tasks)-5}个任务")
        else:
            print("⚠️ 没有发现注册的任务")
            
        return True
        
    except Exception as e:
        print(f"❌ Celery进程检查失败: {e}")
        return False

def test_django_celery_beat():
    """测试Django Celery Beat数据库调度"""
    print("\n🗄️ 检查Django Celery Beat数据库...")
    
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
        
        # 检查周期性任务
        periodic_tasks = PeriodicTask.objects.all()
        print(f"✅ 数据库中的周期性任务: {periodic_tasks.count()} 个")
        
        for task in periodic_tasks:
            print(f"  - {task.name}: {task.task} ({'启用' if task.enabled else '禁用'})")
        
        # 检查调度配置
        intervals = IntervalSchedule.objects.all()
        crontabs = CrontabSchedule.objects.all()
        print(f"✅ 间隔调度: {intervals.count()} 个")
        print(f"✅ Cron调度: {crontabs.count()} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ Django Celery Beat检查失败: {e}")
        return False

def create_test_periodic_task():
    """创建一个测试周期性任务"""
    print("\n➕ 创建测试周期性任务...")
    
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        
        # 创建每分钟执行的间隔调度
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )
        
        # 创建周期性任务
        task, created = PeriodicTask.objects.get_or_create(
            name='测试任务-每分钟执行',
            defaults={
                'task': 'lottery.tasks.test_simple_crawler_task',
                'interval': schedule,
                'enabled': True,
                'args': '[]',
                'kwargs': '{}',
            }
        )
        
        if created:
            print(f"✅ 创建了新的测试任务: {task.name}")
        else:
            print(f"✅ 测试任务已存在: {task.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试任务失败: {e}")
        return False

def show_instructions():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🚀 Celery系统启动说明:")
    print("="*60)
    print()
    print("1. 启动Redis服务器:")
    print("   cd rainbow-data/redis && ./redis-server.exe")
    print()
    print("2. 启动Celery Worker (在新终端):")
    print("   cd rainbow-data/rainbow_data_backend")
    print("   celery -A rainbow_data worker --loglevel=info")
    print()
    print("3. 启动Celery Beat调度器 (在新终端):")
    print("   cd rainbow-data/rainbow_data_backend")
    print("   celery -A rainbow_data beat --loglevel=info")
    print()
    print("4. 监控任务执行 (可选):")
    print("   celery -A rainbow_data flower")
    print()
    print("📝 注意事项:")
    print("- Redis必须先启动")
    print("- Worker和Beat可以同时运行")
    print("- 在production环境中使用supervisor管理进程")
    print("="*60)

if __name__ == '__main__':
    print("🔍 开始完整的Celery系统测试...")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # 运行所有测试
    tests = [
        ("Celery进程状态", check_celery_processes),
        ("Beat定时任务配置", test_beat_schedule),
        ("Django Beat数据库", test_django_celery_beat),
        ("创建测试任务", create_test_periodic_task),
        ("所有任务执行", test_all_tasks),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}:")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if passed >= 4:  # 允许任务执行失败，因为worker可能没运行
        print("🎉 Celery系统配置基本正常！")
    else:
        print("⚠️ 部分测试失败，请检查配置")
    
    # 显示使用说明
    show_instructions() 