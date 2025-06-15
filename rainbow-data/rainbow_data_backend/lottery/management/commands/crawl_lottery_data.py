"""
彩票数据爬取管理命令
==================

支持命令行方式启动数据爬取任务的Django管理命令。

使用示例：
    # 爬取最新数据
    python manage.py crawl_lottery_data --source zhcw --type latest
    
    # 爬取历史数据
    python manage.py crawl_lottery_data --source zhcw --type history --start-date 2024-01-01 --end-date 2024-12-31
    
    # 增量爬取
    python manage.py crawl_lottery_data --source zhcw --type incremental
    
    # 试运行模式
    python manage.py crawl_lottery_data --source zhcw --type latest --dry-run
"""

import uuid
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from typing import Dict, List

from lottery.models import DataSource, CrawlLog
from lottery.scrapers import ZhcwScraper


class Command(BaseCommand):
    """
    彩票数据爬取命令类
    """
    
    help = '爬取彩票开奖数据'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--source',
            type=str,
            required=True,
            choices=['zhcw', 'c500', 'api'],
            help='数据源类型 (zhcw: 中彩网, c500: 500彩票网, api: 第三方API)'
        )
        
        parser.add_argument(
            '--type',
            type=str,
            required=True,
            choices=['latest', 'history', 'incremental'],
            help='爬取类型 (latest: 最新数据, history: 历史数据, incremental: 增量数据)'
        )
        
        parser.add_argument(
            '--start-date',
            type=str,
            help='开始日期 (格式: YYYY-MM-DD，历史数据爬取时必填)'
        )
        
        parser.add_argument(
            '--end-date',
            type=str,
            help='结束日期 (格式: YYYY-MM-DD，历史数据爬取时必填)'
        )
        
        parser.add_argument(
            '--last-issue',
            type=str,
            help='最后期号 (增量爬取时可选，不填则自动从数据库获取)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不保存数据到数据库'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，即使数据源未启用'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='详细输出模式'
        )
    
    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            # 设置日志级别
            if options['verbose']:
                import logging
                logging.basicConfig(level=logging.INFO)
            
            # 输出开始信息
            self.stdout.write(
                self.style.SUCCESS(
                    f"开始爬取彩票数据: {options['source']} - {options['type']}"
                )
            )
            
            # 验证参数
            self._validate_options(options)
            
            # 获取数据源
            data_source = self._get_data_source(options['source'], options['force'])
            
            # 创建爬虫实例
            scraper = self._create_scraper(data_source, options['source'])
            
            # 执行爬取任务
            results = self._execute_crawl_task(scraper, options)
            
            # 输出结果
            self._output_results(results, options)
            
        except Exception as e:
            raise CommandError(f"爬取失败: {str(e)}")
    
    def _validate_options(self, options: Dict) -> None:
        """
        验证命令行选项
        
        Args:
            options: 命令行选项字典
        """
        crawl_type = options['type']
        
        # 历史数据爬取需要日期参数
        if crawl_type == 'history':
            if not options['start_date'] or not options['end_date']:
                raise CommandError("历史数据爬取需要指定 --start-date 和 --end-date 参数")
            
            # 验证日期格式
            try:
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
                
                if start_date > end_date:
                    raise CommandError("开始日期不能晚于结束日期")
                
                if end_date > date.today():
                    raise CommandError("结束日期不能是未来日期")
                    
            except ValueError:
                raise CommandError("日期格式错误，请使用 YYYY-MM-DD 格式")
    
    def _get_data_source(self, source_type: str, force: bool = False) -> DataSource:
        """
        获取数据源对象
        
        Args:
            source_type: 数据源类型
            force: 是否强制执行
            
        Returns:
            DataSource: 数据源对象
        """
        try:
            data_source = DataSource.objects.get(source_type=source_type)
            
            if not data_source.is_enabled and not force:
                raise CommandError(f"数据源 {source_type} 未启用，使用 --force 参数强制执行")
            
            if data_source.status == 'maintenance':
                self.stdout.write(
                    self.style.WARNING(f"数据源 {source_type} 正在维护中")
                )
            
            return data_source
            
        except DataSource.DoesNotExist:
            raise CommandError(f"数据源 {source_type} 不存在，请先在管理后台创建")
    
    def _create_scraper(self, data_source: DataSource, source_type: str):
        """
        创建爬虫实例
        
        Args:
            data_source: 数据源对象
            source_type: 数据源类型
            
        Returns:
            BaseScraper: 爬虫实例
        """
        if source_type == 'zhcw':
            return ZhcwScraper(data_source)
        elif source_type == 'c500':
            # TODO: 实现500彩票网爬虫
            raise CommandError("500彩票网爬虫尚未实现")
        elif source_type == 'api':
            # TODO: 实现API爬虫
            raise CommandError("API爬虫尚未实现")
        else:
            raise CommandError(f"不支持的数据源类型: {source_type}")
    
    def _execute_crawl_task(self, scraper, options: Dict) -> List[Dict]:
        """
        执行爬取任务
        
        Args:
            scraper: 爬虫实例
            options: 命令行选项
            
        Returns:
            List[Dict]: 爬取结果
        """
        crawl_type = options['type']
        
        try:
            if crawl_type == 'latest':
                results = scraper.fetch_latest()
                
            elif crawl_type == 'history':
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
                results = scraper.fetch_history(start_date, end_date)
                
            elif crawl_type == 'incremental':
                last_issue = options.get('last_issue')
                results = scraper.fetch_incremental(last_issue)
                
            else:
                raise CommandError(f"不支持的爬取类型: {crawl_type}")
            
            return results
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"爬取过程中发生错误: {str(e)}")
            )
            raise
    
    def _output_results(self, results: List[Dict], options: Dict) -> None:
        """
        输出爬取结果
        
        Args:
            results: 爬取结果
            options: 命令行选项
        """
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING("试运行模式，数据未保存到数据库")
            )
        
        if not results:
            self.stdout.write(
                self.style.WARNING("未获取到任何数据")
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f"成功获取 {len(results)} 条数据:")
        )
        
        # 输出详细信息
        if options['verbose']:
            for i, item in enumerate(results[:10], 1):  # 最多显示10条
                issue = item.get('issue', '未知')
                draw_date = item.get('draw_date', '未知')
                red_balls = item.get('red_balls', [])
                blue_ball = item.get('blue_ball', '未知')
                
                self.stdout.write(f"  {i}. 期号: {issue}, 日期: {draw_date}")
                self.stdout.write(f"     红球: {red_balls}, 蓝球: {blue_ball}")
            
            if len(results) > 10:
                self.stdout.write(f"  ... 还有 {len(results) - 10} 条数据")
        
        # 输出统计信息
        if results:
            first_date = min(item['draw_date'] for item in results if item.get('draw_date'))
            last_date = max(item['draw_date'] for item in results if item.get('draw_date'))
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"数据时间范围: {first_date} ~ {last_date}"
                )
            )
    
    def _create_manual_crawl_log(self, data_source: DataSource, options: Dict) -> CrawlLog:
        """
        创建手动爬取日志
        
        Args:
            data_source: 数据源对象
            options: 命令行选项
            
        Returns:
            CrawlLog: 爬取日志对象
        """
        task_id = f"manual_{data_source.source_type}_{uuid.uuid4().hex[:8]}"
        
        parameters = {
            'source': options['source'],
            'type': options['type'],
            'dry_run': options['dry_run'],
            'force': options['force'],
            'manual': True
        }
        
        if options['start_date']:
            parameters['start_date'] = options['start_date']
        if options['end_date']:
            parameters['end_date'] = options['end_date']
        if options['last_issue']:
            parameters['last_issue'] = options['last_issue']
        
        crawl_log = CrawlLog.objects.create(
            task_id=task_id,
            task_type='manual_crawl',
            data_source=data_source,
            parameters=parameters,
            status='pending'
        )
        
        return crawl_log 