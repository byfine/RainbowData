from django.core.management.base import BaseCommand
from lottery.models import SystemConfig


class Command(BaseCommand):
    help = '初始化系统配置'

    def handle(self, *args, **options):
        """执行初始化系统配置"""
        
        # 爬虫配置
        crawler_configs = [
            {
                'key': 'crawler.default_interval',
                'config_type': 'crawler',
                'name': '默认爬取间隔',
                'description': '爬虫默认请求间隔时间（秒）',
                'value': '5',
                'default_value': '5',
                'data_type': 'integer',
                'validation_rules': {'min': 1, 'max': 60}
            },
            {
                'key': 'crawler.max_retries',
                'config_type': 'crawler',
                'name': '最大重试次数',
                'description': '爬虫请求失败时的最大重试次数',
                'value': '3',
                'default_value': '3',
                'data_type': 'integer',
                'validation_rules': {'min': 0, 'max': 10}
            },
            {
                'key': 'crawler.timeout',
                'config_type': 'crawler',
                'name': '请求超时时间',
                'description': '单次爬虫请求的超时时间（秒）',
                'value': '30',
                'default_value': '30',
                'data_type': 'integer',
                'validation_rules': {'min': 5, 'max': 300}
            },
        ]
        
        # 分析配置
        analysis_configs = [
            {
                'key': 'analysis.max_prediction_history',
                'config_type': 'analysis',
                'name': '最大预测历史记录数',
                'description': '每个用户最多保存的预测记录数量',
                'value': '50',
                'default_value': '50',
                'data_type': 'integer',
                'validation_rules': {'min': 10, 'max': 200}
            },
            {
                'key': 'analysis.default_algorithm',
                'config_type': 'analysis',
                'name': '默认预测算法',
                'description': '系统默认使用的预测算法',
                'value': 'frequency',
                'default_value': 'frequency',
                'data_type': 'string',
                'validation_rules': {'enum': ['frequency', 'trend', 'regression', 'ensemble']}
            },
        ]
        
        # 系统配置
        system_configs = [
            {
                'key': 'system.site_name',
                'config_type': 'system',
                'name': '网站名称',
                'description': '网站显示的名称',
                'value': '彩虹数据',
                'default_value': '彩虹数据',
                'data_type': 'string',
                'validation_rules': {'max_length': 50}
            },
            {
                'key': 'system.maintenance_mode',
                'config_type': 'system',
                'name': '维护模式',
                'description': '是否启用维护模式',
                'value': 'false',
                'default_value': 'false',
                'data_type': 'boolean',
                'validation_rules': {}
            },
        ]
        
        # 合并所有配置
        all_configs = crawler_configs + analysis_configs + system_configs
        
        created_count = 0
        updated_count = 0
        
        for config_data in all_configs:
            config, created = SystemConfig.objects.get_or_create(
                key=config_data['key'],
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建配置: {config.name} ({config.key})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠ 配置已存在: {config.name} ({config.key})')
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'系统配置初始化完成!'))
        self.stdout.write(f'  创建配置项: {created_count} 个')
        self.stdout.write(f'  已存在配置项: {updated_count} 个')
        self.stdout.write(f'  总配置项: {SystemConfig.objects.count()} 个') 