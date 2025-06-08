from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import LotteryResult, Statistics, Prediction, UserAnalysisLog, DataSource, CrawlLog, UserProfile


class LotteryResultSerializer(serializers.ModelSerializer):
    """开奖结果序列化器"""
    red_balls = serializers.SerializerMethodField()
    all_balls = serializers.SerializerMethodField()
    
    class Meta:
        model = LotteryResult
        fields = [
            'id', 'issue', 'draw_date', 
            'red_ball_1', 'red_ball_2', 'red_ball_3', 
            'red_ball_4', 'red_ball_5', 'red_ball_6', 
            'blue_ball', 'red_balls', 'all_balls',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_red_balls(self, obj):
        """获取红球号码列表"""
        return obj.get_red_balls()
    
    def get_all_balls(self, obj):
        """获取所有号码"""
        return obj.get_all_balls()


class StatisticsSerializer(serializers.ModelSerializer):
    """统计分析序列化器"""
    ball_type_display = serializers.CharField(source='get_ball_type_display', read_only=True)
    
    class Meta:
        model = Statistics
        fields = [
            'id', 'ball_number', 'ball_type', 'ball_type_display',
            'appear_count', 'last_appear_issue', 'max_interval', 'avg_interval',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PredictionSerializer(serializers.ModelSerializer):
    """预测记录序列化器"""
    algorithm_display = serializers.CharField(source='get_algorithm_display', read_only=True)
    predicted_numbers = serializers.SerializerMethodField()
    
    class Meta:
        model = Prediction
        fields = [
            'id', 'algorithm', 'algorithm_display', 'target_issue',
            'predicted_red_balls', 'predicted_blue_ball', 'predicted_numbers',
            'confidence', 'is_accurate', 'red_match_count', 'blue_match',
            'accuracy_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'accuracy_score']
    
    def get_predicted_numbers(self, obj):
        """获取预测号码的完整信息"""
        return obj.get_predicted_numbers()


class UserAnalysisLogSerializer(serializers.ModelSerializer):
    """用户分析日志序列化器"""
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)
    
    class Meta:
        model = UserAnalysisLog
        fields = [
            'id', 'analysis_type', 'analysis_type_display',
            'parameters', 'result_summary', 'created_at'
        ]
        read_only_fields = ['created_at']


class LotteryResultCreateSerializer(serializers.ModelSerializer):
    """开奖结果创建序列化器（用于数据导入）"""
    
    class Meta:
        model = LotteryResult
        fields = [
            'issue', 'draw_date',
            'red_ball_1', 'red_ball_2', 'red_ball_3',
            'red_ball_4', 'red_ball_5', 'red_ball_6',
            'blue_ball'
        ]
    
    def validate(self, data):
        """验证开奖数据"""
        # 验证红球号码范围
        red_balls = [
            data['red_ball_1'], data['red_ball_2'], data['red_ball_3'],
            data['red_ball_4'], data['red_ball_5'], data['red_ball_6']
        ]
        
        for ball in red_balls:
            if not (1 <= ball <= 33):
                raise serializers.ValidationError(f'红球号码必须在1-33之间，当前值：{ball}')
        
        # 验证红球号码不重复
        if len(set(red_balls)) != 6:
            raise serializers.ValidationError('红球号码不能重复')
        
        # 验证蓝球号码范围
        if not (1 <= data['blue_ball'] <= 16):
            raise serializers.ValidationError(f'蓝球号码必须在1-16之间，当前值：{data["blue_ball"]}')
        
        return data


class PredictionCreateSerializer(serializers.ModelSerializer):
    """预测记录创建序列化器"""
    
    class Meta:
        model = Prediction
        fields = [
            'algorithm', 'target_issue',
            'predicted_red_balls', 'predicted_blue_ball',
            'confidence'
        ]
    
    def validate_predicted_red_balls(self, value):
        """验证预测红球"""
        if not isinstance(value, list) or len(value) != 6:
            raise serializers.ValidationError('预测红球必须是包含6个号码的列表')
        
        for ball in value:
            if not isinstance(ball, int) or not (1 <= ball <= 33):
                raise serializers.ValidationError('红球号码必须是1-33之间的整数')
        
        if len(set(value)) != 6:
            raise serializers.ValidationError('红球号码不能重复')
        
        return value
    
    def validate_predicted_blue_ball(self, value):
        """验证预测蓝球"""
        if not (1 <= value <= 16):
            raise serializers.ValidationError('蓝球号码必须在1-16之间')
        return value


class DataSourceSerializer(serializers.ModelSerializer):
    """数据源配置序列化器"""
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'source_type', 'source_type_display', 'base_url', 'api_endpoint',
            'headers', 'request_interval', 'timeout', 'max_retries',
            'selector_config', 'field_mapping',
            'status', 'status_display', 'is_enabled', 'priority',
            'last_success_time', 'last_error_time', 'last_error_message',
            'total_success_count', 'total_error_count', 'success_rate',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'last_success_time', 'last_error_time', 'last_error_message',
            'total_success_count', 'total_error_count', 'success_rate',
            'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        """计算成功率"""
        total = obj.total_success_count + obj.total_error_count
        if total == 0:
            return None
        return round((obj.total_success_count / total) * 100, 2)


class DataSourceCreateSerializer(serializers.ModelSerializer):
    """数据源创建序列化器"""
    
    class Meta:
        model = DataSource
        fields = [
            'name', 'source_type', 'base_url', 'api_endpoint',
            'headers', 'request_interval', 'timeout', 'max_retries',
            'selector_config', 'field_mapping',
            'is_enabled', 'priority', 'description'
        ]
    
    def validate_base_url(self, value):
        """验证基础URL"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError('基础URL必须以http://或https://开头')
        return value
    
    def validate_request_interval(self, value):
        """验证请求间隔"""
        if value < 1:
            raise serializers.ValidationError('请求间隔不能小于1秒')
        return value


class CrawlLogSerializer(serializers.ModelSerializer):
    """爬虫执行记录序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    data_source_type = serializers.CharField(source='data_source.source_type', read_only=True)
    
    class Meta:
        model = CrawlLog
        fields = [
            'id', 'task_id', 'task_type', 'task_type_display',
            'data_source', 'data_source_name', 'data_source_type',
            'status', 'status_display', 'start_time', 'end_time', 'duration_seconds',
            'parameters', 'target_date_range',
            'total_requests', 'success_requests', 'failed_requests',
            'records_found', 'records_created', 'records_updated', 'records_skipped',
            'error_message', 'error_traceback', 'execution_log',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'start_time', 'end_time', 'duration_seconds',
            'total_requests', 'success_requests', 'failed_requests',
            'records_found', 'records_created', 'records_updated', 'records_skipped',
            'error_message', 'error_traceback', 'execution_log',
            'created_at', 'updated_at'
        ]


class CrawlLogCreateSerializer(serializers.ModelSerializer):
    """爬虫执行记录创建序列化器"""
    
    class Meta:
        model = CrawlLog
        fields = [
            'task_id', 'task_type', 'data_source',
            'parameters', 'target_date_range'
        ]
    
    def validate_task_id(self, value):
        """验证任务ID唯一性"""
        if CrawlLog.objects.filter(task_id=value).exists():
            raise serializers.ValidationError('任务ID已存在')
        return value


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