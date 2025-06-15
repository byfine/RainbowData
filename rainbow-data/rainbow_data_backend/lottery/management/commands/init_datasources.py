"""
数据源初始化管理命令
==================

用于在数据库中创建和初始化数据源配置的Django管理命令。

使用示例：
    # 初始化所有数据源
    python manage.py init_datasources
    
    # 只初始化特定数据源
    python manage.py init_datasources --source zhcw
    
    # 强制覆盖现有配置
    python manage.py init_datasources --force
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from typing import Dict, Any

from lottery.models import DataSource
from lottery.scrapers.scraper_config import scraper_config


class Command(BaseCommand):
    """
    数据源初始化命令类
    """
    
    help = '初始化数据源配置'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--source',
            type=str,
            choices=['zhcw', 'c500', 'api'],
            help='指定要初始化的数据源类型，不指定则初始化所有数据源'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制覆盖现有数据源配置'
        )
        
        parser.add_argument(
            '--disable-existing',
            action='store_true',
            help='禁用现有数据源（不删除，仅标记为停用）'
        )
    
    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            source_filter = options.get('source')
            force = options['force']
            disable_existing = options['disable_existing']
            
            self.stdout.write(
                self.style.SUCCESS("开始初始化数据源配置...")
            )
            
            # 获取要初始化的数据源列表
            if source_filter:
                sources_to_init = [source_filter]
            else:
                sources_to_init = scraper_config.get_supported_sources()
            
            # 禁用现有数据源（如果指定）
            if disable_existing:
                self._disable_existing_sources(sources_to_init)
            
            # 初始化数据源
            created_count = 0
            updated_count = 0
            
            with transaction.atomic():
                for source_type in sources_to_init:
                    created, updated = self._init_data_source(source_type, force)
                    if created:
                        created_count += 1
                    elif updated:
                        updated_count += 1
            
            # 输出结果
            self.stdout.write(
                self.style.SUCCESS(
                    f"数据源初始化完成: 新建 {created_count} 个, 更新 {updated_count} 个"
                )
            )
            
            # 显示当前数据源状态
            self._show_datasource_status()
            
        except Exception as e:
            raise CommandError(f"初始化失败: {str(e)}")
    
    def _disable_existing_sources(self, source_types: list) -> None:
        """
        禁用现有数据源
        
        Args:
            source_types: 要禁用的数据源类型列表
        """
        disabled_count = DataSource.objects.filter(
            source_type__in=source_types,
            is_enabled=True
        ).update(is_enabled=False, status='inactive')
        
        if disabled_count > 0:
            self.stdout.write(
                self.style.WARNING(f"已禁用 {disabled_count} 个现有数据源")
            )
    
    def _init_data_source(self, source_type: str, force: bool = False) -> tuple:
        """
        初始化单个数据源
        
        Args:
            source_type: 数据源类型
            force: 是否强制覆盖
            
        Returns:
            tuple: (是否新建, 是否更新)
        """
        try:
            # 获取默认配置
            config = scraper_config.get_config(source_type)
            if not config:
                self.stdout.write(
                    self.style.ERROR(f"无法获取 {source_type} 的配置")
                )
                return False, False
            
            # 检查是否已存在
            existing = DataSource.objects.filter(source_type=source_type).first()
            
            if existing and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f"数据源 {source_type} 已存在，使用 --force 参数强制覆盖"
                    )
                )
                return False, False
            
            # 准备数据源数据
            datasource_data = self._prepare_datasource_data(source_type, config)
            
            if existing:
                # 更新现有数据源
                for field, value in datasource_data.items():
                    setattr(existing, field, value)
                existing.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f"✓ 已更新数据源: {source_type}")
                )
                return False, True
            else:
                # 创建新数据源
                DataSource.objects.create(**datasource_data)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✓ 已创建数据源: {source_type}")
                )
                return True, False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ 初始化 {source_type} 失败: {str(e)}")
            )
            return False, False
    
    def _prepare_datasource_data(self, source_type: str, config: Dict[str, Any]) -> Dict:
        """
        准备数据源数据
        
        Args:
            source_type: 数据源类型
            config: 配置字典
            
        Returns:
            Dict: 数据源数据
        """
        # 基础数据
        data = {
            'name': config.get('name', f'{source_type.upper()}数据源'),
            'source_type': source_type,
            'base_url': config.get('base_url', ''),
            'is_enabled': True,
            'status': 'active',
            'priority': self._get_default_priority(source_type)
        }
        
        # 请求配置
        request_config = config.get('request', {})
        if request_config:
            data.update({
                'request_interval': request_config.get('interval', 5),
                'timeout': request_config.get('timeout', 30),
                'max_retries': request_config.get('max_retries', 3),
                'headers': request_config.get('headers', {})
            })
        
        # 选择器配置
        selectors = config.get('selectors', {})
        if selectors:
            data['selector_config'] = selectors
        
        # 字段映射配置
        field_mapping = config.get('field_mapping', {})
        if field_mapping:
            data['field_mapping'] = field_mapping
        
        return data
    
    def _get_default_priority(self, source_type: str) -> int:
        """
        获取默认优先级
        
        Args:
            source_type: 数据源类型
            
        Returns:
            int: 优先级（数字越小优先级越高）
        """
        priority_map = {
            'zhcw': 1,    # 官方网站，最高优先级
            'c500': 2,    # 知名彩票网站，次优先级
            'api': 3      # 第三方API，最低优先级
        }
        return priority_map.get(source_type, 10)
    
    def _show_datasource_status(self) -> None:
        """显示当前数据源状态"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("当前数据源状态:"))
        self.stdout.write("=" * 60)
        
        datasources = DataSource.objects.all().order_by('priority')
        
        if not datasources:
            self.stdout.write(self.style.WARNING("没有配置任何数据源"))
            return
        
        for ds in datasources:
            status_color = self.style.SUCCESS if ds.is_enabled else self.style.ERROR
            status_text = "启用" if ds.is_enabled else "禁用"
            
            self.stdout.write(
                f"• {ds.name} ({ds.source_type})"
            )
            self.stdout.write(
                f"  状态: {status_color(status_text)} | "
                f"优先级: {ds.priority} | "
                f"URL: {ds.base_url}"
            )
            self.stdout.write(
                f"  间隔: {ds.request_interval}s | "
                f"超时: {ds.timeout}s | "
                f"重试: {ds.max_retries}次"
            )
            
            if ds.last_success_time:
                self.stdout.write(
                    f"  最后成功: {ds.last_success_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            if ds.last_error_time and ds.last_error_message:
                self.stdout.write(
                    self.style.WARNING(
                        f"  最后错误: {ds.last_error_time.strftime('%Y-%m-%d %H:%M:%S')} - {ds.last_error_message[:50]}..."
                    )
                )
            
            self.stdout.write("")  # 空行分隔
        
        self.stdout.write("=" * 60) 