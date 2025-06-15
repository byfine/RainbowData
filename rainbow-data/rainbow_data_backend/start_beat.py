#!/usr/bin/env python
"""
启动Celery Beat定时任务调度器
"""

import os
import sys
import subprocess
from pathlib import Path

# 确保在正确的目录
PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

def main():
    print("🚀 启动Celery Beat定时任务调度器...")
    print("=" * 50)
    
    try:
        # 使用Python模块方式启动Beat
        process = subprocess.Popen([
            sys.executable, "-m", "celery", 
            "-A", "rainbow_data", 
            "beat", 
            "--loglevel=info"
        ], cwd=str(PROJECT_DIR))
        
        print(f"✅ Celery Beat启动成功 (PID: {process.pid})")
        print("📋 配置的定时任务:")
        print("  - 每天21:30: 爬取最新开奖数据")
        print("  - 每天22:00: 更新统计数据")
        print("  - 每周日02:00: 数据质量检查")
        print("  - 每小时: 检查数据源状态")
        print("=" * 50)
        print("💡 按Ctrl+C停止Beat")
        
        # 保持运行
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 停止Celery Beat...")
        process.terminate()
        print("✅ Beat已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 