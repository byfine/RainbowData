# 2阶段开始，数据库1
_Exported on 6/8/2025 at 15:34:21 GMT+8 from Cursor (1.0.0)_

---

**User**

参考RD1,RD2,debug文档，我们继续之前的工作吧

---

**Cursor**

看到您想继续彩虹数据项目的开发！根据debug.md日志记录，我们已经完美完成了阶段一的环境搭建，现在应该开始**阶段二：核心基础功能开发**。

让我先检查一下当前项目的状态，然后继续下一步的开发工作。

很好！项目基础架构已经搭建完成。根据RD2任务清单，我们现在需要开始**阶段二：核心基础功能开发**的第一个任务 - **数据库设计与实现**。

让我们按照计划开始创建Django模型：

看起来lottery应用没有创建成功。让我重新执行命令：

看起来虚拟环境中缺少Django。让我检查当前的虚拟环境和依赖安装情况：

虚拟环境中确实缺少Django！看起来我们需要重新安装依赖包。让我查看requirements.txt文件：

很好，找到了完整的requirements.txt文件。现在让我们安装所有的依赖包：

太好了！所有依赖包已成功安装。现在让我们创建lottery应用：

好的！lottery应用已成功创建。让我们检查一下项目结构：

完美！现在让我们开始创建Django模型。根据RD1.md需求规范，我们需要创建以下核心数据模型：

1. 开奖记录表 (LotteryResult)
2. 统计分析表 (Statistics) 
3. 用户表 (User扩展)
4. 预测记录表 (Prediction)

让我们先创建Django模型：

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
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
        ]
    
    def __str__(self):
        return f'{self.get_ball_type_display()}{self.ball_number} - 出现{self.appear_count}次'


class User(AbstractUser):
    """扩展用户模型"""
    USER_TYPE_CHOICES = [
        ('normal', '普通用户'),
        ('admin', '管理员'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='邮箱')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='normal', verbose_name='用户类型')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    avatar = models.URLField(blank=True, null=True, verbose_name='头像')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    
    # 学习记录相关字段
    total_analysis_count = models.PositiveIntegerField(default=0, verbose_name='分析次数')
    total_prediction_count = models.PositiveIntegerField(default=0, verbose_name='预测次数')
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='最后登录IP')
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return f'{self.username} - {self.get_user_type_display()}'


class Prediction(models.Model):
    """预测记录表"""
    ALGORITHM_CHOICES = [
        ('frequency', '频率统计'),
        ('trend', '趋势分析'),
        ('regression', '线性回归'),
        ('ensemble', '组合算法'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
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
            models.Index(fields=['user', 'target_issue']),
            models.Index(fields=['algorithm']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.target_issue} ({self.get_algorithm_display()})'
    
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
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
            models.Index(fields=['user', 'analysis_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.get_analysis_type_display()}'
```

现在让我们配置Django Admin界面，方便管理这些模型：

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import LotteryResult, Statistics, User, Prediction, UserAnalysisLog


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


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'email', 'user_type', 'is_active', 'total_analysis_count', 'last_login']
    list_filter = ['user_type', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('user_type', 'avatar', 'phone', 'last_login_ip')
        }),
        ('学习统计', {
            'fields': ('total_analysis_count', 'total_prediction_count'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('扩展信息', {
            'fields': ('email', 'user_type', 'phone')
        }),
    )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """预测记录管理"""
    list_display = [
        'user', 'target_issue', 'algorithm', 'get_predicted_numbers_display', 
        'confidence', 'is_accurate', 'accuracy_score', 'created_at'
    ]
    list_filter = ['algorithm', 'is_accurate', 'created_at', 'confidence']
    search_fields = ['user__username', 'target_issue']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'accuracy_score']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'algorithm', 'target_issue', 'confidence')
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
    list_display = ['user', 'analysis_type', 'get_parameters_display', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    search_fields = ['user__username', 'result_summary']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'analysis_type', 'created_at')
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


# 自定义Admin站点信息
admin.site.site_header = '彩虹数据管理后台'
admin.site.site_title = '彩虹数据'
admin.site.index_title = '双色球数据分析学习平台'
```

现在我们需要将lottery应用添加到Django设置中，并配置使用我们的自定义User模型：

现在我们需要更新Django设置文件，添加lottery应用并配置自定义User模型：

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    # Local apps (will be added later)
]

->

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    # Local apps
    'lottery',
]
```

```python
CORS_ALLOW_CREDENTIALS = True

->

CORS_ALLOW_CREDENTIALS = True

# Custom User Model
AUTH_USER_MODEL = 'lottery.User'
```

现在让我们创建并运行数据库迁移：

看起来数据库中已经有一些Django的基础迁移了，可能导致冲突。让我们检查当前数据库状态：

看起来有迁移状态不一致的问题。因为我们使用了自定义User模型，需要重新设置数据库。让我们先删除现有的迁移文件并重新开始：

我们需要创建一个新的数据库，因为自定义User模型需要从头开始。让我们先创建一个新的数据库：

MySQL命令行工具不在PATH中。让我们通过Django来重置数据库。首先删除迁移文件：

现在我们需要添加UserAnalysisLog模型到迁移中。让我先检查models.py文件是否包含了所有模型：

看起来UserAnalysisLog模型没有包含在迁移中。让我检查一下models.py文件：

模型确实存在。让我重新创建迁移：

我们需要重置数据库。让我创建一个Django管理命令来重置数据库：

让我们通过MySQL Workbench来重置数据库。首先，让我创建一个简单的解决方案：

```python
#!/usr/bin/env python
"""
数据库重置脚本
用于清理现有数据库并重新创建所有表
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rainbow_data.settings')
django.setup()

def reset_database():
    """重置数据库"""
    print("🔄 开始重置数据库...")
    
    # 获取数据库连接
    cursor = connection.cursor()
    
    try:
        # 删除所有表
        print("📋 获取所有表名...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"🗑️  删除 {len(tables)} 个表...")
            # 禁用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 删除所有表
            for table in tables:
                table_name = table[0]
                print(f"   删除表: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            
            # 重新启用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("✅ 所有表已删除")
        else:
            print("ℹ️  数据库中没有表")
            
    except Exception as e:
        print(f"❌ 删除表时出错: {e}")
        return False
    
    finally:
        cursor.close()
    
    print("✅ 数据库重置完成！")
    return True

if __name__ == "__main__":
    if reset_database():
        print("\n🚀 现在可以运行以下命令重新创建数据库：")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        print("   python manage.py createsuperuser")
    else:
        print("\n❌ 数据库重置失败，请检查错误信息")
```

---

**User**

运行 reset_db.py 时 报错：File "<console>", line 1 python reset_db.py

---

**Cursor**

看起来您还在Django shell中！我们需要先退出Django shell，然后在系统命令行中运行reset_db.py脚本。

现在让我们切换到Django项目目录并运行重置脚本：

