#!/usr/bin/env python
"""
简化的Celery启动脚本
直接使用Python模块启动Celery服务
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 确保在正确的目录
PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

# 添加项目到Python路径
sys.path.insert(0, str(PROJECT_DIR))

def start_redis():
    """启动Redis服务"""
    redis_dir = PROJECT_DIR.parent / "redis"
    redis_exe = redis_dir / "redis-server.exe"
    redis_cli = redis_dir / "redis-cli.exe"
    
    # 检查Redis是否已经运行
    try:
        result = subprocess.run([str(redis_cli), "ping"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis服务已经在运行")
            return True
    except:
        pass
    
    print("🚀 启动Redis服务...")
    try:
        # 启动Redis
        process = subprocess.Popen(
            [str(redis_exe)],
            cwd=str(redis_dir),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # 等待启动
        for _ in range(10):
            time.sleep(1)
            try:
                result = subprocess.run([str(redis_cli), "ping"], capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and "PONG" in result.stdout:
                    print("✅ Redis服务启动成功")
                    return True
            except:
                continue
        
        print("❌ Redis服务启动失败")
        return False
        
    except Exception as e:
        print(f"❌ Redis服务启动失败: {e}")
        return False

def start_worker():
    """启动Celery Worker"""
    print("🚀 启动Celery Worker...")
    try:
        # 使用Python模块方式启动
        process = subprocess.Popen([
            sys.executable, "-m", "celery", 
            "-A", "rainbow_data", 
            "worker", 
            "--loglevel=info"
        ], cwd=str(PROJECT_DIR))
        
        print(f"✅ Celery Worker启动成功 (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Celery Worker启动失败: {e}")
        return None

def start_beat():
    """启动Celery Beat"""
    print("🚀 启动Celery Beat...")
    try:
        # 使用Python模块方式启动
        process = subprocess.Popen([
            sys.executable, "-m", "celery", 
            "-A", "rainbow_data", 
            "beat", 
            "--loglevel=info"
        ], cwd=str(PROJECT_DIR))
        
        print(f"✅ Celery Beat启动成功 (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Celery Beat启动失败: {e}")
        return None

def test_celery():
    """测试Celery功能"""
    print("🧪 测试Celery功能...")
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
        
        import django
        django.setup()
        
        from lottery.tasks import test_simple_crawler_task
        
        # 测试任务
        result = test_simple_crawler_task.delay()
        print(f"任务提交成功，ID: {result.id}")
        
        # 等待结果
        task_result = result.get(timeout=10)
        print(f"✅ 任务执行成功: {task_result}")
        return True
        
    except Exception as e:
        print(f"❌ Celery功能测试失败: {e}")
        return False

def main():
    print("🚀 启动简化Celery系统...")
    print("=" * 50)
    
    # 1. 启动Redis
    if not start_redis():
        return
    
    # 2. 启动Worker
    worker_process = start_worker()
    if not worker_process:
        return
    
    # 等待Worker启动
    print("⏳ 等待Worker启动...")
    time.sleep(5)
    
    # 3. 测试Celery功能
    if test_celery():
        print("🎉 Celery系统启动成功！")
    else:
        print("⚠️ Celery功能测试失败，但Worker已启动")
    
    print("=" * 50)
    print("📝 现在可以:")
    print("1. 在另一个终端启动Beat: python -m celery -A rainbow_data beat --loglevel=info")
    print("2. 监控任务: python test_celery_full.py")
    print("3. 按Ctrl+C停止Worker")
    
    try:
        # 保持Worker运行
        worker_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 停止Worker...")
        worker_process.terminate()
        print("✅ Worker已停止")

if __name__ == "__main__":
    main() 