#!/usr/bin/env python
"""
修复Worker问题并重启Celery系统
"""

import os
import sys
import django
import subprocess
import time
from pathlib import Path

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

def clear_stuck_tasks():
    """清理卡住的任务"""
    print("🧹 清理卡住的任务...")
    
    try:
        from rainbow_data.celery import app
        
        # 清理保留任务
        inspect = app.control.inspect()
        reserved = inspect.reserved()
        
        if reserved:
            for worker, tasks in reserved.items():
                print(f"清理Worker {worker} 的 {len(tasks)} 个保留任务")
                for task in tasks:
                    print(f"  - 撤销任务: {task['id']}")
                    app.control.revoke(task['id'], terminate=True)
        
        # 清理活跃任务
        active = inspect.active()
        if active:
            for worker, tasks in active.items():
                print(f"清理Worker {worker} 的 {len(tasks)} 个活跃任务")
                for task in tasks:
                    print(f"  - 撤销任务: {task['id']}")
                    app.control.revoke(task['id'], terminate=True)
        
        print("✅ 任务清理完成")
        return True
        
    except Exception as e:
        print(f"❌ 任务清理失败: {e}")
        return False

def flush_redis():
    """清空Redis队列"""
    print("\n🗑️ 清空Redis任务队列...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # 获取所有以celery开头的键
        keys = r.keys('celery*')
        if keys:
            r.delete(*keys)
            print(f"✅ 删除了 {len(keys)} 个Celery相关键")
        else:
            print("✅ Redis队列已经是空的")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis清理失败: {e}")
        return False

def test_simple_task():
    """测试简单任务"""
    print("\n🧪 测试简单任务执行...")
    
    try:
        from lottery.tasks import test_simple_crawler_task
        
        result = test_simple_crawler_task.delay()
        print(f"任务ID: {result.id}")
        
        # 较短的超时时间
        task_result = result.get(timeout=5)
        print(f"✅ 任务执行成功: {task_result}")
        return True
        
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        print(f"任务状态: {result.state}")
        return False

def restart_worker():
    """重启Worker（通过控制命令）"""
    print("\n🔄 重启Worker...")
    
    try:
        from rainbow_data.celery import app
        
        # 停止所有worker
        app.control.broadcast('shutdown')
        print("📤 发送Worker停止信号")
        
        time.sleep(2)
        
        # 检查是否还有活跃的worker
        inspect = app.control.inspect()
        stats = inspect.stats()
        if stats:
            print("⚠️ 还有活跃的Worker，强制停止")
        else:
            print("✅ 所有Worker已停止")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker重启失败: {e}")
        return False

def check_celery_config():
    """检查Celery配置"""
    print("\n🔍 检查Celery配置...")
    
    try:
        from rainbow_data.celery import app
        from django.conf import settings
        
        print(f"✅ Broker URL: {app.conf.broker_url}")
        print(f"✅ Result Backend: {app.conf.result_backend}")
        print(f"✅ Task Serializer: {app.conf.task_serializer}")
        print(f"✅ Accept Content: {app.conf.accept_content}")
        
        # 检查任务路由
        if hasattr(app.conf, 'task_routes'):
            print(f"✅ Task Routes: {app.conf.task_routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def main():
    print("🔧 修复Celery Worker问题")
    print("=" * 50)
    
    steps = [
        ("检查Celery配置", check_celery_config),
        ("清理卡住的任务", clear_stuck_tasks),
        ("清空Redis队列", flush_redis),
        ("重启Worker", restart_worker),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}:")
        step_func()
        print("-" * 30)
    
    print("\n💡 修复完成！现在请：")
    print("1. 手动重启Worker: python -m celery -A rainbow_data worker --loglevel=info")
    print("2. 等待几秒后测试: python debug_task_timeout.py")
    print("3. 如果还有问题，检查Worker终端输出")

if __name__ == "__main__":
    main() 