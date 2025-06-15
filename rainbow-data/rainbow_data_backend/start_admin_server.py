#!/usr/bin/env python
"""
启动Django Admin后台管理服务器
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 启动彩虹数据Django Admin后台管理系统")
    print("=" * 60)
    
    # 检查虚拟环境
    print("1. 检查环境...")
    venv_path = Path("venv/Scripts/python.exe")
    if venv_path.exists():
        python_cmd = str(venv_path)
        print("   ✓ 使用虚拟环境Python")
    else:
        python_cmd = "python"
        print("   ⚠ 使用系统Python")
    
    # 检查必要文件
    print("2. 检查项目文件...")
    required_files = [
        "manage.py",
        "lottery/admin.py",
        "lottery/models.py",
        "rainbow_data/settings.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} 不存在")
            return
    
    # 应用数据库迁移
    print("3. 应用数据库迁移...")
    try:
        result = subprocess.run(
            [python_cmd, "manage.py", "migrate"],
            capture_output=True,
            text=True,
            check=True
        )
        print("   ✓ 数据库迁移完成")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 数据库迁移失败: {e}")
        return
    
    # 收集静态文件（如果需要）
    print("4. 收集静态文件...")
    try:
        result = subprocess.run(
            [python_cmd, "manage.py", "collectstatic", "--noinput"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ 静态文件收集完成")
        else:
            print("   ⚠ 静态文件收集跳过（开发环境可忽略）")
    except Exception:
        print("   ⚠ 静态文件收集跳过（开发环境可忽略）")
    
    # 显示管理员信息
    print("5. 管理员账户信息:")
    print("   📋 可用管理员账户:")
    print("      • 用户名: admin")
    print("      • 密码: admin123")
    print("      • 或使用已有的超级用户账户")
    
    # 启动服务器
    print("6. 启动Django开发服务器...")
    server_url = "http://127.0.0.1:8001"
    admin_url = f"{server_url}/admin/"
    api_docs_url = f"{server_url}/api/docs/"
    
    print(f"   🌐 服务器地址: {server_url}")
    print(f"   🔧 Admin后台: {admin_url}")
    print(f"   📚 API文档: {api_docs_url}")
    print("")
    print("   💡 提示:")
    print("      • 使用 Ctrl+C 停止服务器")
    print("      • Admin后台可管理所有系统数据")
    print("      • 支持用户管理、数据管理、系统配置等")
    print("")
    
    # 等待一秒后打开浏览器
    print("   ⏳ 3秒后自动打开Admin后台...")
    time.sleep(3)
    
    try:
        webbrowser.open(admin_url)
        print("   ✓ 已打开Admin后台页面")
    except Exception:
        print("   ⚠ 无法自动打开浏览器，请手动访问Admin后台")
    
    print("")
    print("=" * 60)
    
    # 启动Django服务器
    try:
        subprocess.run([python_cmd, "manage.py", "runserver", "8001"])
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
        print("✅ Django Admin后台管理系统已关闭")


if __name__ == '__main__':
    main() 