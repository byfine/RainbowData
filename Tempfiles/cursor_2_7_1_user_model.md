# 2.7 user model
_Exported on 6/8/2025 at 18:29:38 GMT+8 from Cursor (1.0.0)_

---

**User**

继续2.2 用户认证系统的开发

---

**Cursor**

好的，我来继续开发2.2用户认证系统。让我先检查当前的项目状态，然后实现缺失的功能。

现在让我检查当前的模型和API结构：

现在让我检查当前的views和序列化器：

现在让我检查序列化器：

现在让我检查URL配置：

现在我了解了当前的项目状态。让我开始实现用户认证系统的缺失功能。我将按照RD2.md的任务清单来实现：

1. 首先实现用户注册和登录的API接口
2. 然后实现JWT Token认证
3. 最后创建前端认证页面

让我开始实现：

```python
# ... existing code ...

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import LotteryResult, Statistics, Prediction, UserAnalysisLog, DataSource, CrawlLog, UserProfile

# ... existing serializers ...

class UserSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login', 'profile']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_profile(self, obj):
        """获取用户扩展信息"""
        try:
            profile = obj.userprofile
            return {
                'user_type': profile.get_user_type_display(),
                'avatar': profile.avatar,
                'phone': profile.phone,
                'total_analysis_count': profile.total_analysis_count,
                'total_prediction_count': profile.total_prediction_count,
            }
        except UserProfile.DoesNotExist:
            return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        """验证注册数据"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('两次输入的密码不一致')
        
        # 检查用户名是否已存在
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('用户名已存在')
        
        # 检查邮箱是否已存在
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('邮箱已被注册')
        
        return data
    
    def create(self, validated_data):
        """创建用户"""
        # 移除确认密码字段
        validated_data.pop('password_confirm')
        
        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # 创建用户扩展信息
        UserProfile.objects.create(
            user=user,
            user_type='normal'
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        """验证登录信息"""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # 支持用户名或邮箱登录
            if '@' in username:
                # 邮箱登录
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    raise serializers.ValidationError('邮箱或密码错误')
            
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('用户名/邮箱或密码错误')
            
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')
            
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError('必须提供用户名和密码')


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(min_length=8, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        """验证密码修改数据"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError('两次输入的新密码不一致')
        
        return data
    
    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('当前密码错误')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """用户扩展信息序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'user_type', 'user_type_display', 'avatar', 'phone',
            'total_analysis_count', 'total_prediction_count',
            'last_login_ip', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'username', 'email', 'user_type', 'user_type_display',
            'total_analysis_count', 'total_prediction_count',
            'last_login_ip', 'created_at', 'updated_at'
        ]
    
    def update(self, instance, validated_data):
        """更新用户信息"""
        # 更新User模型字段
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
        
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # 更新UserProfile字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
```

现在创建用户认证的视图：

