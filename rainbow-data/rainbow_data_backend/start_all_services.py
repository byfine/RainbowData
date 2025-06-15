#!/usr/bin/env python
"""
启动所有必需的服务（Redis、Celery Worker、Django）
"""
import subprocess
import sys
import time
import os

def run_command(cmd, description, background=False):
    """运行命令"""
    print(f"🚀 {description}...")
    try:
        if background:
            process = subprocess.Popen(cmd, shell=True)
            print(f"  ✅ 后台启动成功 (PID: {process.pid})")
            return process
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ 成功")
                if result.stdout.strip():
                    print(f"  输出: {result.stdout.strip()}")
            else:
                print(f"  ❌ 失败: {result.stderr.strip()}")
            return result
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return None

def main():
    print("🔧 启动彩虹数据项目所有服务")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('manage.py'):
        print("❌ 请在rainbow_data_backend目录下运行此脚本")
        sys.exit(1)
    
    # 1. 检查Redis连接
    print("\n1. 检查Redis服务...")
    redis_check = run_command(
        'python -c "import redis; r=redis.Redis(); print(\'Redis状态:\', \'连接正常\' if r.ping() else \'连接失败\')"',
        "检查Redis连接"
    )
    
    # 2. 启动Celery Worker
    print("\n2. 启动Celery Worker...")
    celery_cmd = "..\\venv\\Scripts\\celery.exe -A rainbow_data worker --loglevel=info --concurrency=1"
    celery_process = run_command(celery_cmd, "启动Celery Worker", background=True)
    
    # 等待Celery启动
    print("  等待Celery Worker启动...")
    time.sleep(3)
    
    # 3. 测试简单任务
    print("\n3. 测试Celery任务...")
    test_cmd = "python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings'); import django; django.setup(); from lottery.tasks import crawl_latest_data; print('任务模块导入成功')\""
    run_command(test_cmd, "测试任务导入")
    
    print("\n🎉 服务启动完成！")
    print("=" * 50)
    print("现在你可以运行 test_celery_simple.py 来测试异步任务")

if __name__ == "__main__":
    main() 