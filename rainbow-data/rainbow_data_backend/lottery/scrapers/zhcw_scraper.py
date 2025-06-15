"""
中彩网爬虫实现
============

从中彩网（www.zhcw.com）获取双色球开奖数据。
这是福彩官方网站，数据权威可靠。
"""

import re
import uuid
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper
from .data_parser import DataParser
from .data_cleaner import DataCleaner
from .scraper_config import scraper_config


class ZhcwScraper(BaseScraper):
    """
    中彩网爬虫类
    
    支持功能：
    1. 获取最新开奖结果
    2. 获取历史开奖数据
    3. 增量数据更新
    4. 分页数据处理
    """
    
    def __init__(self, data_source):
        """
        初始化中彩网爬虫
        
        Args:
            data_source: 数据源配置对象
        """
        super().__init__(data_source)
        
        # 获取配置
        self.config = scraper_config.get_config('zhcw', data_source)
        
        # 初始化解析器和清洗器
        self.parser = DataParser('zhcw')
        self.cleaner = DataCleaner('zhcw')
        
        # 设置基础URL
        self.base_url = self.config['base_url']
        
        self.log_info(f"中彩网爬虫初始化完成: {self.base_url}")
    
    def fetch_latest(self) -> List[Dict]:
        """
        获取最新开奖数据
        
        Returns:
            List[Dict]: 最新开奖数据列表
        """
        task_id = f"zhcw_latest_{uuid.uuid4().hex[:8]}"
        self.create_crawl_log(task_id, 'latest_sync')
        self.start_crawl()
        
        try:
            self.log_info("开始获取最新开奖数据")
            
            # 构建最新数据URL
            latest_url = scraper_config.get_url('zhcw', 'latest')
            
            # 发起请求
            response = self.make_request(latest_url)
            if not response:
                raise Exception("无法获取最新数据页面")
            
            # 解析HTML
            selector_config = scraper_config.get_selectors('zhcw')
            raw_data = self.parser.parse_html(response.text, selector_config)
            
            if not raw_data:
                self.log_warning("未解析到任何数据")
                return []
            
            # 清洗数据
            cleaned_data = self.cleaner.clean_data(raw_data)
            
            # 只取最新的几条记录
            latest_data = cleaned_data[:5]  # 最新5期
            
            # 保存到数据库
            created, updated = self.save_lottery_data(latest_data)
            
            self.log_info(f"获取最新数据完成: 新建{created}条, 更新{updated}条")
            self.complete_crawl(success=True)
            
            return latest_data
            
        except Exception as e:
            error_msg = f"获取最新数据失败: {str(e)}"
            self.log_error(error_msg)
            self.complete_crawl(success=False, error_message=error_msg)
            return []
    
    def fetch_history(self, start_date: date, end_date: date) -> List[Dict]:
        """
        获取历史开奖数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 历史开奖数据列表
        """
        task_id = f"zhcw_history_{uuid.uuid4().hex[:8]}"
        self.create_crawl_log(task_id, 'full_sync', {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })
        self.start_crawl()
        
        try:
            self.log_info(f"开始获取历史数据: {start_date} ~ {end_date}")
            
            all_data = []
            page = 1
            max_pages = self.config.get('pagination', {}).get('max_pages', 50)
            
            while page <= max_pages:
                self.log_info(f"正在获取第{page}页数据")
                
                # 构建历史数据URL
                history_url = self._build_history_url(page)
                
                # 发起请求
                response = self.make_request(history_url)
                if not response:
                    self.log_warning(f"第{page}页请求失败")
                    break
                
                # 解析页面数据
                page_data = self._parse_history_page(response.text, start_date, end_date)
                
                if not page_data:
                    self.log_info(f"第{page}页没有数据，停止翻页")
                    break
                
                all_data.extend(page_data)
                
                # 检查是否已获取到目标日期范围的数据
                if self._is_data_complete(page_data, start_date):
                    self.log_info("已获取到目标日期范围的所有数据")
                    break
                
                page += 1
            
            # 清洗数据
            cleaned_data = self.cleaner.clean_data(all_data)
            
            # 按日期过滤
            filtered_data = self._filter_by_date_range(cleaned_data, start_date, end_date)
            
            # 保存到数据库
            created, updated = self.save_lottery_data(filtered_data)
            
            self.log_info(f"历史数据获取完成: 总计{len(filtered_data)}条, 新建{created}条, 更新{updated}条")
            self.complete_crawl(success=True)
            
            return filtered_data
            
        except Exception as e:
            error_msg = f"获取历史数据失败: {str(e)}"
            self.log_error(error_msg)
            self.complete_crawl(success=False, error_message=error_msg)
            return []
    
    def fetch_incremental(self, last_issue: str = None) -> List[Dict]:
        """
        获取增量开奖数据
        
        Args:
            last_issue: 最后一期的期号
            
        Returns:
            List[Dict]: 新的开奖数据列表
        """
        task_id = f"zhcw_incremental_{uuid.uuid4().hex[:8]}"
        self.create_crawl_log(task_id, 'incremental_sync', {
            'last_issue': last_issue
        })
        self.start_crawl()
        
        try:
            self.log_info(f"开始增量更新，最后期号: {last_issue}")
            
            # 如果没有提供最后期号，从数据库获取
            if not last_issue:
                from ..models import LotteryResult
                latest_result = LotteryResult.objects.order_by('-draw_date').first()
                last_issue = latest_result.issue if latest_result else None
            
            # 获取已存在的期号集合
            existing_issues = self.get_existing_issues()
            
            # 获取最新数据
            latest_data = self.fetch_latest()
            
            # 过滤出新数据
            new_data = []
            for item in latest_data:
                if item['issue'] not in existing_issues:
                    new_data.append(item)
            
            self.log_info(f"增量更新完成: 发现{len(new_data)}条新数据")
            self.complete_crawl(success=True)
            
            return new_data
            
        except Exception as e:
            error_msg = f"增量更新失败: {str(e)}"
            self.log_error(error_msg)
            self.complete_crawl(success=False, error_message=error_msg)
            return []
    
    def _build_history_url(self, page: int = 1) -> str:
        """
        构建历史数据URL
        
        Args:
            page: 页码
            
        Returns:
            str: URL字符串
        """
        base_url = scraper_config.get_url('zhcw', 'history')
        
        # 中彩网的分页参数可能需要调整
        if page > 1:
            # 添加分页参数
            separator = '&' if '?' in base_url else '?'
            return f"{base_url}{separator}page={page}"
        
        return base_url
    
    def _parse_history_page(self, html_content: str, start_date: date, end_date: date) -> List[Dict]:
        """
        解析历史数据页面
        
        Args:
            html_content: HTML内容
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 页面数据列表
        """
        try:
            # 使用解析器解析HTML
            selector_config = scraper_config.get_selectors('zhcw')
            raw_data = self.parser.parse_html(html_content, selector_config)
            
            # 按日期初步过滤（提高效率）
            filtered_data = []
            for item in raw_data:
                try:
                    item_date = item.get('draw_date')
                    if isinstance(item_date, str):
                        item_date = datetime.strptime(item_date, '%Y-%m-%d').date()
                    
                    if start_date <= item_date <= end_date:
                        filtered_data.append(item)
                except (ValueError, TypeError):
                    continue
            
            return filtered_data
            
        except Exception as e:
            self.log_error(f"解析历史页面失败: {str(e)}")
            return []
    
    def _is_data_complete(self, page_data: List[Dict], start_date: date) -> bool:
        """
        检查是否已获取到完整数据
        
        Args:
            page_data: 当前页数据
            start_date: 开始日期
            
        Returns:
            bool: 是否完整
        """
        if not page_data:
            return True
        
        try:
            # 检查最早的数据是否已经小于开始日期
            earliest_date = None
            for item in page_data:
                item_date = item.get('draw_date')
                if isinstance(item_date, str):
                    item_date = datetime.strptime(item_date, '%Y-%m-%d').date()
                
                if earliest_date is None or item_date < earliest_date:
                    earliest_date = item_date
            
            return earliest_date < start_date if earliest_date else False
            
        except (ValueError, TypeError):
            return False
    
    def _filter_by_date_range(self, data: List[Dict], start_date: date, end_date: date) -> List[Dict]:
        """
        按日期范围过滤数据
        
        Args:
            data: 原始数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 过滤后的数据
        """
        filtered_data = []
        
        for item in data:
            try:
                item_date = item.get('draw_date')
                if isinstance(item_date, str):
                    item_date = datetime.strptime(item_date, '%Y-%m-%d').date()
                elif isinstance(item_date, datetime):
                    item_date = item_date.date()
                
                if start_date <= item_date <= end_date:
                    filtered_data.append(item)
                    
            except (ValueError, TypeError):
                continue
        
        return filtered_data
    
    def test_connection(self) -> bool:
        """
        测试连接是否正常
        
        Returns:
            bool: 连接是否正常
        """
        try:
            test_url = scraper_config.get_url('zhcw', 'latest')
            response = self.make_request(test_url)
            
            if response and response.status_code == 200:
                self.log_info("中彩网连接测试成功")
                return True
            else:
                self.log_warning("中彩网连接测试失败")
                return False
                
        except Exception as e:
            self.log_error(f"中彩网连接测试异常: {str(e)}")
            return False
    
    def get_robots_txt(self) -> str:
        """
        获取robots.txt文件内容
        
        Returns:
            str: robots.txt内容
        """
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = self.make_request(robots_url)
            
            if response and response.status_code == 200:
                return response.text
            else:
                return ""
                
        except Exception as e:
            self.log_warning(f"无法获取robots.txt: {str(e)}")
            return ""
    
    def check_robots_compliance(self) -> bool:
        """
        检查是否遵守robots.txt规则
        
        Returns:
            bool: 是否合规
        """
        try:
            robots_content = self.get_robots_txt()
            if not robots_content:
                # 如果没有robots.txt，默认允许
                return True
            
            # 简单的robots.txt解析
            # 实际项目中可以使用更专业的robots.txt解析库
            lines = robots_content.lower().split('\n')
            user_agent_applies = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('user-agent:'):
                    ua = line.split(':', 1)[1].strip()
                    if ua == '*' or 'python' in ua or 'bot' in ua:
                        user_agent_applies = True
                    else:
                        user_agent_applies = False
                elif user_agent_applies and line.startswith('disallow:'):
                    disallowed_path = line.split(':', 1)[1].strip()
                    if disallowed_path and '/kjxx/' in disallowed_path:
                        return False
            
            return True
            
        except Exception as e:
            self.log_warning(f"robots.txt合规检查失败: {str(e)}")
            return True  # 默认允许 