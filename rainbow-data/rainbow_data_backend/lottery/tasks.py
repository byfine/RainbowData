"""
Celery异步任务定义
包含爬虫数据获取、统计更新、数据检查等任务
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from celery import shared_task
from celery.exceptions import Retry

from .models import (
    LotteryResult, Statistics, CrawlLog, DataSource,
    UserAnalysisLog
)
from lottery.scrapers.c500_scraper_enhanced import C500ScraperEnhanced
from lottery.scrapers.data_cleaner import DataCleaner

# 配置日志
logger = logging.getLogger(__name__)


@shared_task(bind=True)
def test_simple_crawler_task(self):
    """
    超级简单的爬虫测试任务
    """
    task_id = self.request.id
    logger.info(f"简单爬虫测试任务 {task_id} 开始执行")
    
    try:
        # 只做最基本的操作
        from lottery.models import DataSource
        data_source, created = DataSource.objects.get_or_create(
            name='500彩票网',
            defaults={
                'source_type': 'c500',
                'base_url': 'https://datachart.500.com/ssq/',
                'is_enabled': True,
                'status': 'active'
            }
        )
        
        logger.info(f"简单爬虫测试任务 {task_id} 完成")
        return {
            'task_id': task_id,
            'success': True,
            'message': '简单爬虫测试成功'
        }
        
    except Exception as exc:
        logger.error(f"简单爬虫测试任务 {task_id} 失败：{exc}")
        return {
            'task_id': task_id,
            'success': False,
            'error': str(exc)
        }


@shared_task
def crawl_latest_data_simple():
    """
    爬取最新数据的完整任务（包含数据库存储）
    """
    try:
        logger.info("开始执行爬取最新数据任务")
        
        # 导入爬虫模块
        from lottery.scrapers.c500_scraper_enhanced import C500ScraperEnhanced
        from lottery.scrapers.data_cleaner import DataCleaner
        from lottery.models import LotteryResult, CrawlLog, DataSource
        from django.utils import timezone
        
        # 获取或创建数据源记录
        data_source, created = DataSource.objects.get_or_create(
            name='500彩票网',
            defaults={
                'source_type': 'c500',
                'base_url': 'https://datachart.500.com/ssq/',
                'is_enabled': True,
                'status': 'active'
            }
        )
        
        # 创建爬取日志
        crawl_log = CrawlLog.objects.create(
            data_source=data_source,
            start_time=timezone.now(),
            status='running'
        )
        
        try:
            # 初始化爬虫
            scraper = C500ScraperEnhanced()
            logger.info("爬虫初始化成功")
            
            # 执行爬取
            crawl_result = scraper.crawl_latest_data()
            logger.info(f"爬取执行完成: {crawl_result['success']}")
            
            if crawl_result['success']:
                # 获取爬取的数据
                raw_data = crawl_result.get('data', [])
                logger.info(f"获取到 {len(raw_data)} 条原始数据")
                
                # 数据清洗
                cleaner = DataCleaner(source_type='c500')
                clean_data = []
                
                for item in raw_data:
                    cleaned = cleaner.clean_lottery_data(item)
                    if cleaned:
                        clean_data.append(cleaned)
                
                logger.info(f"清洗后得到 {len(clean_data)} 条有效数据")
                
                # 存储到数据库
                new_records = 0
                updated_records = 0
                
                for data in clean_data:
                    # 检查是否已存在
                    existing = LotteryResult.objects.filter(issue=data['issue']).first()
                    
                    if existing:
                        # 更新现有记录
                        for key, value in data.items():
                            setattr(existing, key, value)
                        existing.save()
                        updated_records += 1
                        logger.info(f"更新期号 {data['issue']} 的数据")
                    else:
                        # 创建新记录
                        LotteryResult.objects.create(**data)
                        new_records += 1
                        logger.info(f"创建期号 {data['issue']} 的新数据")
                
                # 更新爬取日志
                crawl_log.end_time = timezone.now()
                crawl_log.status = 'completed'
                crawl_log.records_found = len(clean_data)
                crawl_log.records_saved = new_records + updated_records
                crawl_log.records_updated = updated_records
                crawl_log.save()
                
                return {
                    'success': True,
                    'data_source': '500彩票网',
                    'raw_records': len(raw_data),
                    'clean_records': len(clean_data),
                    'new_records': new_records,
                    'updated_records': updated_records,
                    'message': f'爬取完成：新增{new_records}条，更新{updated_records}条'
                }
            
            else:
                # 爬取失败
                crawl_log.end_time = timezone.now()
                crawl_log.status = 'failed'
                crawl_log.error_message = crawl_result.get('error', '爬取失败')
                crawl_log.save()
                
                return {
                    'success': False,
                    'data_source': '500彩票网',
                    'error': crawl_result.get('error', '爬取失败'),
                    'message': '爬取任务失败'
                }
                
        except Exception as inner_exc:
            # 内部异常处理
            crawl_log.end_time = timezone.now()
            crawl_log.status = 'failed'
            crawl_log.error_message = str(inner_exc)
            crawl_log.save()
            raise inner_exc
            
    except Exception as exc:
        logger.error(f"爬取任务失败：{exc}")
        return {
            'success': False,
            'data_source': '500彩票网',
            'error': str(exc),
            'message': '爬取任务执行异常'
        }


@shared_task(bind=True)
def update_statistics(self):
    """
    更新统计数据的异步任务
    """
    task_id = self.request.id
    
    try:
        logger.info(f"开始执行统计更新任务 {task_id}")
        
        # 获取最近100期数据进行统计
        recent_results = LotteryResult.objects.order_by('-draw_date')[:100]
        
        if not recent_results:
            logger.warning("没有开奖数据，跳过统计更新")
            return {
                'task_id': task_id,
                'success': True,
                'message': '没有数据需要统计'
            }
        
        # 清空现有统计数据
        Statistics.objects.all().delete()
        
        # 统计红球频率（1-33）
        red_ball_stats = {}
        for i in range(1, 34):
            red_ball_stats[i] = 0
        
        # 统计蓝球频率（1-16）
        blue_ball_stats = {}
        for i in range(1, 17):
            blue_ball_stats[i] = 0
        
        # 计算频率
        for result in recent_results:
            red_balls = [
                result.red_ball_1, result.red_ball_2, result.red_ball_3,
                result.red_ball_4, result.red_ball_5, result.red_ball_6
            ]
            
            for ball in red_balls:
                red_ball_stats[ball] += 1
            
            blue_ball_stats[result.blue_ball] += 1
        
        # 保存红球统计
        for number, frequency in red_ball_stats.items():
            Statistics.objects.create(
                ball_type='red',
                ball_number=number,
                appear_count=frequency
            )
        
        # 保存蓝球统计
        for number, frequency in blue_ball_stats.items():
            Statistics.objects.create(
                ball_type='blue',
                ball_number=number,
                appear_count=frequency
            )
        
        logger.info(f"统计更新任务 {task_id} 完成，处理了{len(recent_results)}期数据")
        
        return {
            'task_id': task_id,
            'success': True,
            'records_processed': len(recent_results),
            'red_balls_updated': len(red_ball_stats),
            'blue_balls_updated': len(blue_ball_stats),
            'message': '统计数据更新完成'
        }
        
    except Exception as exc:
        logger.error(f"统计更新任务 {task_id} 失败：{exc}")
        return {
            'task_id': task_id,
            'success': False,
            'error': str(exc),
            'message': '统计数据更新失败'
        }


@shared_task(bind=True)
def data_quality_check(self):
    """
    数据质量检查任务
    """
    task_id = self.request.id
    
    try:
        logger.info(f"开始执行数据质量检查任务 {task_id}")
        
        issues = []
        
        # 检查重复数据
        duplicate_results = LotteryResult.objects.values('issue').annotate(
            count=models.Count('issue')
        ).filter(count__gt=1)
        
        if duplicate_results:
            issues.append(f"发现{duplicate_results.count()}个重复期号")
        
        # 检查数据完整性
        incomplete_results = LotteryResult.objects.filter(
            models.Q(red_ball_1__isnull=True) |
            models.Q(red_ball_2__isnull=True) |
            models.Q(red_ball_3__isnull=True) |
            models.Q(red_ball_4__isnull=True) |
            models.Q(red_ball_5__isnull=True) |
            models.Q(red_ball_6__isnull=True) |
            models.Q(blue_ball__isnull=True)
        )
        
        if incomplete_results:
            issues.append(f"发现{incomplete_results.count()}条不完整数据")
        
        # 检查数据范围
        invalid_red_balls = LotteryResult.objects.filter(
            models.Q(red_ball_1__lt=1) | models.Q(red_ball_1__gt=33) |
            models.Q(red_ball_2__lt=1) | models.Q(red_ball_2__gt=33) |
            models.Q(red_ball_3__lt=1) | models.Q(red_ball_3__gt=33) |
            models.Q(red_ball_4__lt=1) | models.Q(red_ball_4__gt=33) |
            models.Q(red_ball_5__lt=1) | models.Q(red_ball_5__gt=33) |
            models.Q(red_ball_6__lt=1) | models.Q(red_ball_6__gt=33)
        )
        
        invalid_blue_balls = LotteryResult.objects.filter(
            models.Q(blue_ball__lt=1) | models.Q(blue_ball__gt=16)
        )
        
        if invalid_red_balls:
            issues.append(f"发现{invalid_red_balls.count()}条红球数据超出范围")
        
        if invalid_blue_balls:
            issues.append(f"发现{invalid_blue_balls.count()}条蓝球数据超出范围")
        
        logger.info(f"数据质量检查任务 {task_id} 完成")
        
        return {
            'task_id': task_id,
            'success': True,
            'issues_found': len(issues),
            'issues': issues,
            'message': f'数据质量检查完成，发现{len(issues)}个问题'
        }
        
    except Exception as exc:
        logger.error(f"数据质量检查任务 {task_id} 失败：{exc}")
        return {
            'task_id': task_id,
            'success': False,
            'error': str(exc),
            'message': '数据质量检查失败'
        }


@shared_task(bind=True)
def check_data_sources(self):
    """
    检查数据源状态任务
    """
    task_id = self.request.id
    
    try:
        logger.info(f"开始执行数据源检查任务 {task_id}")
        
        data_sources = DataSource.objects.filter(is_enabled=True)
        results = []
        
        for source in data_sources:
            try:
                # 这里可以添加具体的数据源连通性检查
                # 目前简单检查数据源记录
                source.last_check_time = timezone.now()
                source.status = 'active'
                source.save()
                
                results.append({
                    'name': source.name,
                    'status': 'active',
                    'message': '数据源正常'
                })
                
            except Exception as e:
                source.status = 'error'
                source.error_message = str(e)
                source.save()
                
                results.append({
                    'name': source.name,
                    'status': 'error',
                    'message': str(e)
                })
        
        logger.info(f"数据源检查任务 {task_id} 完成")
        
        return {
            'task_id': task_id,
            'success': True,
            'sources_checked': len(results),
            'results': results,
            'message': '数据源状态检查完成'
        }
        
    except Exception as exc:
        logger.error(f"数据源检查任务 {task_id} 失败：{exc}")
        return {
            'task_id': task_id,
            'success': False,
            'error': str(exc),
            'message': '数据源状态检查失败'
        }


@shared_task(bind=True)
def manual_crawl_task(self, data_source='500彩票网', start_date=None, end_date=None):
    """
    手动爬取任务，支持日期范围
    """
    return crawl_latest_data.apply_async(
        args=[data_source],
        task_id=self.request.id
    )


@shared_task(bind=True)
def test_step_by_step_crawler(self, step=1):
    """
    逐步测试爬虫任务的各个步骤
    step 1: 基础设置
    step 2: 导入爬虫模块  
    step 3: 创建爬虫实例
    step 4: 执行爬虫
    step 5: 数据处理
    """
    task_id = self.request.id
    logger.info(f"逐步测试任务 {task_id} 开始，步骤：{step}")
    
    try:
        if step >= 1:
            # 步骤1：基础设置
            from lottery.models import DataSource, CrawlLog
            data_source, created = DataSource.objects.get_or_create(
                name='500彩票网',
                defaults={
                    'source_type': 'c500',
                    'base_url': 'https://datachart.500.com/ssq/',
                    'is_enabled': True,
                    'status': 'active'
                }
            )
            logger.info(f"步骤1完成：基础设置")
        
        if step >= 2:
            # 步骤2：导入爬虫模块
            from lottery.scrapers.c500_scraper_enhanced import C500ScraperEnhanced
            logger.info(f"步骤2完成：爬虫模块导入")
        
        if step >= 3:
            # 步骤3：创建爬虫实例
            scraper = C500ScraperEnhanced()
            logger.info(f"步骤3完成：爬虫实例创建")
        
        if step >= 4:
            # 步骤4：执行爬虫（最可能的问题点）
            result = scraper.crawl_latest_data()
            logger.info(f"步骤4完成：爬虫执行，result: {result['success']}")
        
        if step >= 5:
            # 步骤5：数据处理
            if result['success']:
                from lottery.scrapers.data_cleaner import DataCleaner
                cleaner = DataCleaner(source_type='c500')
                logger.info(f"步骤5完成：数据处理准备")
        
        logger.info(f"逐步测试任务 {task_id} 完成到步骤 {step}")
        return {
            'task_id': task_id,
            'success': True,
            'step_completed': step,
            'message': f'成功完成到步骤 {step}'
        }
        
    except Exception as exc:
        logger.error(f"逐步测试任务 {task_id} 在步骤 {step} 失败：{exc}")
        return {
            'task_id': task_id,
            'success': False,
            'failed_at_step': step,
            'error': str(exc)
        }


@shared_task(bind=True)
def test_imports_only(self):
    """
    只测试导入的任务
    """
    task_id = self.request.id
    logger.info(f"测试导入任务 {task_id} 开始")
    
    try:
        # 测试导入1
        logger.info("测试导入C500ScraperEnhanced...")
        scraper = C500ScraperEnhanced()
        logger.info("C500ScraperEnhanced导入成功")
        
        # 测试导入2  
        logger.info("测试导入DataCleaner...")
        cleaner = DataCleaner(source_type='c500')
        logger.info("DataCleaner导入成功")
        
        logger.info(f"测试导入任务 {task_id} 完成")
        return {
            'task_id': task_id,
            'success': True,
            'message': '所有导入测试成功'
        }
        
    except Exception as exc:
        logger.error(f"测试导入任务 {task_id} 失败：{exc}")
        return {
            'task_id': task_id,
            'success': False,
            'error': str(exc)
        }


@shared_task
def crawl_simple_task():
    """
    与debug_task相同结构的简单爬虫任务
    """
    return '爬虫任务测试成功!' 