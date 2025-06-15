"""
数据清洗器
=========

用于彩票数据的验证、去重、标准化处理。
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Set, Tuple, Optional
from collections import Counter


class DataCleaner:
    """
    数据清洗器类
    
    主要功能：
    1. 数据格式验证
    2. 数据去重
    3. 数据标准化
    4. 异常数据检测
    5. 数据质量评估
    """
    
    def __init__(self, source_type: str):
        """
        初始化数据清洗器
        
        Args:
            source_type: 数据源类型
        """
        self.source_type = source_type
        self.logger = logging.getLogger(f'cleaner.{source_type}')
        
        # 统计信息
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'duplicated': 0,
            'cleaned': 0
        }
    
    def clean_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        清洗原始数据
        
        Args:
            raw_data: 原始数据列表
            
        Returns:
            List[Dict]: 清洗后的数据列表
        """
        self.stats['total'] = len(raw_data)
        self.logger.info(f"开始清洗数据，共{self.stats['total']}条记录")
        
        # 1. 格式验证和标准化
        validated_data = []
        for item in raw_data:
            cleaned_item = self._validate_and_normalize(item)
            if cleaned_item:
                validated_data.append(cleaned_item)
                self.stats['valid'] += 1
            else:
                self.stats['invalid'] += 1
        
        # 2. 去重处理
        deduplicated_data = self._remove_duplicates(validated_data)
        self.stats['duplicated'] = len(validated_data) - len(deduplicated_data)
        
        # 3. 异常数据检测
        final_data = self._detect_anomalies(deduplicated_data)
        self.stats['cleaned'] = len(final_data)
        
        self._log_stats()
        return final_data
    
    def _validate_and_normalize(self, item: Dict) -> Optional[Dict]:
        """
        验证并标准化单条数据
        
        Args:
            item: 原始数据项
            
        Returns:
            Optional[Dict]: 标准化后的数据项，验证失败返回None
        """
        try:
            # 验证必要字段
            if not self._validate_required_fields(item):
                return None
            
            # 标准化期号
            issue = self._normalize_issue(item['issue'])
            if not issue:
                self.logger.warning(f"期号格式无效: {item.get('issue')}")
                return None
            
            # 标准化日期
            draw_date = self._normalize_date(item['draw_date'])
            if not draw_date:
                self.logger.warning(f"日期格式无效: {item.get('draw_date')}")
                return None
            
            # 标准化红球
            red_balls = self._normalize_red_balls(item['red_balls'])
            if not red_balls:
                self.logger.warning(f"红球数据无效: {item.get('red_balls')}")
                return None
            
            # 标准化蓝球
            blue_ball = self._normalize_blue_ball(item['blue_ball'])
            if not blue_ball:
                self.logger.warning(f"蓝球数据无效: {item.get('blue_ball')}")
                return None
            
            return {
                'issue': issue,
                'draw_date': draw_date,
                'red_balls': red_balls,
                'blue_ball': blue_ball
            }
            
        except Exception as e:
            self.logger.error(f"数据标准化失败: {str(e)} - {item}")
            return None
    
    def _validate_required_fields(self, item: Dict) -> bool:
        """
        验证必要字段是否存在
        
        Args:
            item: 数据项
            
        Returns:
            bool: 验证结果
        """
        required_fields = ['issue', 'draw_date', 'red_balls', 'blue_ball']
        for field in required_fields:
            if field not in item or item[field] is None:
                self.logger.warning(f"缺少必要字段: {field}")
                return False
        return True
    
    def _normalize_issue(self, issue: any) -> Optional[str]:
        """
        标准化期号
        
        Args:
            issue: 原始期号
            
        Returns:
            Optional[str]: 标准化后的期号
        """
        try:
            issue_str = str(issue).strip()
            
            # 移除可能的前缀和后缀
            issue_str = issue_str.replace('期', '').replace('第', '')
            
            # 确保是数字格式
            if not issue_str.isdigit():
                return None
            
            # 双色球期号通常是7位数字（如2024001）
            if len(issue_str) < 4:
                return None
            
            # 如果是4位数字，可能是简化格式（如0001），需要加上年份
            if len(issue_str) == 4:
                current_year = datetime.now().year
                issue_str = f"{current_year}{issue_str}"
            
            return issue_str
            
        except Exception:
            return None
    
    def _normalize_date(self, draw_date: any) -> Optional[date]:
        """
        标准化开奖日期
        
        Args:
            draw_date: 原始日期
            
        Returns:
            Optional[date]: 标准化后的日期
        """
        try:
            if isinstance(draw_date, date):
                return draw_date
            
            if isinstance(draw_date, datetime):
                return draw_date.date()
            
            # 字符串日期解析
            date_str = str(draw_date).strip()
            
            # 支持的日期格式
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
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _normalize_red_balls(self, red_balls: any) -> Optional[List[int]]:
        """
        标准化红球数据
        
        Args:
            red_balls: 原始红球数据
            
        Returns:
            Optional[List[int]]: 标准化后的红球列表
        """
        try:
            # 处理不同类型的输入
            if isinstance(red_balls, list):
                balls = [int(ball) for ball in red_balls]
            elif isinstance(red_balls, str):
                # 解析字符串格式，如 "01,05,12,18,25,28" 或 "1 5 12 18 25 28"
                balls = []
                for ball_str in red_balls.replace(',', ' ').split():
                    balls.append(int(ball_str.strip()))
            else:
                return None
            
            # 验证红球数据
            if len(balls) != 6:
                return None
            
            # 验证号码范围
            for ball in balls:
                if not isinstance(ball, int) or ball < 1 or ball > 33:
                    return None
            
            # 检查是否有重复
            if len(set(balls)) != 6:
                return None
            
            # 排序（标准化）
            return sorted(balls)
            
        except (ValueError, TypeError):
            return None
    
    def _normalize_blue_ball(self, blue_ball: any) -> Optional[int]:
        """
        标准化蓝球数据
        
        Args:
            blue_ball: 原始蓝球数据
            
        Returns:
            Optional[int]: 标准化后的蓝球
        """
        try:
            ball = int(blue_ball)
            
            # 验证蓝球范围
            if ball < 1 or ball > 16:
                return None
            
            return ball
            
        except (ValueError, TypeError):
            return None
    
    def _remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """
        去除重复数据
        
        Args:
            data: 数据列表
            
        Returns:
            List[Dict]: 去重后的数据列表
        """
        seen_issues = set()
        deduplicated = []
        
        for item in data:
            issue = item['issue']
            if issue not in seen_issues:
                seen_issues.add(issue)
                deduplicated.append(item)
            else:
                self.logger.warning(f"发现重复期号: {issue}")
        
        return deduplicated
    
    def _detect_anomalies(self, data: List[Dict]) -> List[Dict]:
        """
        检测异常数据
        
        Args:
            data: 数据列表
            
        Returns:
            List[Dict]: 过滤异常后的数据列表
        """
        if not data:
            return data
        
        filtered_data = []
        
        # 统计红球出现频率，检测异常
        all_red_balls = []
        for item in data:
            all_red_balls.extend(item['red_balls'])
        
        red_ball_counter = Counter(all_red_balls)
        
        # 统计蓝球出现频率
        blue_balls = [item['blue_ball'] for item in data]
        blue_ball_counter = Counter(blue_balls)
        
        for item in data:
            if self._is_data_normal(item, red_ball_counter, blue_ball_counter):
                filtered_data.append(item)
            else:
                self.logger.warning(f"检测到异常数据: {item}")
        
        return filtered_data
    
    def _is_data_normal(self, item: Dict, red_counter: Counter, blue_counter: Counter) -> bool:
        """
        检查数据是否正常
        
        Args:
            item: 数据项
            red_counter: 红球计数器
            blue_counter: 蓝球计数器
            
        Returns:
            bool: 是否正常
        """
        # 检查日期是否合理（不能是未来日期）
        if item['draw_date'] > date.today():
            return False
        
        # 检查是否过于古老（双色球2003年开始）
        if item['draw_date'] < date(2003, 1, 1):
            return False
        
        # 可以添加更多异常检测逻辑
        # 例如：检查号码组合是否过于异常等
        
        return True
    
    def _log_stats(self):
        """记录清洗统计信息"""
        self.logger.info(f"数据清洗完成:")
        self.logger.info(f"  总记录数: {self.stats['total']}")
        self.logger.info(f"  有效记录: {self.stats['valid']}")
        self.logger.info(f"  无效记录: {self.stats['invalid']}")
        self.logger.info(f"  重复记录: {self.stats['duplicated']}")
        self.logger.info(f"  最终清洗: {self.stats['cleaned']}")
        
        if self.stats['total'] > 0:
            success_rate = (self.stats['cleaned'] / self.stats['total']) * 100
            self.logger.info(f"  清洗成功率: {success_rate:.1f}%")
    
    def get_stats(self) -> Dict:
        """
        获取清洗统计信息
        
        Returns:
            Dict: 统计信息
        """
        return self.stats.copy()
    
    def validate_data_quality(self, data: List[Dict]) -> Dict:
        """
        评估数据质量
        
        Args:
            data: 数据列表
            
        Returns:
            Dict: 质量评估报告
        """
        if not data:
            return {'quality_score': 0, 'issues': ['无数据']}
        
        issues = []
        quality_score = 100
        
        # 检查期号连续性
        issues_list = [item['issue'] for item in data]
        issues_list.sort()
        
        # 检查日期连续性
        dates = [item['draw_date'] for item in data]
        dates.sort()
        
        # 检查数据完整性
        total_items = len(data)
        if total_items < 10:
            issues.append('数据量过少')
            quality_score -= 20
        
        # 检查日期跨度
        if dates:
            date_span = (dates[-1] - dates[0]).days
            if date_span < 30:
                issues.append('数据时间跨度过短')
                quality_score -= 10
        
        # 检查期号格式一致性
        issue_formats = set(len(issue) for issue in issues_list)
        if len(issue_formats) > 2:
            issues.append('期号格式不一致')
            quality_score -= 15
        
        quality_score = max(0, quality_score)
        
        return {
            'quality_score': quality_score,
            'total_records': total_items,
            'date_range': f"{dates[0]} ~ {dates[-1]}" if dates else "无",
            'issues': issues,
            'first_issue': issues_list[0] if issues_list else None,
            'last_issue': issues_list[-1] if issues_list else None
        } 