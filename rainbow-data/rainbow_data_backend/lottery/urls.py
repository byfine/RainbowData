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

# 爬虫管理相关路由
router.register(r'datasources', views.DataSourceViewSet, basename='datasource')
router.register(r'crawler/logs', views.CrawlLogViewSet, basename='crawllog')

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
    
    # 爬虫管理API端点
    path('api/v1/crawler/', views.CrawlerManagementView.as_view(), name='crawler_management'),
    path('api/v1/sync/', views.DataSyncView.as_view(), name='data_sync'),
    
    # API文档端点
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='lottery:schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='lottery:schema'), name='redoc'),
    
    # 额外的自定义端点（如果需要）
    # path('api/v1/health/', views.health_check, name='health_check'),
] 