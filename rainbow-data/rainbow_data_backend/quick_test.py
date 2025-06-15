#!/usr/bin/env python
"""
快速测试用户统计功能
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

from django.contrib.auth.models import User
from lottery.models import UserAnalysisLog, Prediction, UserProfile

def main():
    print("🔍 用户统计功能快速检查")
    print("=" * 40)
    
    # 检查数据库连接
    user_count = User.objects.count()
    print(f"📊 数据库连接正常，用户数: {user_count}")
    
    # 检查每个用户的数据
    for user in User.objects.all():
        print(f"\n👤 用户: {user.username}")
        
        # 获取用户扩展资料
        try:
            profile = user.userprofile
            print(f"   ✅ 用户扩展资料存在: {profile}")
        except UserProfile.DoesNotExist:
            print(f"   ❌ 用户扩展资料不存在，需要创建")
            profile = UserProfile.objects.create(user=user, user_type='normal')
            print(f"   ✅ 已创建用户扩展资料: {profile}")
        
        # 检查分析日志
        analysis_count = UserAnalysisLog.objects.filter(user_profile=profile).count()
        print(f"   📈 分析次数: {analysis_count}")
        
        if analysis_count > 0:
            latest = UserAnalysisLog.objects.filter(user_profile=profile).latest('created_at')
            print(f"   📅 最新分析: {latest.analysis_type} ({latest.created_at})")
        
        # 检查预测记录
        prediction_count = Prediction.objects.filter(user=profile).count()
        print(f"   🎯 预测次数: {prediction_count}")
        
        if prediction_count > 0:
            latest = Prediction.objects.filter(user=profile).latest('created_at')
            print(f"   📅 最新预测: {latest.algorithm} ({latest.created_at})")
        
        # 计算学习时长
        study_hours = analysis_count * 0.5 + prediction_count * 0.2
        print(f"   ⏰ 学习时长: {study_hours:.1f} 小时")
    
    print("\n" + "=" * 40)
    print("✅ 检查完成！请登录前端查看个人中心统计数据")

if __name__ == '__main__':
    main() 