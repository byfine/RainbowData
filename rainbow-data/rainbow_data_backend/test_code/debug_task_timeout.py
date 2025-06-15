#!/usr/bin/env python
"""
调试任务超时问题
"""

import os
import sys
import django
import time
from pathlib import Path

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

def test_synchronous_task():
    """测试同步任务执行"""
    print("🧪 测试同步任务执行...")
    
    try:
        from lottery.tasks import test_simple_crawler_task
        
        # 直接调用任务函数（同步）
        print("📋 直接调用任务函数...")
        mock_request = type('MockRequest', (), {'id': 'sync-test'})()
        
        # 创建任务实例并调用
        task_instance = test_simple_crawler_task
        result = task_instance.apply(args=(), kwargs={}).result
        print(f"✅ 同步执行成功: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 同步执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_async_task_with_timeout():
    """测试异步任务执行（短超时）"""
    print("\n🧪 测试异步任务执行...")
    
    try:
        from lottery.tasks import test_simple_crawler_task
        
        # 异步调用任务
        print("📋 异步调用任务...")
        result = test_simple_crawler_task.delay()
        print(f"任务ID: {result.id}")
        
        # 短超时测试
        print("等待结果（3秒超时）...")
        task_result = result.get(timeout=3)
        print(f"✅ 异步执行成功: {task_result}")
        return True
        
    except Exception as e:
        print(f"❌ 异步执行失败: {e}")
        
        # 检查任务状态
        try:
            print(f"任务状态: {result.state}")
            if hasattr(result, 'info'):
                print(f"任务信息: {result.info}")
        except:
            pass
        
        return False

def check_worker_logs():
    """检查Worker状态"""
    print("\n🔍 检查Worker状态...")
    
    try:
        from rainbow_data.celery import app
        inspect = app.control.inspect()
        
        # 检查活跃任务
        active = inspect.active()
        if active:
            print("✅ 活跃任务:")
            for worker, tasks in active.items():
                print(f"  Worker {worker}: {len(tasks)} 个任务")
                for task in tasks:
                    print(f"    - {task['name']} ({task['id']})")
        else:
            print("⚠️ 没有活跃任务")
        
        # 检查保留任务
        reserved = inspect.reserved()
        if reserved:
            print("📋 保留任务:")
            for worker, tasks in reserved.items():
                print(f"  Worker {worker}: {len(tasks)} 个任务")
        else:
            print("✅ 没有保留任务")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查Worker失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接性能"""
    print("\n🔍 测试Redis连接性能...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # 测试连接速度
        start_time = time.time()
        result = r.ping()
        ping_time = time.time() - start_time
        
        print(f"✅ Redis Ping: {result} ({ping_time:.3f}s)")
        
        # 测试读写性能
        start_time = time.time()
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        rw_time = time.time() - start_time
        
        print(f"✅ Redis 读写测试: {rw_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis测试失败: {e}")
        return False

def main():
    print("🔍 Celery任务超时调试")
    print("=" * 50)
    
    tests = [
        ("Redis连接性能", test_redis_connection),
        ("Worker状态检查", check_worker_logs),
        ("同步任务执行", test_synchronous_task),
        ("异步任务执行", test_async_task_with_timeout),
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        test_func()
        print("-" * 30)
    
    print("\n💡 调试建议:")
    print("1. 如果同步执行成功但异步失败，可能是Worker通信问题")
    print("2. 如果Redis连接慢，可能是网络或配置问题")
    print("3. 如果有活跃任务卡住，可能是任务代码有问题")
    print("4. 检查Worker终端是否有错误输出")

if __name__ == "__main__":
    main() 