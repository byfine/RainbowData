"""
数据解析器
=========

用于解析不同数据源的HTML和JSON数据，提取双色球开奖信息。
"""

import re
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import logging


class DataParser:
    """
    数据解析器类
    
    支持多种数据格式的解析：
    1. HTML页面解析（BeautifulSoup）
    2. JSON数据解析
    3. XML数据解析（可扩展）
    """
    
    def __init__(self, source_type: str):
        """
        初始化解析器
        
        Args:
            source_type: 数据源类型（zhcw、c500、api等）
        """
        self.source_type = source_type
        self.logger = logging.getLogger(f'parser.{source_type}')
    
    def parse_html(self, html_content: str, selector_config: Dict) -> List[Dict]:
        """
        解析HTML内容
        
        Args:
            html_content: HTML内容
            selector_config: 选择器配置
            
        Returns:
            List[Dict]: 解析出的开奖数据列表
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            if self.source_type == 'zhcw':
                results = self._parse_zhcw_html(soup, selector_config)
            elif self.source_type == 'c500':
                results = self._parse_c500_html(soup, selector_config)
            else:
                self.logger.warning(f"未支持的HTML解析类型: {self.source_type}")
                
            return results
            
        except Exception as e:
            self.logger.error(f"HTML解析失败: {str(e)}")
            return []
    
    def parse_json(self, json_content: str, field_mapping: Dict) -> List[Dict]:
        """
        解析JSON内容
        
        Args:
            json_content: JSON内容
            field_mapping: 字段映射配置
            
        Returns:
            List[Dict]: 解析出的开奖数据列表
        """
        try:
            data = json.loads(json_content)
            results = []
            
            if self.source_type == 'api':
                results = self._parse_api_json(data, field_mapping)
            else:
                # 通用JSON解析
                results = self._parse_generic_json(data, field_mapping)
                
            return results
            
        except Exception as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            return []
    
    def _parse_zhcw_html(self, soup: BeautifulSoup, selector_config: Dict) -> List[Dict]:
        """
        解析中彩网HTML数据
        
        Args:
            soup: BeautifulSoup对象
            selector_config: 选择器配置
            
        Returns:
            List[Dict]: 开奖数据列表
        """
        results = []
        
        try:
            # 根据中彩网页面结构解析
            # 这里需要根据实际网站结构来调整选择器
            
            # 示例选择器配置：
            # {
            #     'container': 'table.ssq tbody tr',
            #     'issue': 'td:nth-child(1)',
            #     'draw_date': 'td:nth-child(2)',
            #     'red_balls': 'td:nth-child(3) span.ball_red',
            #     'blue_ball': 'td:nth-child(3) span.ball_blue'
            # }
            
            container_selector = selector_config.get('container', 'tr')
            rows = soup.select(container_selector)
            
            for row in rows:
                try:
                    # 提取期号
                    issue_elem = row.select_one(selector_config.get('issue', 'td:first-child'))
                    if not issue_elem:
                        continue
                    issue = issue_elem.get_text(strip=True)
                    
                    # 提取开奖日期
                    date_elem = row.select_one(selector_config.get('draw_date', 'td:nth-child(2)'))
                    if not date_elem:
                        continue
                    date_str = date_elem.get_text(strip=True)
                    draw_date = self._parse_date(date_str)
                    
                    # 提取红球
                    red_ball_elems = row.select(selector_config.get('red_balls', 'span.ball_red'))
                    if len(red_ball_elems) != 6:
                        continue
                    red_balls = [int(elem.get_text(strip=True)) for elem in red_ball_elems]
                    
                    # 提取蓝球
                    blue_ball_elem = row.select_one(selector_config.get('blue_ball', 'span.ball_blue'))
                    if not blue_ball_elem:
                        continue
                    blue_ball = int(blue_ball_elem.get_text(strip=True))
                    
                    results.append({
                        'issue': issue,
                        'draw_date': draw_date,
                        'red_balls': red_balls,
                        'blue_ball': blue_ball
                    })
                    
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"解析行数据失败: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"中彩网HTML解析失败: {str(e)}")
        
        return results
    
    def _parse_c500_html(self, soup: BeautifulSoup, selector_config: Dict) -> List[Dict]:
        """
        解析500彩票网HTML数据
        
        Args:
            soup: BeautifulSoup对象
            selector_config: 选择器配置
            
        Returns:
            List[Dict]: 开奖数据列表
        """
        results = []
        
        try:
            # 500彩票网通常使用表格展示数据
            # 示例选择器配置：
            # {
            #     'container': 'table tbody tr',
            #     'issue': 'td:nth-child(1)',
            #     'draw_date': 'td:nth-child(2)',
            #     'numbers': 'td:nth-child(3)'
            # }
            
            container_selector = selector_config.get('container', 'tbody tr')
            rows = soup.select(container_selector)
            
            for row in rows:
                try:
                    # 提取期号
                    issue_elem = row.select_one(selector_config.get('issue', 'td:first-child'))
                    if not issue_elem:
                        continue
                    issue = issue_elem.get_text(strip=True)
                    
                    # 提取开奖日期
                    date_elem = row.select_one(selector_config.get('draw_date', 'td:nth-child(2)'))
                    if not date_elem:
                        continue
                    date_str = date_elem.get_text(strip=True)
                    draw_date = self._parse_date(date_str)
                    
                    # 提取号码（通常在一个单元格内）
                    numbers_elem = row.select_one(selector_config.get('numbers', 'td:nth-child(3)'))
                    if not numbers_elem:
                        continue
                    
                    # 解析号码文本，如 "01 05 12 18 25 28 + 08"
                    numbers_text = numbers_elem.get_text(strip=True)
                    red_balls, blue_ball = self._parse_numbers_text(numbers_text)
                    
                    if red_balls and blue_ball:
                        results.append({
                            'issue': issue,
                            'draw_date': draw_date,
                            'red_balls': red_balls,
                            'blue_ball': blue_ball
                        })
                    
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"解析500彩票网行数据失败: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"500彩票网HTML解析失败: {str(e)}")
        
        return results
    
    def _parse_api_json(self, data: Any, field_mapping: Dict) -> List[Dict]:
        """
        解析API JSON数据
        
        Args:
            data: JSON数据
            field_mapping: 字段映射配置
            
        Returns:
            List[Dict]: 开奖数据列表
        """
        results = []
        
        try:
            # 字段映射示例：
            # {
            #     'data_path': 'data.list',  # 数据数组路径
            #     'issue': 'issue',          # 期号字段
            #     'draw_date': 'drawDate',   # 开奖日期字段
            #     'red_balls': 'redBalls',   # 红球字段
            #     'blue_ball': 'blueBall'    # 蓝球字段
            # }
            
            # 获取数据数组
            data_path = field_mapping.get('data_path', '')
            if data_path:
                data_list = self._get_nested_value(data, data_path)
            else:
                data_list = data if isinstance(data, list) else [data]
            
            for item in data_list:
                try:
                    # 提取各字段
                    issue = self._get_nested_value(item, field_mapping.get('issue', 'issue'))
                    date_str = self._get_nested_value(item, field_mapping.get('draw_date', 'drawDate'))
                    red_balls_data = self._get_nested_value(item, field_mapping.get('red_balls', 'redBalls'))
                    blue_ball_data = self._get_nested_value(item, field_mapping.get('blue_ball', 'blueBall'))
                    
                    # 转换数据类型
                    draw_date = self._parse_date(str(date_str))
                    
                    # 处理红球数据（可能是字符串或数组）
                    if isinstance(red_balls_data, str):
                        red_balls = [int(x.strip()) for x in red_balls_data.split(',')]
                    elif isinstance(red_balls_data, list):
                        red_balls = [int(x) for x in red_balls_data]
                    else:
                        continue
                    
                    blue_ball = int(blue_ball_data)
                    
                    results.append({
                        'issue': str(issue),
                        'draw_date': draw_date,
                        'red_balls': red_balls,
                        'blue_ball': blue_ball
                    })
                    
                except (ValueError, KeyError, TypeError) as e:
                    self.logger.warning(f"解析API数据项失败: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"API JSON解析失败: {str(e)}")
        
        return results
    
    def _parse_generic_json(self, data: Any, field_mapping: Dict) -> List[Dict]:
        """
        通用JSON解析器
        
        Args:
            data: JSON数据
            field_mapping: 字段映射配置
            
        Returns:
            List[Dict]: 开奖数据列表
        """
        # 与_parse_api_json类似，但更通用
        return self._parse_api_json(data, field_mapping)
    
    def _parse_date(self, date_str: str) -> date:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            date: 日期对象
        """
        # 支持多种日期格式
        formats = [
            '%Y-%m-%d',
            '%Y年%m月%d日',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y%m%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        # 如果都不匹配，抛出异常
        raise ValueError(f"无法解析日期格式: {date_str}")
    
    def _parse_numbers_text(self, numbers_text: str) -> tuple:
        """
        解析号码文本
        
        Args:
            numbers_text: 号码文本，如 "01 05 12 18 25 28 + 08"
            
        Returns:
            tuple: (红球列表, 蓝球)
        """
        try:
            # 常见格式处理
            # "01 05 12 18 25 28 + 08"
            # "01,05,12,18,25,28+08"
            # "01|05|12|18|25|28|08"
            
            # 清理文本
            clean_text = re.sub(r'[^\d\s+,|]', '', numbers_text)
            
            # 分割红球和蓝球
            if '+' in clean_text:
                red_part, blue_part = clean_text.split('+', 1)
            elif '|' in clean_text:
                parts = clean_text.split('|')
                red_part = '|'.join(parts[:-1])
                blue_part = parts[-1]
            else:
                # 假设前6个是红球，最后1个是蓝球
                numbers = re.findall(r'\d+', clean_text)
                if len(numbers) >= 7:
                    red_part = ' '.join(numbers[:6])
                    blue_part = numbers[6]
                else:
                    return None, None
            
            # 提取红球
            red_numbers = re.findall(r'\d+', red_part)
            if len(red_numbers) != 6:
                return None, None
            red_balls = [int(num) for num in red_numbers]
            
            # 提取蓝球
            blue_numbers = re.findall(r'\d+', blue_part)
            if len(blue_numbers) != 1:
                return None, None
            blue_ball = int(blue_numbers[0])
            
            return red_balls, blue_ball
            
        except Exception as e:
            self.logger.warning(f"解析号码文本失败: {numbers_text} - {str(e)}")
            return None, None
    
    def _get_nested_value(self, data: Any, path: str) -> Any:
        """
        获取嵌套字典/对象的值
        
        Args:
            data: 数据对象
            path: 路径，如 'data.list' 或 'result.items'
            
        Returns:
            Any: 字段值
        """
        if not path:
            return data
        
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if 0 <= index < len(current) else None
            else:
                return None
                
            if current is None:
                break
        
        return current 