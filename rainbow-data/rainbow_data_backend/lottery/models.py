from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class LotteryResult(models.Model):
    """双色球开奖记录表"""
    issue = models.CharField(max_length=20, unique=True, verbose_name='期号')
    draw_date = models.DateField(verbose_name='开奖日期')
    
    # 红球号码 (1-33)
    red_ball_1 = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)],
        verbose_name='红球1'
    )
    red_ball_2 = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)],
        verbose_name='红球2'
    )
    red_ball_3 = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)],
        verbose_name='红球3'
    )
    red_ball_4 = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)],
        verbose_name='红球4'
    )
    red_ball_5 = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)],
        verbose_name='红球5'
    )
    red_ball_6 = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)],
        verbose_name='红球6'
    )
    
    # 蓝球号码 (1-16)
    blue_ball = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        verbose_name='蓝球'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'lottery_results'
        verbose_name = '开奖记录'
        verbose_name_plural = '开奖记录'
        ordering = ['-draw_date', '-issue']
        indexes = [
            models.Index(fields=['draw_date']),
            models.Index(fields=['issue']),
            models.Index(fields=['-draw_date', 'issue']),
            models.Index(fields=['red_ball_1', 'red_ball_2', 'red_ball_3']),
            models.Index(fields=['blue_ball']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.issue} - 红球: {self.get_red_balls()} 蓝球: {self.blue_ball}'
    
    def get_red_balls(self):
        """获取红球号码列表"""
        return [
            self.red_ball_1, self.red_ball_2, self.red_ball_3,
            self.red_ball_4, self.red_ball_5, self.red_ball_6
        ]
    
    def get_all_balls(self):
        """获取所有号码"""
        return {
            'red_balls': self.get_red_balls(),
            'blue_ball': self.blue_ball
        }


class Statistics(models.Model):
    """号码统计分析表"""
    BALL_TYPE_CHOICES = [
        ('red', '红球'),
        ('blue', '蓝球'),
    ]
    
    ball_number = models.PositiveSmallIntegerField(verbose_name='球号')
    ball_type = models.CharField(max_length=4, choices=BALL_TYPE_CHOICES, verbose_name='球类型')
    appear_count = models.PositiveIntegerField(default=0, verbose_name='出现次数')
    last_appear_issue = models.CharField(max_length=20, null=True, blank=True, verbose_name='最后出现期号')
    max_interval = models.PositiveIntegerField(default=0, verbose_name='最大间隔')
    avg_interval = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='平均间隔')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'statistics'
        verbose_name = '统计分析'
        verbose_name_plural = '统计分析'
        unique_together = ['ball_number', 'ball_type']
        indexes = [
            models.Index(fields=['ball_type', 'ball_number']),
            models.Index(fields=['appear_count']),
            models.Index(fields=['-appear_count']),
            models.Index(fields=['ball_type', '-appear_count']),
            models.Index(fields=['max_interval']),
            models.Index(fields=['last_appear_issue']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f'{self.get_ball_type_display()}{self.ball_number} - 出现{self.appear_count}次'


# 用户扩展信息模型（避免与Django User冲突）
class UserProfile(models.Model):
    """用户扩展信息模型"""
    USER_TYPE_CHOICES = [
        ('normal', '普通用户'),
        ('admin', '管理员'),
    ]
    
    # 关联Django默认User模型
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, verbose_name='关联用户')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='normal', verbose_name='用户类型')
    avatar = models.URLField(blank=True, null=True, verbose_name='头像')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    
    # 学习记录相关字段
    total_analysis_count = models.PositiveIntegerField(default=0, verbose_name='分析次数')
    total_prediction_count = models.PositiveIntegerField(default=0, verbose_name='预测次数')
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='最后登录IP')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.get_user_type_display()}'


