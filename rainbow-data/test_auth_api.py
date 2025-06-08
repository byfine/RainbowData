#!/usr/bin/env python3
"""
测试用户认证API的脚本
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_user_registration():
    """测试用户注册"""
    print("🧪 测试用户注册API...")
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "password_confirm": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("✅ 用户注册成功！")
            return response.json()
        else:
            print("❌ 用户注册失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_user_login(username="testuser", password="testpassword123"):
    """测试用户登录"""
    print("🧪 测试用户登录API...")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 用户登录成功！")
            return response.json()
        else:
            print("❌ 用户登录失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_current_user(token):
    """测试获取当前用户信息"""
    print("🧪 测试获取当前用户信息API...")
    
    url = f"{BASE_URL}/auth/me/"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 获取当前用户信息成功！")
            return response.json()
        else:
            print("❌ 获取当前用户信息失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_user_profile(token):
    """测试获取用户资料"""
    print("🧪 测试获取用户资料API...")
    
    url = f"{BASE_URL}/user/profile/"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 获取用户资料成功！")
            return response.json()
        else:
            print("❌ 获取用户资料失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_server_connection():
    """测试服务器连接"""
    print("🧪 测试Django服务器连接...")
    
    try:
        response = requests.get(f"{BASE_URL}/results/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Django服务器连接正常！")
            return True
        else:
            print("❌ Django服务器响应异常")
            return False
            
    except Exception as e:
        print(f"❌ 无法连接到Django服务器: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🌈 彩虹数据 - 用户认证API测试")
    print("=" * 50)
    
    # 1. 测试服务器连接
    if not test_server_connection():
        print("🛑 Django服务器未运行，请先启动服务器")
        exit(1)
    
    print()
    
    # 2. 测试用户注册
    registration_result = test_user_registration()
    print()
    
    # 3. 测试用户登录
    login_result = test_user_login()
    print()
    
    # 如果登录成功，测试需要认证的API
    if login_result and 'data' in login_result and 'token' in login_result['data']:
        token = login_result['data']['token']
        
        # 4. 测试获取当前用户信息
        test_current_user(token)
        print()
        
        # 5. 测试获取用户资料
        test_user_profile(token)
        print()
    
    print("=" * 50)
    print("🎉 用户认证API测试完成！")
    print("=" * 50) 