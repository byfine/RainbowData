from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import LotteryResult, Statistics, Prediction, UserAnalysisLog, DataSource, CrawlLog


@admin.register(LotteryResult)
class LotteryResultAdmin(admin.ModelAdmin):
    """开奖记录管理"""
    list_display = ['issue', 'draw_date', 'get_red_balls_display', 'blue_ball', 'created_at']
    list_filter = ['draw_date', 'blue_ball']
    search_fields = ['issue']
    ordering = ['-draw_date', '-issue']
    readonly_fields = ['created_at', 'updated_at']
    
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


# 自定义Admin站点信息
admin.site.site_header = '彩虹数据管理后台'
admin.site.site_title = '彩虹数据'
admin.site.index_title = '双色球数据分析学习平台'