class Prediction(models.Model):
    """预测记录表"""
    ALGORITHM_CHOICES = [
        ('frequency', '频率统计'),
        ('trend', '趋势分析'),
        ('regression', '线性回归'),
        ('ensemble', '组合算法'),
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户', null=True, blank=True)
    algorithm = models.CharField(max_length=20, choices=ALGORITHM_CHOICES, verbose_name='预测算法')
    target_issue = models.CharField(max_length=20, verbose_name='预测期号')
    
    # 预测号码存储为JSON格式
    predicted_red_balls = models.JSONField(verbose_name='预测红球')  # 例: [1, 5, 12, 18, 23, 31]
    predicted_blue_ball = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        verbose_name='预测蓝球'
    )
    
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='置信度')
    is_accurate = models.BooleanField(null=True, blank=True, verbose_name='是否准确')
    
    # 预测结果分析
    red_match_count = models.PositiveSmallIntegerField(default=0, verbose_name='红球命中数')
    blue_match = models.BooleanField(default=False, verbose_name='蓝球是否命中')
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='准确率得分')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'predictions'
        verbose_name = '预测记录'
        verbose_name_plural = '预测记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_issue']),
            models.Index(fields=['algorithm']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.target_issue} ({self.get_algorithm_display()})'
    
    def get_predicted_numbers(self):
        """获取预测号码的完整信息"""
        return {
            'red_balls': self.predicted_red_balls,
            'blue_ball': self.predicted_blue_ball
        }
    
    def calculate_accuracy(self, actual_result):
        """计算预测准确率"""
        if not actual_result:
            return None
            
        # 计算红球命中数
        actual_red = actual_result.get_red_balls()
        predicted_red = self.predicted_red_balls
        red_matches = len(set(actual_red) & set(predicted_red))
        
        # 计算蓝球是否命中
        blue_matches = actual_result.blue_ball == self.predicted_blue_ball
        
        # 更新记录
        self.red_match_count = red_matches
        self.blue_match = blue_matches
        
        # 计算综合准确率得分 (红球每个2分，蓝球10分，满分22分)
        score = red_matches * 2 + (10 if blue_matches else 0)
        self.accuracy_score = (score / 22) * 100  # 转换为百分比
        
        # 判断是否算作准确预测 (至少命中3个红球或蓝球)
        self.is_accurate = red_matches >= 3 or blue_matches
        
        self.save()
        return self.accuracy_score


class UserAnalysisLog(models.Model):
    """用户分析日志表"""
    ANALYSIS_TYPE_CHOICES = [
        ('frequency', '频率分析'),
        ('trend', '趋势分析'),
        ('pattern', '模式分析'),
        ('prediction', '预测生成'),
        ('export', '数据导出'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户', null=True, blank=True, db_column='user_id')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, verbose_name='分析类型')
    parameters = models.JSONField(null=True, blank=True, verbose_name='分析参数')
    result_summary = models.TextField(blank=True, verbose_name='结果摘要')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'user_analysis_logs'
        verbose_name = '用户分析日志'
        verbose_name_plural = '用户分析日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_profile', 'created_at']),
            models.Index(fields=['analysis_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_name = self.user_profile.user.username if self.user_profile else '匿名'
        return f'{user_name} - {self.get_analysis_type_display()}'


class UserFavorite(models.Model):
    """用户收藏表"""
    FAVORITE_TYPE_CHOICES = [
        ('lottery_result', '开奖结果'),
        ('prediction', '预测记录'),
        ('analysis', '分析结果'),
        ('number_set', '号码组合'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    favorite_type = models.CharField(max_length=20, choices=FAVORITE_TYPE_CHOICES, verbose_name='收藏类型')
    
    # 收藏的内容（根据类型存储不同的数据）
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='对象ID')  # 关联对象的ID
    content_data = models.JSONField(null=True, blank=True, verbose_name='收藏内容')  # 存储具体内容数据
    
    # 收藏信息
    title = models.CharField(max_length=200, verbose_name='收藏标题')
    description = models.TextField(blank=True, verbose_name='收藏描述')
    tags = models.JSONField(default=list, blank=True, verbose_name='标签')
    
    # 元数据
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    view_count = models.PositiveIntegerField(default=0, verbose_name='查看次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_favorites'
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'
        ordering = ['-created_at']
        unique_together = ['user_profile', 'favorite_type', 'object_id']  # 防止重复收藏同一内容
        indexes = [
            models.Index(fields=['user_profile', 'favorite_type']),
            models.Index(fields=['favorite_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_public']),
        ]
    
    def get_content_summary(self):
        """获取收藏内容摘要"""
        if self.favorite_type == 'number_set' and self.content_data:
            red_balls = self.content_data.get('red_balls', [])
            blue_ball = self.content_data.get('blue_ball', 0)
            return f"红球: {', '.join(map(str, red_balls))} 蓝球: {blue_ball}"
        elif self.favorite_type == 'lottery_result' and self.object_id:
            try:
                result = LotteryResult.objects.get(id=self.object_id)
                return f"期号: {result.issue} 日期: {result.draw_date}"
            except LotteryResult.DoesNotExist:
                return "开奖结果不存在"
        elif self.favorite_type == 'prediction' and self.object_id:
            try:
                prediction = Prediction.objects.get(id=self.object_id)
                return f"预测期号: {prediction.target_issue} 算法: {prediction.algorithm}"
            except Prediction.DoesNotExist:
                return "预测记录不存在"
        elif self.favorite_type == 'analysis' and self.content_data:
            # 分析结果的摘要显示
            analysis_type = self.content_data.get('analysis_type', '未知分析')
            return f"分析类型: {analysis_type}"
        else:
            return self.description[:50] + '...' if len(self.description) > 50 else self.description
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class DataSource(models.Model):
    """数据源配置表"""
    SOURCE_TYPE_CHOICES = [
        ('zhcw', '中彩网'),
        ('c500', '500彩票网'),
        ('api', '第三方API'),
        ('manual', '手动导入'),
    ]
    
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '停用'),
        ('error', '错误'),
        ('maintenance', '维护中'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='数据源名称')
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPE_CHOICES, verbose_name='数据源类型')
    base_url = models.URLField(verbose_name='基础URL')
    api_endpoint = models.CharField(max_length=200, blank=True, verbose_name='API端点')
    
    # 请求配置
    headers = models.JSONField(default=dict, blank=True, verbose_name='请求头配置')
    request_interval = models.PositiveIntegerField(default=5, verbose_name='请求间隔(秒)')
    timeout = models.PositiveIntegerField(default=30, verbose_name='超时时间(秒)')
    max_retries = models.PositiveIntegerField(default=3, verbose_name='最大重试次数')
    
    # 数据解析配置
    selector_config = models.JSONField(default=dict, blank=True, verbose_name='选择器配置')
    field_mapping = models.JSONField(default=dict, blank=True, verbose_name='字段映射')
    
    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    priority = models.PositiveIntegerField(default=1, verbose_name='优先级')
    
    # 统计信息
    last_success_time = models.DateTimeField(null=True, blank=True, verbose_name='最后成功时间')
    last_error_time = models.DateTimeField(null=True, blank=True, verbose_name='最后错误时间')
    last_error_message = models.TextField(blank=True, verbose_name='最后错误信息')
    total_success_count = models.PositiveIntegerField(default=0, verbose_name='成功次数')
    total_error_count = models.PositiveIntegerField(default=0, verbose_name='错误次数')
    
    # 说明和备注
    description = models.TextField(blank=True, verbose_name='描述说明')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'data_sources'
        verbose_name = '数据源配置'
        verbose_name_plural = '数据源配置'
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['source_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_enabled']),
            models.Index(fields=['priority']),
            models.Index(fields=['last_success_time']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.get_source_type_display()}) - {self.get_status_display()}'
    
    def update_success_stats(self):
        """更新成功统计"""
        self.last_success_time = timezone.now()
        self.total_success_count += 1
        self.status = 'active'
        self.save(update_fields=['last_success_time', 'total_success_count', 'status'])
    
    def update_error_stats(self, error_message):
        """更新错误统计"""
        self.last_error_time = timezone.now()
        self.last_error_message = error_message
        self.total_error_count += 1
        self.status = 'error'
        self.save(update_fields=['last_error_time', 'last_error_message', 'total_error_count', 'status'])


