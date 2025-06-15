from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    LotteryResult, Statistics, Prediction, UserAnalysisLog, DataSource, CrawlLog, 
    UserProfile, UserFavorite, SystemConfig, SystemLog
)


# 自定义Django User Admin
class UserProfileInline(admin.StackedInline):
    """用户扩展信息内联编辑"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户扩展信息'


class CustomUserAdmin(BaseUserAdmin):
    """增强的用户管理"""
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'get_user_type', 'is_active', 'get_analysis_count', 'last_login', 'date_joined']
    list_filter = BaseUserAdmin.list_filter + ('userprofile__user_type',)
    search_fields = ['username', 'email', 'userprofile__phone']
    
    def get_user_type(self, obj):
        """获取用户类型"""
        try:
            return obj.userprofile.get_user_type_display()
        except UserProfile.DoesNotExist:
            return '未设置'
    get_user_type.short_description = '用户类型'
    get_user_type.admin_order_field = 'userprofile__user_type'
    
    def get_analysis_count(self, obj):
        """获取分析次数"""
        try:
            return f'{obj.userprofile.total_analysis_count}次'
        except UserProfile.DoesNotExist:
            return '0次'
    get_analysis_count.short_description = '分析次数'
    get_analysis_count.admin_order_field = 'userprofile__total_analysis_count'


# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户扩展信息管理"""
    list_display = [
        'user', 'user_type', 'total_analysis_count', 'total_prediction_count',
        'last_login_ip', 'created_at'
    ]
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['total_analysis_count', 'total_prediction_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('关联用户', {
            'fields': ('user',)
        }),
        ('用户信息', {
            'fields': ('user_type', 'avatar', 'phone')
        }),
        ('学习统计', {
            'fields': ('total_analysis_count', 'total_prediction_count'),
            'classes': ('collapse',)
        }),
        ('登录信息', {
            'fields': ('last_login_ip',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['promote_to_admin', 'demote_to_normal']
    
    def promote_to_admin(self, request, queryset):
        """提升为管理员"""
        updated = queryset.update(user_type='admin')
        self.message_user(request, f'已将 {updated} 个用户提升为管理员')
        # 同时设置Django User的is_staff和is_superuser
        for profile in queryset:
            profile.user.is_staff = True
            profile.user.is_superuser = True
            profile.user.save()
    promote_to_admin.short_description = '提升为管理员'
    
    def demote_to_normal(self, request, queryset):
        """降级为普通用户"""
        updated = queryset.update(user_type='normal')
        self.message_user(request, f'已将 {updated} 个用户降级为普通用户')
        # 同时取消Django User的is_staff和is_superuser
        for profile in queryset:
            if profile.user.username != request.user.username:  # 防止自己降级自己
                profile.user.is_staff = False
                profile.user.is_superuser = False
                profile.user.save()
    demote_to_normal.short_description = '降级为普通用户'


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """用户收藏管理"""
    list_display = [
        'title', 'user_profile', 'favorite_type', 'is_public',
        'view_count', 'created_at'
    ]
    list_filter = ['favorite_type', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'user_profile__user__username']
    ordering = ['-created_at']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user_profile', 'favorite_type', 'title', 'description')
        }),
        ('收藏内容', {
            'fields': ('object_id', 'content_data')
        }),
        ('属性设置', {
            'fields': ('is_public', 'tags')
        }),
        ('统计信息', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_public', 'make_private']
    
    def make_public(self, request, queryset):
        """设为公开"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'已将 {updated} 个收藏设为公开')
    make_public.short_description = '设为公开收藏'
    
    def make_private(self, request, queryset):
        """设为私有"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'已将 {updated} 个收藏设为私有')
    make_private.short_description = '设为私有收藏'


@admin.register(LotteryResult)
class LotteryResultAdmin(admin.ModelAdmin):
    """开奖记录管理"""
    list_display = ['issue', 'draw_date', 'get_red_balls_display', 'blue_ball', 'created_at']
    list_filter = ['draw_date', 'blue_ball']
    search_fields = ['issue']
    ordering = ['-draw_date', '-issue']
    readonly_fields = ['created_at', 'updated_at']
    
    # 新增批量操作
    actions = ['delete_selected', 'export_selected']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('issue', 'draw_date')
        }),
        ('开奖号码', {
            'fields': (
                'red_ball_1', 'red_ball_2', 'red_ball_3',
                'red_ball_4', 'red_ball_5', 'red_ball_6',
                'blue_ball'
            )
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_red_balls_display(self, obj):
        """显示红球号码"""
        red_balls = obj.get_red_balls()
        return ' - '.join(map(str, red_balls))
    get_red_balls_display.short_description = '红球号码'
    
    def export_selected(self, request, queryset):
        """导出选中的开奖记录"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="lottery_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['期号', '开奖日期', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球'])
        
        for result in queryset:
            writer.writerow([
                result.issue, result.draw_date,
                result.red_ball_1, result.red_ball_2, result.red_ball_3,
                result.red_ball_4, result.red_ball_5, result.red_ball_6,
                result.blue_ball
            ])
        
        return response
    export_selected.short_description = '导出选中的开奖记录'


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    """统计分析管理"""
    list_display = ['ball_type', 'ball_number', 'appear_count', 'last_appear_issue', 'avg_interval']
    list_filter = ['ball_type', 'appear_count']
    search_fields = ['ball_number', 'last_appear_issue']
    ordering = ['ball_type', 'ball_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('ball_type', 'ball_number')
        }),
        ('统计数据', {
            'fields': ('appear_count', 'last_appear_issue', 'max_interval', 'avg_interval')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 临时注释掉User管理，等迁移完成后恢复
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     """用户管理"""
#     list_display = ['username', 'email', 'user_type', 'is_active', 'total_analysis_count', 'last_login']
#     list_filter = ['user_type', 'is_active', 'date_joined']
#     search_fields = ['username', 'email', 'phone']
#     ordering = ['-date_joined']
#     
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('扩展信息', {
#             'fields': ('user_type', 'avatar', 'phone', 'last_login_ip')
#         }),
#         ('学习统计', {
#             'fields': ('total_analysis_count', 'total_prediction_count'),
#             'classes': ('collapse',)
#         }),
#     )
#     
#     add_fieldsets = BaseUserAdmin.add_fieldsets + (
#         ('扩展信息', {
#             'fields': ('email', 'user_type', 'phone')
#         }),
#     )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """预测记录管理"""
    list_display = [
        'target_issue', 'algorithm', 'get_predicted_numbers_display', 
        'confidence', 'is_accurate', 'accuracy_score', 'created_at'
    ]
    list_filter = ['algorithm', 'is_accurate', 'created_at', 'confidence']
    search_fields = ['target_issue']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'accuracy_score']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('algorithm', 'target_issue', 'confidence')
        }),
        ('预测号码', {
            'fields': ('predicted_red_balls', 'predicted_blue_ball')
        }),
        ('结果分析', {
            'fields': ('is_accurate', 'red_match_count', 'blue_match', 'accuracy_score')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_predicted_numbers_display(self, obj):
        """显示预测号码"""
        red_balls = ', '.join(map(str, obj.predicted_red_balls))
        return f'红球: {red_balls} | 蓝球: {obj.predicted_blue_ball}'
    get_predicted_numbers_display.short_description = '预测号码'


@admin.register(UserAnalysisLog)
class UserAnalysisLogAdmin(admin.ModelAdmin):
    """用户分析日志管理"""
    list_display = ['analysis_type', 'get_parameters_display', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    search_fields = ['result_summary']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('analysis_type', 'created_at')
        }),
        ('分析详情', {
            'fields': ('parameters', 'result_summary')
        }),
    )
    
    def get_parameters_display(self, obj):
        """显示分析参数"""
        if obj.parameters:
            return str(obj.parameters)[:100] + '...' if len(str(obj.parameters)) > 100 else str(obj.parameters)
        return '无参数'
    get_parameters_display.short_description = '分析参数'


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """数据源配置管理"""
    list_display = [
        'name', 'source_type', 'status', 'is_enabled', 'priority',
        'total_success_count', 'total_error_count', 'get_success_rate',
        'last_success_time'
    ]
    list_filter = ['source_type', 'status', 'is_enabled', 'priority']
    search_fields = ['name', 'base_url', 'description']
    ordering = ['priority', 'name']
    readonly_fields = [
        'last_success_time', 'last_error_time', 'total_success_count', 
        'total_error_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'source_type', 'description', 'priority')
        }),
        ('连接配置', {
            'fields': ('base_url', 'api_endpoint', 'headers')
        }),
        ('请求设置', {
            'fields': ('request_interval', 'timeout', 'max_retries')
        }),
        ('解析配置', {
            'fields': ('selector_config', 'field_mapping')
        }),
        ('状态管理', {
            'fields': ('status', 'is_enabled')
        }),
        ('统计信息', {
            'fields': (
                'last_success_time', 'last_error_time', 'last_error_message',
                'total_success_count', 'total_error_count'
            ),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_success_rate(self, obj):
        """计算成功率"""
        total = obj.total_success_count + obj.total_error_count
        if total == 0:
            return '暂无数据'
        rate = (obj.total_success_count / total) * 100
        return f'{rate:.1f}%'
    get_success_rate.short_description = '成功率'
    
    actions = ['enable_sources', 'disable_sources', 'reset_error_status']
    
    def enable_sources(self, request, queryset):
        """批量启用数据源"""
        updated = queryset.update(is_enabled=True)
        self.message_user(request, f'已启用 {updated} 个数据源')
    enable_sources.short_description = '启用选中的数据源'
    
    def disable_sources(self, request, queryset):
        """批量停用数据源"""
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f'已停用 {updated} 个数据源')
    disable_sources.short_description = '停用选中的数据源'
    
    def reset_error_status(self, request, queryset):
        """重置错误状态"""
        updated = queryset.filter(status='error').update(status='active')
        self.message_user(request, f'已重置 {updated} 个数据源的错误状态')
    reset_error_status.short_description = '重置错误状态'


@admin.register(CrawlLog)
class CrawlLogAdmin(admin.ModelAdmin):
    """爬虫执行记录管理"""
    list_display = [
        'task_id', 'task_type', 'data_source', 'status',
        'start_time', 'duration_seconds', 'records_created',
        'get_success_rate'
    ]
    list_filter = ['task_type', 'status', 'data_source', 'start_time']
    search_fields = ['task_id', 'data_source__name']
    ordering = ['-created_at']
    readonly_fields = [
        'start_time', 'end_time', 'duration_seconds',
        'total_requests', 'success_requests', 'failed_requests',
        'records_found', 'records_created', 'records_updated', 'records_skipped',
        'error_message', 'error_traceback', 'execution_log',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('task_id', 'task_type', 'data_source', 'status')
        }),
        ('执行参数', {
            'fields': ('parameters', 'target_date_range')
        }),
        ('执行时间', {
            'fields': ('start_time', 'end_time', 'duration_seconds')
        }),
        ('请求统计', {
            'fields': ('total_requests', 'success_requests', 'failed_requests')
        }),
        ('数据统计', {
            'fields': ('records_found', 'records_created', 'records_updated', 'records_skipped')
        }),
        ('错误信息', {
            'fields': ('error_message', 'error_traceback'),
            'classes': ('collapse',)
        }),
        ('执行日志', {
            'fields': ('execution_log',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_success_rate(self, obj):
        """计算请求成功率"""
        if obj.total_requests == 0:
            return '暂无数据'
        rate = (obj.success_requests / obj.total_requests) * 100
        return f'{rate:.1f}%'
    get_success_rate.short_description = '请求成功率'
    
    def has_add_permission(self, request):
        """禁止手动添加爬虫记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改爬虫记录"""
        return False


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """系统配置管理"""
    list_display = [
        'name', 'key', 'config_type', 'data_type', 'is_active', 
        'is_editable', 'updated_at'
    ]
    list_filter = ['config_type', 'data_type', 'is_active', 'is_editable']
    search_fields = ['name', 'key', 'description']
    ordering = ['config_type', 'key']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('key', 'name', 'config_type', 'description')
        }),
        ('配置值', {
            'fields': ('value', 'default_value', 'data_type')
        }),
        ('验证规则', {
            'fields': ('validation_rules',),
            'classes': ('collapse',)
        }),
        ('属性设置', {
            'fields': ('is_active', 'is_editable')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_configs', 'deactivate_configs', 'reset_to_default']
    
    def activate_configs(self, request, queryset):
        """激活配置"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'已激活 {updated} 个配置项')
    activate_configs.short_description = '激活选中的配置'
    
    def deactivate_configs(self, request, queryset):
        """停用配置"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'已停用 {updated} 个配置项')
    deactivate_configs.short_description = '停用选中的配置'
    
    def reset_to_default(self, request, queryset):
        """重置为默认值"""
        count = 0
        for config in queryset:
            if config.default_value:
                config.value = config.default_value
                config.save()
                count += 1
        self.message_user(request, f'已重置 {count} 个配置项为默认值')
    reset_to_default.short_description = '重置为默认值'
    
    def get_readonly_fields(self, request, obj=None):
        """根据is_editable动态设置只读字段"""
        readonly = list(self.readonly_fields)
        if obj and not obj.is_editable:
            readonly.extend(['value', 'data_type', 'validation_rules'])
        return readonly


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """系统日志管理"""
    list_display = [
        'get_level_icon', 'log_type', 'get_message_preview', 'user',
        'ip_address', 'created_at'
    ]
    list_filter = ['level', 'log_type', 'created_at', 'user']
    search_fields = ['message', 'module', 'function', 'user__username', 'ip_address']
    ordering = ['-created_at']
    readonly_fields = [
        'level', 'log_type', 'message', 'module', 'function',
        'user', 'ip_address', 'request_method', 'request_path',
        'request_data', 'exception_type', 'exception_message',
        'traceback', 'created_at'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('level', 'log_type', 'message', 'created_at')
        }),
        ('模块信息', {
            'fields': ('module', 'function'),
            'classes': ('collapse',)
        }),
        ('用户信息', {
            'fields': ('user', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('请求信息', {
            'fields': ('request_method', 'request_path', 'request_data'),
            'classes': ('collapse',)
        }),
        ('异常信息', {
            'fields': ('exception_type', 'exception_message', 'traceback'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['delete_selected', 'export_logs']
    
    def get_level_icon(self, obj):
        """显示日志级别图标"""
        icons = {
            'debug': '🔧',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨',
        }
        return f"{icons.get(obj.level, '📝')} {obj.get_level_display()}"
    get_level_icon.short_description = '级别'
    
    def get_message_preview(self, obj):
        """显示消息预览"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    get_message_preview.short_description = '消息内容'
    
    def export_logs(self, request, queryset):
        """导出日志"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="system_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['时间', '级别', '类型', '消息', '用户', 'IP地址', '模块', '函数'])
        
        for log in queryset:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.get_level_display(),
                log.get_log_type_display(),
                log.message,
                log.user.username if log.user else '',
                log.ip_address or '',
                log.module or '',
                log.function or '',
            ])
        
        return response
    export_logs.short_description = '导出选中的日志'
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False


# 自定义Admin站点信息
admin.site.site_header = '彩虹数据管理后台'
admin.site.site_title = '彩虹数据'
admin.site.index_title = '双色球数据分析学习平台'
