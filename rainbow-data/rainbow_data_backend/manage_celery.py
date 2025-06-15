#!/usr/bin/env python
"""
Celery服务管理脚本
简化Celery服务的启动、停止和监控
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path

# 项目配置
PROJECT_DIR = Path(__file__).resolve().parent
REDIS_DIR = PROJECT_DIR.parent / "redis"
REDIS_EXE = REDIS_DIR / "redis-server.exe"
REDIS_CLI = REDIS_DIR / "redis-cli.exe"

# PID文件位置
PID_DIR = PROJECT_DIR / "pids"
PID_DIR.mkdir(exist_ok=True)

REDIS_PID_FILE = PID_DIR / "redis.pid"
WORKER_PID_FILE = PID_DIR / "celery_worker.pid"
BEAT_PID_FILE = PID_DIR / "celery_beat.pid"

class CeleryManager:
    """Celery服务管理器"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        os.chdir(self.project_dir)
    
    def check_redis(self):
        """检查Redis服务状态"""
        try:
            result = subprocess.run(
                [str(REDIS_CLI), "ping"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "PONG" in result.stdout
        except:
            return False
    
    def start_redis(self):
        """启动Redis服务"""
        if self.check_redis():
            print("✅ Redis服务已经在运行")
            return True
        
        print("🚀 启动Redis服务...")
        try:
            # 启动Redis服务器
            process = subprocess.Popen(
                [str(REDIS_EXE)],
                cwd=str(REDIS_DIR),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # 保存PID
            with open(REDIS_PID_FILE, 'w') as f:
                f.write(str(process.pid))
            
            # 等待Redis启动
            for _ in range(10):
                time.sleep(1)
                if self.check_redis():
                    print("✅ Redis服务启动成功")
                    return True
            
            print("❌ Redis服务启动失败")
            return False
            
        except Exception as e:
            print(f"❌ Redis服务启动失败: {e}")
            return False
    
    def stop_redis(self):
        """停止Redis服务"""
        if not self.check_redis():
            print("⚠️ Redis服务未运行")
            return True
        
        print("🛑 停止Redis服务...")
        try:
            # 尝试使用redis-cli停止
            subprocess.run([str(REDIS_CLI), "shutdown"], timeout=5)
            
            # 等待服务停止
            for _ in range(5):
                time.sleep(1)
                if not self.check_redis():
                    print("✅ Redis服务已停止")
                    return True
            
            # 如果redis-cli无法停止，尝试使用PID
            if REDIS_PID_FILE.exists():
                with open(REDIS_PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=5)
                    print("✅ Redis服务已强制停止")
                    return True
                except:
                    pass
            
            print("❌ Redis服务停止失败")
            return False
            
        except Exception as e:
            print(f"❌ Redis服务停止失败: {e}")
            return False
    
    def start_worker(self):
        """启动Celery Worker"""
        print("🚀 启动Celery Worker...")
        try:
            # 启动Worker
            process = subprocess.Popen(
                ["celery", "-A", "rainbow_data", "worker", "--loglevel=info"],
                cwd=str(self.project_dir),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # 保存PID
            with open(WORKER_PID_FILE, 'w') as f:
                f.write(str(process.pid))
            
            print(f"✅ Celery Worker启动成功 (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Celery Worker启动失败: {e}")
            return False
    
    def start_beat(self):
        """启动Celery Beat"""
        print("🚀 启动Celery Beat...")
        try:
            # 启动Beat
            process = subprocess.Popen(
                ["celery", "-A", "rainbow_data", "beat", "--loglevel=info"],
                cwd=str(self.project_dir),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # 保存PID
            with open(BEAT_PID_FILE, 'w') as f:
                f.write(str(process.pid))
            
            print(f"✅ Celery Beat启动成功 (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Celery Beat启动失败: {e}")
            return False
    
    def stop_process(self, pid_file, service_name):
        """停止指定服务"""
        if not pid_file.exists():
            print(f"⚠️ {service_name} PID文件不存在")
            return True
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=10)
            
            pid_file.unlink()
            print(f"✅ {service_name} 已停止")
            return True
            
        except psutil.NoSuchProcess:
            pid_file.unlink()
            print(f"⚠️ {service_name} 进程不存在")
            return True
        except Exception as e:
            print(f"❌ 停止 {service_name} 失败: {e}")
            return False
    
    def stop_worker(self):
        """停止Celery Worker"""
        print("🛑 停止Celery Worker...")
        return self.stop_process(WORKER_PID_FILE, "Celery Worker")
    
    def stop_beat(self):
        """停止Celery Beat"""
        print("🛑 停止Celery Beat...")
        return self.stop_process(BEAT_PID_FILE, "Celery Beat")
    
    def status(self):
        """检查所有服务状态"""
        print("📊 服务状态:")
        print("-" * 40)
        
        # 检查Redis
        redis_status = "✅ 运行中" if self.check_redis() else "❌ 停止"
        print(f"Redis:        {redis_status}")
        
        # 检查Worker
        worker_status = "❌ 停止"
        if WORKER_PID_FILE.exists():
            try:
                with open(WORKER_PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                if psutil.pid_exists(pid):
                    worker_status = f"✅ 运行中 (PID: {pid})"
            except:
                pass
        print(f"Celery Worker: {worker_status}")
        
        # 检查Beat
        beat_status = "❌ 停止"
        if BEAT_PID_FILE.exists():
            try:
                with open(BEAT_PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                if psutil.pid_exists(pid):
                    beat_status = f"✅ 运行中 (PID: {pid})"
            except:
                pass
        print(f"Celery Beat:   {beat_status}")
    
    def start_all(self):
        """启动所有服务"""
        print("🚀 启动所有Celery服务...")
        print("=" * 50)
        
        # 启动Redis
        if not self.start_redis():
            print("❌ Redis启动失败，停止启动流程")
            return False
        
        # 启动Worker
        if not self.start_worker():
            print("❌ Worker启动失败")
            return False
        
        # 启动Beat
        if not self.start_beat():
            print("❌ Beat启动失败")
            return False
        
        print("=" * 50)
        print("🎉 所有服务启动成功！")
        return True
    
    def stop_all(self):
        """停止所有服务"""
        print("🛑 停止所有Celery服务...")
        print("=" * 50)
        
        # 停止Beat
        self.stop_beat()
        
        # 停止Worker
        self.stop_worker()
        
        # 停止Redis
        self.stop_redis()
        
        print("=" * 50)
        print("✅ 所有服务已停止")
    
    def restart_all(self):
        """重启所有服务"""
        print("🔄 重启所有Celery服务...")
        self.stop_all()
        time.sleep(2)
        self.start_all()

def main():
    """主函数"""
    manager = CeleryManager()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python manage_celery.py start     # 启动所有服务")
        print("  python manage_celery.py stop      # 停止所有服务")
        print("  python manage_celery.py restart   # 重启所有服务")
        print("  python manage_celery.py status    # 检查服务状态")
        print("  python manage_celery.py redis     # 只启动Redis")
        print("  python manage_celery.py worker    # 只启动Worker")
        print("  python manage_celery.py beat      # 只启动Beat")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        manager.start_all()
    elif command == "stop":
        manager.stop_all()
    elif command == "restart":
        manager.restart_all()
    elif command == "status":
        manager.status()
    elif command == "redis":
        manager.start_redis()
    elif command == "worker":
        if not manager.check_redis():
            print("❌ Redis未运行，请先启动Redis")
            return
        manager.start_worker()
    elif command == "beat":
        if not manager.check_redis():
            print("❌ Redis未运行，请先启动Redis")
            return
        manager.start_beat()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main() 