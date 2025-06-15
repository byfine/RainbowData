#!/usr/bin/env python
"""
Celery配置诊断脚本
"""

import os
import sys
import django
from pathlib import Path

# 添加Django项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

def test_redis_connection():
    """测试Redis连接"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        result = r.ping()
        print(f"✅ Redis连接测试: {result}")
        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

def test_celery_config():
    """测试Celery配置"""
    try:
        from rainbow_data.celery import app
        print(f"✅ Celery app创建成功: {app}")
        print(f"✅ Broker URL: {app.conf.broker_url}")
        print(f"✅ Result backend: {app.conf.result_backend}")
        return True
    except Exception as e:
        print(f"❌ Celery配置失败: {e}")
        return False

def test_django_settings():
    """测试Django设置"""
    try:
        from django.conf import settings
        print(f"✅ CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
        print(f"✅ CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
        print(f"✅ INSTALLED_APPS包含django_celery_beat: {'django_celery_beat' in settings.INSTALLED_APPS}")
        return True
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return False

def test_task_discovery():
    """测试任务发现"""
    try:
        from rainbow_data.celery import app
        tasks = list(app.tasks.keys())
        print(f"✅ 发现的任务数量: {len(tasks)}")
        for task in tasks[:10]:  # 只显示前10个
            print(f"  - {task}")
        if len(tasks) > 10:
            print(f"  ... 还有{len(tasks)-10}个任务")
        return True
    except Exception as e:
        print(f"❌ 任务发现失败: {e}")
        return False

def test_simple_task():
    """测试简单任务执行"""
    try:
        from lottery.tasks import test_simple_crawler_task
        print("✅ 任务导入成功")
        
        # 尝试异步执行
        result = test_simple_crawler_task.delay()
        print(f"✅ 任务提交成功，ID: {result.id}")
        
        # 等待结果（最多10秒）
        try:
            task_result = result.get(timeout=10)
            print(f"✅ 任务执行成功: {task_result}")
            return True
        except Exception as e:
            print(f"⚠️ 任务执行超时或失败: {e}")
            print("任务已提交，但worker可能未运行")
            return False
            
    except Exception as e:
        print(f"❌ 任务测试失败: {e}")
        return False

if __name__ == '__main__':
    print("🔍 开始Celery配置诊断...")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("Redis连接", test_redis_connection),
        ("Django设置", test_django_settings),
        ("Celery配置", test_celery_config),
        ("任务发现", test_task_discovery),
        ("简单任务", test_simple_task),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}:")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！Celery配置正常")
    else:
        print("⚠️ 部分测试失败，请检查配置")
    
    print("\n💡 如果任务测试失败，请在另一个终端运行:")
    print("celery -A rainbow_data worker --loglevel=info") 