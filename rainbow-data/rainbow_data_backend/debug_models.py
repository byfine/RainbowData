#!/usr/bin/env python3
"""
调试Django模型的脚本
"""
import os
import django

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')

# 配置Django
django.setup()

from lottery.models import UserProfile
from django.contrib.auth.models import User

def test_userprofile_model():
    """测试UserProfile模型"""
    print("🔍 测试UserProfile模型...")
    
    try:
        # 测试查询所有UserProfile
        profiles = UserProfile.objects.all()
        print(f"✅ UserProfile查询成功，共{profiles.count()}条记录")
        
        # 测试创建一个测试用户
        test_user = User.objects.create_user(
            username='debug_user',
            email='debug@test.com',
            password='testpass123'
        )
        print(f"✅ 创建测试用户成功: {test_user.username}")
        
        # 测试创建UserProfile
        profile = UserProfile.objects.create(
            user=test_user,
            user_type='normal'
        )
        print(f"✅ 创建UserProfile成功: {profile}")
        
        # 清理测试数据
        profile.delete()
        test_user.delete()
        print("✅ 清理测试数据成功")
        
    except Exception as e:
        print(f"❌ UserProfile模型测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_user_model():
    """测试User模型"""
    print("🔍 测试User模型...")
    
    try:
        # 测试查询所有User
        users = User.objects.all()
        print(f"✅ User查询成功，共{users.count()}条记录")
        
        # 查看已有用户
        for user in users:
            print(f"  用户: {user.username} ({user.email})")
            try:
                profile = user.userprofile
                print(f"    扩展信息: {profile.user_type}")
            except Exception as e:
                print(f"    无扩展信息: {e}")
        
    except Exception as e:
        print(f"❌ User模型测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("🌈 Django模型调试")
    print("=" * 50)
    
    test_user_model()
    print()
    test_userprofile_model()
    
    print("=" * 50)
    print("🎉 模型调试完成")
    print("=" * 50) 