class CrawlLog(models.Model):
    """爬虫执行记录表"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('full_sync', '全量同步'),
        ('incremental_sync', '增量同步'),
        ('latest_sync', '最新数据同步'),
        ('manual_crawl', '手动爬取'),
        ('scheduled_crawl', '定时爬取'),
    ]
    
    # 基本信息
    task_id = models.CharField(max_length=100, unique=True, verbose_name='任务ID')
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, verbose_name='任务类型')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, verbose_name='数据源')
    
    # 执行状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='执行状态')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, verbose_name='执行耗时(秒)')
    
    # 执行参数
    parameters = models.JSONField(default=dict, blank=True, verbose_name='执行参数')
    target_date_range = models.JSONField(null=True, blank=True, verbose_name='目标日期范围')
    
    # 执行结果
    total_requests = models.PositiveIntegerField(default=0, verbose_name='总请求数')
    success_requests = models.PositiveIntegerField(default=0, verbose_name='成功请求数')
    failed_requests = models.PositiveIntegerField(default=0, verbose_name='失败请求数')
    
    # 数据统计
    records_found = models.PositiveIntegerField(default=0, verbose_name='发现记录数')
    records_created = models.PositiveIntegerField(default=0, verbose_name='新建记录数')
    records_updated = models.PositiveIntegerField(default=0, verbose_name='更新记录数')
    records_skipped = models.PositiveIntegerField(default=0, verbose_name='跳过记录数')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    error_traceback = models.TextField(blank=True, verbose_name='错误堆栈')
    
    # 执行日志
    execution_log = models.TextField(blank=True, verbose_name='执行日志')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'crawl_logs'
        verbose_name = '爬虫执行记录'
        verbose_name_plural = '爬虫执行记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
            models.Index(fields=['task_type']),
            models.Index(fields=['data_source']),
            models.Index(fields=['start_time']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.task_id} - {self.get_status_display()}'
    
    def start_execution(self):
        """开始执行"""
        self.status = 'running'
        self.start_time = timezone.now()
        self.save(update_fields=['status', 'start_time'])
    
    def complete_execution(self, success=True, error_message=''):
        """完成执行"""
        self.end_time = timezone.now()
        if self.start_time:
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        
        if success:
            self.status = 'success'
        else:
            self.status = 'failed'
            self.error_message = error_message
            
        self.save()
    
    def add_log(self, message):
        """添加执行日志"""
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] {message}\n'
        if self.execution_log:
            self.execution_log += log_entry
        else:
            self.execution_log = log_entry
        self.save(update_fields=['execution_log'])


class SystemConfig(models.Model):
    """系统配置表"""
    CONFIG_TYPE_CHOICES = [
        ('crawler', '爬虫配置'),
        ('analysis', '分析配置'),
        ('system', '系统配置'),
        ('notification', '通知配置'),
    ]
    
    # 配置标识
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES, verbose_name='配置类型')
    
    # 配置值
    value = models.TextField(verbose_name='配置值')
    default_value = models.TextField(blank=True, verbose_name='默认值')
    
    # 配置说明
    name = models.CharField(max_length=200, verbose_name='配置名称')
    description = models.TextField(blank=True, verbose_name='配置描述')
    
    # 配置属性
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_editable = models.BooleanField(default=True, verbose_name='是否可编辑')
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('string', '字符串'),
            ('integer', '整数'),
            ('float', '小数'),
            ('boolean', '布尔值'),
            ('json', 'JSON对象'),
        ],
        default='string',
        verbose_name='数据类型'
    )
    
    # 验证规则
    validation_rules = models.JSONField(default=dict, blank=True, verbose_name='验证规则')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['config_type', 'key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['config_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.key})'
    
    def get_typed_value(self):
        """根据数据类型返回正确的值"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        else:
            return self.value
    
    def set_typed_value(self, value):
        """根据数据类型设置值"""
        if self.data_type == 'json':
            import json
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = str(value)
        self.save()


