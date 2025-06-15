"""
基础爬虫类
=========

定义所有爬虫的通用接口和基础功能。
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from fake_useragent import UserAgent
from django.utils import timezone
from django.conf import settings

from ..models import DataSource, CrawlLog, LotteryResult


class BaseScraper(ABC):
    """
    基础爬虫抽象类
    
    所有具体的爬虫类都需要继承这个基类，并实现必要的抽象方法。
    提供了通用的HTTP请求、错误处理、日志记录等功能。
    """
    
    def __init__(self, data_source: DataSource):
        """
        初始化爬虫
        
        Args:
            data_source: 数据源配置对象
        """
        self.data_source = data_source
        self.logger = logging.getLogger(f'scraper.{data_source.source_type}')
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 设置请求配置
        self._setup_session()
        
        # 当前爬取任务日志
        self.crawl_log: Optional[CrawlLog] = None
        
    def _setup_session(self):
        """设置HTTP会话配置"""
        # 基础headers
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 合并数据源配置的headers
        if self.data_source.headers:
            headers.update(self.data_source.headers)
            
        self.session.headers.update(headers)
        
        # 设置超时
        self.session.timeout = self.data_source.timeout
        
        # 可以在这里添加代理配置
        # if hasattr(settings, 'SCRAPER_PROXY'):
        #     self.session.proxies = settings.SCRAPER_PROXY
    
    def create_crawl_log(self, task_id: str, task_type: str, parameters: Dict = None) -> CrawlLog:
        """
        创建爬取日志记录
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            parameters: 执行参数
            
        Returns:
            CrawlLog: 爬取日志对象
        """
        self.crawl_log = CrawlLog.objects.create(
            task_id=task_id,
            task_type=task_type,
            data_source=self.data_source,
            parameters=parameters or {},
            status='pending'
        )
        return self.crawl_log
    
    def start_crawl(self):
        """开始爬取任务"""
        if self.crawl_log:
            self.crawl_log.start_execution()
            self.log_info("爬取任务开始执行")
    
    def complete_crawl(self, success: bool = True, error_message: str = ""):
        """完成爬取任务"""
        if self.crawl_log:
            self.crawl_log.complete_execution(success=success, error_message=error_message)
            if success:
                self.log_info("爬取任务执行成功")
                self.data_source.update_success_stats()
            else:
                self.log_error(f"爬取任务执行失败: {error_message}")
                self.data_source.update_error_stats(error_message)
    
    def log_info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
        if self.crawl_log:
            self.crawl_log.add_log(f"[INFO] {message}")
    
    def log_error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
        if self.crawl_log:
            self.crawl_log.add_log(f"[ERROR] {message}")
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
        if self.crawl_log:
            self.crawl_log.add_log(f"[WARNING] {message}")
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        发起HTTP请求（带重试机制）
        
        Args:
            url: 请求URL
            method: HTTP方法
            **kwargs: 其他请求参数
            
        Returns:
            requests.Response: 响应对象，失败时返回None
        """
        for attempt in range(self.data_source.max_retries + 1):
            try:
                # 请求间隔控制
                if attempt > 0:
                    wait_time = min(2 ** attempt, 30)  # 指数退避，最大30秒
                    self.log_info(f"第{attempt}次重试，等待{wait_time}秒...")
                    time.sleep(wait_time)
                else:
                    # 正常的请求间隔
                    time.sleep(self.data_source.request_interval)
                
                # 更新User-Agent
                self.session.headers['User-Agent'] = self.ua.random
                
                # 发起请求
                response = self.session.request(method, url, **kwargs)
                
                # 更新统计
                if self.crawl_log:
                    self.crawl_log.total_requests += 1
                    if response.status_code == 200:
                        self.crawl_log.success_requests += 1
                    else:
                        self.crawl_log.failed_requests += 1
                    self.crawl_log.save(update_fields=['total_requests', 'success_requests', 'failed_requests'])
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.log_warning(f"请求失败 (尝试 {attempt + 1}/{self.data_source.max_retries + 1}): {str(e)}")
                if attempt == self.data_source.max_retries:
                    self.log_error(f"请求最终失败: {url}")
                    if self.crawl_log:
                        self.crawl_log.failed_requests += 1
                        self.crawl_log.save(update_fields=['failed_requests'])
                    return None
        
        return None
    
    def validate_lottery_data(self, data: Dict) -> bool:
        """
        验证彩票数据格式
        
        Args:
            data: 彩票数据字典
            
        Returns:
            bool: 数据是否有效
        """
        try:
            # 检查必要字段
            required_fields = ['issue', 'draw_date', 'red_balls', 'blue_ball']
            for field in required_fields:
                if field not in data:
                    self.log_warning(f"缺少必要字段: {field}")
                    return False
            
            # 验证红球
            red_balls = data['red_balls']
            if not isinstance(red_balls, list) or len(red_balls) != 6:
                self.log_warning(f"红球数据格式错误: {red_balls}")
                return False
            
            for ball in red_balls:
                if not isinstance(ball, int) or ball < 1 or ball > 33:
                    self.log_warning(f"红球号码超出范围: {ball}")
                    return False
            
            # 检查红球是否有重复
            if len(set(red_balls)) != 6:
                self.log_warning(f"红球号码重复: {red_balls}")
                return False
            
            # 验证蓝球
            blue_ball = data['blue_ball']
            if not isinstance(blue_ball, int) or blue_ball < 1 or blue_ball > 16:
                self.log_warning(f"蓝球号码超出范围: {blue_ball}")
                return False
            
            return True
            
        except Exception as e:
            self.log_error(f"数据验证异常: {str(e)}")
            return False
    
    def save_lottery_data(self, data_list: List[Dict]) -> Tuple[int, int]:
        """
        保存彩票数据到数据库
        
        Args:
            data_list: 彩票数据列表
            
        Returns:
            Tuple[int, int]: (创建数量, 更新数量)
        """
        created_count = 0
        updated_count = 0
        
        for data in data_list:
            if not self.validate_lottery_data(data):
                continue
                
            try:
                # 尝试获取现有记录
                existing = LotteryResult.objects.filter(issue=data['issue']).first()
                
                if existing:
                    # 检查是否需要更新
                    red_balls = data['red_balls']
                    if (existing.red_ball_1 != red_balls[0] or
                        existing.red_ball_2 != red_balls[1] or
                        existing.red_ball_3 != red_balls[2] or
                        existing.red_ball_4 != red_balls[3] or
                        existing.red_ball_5 != red_balls[4] or
                        existing.red_ball_6 != red_balls[5] or
                        existing.blue_ball != data['blue_ball']):
                        
                        # 更新数据
                        existing.red_ball_1 = red_balls[0]
                        existing.red_ball_2 = red_balls[1]
                        existing.red_ball_3 = red_balls[2]
                        existing.red_ball_4 = red_balls[3]
                        existing.red_ball_5 = red_balls[4]
                        existing.red_ball_6 = red_balls[5]
                        existing.blue_ball = data['blue_ball']
                        existing.draw_date = data['draw_date']
                        existing.save()
                        updated_count += 1
                        self.log_info(f"更新开奖记录: {data['issue']}")
                else:
                    # 创建新记录
                    red_balls = data['red_balls']
                    LotteryResult.objects.create(
                        issue=data['issue'],
                        draw_date=data['draw_date'],
                        red_ball_1=red_balls[0],
                        red_ball_2=red_balls[1],
                        red_ball_3=red_balls[2],
                        red_ball_4=red_balls[3],
                        red_ball_5=red_balls[4],
                        red_ball_6=red_balls[5],
                        blue_ball=data['blue_ball']
                    )
                    created_count += 1
                    self.log_info(f"创建开奖记录: {data['issue']}")
                    
            except Exception as e:
                self.log_error(f"保存数据异常: {data.get('issue', 'unknown')} - {str(e)}")
        
        # 更新爬取日志统计
        if self.crawl_log:
            self.crawl_log.records_found += len(data_list)
            self.crawl_log.records_created += created_count
            self.crawl_log.records_updated += updated_count
            self.crawl_log.records_skipped += len(data_list) - created_count - updated_count
            self.crawl_log.save(update_fields=['records_found', 'records_created', 'records_updated', 'records_skipped'])
        
        return created_count, updated_count
    
    def get_existing_issues(self, start_date: date = None, end_date: date = None) -> set:
        """
        获取已存在的期号集合
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            set: 期号集合
        """
        queryset = LotteryResult.objects.all()
        
        if start_date:
            queryset = queryset.filter(draw_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(draw_date__lte=end_date)
            
        return set(queryset.values_list('issue', flat=True))
    
    # 抽象方法，子类必须实现
    
    @abstractmethod
    def fetch_latest(self) -> List[Dict]:
        """
        获取最新开奖数据
        
        Returns:
            List[Dict]: 开奖数据列表
        """
        pass
    
    @abstractmethod
    def fetch_history(self, start_date: date, end_date: date) -> List[Dict]:
        """
        获取历史开奖数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 开奖数据列表
        """
        pass
    
    @abstractmethod  
    def fetch_incremental(self, last_issue: str = None) -> List[Dict]:
        """
        获取增量开奖数据
        
        Args:
            last_issue: 最后一期的期号
            
        Returns:
            List[Dict]: 新的开奖数据列表
        """
        pass
    
    def __del__(self):
        """析构函数，关闭session"""
        if hasattr(self, 'session'):
            self.session.close() 