```python
# ... existing code ...

from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Max, Min, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import LotteryResult, Statistics, Prediction, UserAnalysisLog, UserProfile
from .serializers import (
    LotteryResultSerializer, LotteryResultCreateSerializer,
    StatisticsSerializer, PredictionSerializer, PredictionCreateSerializer,
    UserAnalysisLogSerializer, UserSerializer, UserRegistrationSerializer,
    UserLoginSerializer, ChangePasswordSerializer, UserProfileSerializer
)

# ... existing viewsets ...

class UserRegistrationView(APIView):
    """用户注册API视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """用户注册"""
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                # 生成Token
                token, created = Token.objects.get_or_create(user=user)
                
                # 返回用户信息和Token
                user_serializer = UserSerializer(user)
                
                return Response({
                    'code': 201,
                    'message': '注册成功',
                    'data': {
                        'user': user_serializer.data,
                        'token': token.key
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'code': 400,
                    'message': '注册失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    """用户登录API视图"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """用户登录"""
        try:
            serializer = UserLoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # 更新最后登录时间
                user.last_login = timezone.now()
                user.save()
                
                # 更新用户扩展信息中的IP地址
                try:
                    profile = user.userprofile
                    # 获取客户端IP地址
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    profile.last_login_ip = ip
                    profile.save()
                except UserProfile.DoesNotExist:
                    # 如果用户扩展信息不存在，创建一个
                    UserProfile.objects.create(
                        user=user,
                        user_type='normal',
                        last_login_ip=request.META.get('REMOTE_ADDR')
                    )
                
                # 获取或创建Token
                token, created = Token.objects.get_or_create(user=user)
                
                # 返回用户信息和Token
                user_serializer = UserSerializer(user)
                
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'user': user_serializer.data,
                        'token': token.key
                    }
                })
            else:
                return Response({
                    'code': 400,
                    'message': '登录失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogoutView(APIView):
    """用户登出API视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """用户登出"""
        try:
            # 删除用户的Token
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            
            return Response({
                'code': 200,
                'message': '登出成功',
                'data': None
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """用户资料API视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户资料"""
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'user_type': 'normal'}
            )
            serializer = UserProfileSerializer(profile)
            
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """更新用户资料"""
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'user_type': 'normal'}
            )
            
            serializer = UserProfileSerializer(
                profile, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'message': '更新成功',
                    'data': serializer.data
                })
            else:
                return Response({
                    'code': 400,
                    'message': '更新失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    """修改密码API视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """修改密码"""
        try:
            serializer = ChangePasswordSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                user = request.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # 删除旧的Token，强制重新登录
                try:
                    token = Token.objects.get(user=user)
                    token.delete()
                except Token.DoesNotExist:
                    pass
                
                return Response({
                    'code': 200,
                    'message': '密码修改成功，请重新登录',
                    'data': None
                })
            else:
                return Response({
                    'code': 400,
                    'message': '密码修改失败',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CurrentUserView(APIView):
    """当前用户信息API视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前登录用户信息"""
        try:
            serializer = UserSerializer(request.user)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

现在更新URL配置以包含新的认证端点：

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from . import views

# 创建DRF路由器
router = DefaultRouter()
router.register(r'results', views.LotteryResultViewSet, basename='lotteryresult')
router.register(r'statistics', views.StatisticsViewSet, basename='statistics')
router.register(r'predictions', views.PredictionViewSet, basename='prediction')
router.register(r'logs', views.UserAnalysisLogViewSet, basename='useranalysislog')

# 应用的URL模式
app_name = 'lottery'

urlpatterns = [
    # DRF路由器生成的API端点
    path('api/v1/', include(router.urls)),
    
    # 用户认证API端点
    path('api/v1/auth/register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('api/v1/auth/login/', views.UserLoginView.as_view(), name='user_login'),
    path('api/v1/auth/logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('api/v1/auth/me/', views.CurrentUserView.as_view(), name='current_user'),
    path('api/v1/user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('api/v1/user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # API文档端点
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='lottery:schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='lottery:schema'), name='redoc'),
    
    # 额外的自定义端点（如果需要）
    # path('api/v1/health/', views.health_check, name='health_check'),
]
```

现在让我们测试后端的认证API是否正常工作：

需要激活虚拟环境。让我激活虚拟环境并检查：

好的，检查通过。现在让我启动Django服务器来测试认证API：

现在让我们测试用户注册API：

看起来curl命令有问题。让我创建一个简单的Python脚本来测试API：

```python
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
```

现在运行测试脚本：

看起来有数据库结构问题。需要生成新的迁移文件并应用迁移。让我检查数据库迁移状态：

迁移都已应用。让我检查UserProfile模型的实际数据库结构：

让我直接检查UserProfile表的结构。问题可能是UserProfile模型的user字段名在数据库中是user_id，但我们的代码中使用的是user。让我检查并修复这个问题：

让我查看最近的迁移文件来了解表结构：

问题可能在于Django ORM的字段映射。让我创建一个简单的测试脚本来检查具体错误：

```python
#!/usr/bin/env python3
"""
调试Django模型的脚本
"""
import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.append('rainbow_data_backend')

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
            except:
                print(f"    无扩展信息")
        
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
```

看起来仍然在Django shell中。让我退出并重新运行：

现在运行调试脚本：

让我修复调试脚本的路径问题，直接在Django项目目录内创建：

