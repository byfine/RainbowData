"""
爬虫配置管理器
============

统一管理不同数据源的爬虫配置。
"""

import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings


class ScraperConfig:
    """
    爬虫配置管理器
    
    提供统一的配置管理接口，支持：
    1. 默认配置
    2. 数据库配置
    3. 环境变量配置
    4. 配置验证
    """
    
    # 默认配置
    DEFAULT_CONFIGS = {
        'zhcw': {
            'name': '中彩网',
            'base_url': 'https://www.zhcw.com',
            'endpoints': {
                'latest': '/kjxx/ssq/',
                'history': '/kjxx/ssq/kjgg_ssq.shtml',
                'detail': '/kjxx/ssq/{issue}.shtml'
            },
            'request': {
                'interval': 3,  # 请求间隔（秒）
                'timeout': 30,  # 超时时间（秒）
                'max_retries': 3,  # 最大重试次数
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive'
                }
            },
            'selectors': {
                'container': 'table.ssq_right_tab tbody tr',
                'issue': 'td:nth-child(1)',
                'draw_date': 'td:nth-child(2)',
                'red_balls': 'td:nth-child(3) .ball_red',
                'blue_ball': 'td:nth-child(3) .ball_blue'
            },
            'pagination': {
                'enabled': True,
                'page_param': 'page',
                'page_size': 20,
                'max_pages': 50
            }
        },
        
        'c500': {
            'name': '500彩票网',
            'base_url': 'https://datachart.500.com',
            'endpoints': {
                'latest': '/ssq/',
                'history': '/ssq/history/newinc/history.php',
                'ajax': '/ssq/history/newinc/history_ajax.php'
            },
            'request': {
                'interval': 2,
                'timeout': 25,
                'max_retries': 3,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://datachart.500.com/ssq/',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            },
            'selectors': {
                'container': '#tdata tbody tr',
                'issue': 'td:nth-child(1)',
                'draw_date': 'td:nth-child(2)',
                'numbers': 'td:nth-child(3)'
            },
            'ajax': {
                'enabled': True,
                'method': 'POST',
                'params': {
                    'start': 0,
                    'limit': 30
                }
            }
        },
        
        'api': {
            'name': '第三方API',
            'base_url': 'https://api.example.com',
            'endpoints': {
                'latest': '/lottery/ssq/latest',
                'history': '/lottery/ssq/history',
                'range': '/lottery/ssq/range'
            },
            'request': {
                'interval': 1,
                'timeout': 20,
                'max_retries': 5,
                'headers': {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            },
            'auth': {
                'type': 'api_key',
                'key_param': 'api_key',
                'key_value': None  # 需要在环境变量中设置
            },
            'field_mapping': {
                'data_path': 'data.list',
                'issue': 'issue',
                'draw_date': 'drawDate',
                'red_balls': 'redBalls',
                'blue_ball': 'blueBall'
            }
        }
    }
    
    def __init__(self):
        """初始化配置管理器"""
        self.logger = logging.getLogger('scraper.config')
        self._cache = {}
    
    def get_config(self, source_type: str, data_source_obj=None) -> Dict[str, Any]:
        """
        获取指定数据源的完整配置
        
        Args:
            source_type: 数据源类型（zhcw、c500、api）
            data_source_obj: 数据源对象（可选）
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        cache_key = f"{source_type}_{id(data_source_obj) if data_source_obj else 'default'}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 获取默认配置
        config = self.DEFAULT_CONFIGS.get(source_type, {}).copy()
        
        if not config:
            self.logger.warning(f"未找到数据源配置: {source_type}")
            return {}
        
        # 合并数据库配置
        if data_source_obj:
            config = self._merge_database_config(config, data_source_obj)
        
        # 合并环境变量配置
        config = self._merge_env_config(config, source_type)
        
        # 验证配置
        if self._validate_config(config, source_type):
            self._cache[cache_key] = config
            return config
        else:
            self.logger.error(f"配置验证失败: {source_type}")
            return {}
    
    def _merge_database_config(self, config: Dict, data_source_obj) -> Dict:
        """
        合并数据库中的配置
        
        Args:
            config: 基础配置
            data_source_obj: 数据源对象
            
        Returns:
            Dict: 合并后的配置
        """
        try:
            # 更新基础URL
            if data_source_obj.base_url:
                config['base_url'] = data_source_obj.base_url
            
            # 更新请求配置
            if hasattr(data_source_obj, 'request_interval'):
                config['request']['interval'] = data_source_obj.request_interval
            if hasattr(data_source_obj, 'timeout'):
                config['request']['timeout'] = data_source_obj.timeout
            if hasattr(data_source_obj, 'max_retries'):
                config['request']['max_retries'] = data_source_obj.max_retries
            
            # 更新headers
            if data_source_obj.headers:
                config['request']['headers'].update(data_source_obj.headers)
            
            # 更新选择器配置
            if data_source_obj.selector_config:
                config.setdefault('selectors', {})
                config['selectors'].update(data_source_obj.selector_config)
            
            # 更新字段映射
            if data_source_obj.field_mapping:
                config.setdefault('field_mapping', {})
                config['field_mapping'].update(data_source_obj.field_mapping)
                
        except Exception as e:
            self.logger.error(f"合并数据库配置失败: {str(e)}")
        
        return config
    
    def _merge_env_config(self, config: Dict, source_type: str) -> Dict:
        """
        合并环境变量配置
        
        Args:
            config: 基础配置
            source_type: 数据源类型
            
        Returns:
            Dict: 合并后的配置
        """
        try:
            # API密钥配置
            if source_type == 'api':
                api_key = getattr(settings, 'LOTTERY_API_KEY', None)
                if api_key and 'auth' in config:
                    config['auth']['key_value'] = api_key
            
            # 代理配置
            proxy_config = getattr(settings, 'SCRAPER_PROXY', None)
            if proxy_config:
                config['request']['proxy'] = proxy_config
            
            # 调试模式
            if getattr(settings, 'DEBUG', False):
                config['request']['interval'] = max(config['request']['interval'], 5)
                
        except Exception as e:
            self.logger.error(f"合并环境变量配置失败: {str(e)}")
        
        return config
    
    def _validate_config(self, config: Dict, source_type: str) -> bool:
        """
        验证配置有效性
        
        Args:
            config: 配置字典
            source_type: 数据源类型
            
        Returns:
            bool: 是否有效
        """
        try:
            # 检查必要字段
            required_fields = ['base_url', 'endpoints', 'request']
            for field in required_fields:
                if field not in config:
                    self.logger.error(f"缺少必要配置字段: {field}")
                    return False
            
            # 检查URL有效性
            base_url = config['base_url']
            if not base_url.startswith(('http://', 'https://')):
                self.logger.error(f"无效的base_url: {base_url}")
                return False
            
            # 检查请求配置
            request_config = config['request']
            if request_config['interval'] < 0:
                self.logger.error("请求间隔不能为负数")
                return False
            if request_config['timeout'] <= 0:
                self.logger.error("超时时间必须大于0")
                return False
            if request_config['max_retries'] < 0:
                self.logger.error("重试次数不能为负数")
                return False
            
            # 检查特定数据源的配置
            if source_type in ['zhcw', 'c500'] and 'selectors' not in config:
                self.logger.error(f"HTML数据源缺少selectors配置: {source_type}")
                return False
            
            if source_type == 'api' and 'field_mapping' not in config:
                self.logger.error("API数据源缺少field_mapping配置")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证异常: {str(e)}")
            return False
    
    def get_url(self, source_type: str, endpoint: str, **kwargs) -> str:
        """
        构建完整URL
        
        Args:
            source_type: 数据源类型
            endpoint: 端点名称
            **kwargs: URL参数
            
        Returns:
            str: 完整URL
        """
        config = self.get_config(source_type)
        if not config:
            return ""
        
        base_url = config['base_url'].rstrip('/')
        endpoint_path = config['endpoints'].get(endpoint, '')
        
        # 格式化端点路径
        if kwargs:
            try:
                endpoint_path = endpoint_path.format(**kwargs)
            except KeyError as e:
                self.logger.warning(f"URL参数缺失: {e}")
        
        return f"{base_url}{endpoint_path}"
    
    def get_request_config(self, source_type: str) -> Dict:
        """
        获取请求配置
        
        Args:
            source_type: 数据源类型
            
        Returns:
            Dict: 请求配置
        """
        config = self.get_config(source_type)
        return config.get('request', {})
    
    def get_selectors(self, source_type: str) -> Dict:
        """
        获取选择器配置
        
        Args:
            source_type: 数据源类型
            
        Returns:
            Dict: 选择器配置
        """
        config = self.get_config(source_type)
        return config.get('selectors', {})
    
    def get_field_mapping(self, source_type: str) -> Dict:
        """
        获取字段映射配置
        
        Args:
            source_type: 数据源类型
            
        Returns:
            Dict: 字段映射配置
        """
        config = self.get_config(source_type)
        return config.get('field_mapping', {})
    
    def clear_cache(self):
        """清除配置缓存"""
        self._cache.clear()
        self.logger.info("配置缓存已清除")
    
    def export_config(self, source_type: str) -> str:
        """
        导出配置为JSON字符串
        
        Args:
            source_type: 数据源类型
            
        Returns:
            str: JSON配置字符串
        """
        config = self.get_config(source_type)
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def import_config(self, source_type: str, config_json: str) -> bool:
        """
        从JSON字符串导入配置
        
        Args:
            source_type: 数据源类型
            config_json: JSON配置字符串
            
        Returns:
            bool: 是否成功
        """
        try:
            config = json.loads(config_json)
            if self._validate_config(config, source_type):
                self.DEFAULT_CONFIGS[source_type] = config
                self.clear_cache()
                return True
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON配置解析失败: {str(e)}")
            return False
    
    def get_supported_sources(self) -> list:
        """
        获取支持的数据源类型列表
        
        Returns:
            list: 数据源类型列表
        """
        return list(self.DEFAULT_CONFIGS.keys())
    
    def is_source_supported(self, source_type: str) -> bool:
        """
        检查是否支持指定数据源
        
        Args:
            source_type: 数据源类型
            
        Returns:
            bool: 是否支持
        """
        return source_type in self.DEFAULT_CONFIGS


# 全局配置管理器实例
scraper_config = ScraperConfig() 