"""
彩虹数据权限管理模块
实现基于角色的权限控制系统
"""

from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User
from .models import UserProfile


class IsNormalUser(BasePermission):
    """普通用户权限"""
    
    def has_permission(self, request, view):
        """检查用户是否为普通用户"""
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = request.user.userprofile
            return user_profile.user_type in ['normal', 'admin']  # 管理员也有普通用户权限
        except UserProfile.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        """检查对象级权限"""
        if not self.has_permission(request, view):
            return False
        
        # 用户只能访问自己的数据
        if hasattr(obj, 'user') and obj.user:
            return obj.user.user == request.user
        
        return True


class IsAdminUser(BasePermission):
    """管理员权限"""
    
    def has_permission(self, request, view):
        """检查用户是否为管理员"""
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = request.user.userprofile
            return user_profile.user_type == 'admin'
        except UserProfile.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        """管理员拥有所有对象权限"""
        return self.has_permission(request, view)


class IsCrawlerManager(BasePermission):
    """爬虫管理权限 - 只有管理员可以操作爬虫"""
    
    def has_permission(self, request, view):
        """检查用户是否有爬虫管理权限"""
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = request.user.userprofile
            return user_profile.user_type == 'admin'
        except UserProfile.DoesNotExist:
            return False


class IsDataSourceManager(BasePermission):
    """数据源管理权限 - 只有管理员可以配置数据源"""
    
    def has_permission(self, request, view):
        """检查用户是否有数据源管理权限"""
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = request.user.userprofile
            return user_profile.user_type == 'admin'
        except UserProfile.DoesNotExist:
            return False


class IsOwnerOrAdmin(BasePermission):
    """所有者或管理员权限 - 用户可以访问自己的数据，管理员可以访问所有数据"""
    
    def has_permission(self, request, view):
        """基础权限检查"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """对象级权限检查"""
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = request.user.userprofile
            
            # 管理员拥有所有权限
            if user_profile.user_type == 'admin':
                return True
            
            # 用户只能访问自己的数据
            if hasattr(obj, 'user') and obj.user:
                return obj.user.user == request.user
            
            # 如果对象没有用户关联，则拒绝访问
            return False
            
        except UserProfile.DoesNotExist:
            return False


class IsReadOnlyOrAdmin(BasePermission):
    """只读或管理员权限 - 普通用户只读，管理员可写"""
    
    def has_permission(self, request, view):
        """权限检查"""
        if not request.user.is_authenticated:
            # 允许匿名用户进行只读操作
            return request.method in ['GET', 'HEAD', 'OPTIONS']
        
        try:
            user_profile = request.user.userprofile
            
            # 管理员拥有所有权限
            if user_profile.user_type == 'admin':
                return True
            
            # 普通用户只能进行只读操作
            return request.method in ['GET', 'HEAD', 'OPTIONS']
            
        except UserProfile.DoesNotExist:
            # 未创建用户资料的用户只能进行只读操作
            return request.method in ['GET', 'HEAD', 'OPTIONS']


class CanViewCrawlerLogs(BasePermission):
    """爬取日志查看权限 - 管理员可以查看所有日志"""
    
    def has_permission(self, request, view):
        """检查用户是否可以查看爬取日志"""
        if not request.user.is_authenticated:
            return False
        
        try:
            user_profile = request.user.userprofile
            return user_profile.user_type == 'admin'
        except UserProfile.DoesNotExist:
            return False


def get_user_permissions(user):
    """获取用户权限信息"""
    if not user.is_authenticated:
        return {
            'user_type': 'anonymous',
            'permissions': ['view_public_data'],
            'can_predict': True,  # 匿名用户可以体验预测功能
            'can_save_prediction': False,
            'can_manage_crawler': False,
            'can_manage_datasource': False,
            'can_view_crawler_logs': False,
            'can_access_admin': False,
        }
    
    try:
        user_profile = user.userprofile
        user_type = user_profile.user_type
        
        permissions = ['view_public_data', 'view_own_data']
        
        if user_type == 'admin':
            permissions.extend([
                'manage_all_data',
                'manage_users',
                'manage_crawler', 
                'manage_datasource',
                'view_crawler_logs',
                'access_admin',
                'manage_system_config'
            ])
            
            return {
                'user_type': 'admin',
                'permissions': permissions,
                'can_predict': True,
                'can_save_prediction': True,
                'can_manage_crawler': True,
                'can_manage_datasource': True,
                'can_view_crawler_logs': True,
                'can_access_admin': True,
            }
        
        else:  # normal user
            permissions.extend([
                'create_prediction',
                'view_own_prediction',
                'update_own_profile'
            ])
            
            return {
                'user_type': 'normal',
                'permissions': permissions,
                'can_predict': True,
                'can_save_prediction': True,
                'can_manage_crawler': False,
                'can_manage_datasource': False,
                'can_view_crawler_logs': False,
                'can_access_admin': False,
            }
            
    except UserProfile.DoesNotExist:
        # 用户没有扩展资料，视为普通用户
        return {
            'user_type': 'normal',
            'permissions': ['view_public_data'],
            'can_predict': True,
            'can_save_prediction': False,
            'can_manage_crawler': False,
            'can_manage_datasource': False,
            'can_view_crawler_logs': False,
            'can_access_admin': False,
        }


def check_crawler_permission(user, action='view'):
    """检查爬虫相关权限"""
    if not user.is_authenticated:
        return False
    
    try:
        user_profile = user.userprofile
        return user_profile.user_type == 'admin'
    except UserProfile.DoesNotExist:
        return False


def check_admin_permission(user):
    """检查管理员权限"""
    if not user.is_authenticated:
        return False
    
    try:
        user_profile = user.userprofile
        return user_profile.user_type == 'admin'
    except UserProfile.DoesNotExist:
        return False


def ensure_user_profile(user):
    """确保用户有扩展资料"""
    if user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'user_type': 'normal'}
        )
        return user_profile
    return None 