```python
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
```

现在我明白问题了！数据库中的`user_profiles`表缺少`user_id`字段。这意味着之前的迁移没有正确创建字段。让我检查实际的表结构，然后创建一个修复迁移：



现在编辑这个迁移文件来添加缺失的user字段：

```python
# Generated by Django 4.2.22 on 2025-06-08 10:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lottery', '0004_add_crawler_models'),
    ]

    operations = [
        # 添加UserProfile表的user字段
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='关联用户',
                default=1  # 临时默认值，稍后会移除
            ),
            preserve_default=False,
        ),
    ]
```

现在应用这个迁移：

现在再次测试模型：

好的，现在UserProfile模型可以正常查询了，只是测试用户名重复了。让我修改调试脚本使用不同的用户名，然后测试认证API：

太好了！用户认证API现在完全正常工作了！🎉 让我测试一个新用户的注册：

```python
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
```

完美！🎉 现在让我们创建前端的认证页面。首先检查前端项目结构：

感谢您的总结！看起来2.2用户认证系统的后端部分已经完全开发完成并测试通过了。让我继续开发前端认证页面部分。

现在我看到项目已经有了完整的前端Vue.js应用和后端Django认证系统。我需要在现有的前端基础上添加用户认证功能。让我先检查是否已经有认证相关的组件：

我看到前端还没有认证相关的组件。现在我需要创建登录和注册组件，并修改主应用以支持用户认证功能。让我开始创建这些组件：