class SystemLog(models.Model):
    """系统日志表"""
    LOG_LEVEL_CHOICES = [
        ('debug', 'DEBUG'),
        ('info', 'INFO'),
        ('warning', 'WARNING'),
        ('error', 'ERROR'),
        ('critical', 'CRITICAL'),
    ]
    
    LOG_TYPE_CHOICES = [
        ('system', '系统日志'),
        ('user', '用户日志'),
        ('crawler', '爬虫日志'),
        ('api', 'API日志'),
        ('security', '安全日志'),
    ]
    
    # 日志基本信息
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, verbose_name='日志级别')
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, verbose_name='日志类型')
    
    # 日志内容
    message = models.TextField(verbose_name='日志消息')
    module = models.CharField(max_length=100, blank=True, verbose_name='模块名称')
    function = models.CharField(max_length=100, blank=True, verbose_name='函数名称')
    
    # 用户信息
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    
    # 请求信息
    request_method = models.CharField(max_length=10, blank=True, verbose_name='请求方法')
    request_path = models.CharField(max_length=500, blank=True, verbose_name='请求路径')
    request_data = models.JSONField(null=True, blank=True, verbose_name='请求数据')
    
    # 异常信息
    exception_type = models.CharField(max_length=200, blank=True, verbose_name='异常类型')
    exception_message = models.TextField(blank=True, verbose_name='异常消息')
    traceback = models.TextField(blank=True, verbose_name='异常堆栈')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'system_logs'
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['log_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f'[{self.get_level_display()}] {self.message[:50]}...'
    
    @classmethod
    def log(cls, level, message, log_type='system', user=None, request=None, exception=None, **kwargs):
        """便捷的日志记录方法"""
        log_data = {
            'level': level,
            'log_type': log_type,
            'message': message,
            'user': user,
        }
        
        # 处理请求信息
        if request:
            log_data.update({
                'ip_address': cls._get_client_ip(request),
                'request_method': request.method,
                'request_path': request.path,
                'request_data': cls._get_request_data(request),
            })
        
        # 处理异常信息
        if exception:
            import traceback
            log_data.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc(),
            })
        
        # 添加其他参数
        log_data.update(kwargs)
        
        return cls.objects.create(**log_data)
    
    @staticmethod
    def _get_client_ip(request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _get_request_data(request):
        """获取请求数据"""
        try:
            if request.method == 'GET':
                return dict(request.GET)
            elif request.method == 'POST':
                return dict(request.POST)
            else:
                return {}
        except:
            return {}
