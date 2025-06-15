#!/usr/bin/env python
"""
快速检查Celery系统状态
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

def check_redis():
    """检查Redis连接"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        result = r.ping()
        print(f"✅ Redis状态: 正常运行 ({result})")
        return True
    except Exception as e:
        print(f"❌ Redis状态: 连接失败 ({e})")
        return False

def check_celery_workers():
    """检查Celery Worker状态"""
    try:
        from rainbow_data.celery import app
        inspect = app.control.inspect()
        
        # 检查活跃worker
        active = inspect.active_queues()
        if active:
            print(f"✅ Celery Worker: {len(active)} 个活跃")
            for worker_name in active.keys():
                print(f"  - {worker_name}")
        else:
            print("❌ Celery Worker: 没有活跃的Worker")
        
        return bool(active)
    except Exception as e:
        print(f"❌ Celery Worker检查失败: {e}")
        return False

def check_celery_beat():
    """检查Celery Beat配置"""
    try:
        from rainbow_data.celery import app
        schedule = app.conf.beat_schedule
        print(f"✅ Celery Beat配置: {len(schedule)} 个定时任务")
        for task_name in schedule.keys():
            print(f"  - {task_name}")
        return True
    except Exception as e:
        print(f"❌ Celery Beat检查失败: {e}")
        return False

def test_simple_task():
    """测试简单任务"""
    try:
        from lottery.tasks import test_simple_crawler_task
        
        print("🧪 测试任务执行...")
        result = test_simple_crawler_task.delay()
        task_result = result.get(timeout=10)
        print(f"✅ 任务执行成功: {task_result['message']}")
        return True
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        return False

def main():
    print("🔍 Celery系统状态检查")
    print("=" * 40)
    
    checks = [
        ("Redis连接", check_redis),
        ("Celery Worker", check_celery_workers),
        ("Celery Beat配置", check_celery_beat),
        ("任务执行测试", test_simple_task),
    ]
    
    passed = 0
    for name, check_func in checks:
        print(f"\n📋 检查 {name}:")
        if check_func():
            passed += 1
        print("-" * 20)
    
    print(f"\n📊 检查结果: {passed}/{len(checks)} 通过")
    
    if passed == len(checks):
        print("🎉 Celery系统运行正常！")
    elif passed >= 3:
        print("⚠️ Celery系统基本正常，部分功能可能需要调试")
    else:
        print("❌ Celery系统存在问题，请检查配置")

if __name__ == "__main__":
    main() 