```vue
<template>
  <div class="login-container">
    <!-- 登录表单卡片 -->
    <el-card class="login-card" shadow="always">
      <template #header>
        <div class="card-header">
          <span class="header-icon">🔐</span>
          <span class="header-title">用户登录</span>
        </div>
      </template>
      
      <el-form 
        :model="loginForm" 
        :rules="loginRules" 
        ref="loginFormRef"
        label-width="80px"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="loading"
            style="width: 100%"
            size="large"
          >
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="login-footer">
            <span>还没有账户？</span>
            <el-button type="text" @click="$emit('switch-to-register')">
              立即注册
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['login-success', 'switch-to-register'])

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const loginFormRef = ref()

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 表单验证
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // 调用登录API
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login/`, {
      username: loginForm.username,
      password: loginForm.password
    })
    
    if (response.data.code === 200) {
      // 登录成功
      const { user, token } = response.data.data
      
      // 保存用户信息和Token到localStorage
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', token)
      
      // 设置axios默认请求头
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
      
      ElMessage.success('登录成功！')
      
      // 触发登录成功事件
      emit('login-success', { user, token })
      
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
    
  } catch (error) {
    console.error('登录失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        // 显示字段验证错误
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '登录失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (loginFormRef.value) {
    loginFormRef.value.resetFields()
  }
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.header-icon {
  font-size: 24px;
  margin-right: 8px;
}

.header-title {
  font-family: 'Microsoft YaHei', sans-serif;
}

.login-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.login-footer .el-button {
  padding: 0;
  margin-left: 5px;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }
  
  .login-card {
    margin: 0;
  }
}
</style>
```

```vue
<template>
  <div class="register-container">
    <!-- 注册表单卡片 -->
    <el-card class="register-card" shadow="always">
      <template #header>
        <div class="card-header">
          <span class="header-icon">📝</span>
          <span class="header-title">用户注册</span>
        </div>
      </template>
      
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef"
        label-width="100px"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20个字符）"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱地址"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="first_name">
          <el-input
            v-model="registerForm.first_name"
            placeholder="请输入真实姓名（可选）"
            prefix-icon="Avatar"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少8个字符）"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="password_confirm">
          <el-input
            v-model="registerForm.password_confirm"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="agreeTerms">
            我已阅读并同意
            <el-button type="text" @click="showTermsDialog = true">
              《用户协议》
            </el-button>
            和
            <el-button type="text" @click="showPrivacyDialog = true">
              《隐私政策》
            </el-button>
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister" 
            :loading="loading"
            :disabled="!agreeTerms"
            style="width: 100%"
            size="large"
          >
            <span v-if="!loading">注册</span>
            <span v-else>注册中...</span>
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="register-footer">
            <span>已有账户？</span>
            <el-button type="text" @click="$emit('switch-to-login')">
              立即登录
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="showTermsDialog"
      title="用户协议"
      width="80%"
      max-width="600px"
    >
      <div class="terms-content">
        <h3>彩虹数据学习平台用户协议</h3>
        <p><strong>1. 平台性质</strong></p>
        <p>本平台是一个专注于数据分析技术学习的教育平台，通过双色球历史数据进行统计分析实践。</p>
        
        <p><strong>2. 使用目的</strong></p>
        <p>用户使用本平台仅限于学习数据分析技术，不得用于任何商业或投注目的。</p>
        
        <p><strong>3. 免责声明</strong></p>
        <p>平台提供的所有预测功能纯属娱乐和学习用途，不构成任何投注建议。彩票开奖结果完全随机，历史数据无法预测未来结果。</p>
        
        <p><strong>4. 用户责任</strong></p>
        <p>用户应理性对待彩票，适度娱乐，不得将平台预测结果作为投注依据。</p>
        
        <p><strong>5. 数据安全</strong></p>
        <p>我们承诺保护用户隐私，不会泄露用户个人信息。</p>
      </div>
      <template #footer>
        <el-button @click="showTermsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="showPrivacyDialog"
      title="隐私政策"
      width="80%"
      max-width="600px"
    >
      <div class="privacy-content">
        <h3>隐私政策</h3>
        <p><strong>1. 信息收集</strong></p>
        <p>我们仅收集用户注册时提供的基本信息（用户名、邮箱、姓名）用于账户管理。</p>
        
        <p><strong>2. 信息使用</strong></p>
        <p>收集的信息仅用于：</p>
        <ul>
          <li>提供平台服务</li>
          <li>用户身份验证</li>
          <li>学习记录统计</li>
        </ul>
        
        <p><strong>3. 信息保护</strong></p>
        <p>我们采用适当的技术和管理措施保护用户信息安全，不会向第三方泄露用户个人信息。</p>
        
        <p><strong>4. Cookie使用</strong></p>
        <p>我们使用Cookie来改善用户体验，用户可以通过浏览器设置管理Cookie。</p>
        
        <p><strong>5. 联系我们</strong></p>
        <p>如有隐私相关问题，请通过平台内联系方式与我们联系。</p>
      </div>
      <template #footer>
        <el-button @click="showPrivacyDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['register-success', 'switch-to-login'])

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const registerFormRef = ref()
const agreeTerms = ref(false)
const showTermsDialog = ref(false)
const showPrivacyDialog = ref(false)

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  first_name: '',
  password: '',
  password_confirm: ''
})

