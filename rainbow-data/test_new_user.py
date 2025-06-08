#!/usr/bin/env python3
"""
测试新用户注册的脚本
"""
import requests
import json
import random

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_new_user_registration():
    """测试新用户注册"""
    # 生成随机用户名避免冲突
    random_num = random.randint(1000, 9999)
    username = f"newuser{random_num}"
    email = f"newuser{random_num}@example.com"
    
    print(f"🧪 测试新用户注册: {username}")
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": username,
        "email": email,
        "password": "newpassword123",
        "password_confirm": "newpassword123",
        "first_name": "New",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("✅ 新用户注册成功！")
            return response.json()
        else:
            print("❌ 新用户注册失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_change_password(token):
    """测试修改密码"""
    print("🧪 测试修改密码API...")
    
    url = f"{BASE_URL}/user/change-password/"
    headers = {
        "Authorization": f"Token {token}"
    }
    data = {
        "old_password": "newpassword123",
        "new_password": "newpassword456",
        "new_password_confirm": "newpassword456"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 修改密码成功！")
            return True
        else:
            print("❌ 修改密码失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🌈 彩虹数据 - 新用户注册测试")
    print("=" * 50)
    
    # 测试新用户注册
    registration_result = test_new_user_registration()
    
    if registration_result and 'data' in registration_result and 'token' in registration_result['data']:
        token = registration_result['data']['token']
        print()
        
        # 测试修改密码
        test_change_password(token)
    
    print("=" * 50)
    print("🎉 新用户注册测试完成！")
    print("=" * 50) 