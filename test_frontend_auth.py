#!/usr/bin/env python3
"""
前端认证功能测试脚本
测试登录、注册、个人中心等功能是否正常工作
"""

import requests
import json
import time

# API配置
API_BASE_URL = 'http://127.0.0.1:8001'
FRONTEND_URL = 'http://localhost:5173'

def test_backend_auth_apis():
    """测试后端认证API"""
    print("🔍 测试后端认证API...")
    
    # 测试用户数据
    test_user = {
        'username': 'testuser_frontend',
        'email': 'testuser_frontend@example.com',
        'first_name': '测试',
        'password': 'TestPass123',
        'password_confirm': 'TestPass123'
    }
    
    try:
        # 1. 测试用户注册
        print("1. 测试用户注册...")
        register_response = requests.post(
            f'{API_BASE_URL}/api/v1/auth/register/',
            json=test_user
        )
        print(f"   注册响应状态: {register_response.status_code}")
        
        if register_response.status_code == 201:
            register_data = register_response.json()
            print(f"   ✅ 注册成功: {register_data['message']}")
            token = register_data['data']['token']
            user_info = register_data['data']['user']
            print(f"   用户信息: {user_info['username']} ({user_info['email']})")
        else:
            print(f"   ❌ 注册失败: {register_response.text}")
            return False
        
        # 2. 测试用户登录
        print("\n2. 测试用户登录...")
        login_response = requests.post(
            f'{API_BASE_URL}/api/v1/auth/login/',
            json={
                'username': test_user['username'],
                'password': test_user['password']
            }
        )
        print(f"   登录响应状态: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"   ✅ 登录成功: {login_data['message']}")
            token = login_data['data']['token']
        else:
            print(f"   ❌ 登录失败: {login_response.text}")
            return False
        
        # 3. 测试获取用户资料
        print("\n3. 测试获取用户资料...")
        headers = {'Authorization': f'Token {token}'}
        profile_response = requests.get(
            f'{API_BASE_URL}/api/v1/user/profile/',
            headers=headers
        )
        print(f"   资料响应状态: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"   ✅ 获取资料成功")
            print(f"   用户信息: {profile_data['data']}")
        else:
            print(f"   ❌ 获取资料失败: {profile_response.text}")
        
        # 4. 测试更新用户资料
        print("\n4. 测试更新用户资料...")
        update_response = requests.put(
            f'{API_BASE_URL}/api/v1/user/profile/',
            headers=headers,
            json={
                'email': 'updated_email@example.com',
                'first_name': '更新的姓名'
            }
        )
        print(f"   更新响应状态: {update_response.status_code}")
        
        if update_response.status_code == 200:
            update_data = update_response.json()
            print(f"   ✅ 更新资料成功")
            print(f"   更新后信息: {update_data['data']}")
        else:
            print(f"   ❌ 更新资料失败: {update_response.text}")
        
        # 5. 测试修改密码
        print("\n5. 测试修改密码...")
        change_password_response = requests.post(
            f'{API_BASE_URL}/api/v1/user/change-password/',
            headers=headers,
            json={
                'old_password': test_user['password'],
                'new_password': 'NewTestPass123'
            }
        )
        print(f"   修改密码响应状态: {change_password_response.status_code}")
        
        if change_password_response.status_code == 200:
            print(f"   ✅ 修改密码成功")
        else:
            print(f"   ❌ 修改密码失败: {change_password_response.text}")
        
        # 6. 测试登出
        print("\n6. 测试用户登出...")
        logout_response = requests.post(
            f'{API_BASE_URL}/api/v1/auth/logout/',
            headers=headers
        )
        print(f"   登出响应状态: {logout_response.status_code}")
        
        if logout_response.status_code == 200:
            print(f"   ✅ 登出成功")
        else:
            print(f"   ❌ 登出失败: {logout_response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保Django服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False

def test_frontend_accessibility():
    """测试前端页面是否可访问"""
    print("\n🌐 测试前端页面可访问性...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ 前端页面可访问: {FRONTEND_URL}")
            return True
        else:
            print(f"   ❌ 前端页面响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 无法连接到前端服务，请确保前端开发服务器正在运行")
        print(f"   请运行: cd rainbow-data/rainbow_data_frontend/rainbow-frontend && npm run dev")
        return False
    except Exception as e:
        print(f"   ❌ 测试前端时出现错误: {str(e)}")
        return False

def print_test_instructions():
    """打印手动测试说明"""
    print("\n📋 前端认证功能手动测试说明:")
    print("=" * 50)
    
    print("\n🌐 1. 访问前端页面:")
    print(f"   在浏览器中打开: {FRONTEND_URL}")
    
    print("\n🔐 2. 测试用户注册:")
    print("   - 点击右上角的'注册'按钮")
    print("   - 填写注册表单:")
    print("     * 用户名: testuser123")
    print("     * 邮箱: test@example.com")
    print("     * 姓名: 测试用户")
    print("     * 密码: TestPass123")
    print("     * 确认密码: TestPass123")
    print("   - 勾选同意协议")
    print("   - 点击'注册'按钮")
    print("   - 应该看到注册成功消息并自动登录")
    
    print("\n🔑 3. 测试用户登录:")
    print("   - 如果已登录，先退出登录")
    print("   - 点击右上角的'登录'按钮")
    print("   - 输入用户名和密码")
    print("   - 点击'登录'按钮")
    print("   - 应该看到登录成功消息")
    
    print("\n👤 4. 测试个人中心:")
    print("   - 登录后，点击右上角用户名下拉菜单")
    print("   - 选择'个人中心'")
    print("   - 查看个人信息展示")
    print("   - 测试编辑个人信息")
    print("   - 测试修改密码功能")
    
    print("\n🚪 5. 测试退出登录:")
    print("   - 点击右上角用户名下拉菜单")
    print("   - 选择'退出登录'")
    print("   - 应该看到退出成功消息")
    print("   - 页面应该回到未登录状态")
    
    print("\n✨ 6. 测试功能集成:")
    print("   - 未登录时点击'个人中心'应该弹出登录对话框")
    print("   - 登录状态在页面刷新后应该保持")
    print("   - 各个页面之间的导航应该正常")
    
    print("\n🎯 预期结果:")
    print("   - 所有表单验证正常工作")
    print("   - API调用成功，显示正确的成功/错误消息")
    print("   - 用户状态正确管理")
    print("   - 界面响应式设计在不同屏幕尺寸下正常")

def main():
    """主测试函数"""
    print("🌈 彩虹数据前端认证功能测试")
    print("=" * 40)
    
    # 测试后端API
    backend_ok = test_backend_auth_apis()
    
    # 测试前端可访问性
    frontend_ok = test_frontend_accessibility()
    
    # 打印测试结果
    print("\n📊 测试结果总结:")
    print("=" * 30)
    print(f"后端认证API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"前端页面访问: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有基础测试通过！")
        print_test_instructions()
    else:
        print("\n⚠️  存在问题，请检查服务状态")
        
        if not backend_ok:
            print("   - 请确保Django后端服务正在运行")
            print("   - 运行: cd rainbow-data/rainbow_data_backend && python manage.py runserver 127.0.0.1:8001")
        
        if not frontend_ok:
            print("   - 请确保前端开发服务器正在运行")
            print("   - 运行: cd rainbow-data/rainbow_data_frontend/rainbow-frontend && npm run dev")

if __name__ == '__main__':
    main() 