// 自定义验证函数
const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateUsername = (rule, value, callback) => {
  if (!/^[a-zA-Z0-9_]{3,20}$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线，长度3-20个字符'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUsername, trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, message: '密码必须包含大小写字母和数字', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  if (!agreeTerms.value) {
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }
  
  try {
    // 表单验证
    await registerFormRef.value.validate()
    
    loading.value = true
    
    // 调用注册API
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/register/`, {
      username: registerForm.username,
      email: registerForm.email,
      first_name: registerForm.first_name,
      password: registerForm.password,
      password_confirm: registerForm.password_confirm
    })
    
    if (response.data.code === 201) {
      // 注册成功
      const { user, token } = response.data.data
      
      ElMessage.success('注册成功！欢迎加入彩虹数据学习平台！')
      
      // 触发注册成功事件
      emit('register-success', { user, token })
      
    } else {
      ElMessage.error(response.data.message || '注册失败')
    }
    
  } catch (error) {
    console.error('注册失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        // 显示字段验证错误
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '注册失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (registerFormRef.value) {
    registerFormRef.value.resetFields()
  }
  agreeTerms.value = false
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 500px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.header-icon {
  font-size: 24px;
  margin-right: 8px;
}

.header-title {
  font-family: 'Microsoft YaHei', sans-serif;
}

.register-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-footer .el-button {
  padding: 0;
  margin-left: 5px;
  font-size: 14px;
}

.terms-content,
.privacy-content {
  line-height: 1.6;
  color: #333;
}

.terms-content h3,
.privacy-content h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.terms-content p,
.privacy-content p {
  margin-bottom: 15px;
}

.terms-content ul,
.privacy-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.terms-content li,
.privacy-content li {
  margin-bottom: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-container {
    padding: 10px;
  }
  
  .register-card {
    margin: 0;
  }
  
  .el-dialog {
    width: 95% !important;
  }
}
</style>
```

```vue
<template>
  <div class="profile-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">👤</span>
        个人中心
      </h2>
      <p class="page-description">
        管理您的个人信息和账户设置
      </p>
    </div>

    <el-row :gutter="20">
      <!-- 用户信息卡片 -->
      <el-col :xs="24" :md="12">
        <el-card class="profile-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📋</span>
              <span class="header-title">基本信息</span>
              <el-button 
                type="text" 
                @click="editMode = !editMode"
                :icon="editMode ? 'Close' : 'Edit'"
              >
                {{ editMode ? '取消' : '编辑' }}
              </el-button>
            </div>
          </template>
          
          <div v-if="!editMode" class="profile-info">
            <div class="info-item">
              <label>用户名：</label>
              <span>{{ userInfo.username }}</span>
            </div>
            <div class="info-item">
              <label>邮箱：</label>
              <span>{{ userInfo.email }}</span>
            </div>
            <div class="info-item">
              <label>姓名：</label>
              <span>{{ userInfo.first_name || '未设置' }}</span>
            </div>
            <div class="info-item">
              <label>注册时间：</label>
              <span>{{ formatDateTime(userInfo.date_joined) }}</span>
            </div>
            <div class="info-item">
              <label>最后登录：</label>
              <span>{{ formatDateTime(userInfo.last_login) }}</span>
            </div>
          </div>
          
          <el-form 
            v-else
            :model="editForm" 
            :rules="editRules" 
            ref="editFormRef"
            label-width="80px"
          >
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" disabled />
              <div class="form-tip">用户名不可修改</div>
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="editForm.email" />
            </el-form-item>
            
            <el-form-item label="姓名" prop="first_name">
              <el-input v-model="editForm.first_name" placeholder="请输入真实姓名" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="updateLoading">
                保存修改
              </el-button>
              <el-button @click="cancelEdit">
                取消
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 密码修改卡片 -->
      <el-col :xs="24" :md="12">
        <el-card class="password-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">🔒</span>
              <span class="header-title">修改密码</span>
            </div>
          </template>
          
          <el-form 
            :model="passwordForm" 
            :rules="passwordRules" 
            ref="passwordFormRef"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                placeholder="请输入当前密码"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码（至少8个字符）"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 账户统计信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📊</span>
              <span class="header-title">学习统计</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="12" :sm="6" v-for="stat in userStats" :key="stat.key">
              <div class="stat-item">
                <div class="stat-icon">{{ stat.icon }}</div>
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const editMode = ref(false)
const updateLoading = ref(false)
const passwordLoading = ref(false)
const editFormRef = ref()
const passwordFormRef = ref()

// 用户信息
const userInfo = ref({
  username: '',
  email: '',
  first_name: '',
  date_joined: '',
  last_login: ''
})

// 编辑表单
const editForm = reactive({
  username: '',
  email: '',
  first_name: ''
})

// 密码修改表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 用户统计数据
const userStats = ref([
  { key: 'predictions', icon: '🎮', label: '预测次数', value: '0' },
  { key: 'analyses', icon: '📈', label: '分析次数', value: '0' },
  { key: 'login_days', icon: '📅', label: '登录天数', value: '0' },
  { key: 'study_time', icon: '⏰', label: '学习时长', value: '0小时' }
])

// 表单验证规则
const editRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 密码验证函数
const validateNewPassword = (rule, value, callback) => {
  if (value.length < 8) {
    callback(new Error('新密码至少8个字符'))
  } else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
    callback(new Error('密码必须包含大小写字母和数字'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: validateNewPassword, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 方法
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '未知'
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}

const loadUserProfile = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/user/profile/`)
    
    if (response.data.code === 200) {
      userInfo.value = response.data.data
      // 同步到编辑表单
      editForm.username = userInfo.value.username
      editForm.email = userInfo.value.email
      editForm.first_name = userInfo.value.first_name
    } else {
      ElMessage.error('加载用户信息失败')
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败，请检查网络连接')
  }
}

const handleUpdateProfile = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    updateLoading.value = true
    
    const response = await axios.put(`${API_BASE_URL}/api/v1/user/profile/`, {
      email: editForm.email,
      first_name: editForm.first_name
    })
    
    if (response.data.code === 200) {
      userInfo.value = response.data.data
      editMode.value = false
      ElMessage.success('个人信息更新成功！')
    } else {
      ElMessage.error(response.data.message || '更新失败')
    }
    
  } catch (error) {
    console.error('更新个人信息失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '更新失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    updateLoading.value = false
  }
}

const cancelEdit = () => {
  editMode.value = false
  // 恢复原始数据
  editForm.username = userInfo.value.username
  editForm.email = userInfo.value.email
  editForm.first_name = userInfo.value.first_name
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    
    // 确认对话框
    await ElMessageBox.confirm(
      '修改密码后需要重新登录，确定要继续吗？',
      '确认修改密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    passwordLoading.value = true
    
    const response = await axios.post(`${API_BASE_URL}/api/v1/user/change-password/`, {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    
    if (response.data.code === 200) {
      ElMessage.success('密码修改成功！请重新登录。')
      
      // 清除本地存储的用户信息
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      
      // 重置表单
      resetPasswordForm()
      
      // 触发重新登录（这里可以发送事件给父组件）
      setTimeout(() => {
        window.location.reload()
      }, 1500)
      
    } else {
      ElMessage.error(response.data.message || '密码修改失败')
    }
    
  } catch (error) {
    if (error === 'cancel') {
      return // 用户取消操作
    }
    
    console.error('修改密码失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '密码修改失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    passwordLoading.value = false
  }
}

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const loadUserStats = async () => {
  try {
    // 这里可以调用统计API，暂时使用模拟数据
    // const response = await axios.get(`${API_BASE_URL}/api/v1/user/stats/`)
    
    // 模拟统计数据
    userStats.value = [
      { key: 'predictions', icon: '🎮', label: '预测次数', value: '12' },
      { key: 'analyses', icon: '📈', label: '分析次数', value: '8' },
      { key: 'login_days', icon: '📅', label: '登录天数', value: '5' },
      { key: 'study_time', icon: '⏰', label: '学习时长', value: '2.5小时' }
    ]
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserProfile()
  loadUserStats()
})
</script>

<style scoped>
.profile-container {
  max-width: 100%;
}

/* 页面头部样式 */
.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  color: #2c3e50;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon {
  font-size: 32px;
  margin-right: 10px;
}

.page-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* 卡片样式 */
.profile-card,
.password-card,
.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
}

.header-icon {
  font-size: 20px;
  margin-right: 8px;
}

.header-title {
  flex: 1;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 用户信息展示样式 */
.profile-info {
  line-height: 1.8;
}

.info-item {
  display: flex;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  font-weight: bold;
  color: #666;
  width: 100px;
  flex-shrink: 0;
}

.info-item span {
  color: #333;
  flex: 1;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

/* 统计卡片样式 */
.stat-item {
  text-align: center;
  padding: 20px 10px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .info-item {
    flex-direction: column;
  }
  
  .info-item label {
    width: auto;
    margin-bottom: 5px;
  }
  
  .stat-item {
    margin-bottom: 15px;
  }
}
</style>
```

现在我需要修改主应用文件，添加用户认证功能和状态管理。让我更新App.vue文件：

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { 
  HomeFilled, 
  DocumentCopy, 
  TrendCharts, 
  MagicStick 
} from '@element-plus/icons-vue'

// 导入组件
import HomeComponent from './components/HomeComponent.vue'
import HistoryComponent from './components/HistoryComponent.vue'
import StatisticsComponent from './components/StatisticsComponent.vue'
import PredictionComponent from './components/PredictionComponent.vue'

// 响应式数据
const activeIndex = ref('home')

// 方法
const handleSelect = (key) => {
  activeIndex.value = key
}

const handleNavigate = (page) => {
  activeIndex.value = page
}

// 组件挂载时
onMounted(() => {
  console.log('🌈 彩虹数据应用已启动')
})

->

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { 
  HomeFilled, 
  DocumentCopy, 
  TrendCharts, 
  MagicStick,
  User,
  UserFilled
} from '@element-plus/icons-vue'

// 导入组件
import HomeComponent from './components/HomeComponent.vue'
import HistoryComponent from './components/HistoryComponent.vue'
import StatisticsComponent from './components/StatisticsComponent.vue'
import PredictionComponent from './components/PredictionComponent.vue'
import LoginComponent from './components/LoginComponent.vue'
import RegisterComponent from './components/RegisterComponent.vue'
import UserProfileComponent from './components/UserProfileComponent.vue'

// 响应式数据
const activeIndex = ref('home')
const isAuthenticated = ref(false)
const currentUser = ref(null)
const showAuthDialog = ref(false)
const authMode = ref('login') // 'login' 或 'register'

// 方法
const handleSelect = (key) => {
  if (key === 'profile' && !isAuthenticated.value) {
    showAuthDialog.value = true
    authMode.value = 'login'
    return
  }
  activeIndex.value = key
}

const handleNavigate = (page) => {
  if (page === 'profile' && !isAuthenticated.value) {
    showAuthDialog.value = true
    authMode.value = 'login'
    return
  }
  activeIndex.value = page
}

const handleLogin = () => {
  showAuthDialog.value = true
  authMode.value = 'login'
}

const handleRegister = () => {
  showAuthDialog.value = true
  authMode.value = 'register'
}

const handleLogout = async () => {
  try {
    // 调用登出API
    await axios.post('http://127.0.0.1:8001/api/v1/auth/logout/')
    
    // 清除本地存储
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    
    // 更新状态
    isAuthenticated.value = false
    currentUser.value = null
    activeIndex.value = 'home'
    
    ElMessage.success('已成功退出登录')
  } catch (error) {
    console.error('登出失败:', error)
    // 即使API调用失败，也清除本地状态
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    isAuthenticated.value = false
    currentUser.value = null
    activeIndex.value = 'home'
    ElMessage.success('已退出登录')
  }
}

const onLoginSuccess = ({ user, token }) => {
  // 保存用户信息和Token
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)
  axios.defaults.headers.common['Authorization'] = `Token ${token}`
  
  // 更新状态
  isAuthenticated.value = true
  currentUser.value = user
  showAuthDialog.value = false
  
  ElMessage.success(`欢迎回来，${user.username}！`)
}

const onRegisterSuccess = ({ user, token }) => {
  // 注册成功后自动登录
  onLoginSuccess({ user, token })
}

const switchAuthMode = (mode) => {
  authMode.value = mode
}

const checkAuthStatus = () => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
      isAuthenticated.value = true
      currentUser.value = user
    } catch (error) {
      console.error('解析用户信息失败:', error)
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }
}

// 组件挂载时
onMounted(() => {
  console.log('🌈 彩虹数据应用已启动')
  checkAuthStatus()
})
```

现在我需要更新模板部分，添加用户认证相关的UI元素：

```vue
        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeIndex"
          class="el-menu-demo"
          mode="horizontal"
          @select="handleSelect"
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="history">
            <el-icon><DocumentCopy /></el-icon>
            <span>历史开奖</span>
          </el-menu-item>
          <el-menu-item index="statistics">
            <el-icon><TrendCharts /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="prediction">
            <el-icon><MagicStick /></el-icon>
            <span>娱乐预测</span>
          </el-menu-item>
        </el-menu>

->

        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeIndex"
          class="el-menu-demo"
          mode="horizontal"
          @select="handleSelect"
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="history">
            <el-icon><DocumentCopy /></el-icon>
            <span>历史开奖</span>
          </el-menu-item>
          <el-menu-item index="statistics">
            <el-icon><TrendCharts /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="prediction">
            <el-icon><MagicStick /></el-icon>
            <span>娱乐预测</span>
          </el-menu-item>
          <el-menu-item v-if="isAuthenticated" index="profile">
            <el-icon><UserFilled /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
        
        <!-- 用户认证区域 -->
        <div class="auth-section">
          <div v-if="!isAuthenticated" class="auth-buttons">
            <el-button type="text" @click="handleLogin" class="auth-btn">
              <el-icon><User /></el-icon>
              登录
            </el-button>
            <el-button type="primary" @click="handleRegister" size="small">
              注册
            </el-button>
          </div>
          
          <div v-else class="user-info">
            <el-dropdown @command="handleUserCommand">
              <span class="user-dropdown">
                <el-icon><UserFilled /></el-icon>
                {{ currentUser.username }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
```

现在我需要添加个人中心页面的内容区域和认证对话框：

```vue
        <!-- 娱乐预测页面 -->
        <div v-if="activeIndex === 'prediction'" class="page-content">
          <PredictionComponent />
        </div>
      </el-main>
    </el-container>

->

        <!-- 娱乐预测页面 -->
        <div v-if="activeIndex === 'prediction'" class="page-content">
          <PredictionComponent />
        </div>
        
        <!-- 个人中心页面 -->
        <div v-if="activeIndex === 'profile'" class="page-content">
          <UserProfileComponent />
        </div>
      </el-main>
    </el-container>
    
    <!-- 用户认证对话框 -->
    <el-dialog
      v-model="showAuthDialog"
      :title="authMode === 'login' ? '用户登录' : '用户注册'"
      width="90%"
      :max-width="authMode === 'login' ? '450px' : '550px'"
      :close-on-click-modal="false"
      center
    >
      <LoginComponent 
        v-if="authMode === 'login'"
        @login-success="onLoginSuccess"
        @switch-to-register="switchAuthMode('register')"
      />
      <RegisterComponent 
        v-else
        @register-success="onRegisterSuccess"
        @switch-to-login="switchAuthMode('login')"
      />
    </el-dialog>
```

现在我需要添加缺少的图标导入和用户下拉菜单处理函数：

```vue
import { 
  HomeFilled, 
  DocumentCopy, 
  TrendCharts, 
  MagicStick,
  User,
  UserFilled
} from '@element-plus/icons-vue'

->

import { 
  HomeFilled, 
  DocumentCopy, 
  TrendCharts, 
  MagicStick,
  User,
  UserFilled,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'
```

```vue
const switchAuthMode = (mode) => {
  authMode.value = mode
}

->

const switchAuthMode = (mode) => {
  authMode.value = mode
}

const handleUserCommand = (command) => {
  if (command === 'profile') {
    activeIndex.value = 'profile'
  } else if (command === 'logout') {
    handleLogout()
  }
}
```

现在我需要添加认证相关的CSS样式：

```vue
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

->

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
```

```vue
.el-menu-demo {
  background-color: transparent !important;
  border-bottom: none;
}

->

.el-menu-demo {
  background-color: transparent !important;
  border-bottom: none;
}

/* 认证区域样式 */
.auth-section {
  margin-left: 20px;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-btn {
  color: white !important;
  padding: 8px 16px;
}

.auth-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-info {
  color: white;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-dropdown .el-icon {
  margin-right: 5px;
}

.user-dropdown .el-icon--right {
  margin-left: 5px;
  margin-right: 0;
}
```

现在我需要更新响应式设计部分，确保在移动端也能正常显示：

```vue
/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 10px;
  }
  
  .logo {
    margin-bottom: 10px;
  }
  
  .main-content {
    padding: 10px;
  }
}

->

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 10px;
  }
  
  .logo {
    margin-bottom: 10px;
  }
  
  .auth-section {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .main-content {
    padding: 10px;
  }
}

@media (max-width: 992px) {
  .header-content {
    flex-wrap: wrap;
  }
  
  .auth-section {
    margin-left: auto;
  }
}
```

现在让我测试一下前端认证功能是否正常工作。首先启动前端开发服务器：

现在让我创建一个测试脚本来验证前端认证功能：

```python
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
```

现在让我运行测试脚本来验证认证功能：

