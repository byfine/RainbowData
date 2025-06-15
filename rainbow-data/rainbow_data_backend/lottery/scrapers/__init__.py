"""
彩票数据爬虫模块
===============

本模块提供多数据源的彩票开奖数据爬取功能，包括：

1. **基础架构**
   - BaseScraper: 抽象基类，定义爬虫接口规范
   - DataParser: 多格式数据解析器
   - DataCleaner: 数据清洗和验证器
   - ScraperConfig: 配置管理器

2. **数据源爬虫**
   - ZhcwScraper: 中彩网官方数据源（权威）
   - C500Scraper: 500彩票网数据源（丰富）
   - [待扩展] APIScaper: 第三方API数据源

3. **核心特性**
   - 多数据源支持
   - 增量数据更新
   - 自动数据清洗
   - 错误处理和重试
   - 合规性检查

使用示例：
```python
from lottery.scrapers import ZhcwScraper, C500Scraper
from lottery.models import DataSource

# 获取数据源配置
zhcw_source = DataSource.objects.get(name='zhcw')
c500_source = DataSource.objects.get(name='c500')

# 创建爬虫实例
zhcw_scraper = ZhcwScraper(zhcw_source)
c500_scraper = C500Scraper(c500_source)

# 获取最新数据
latest_data = zhcw_scraper.fetch_latest()
```
"""

from .base_scraper import BaseScraper
from .data_parser import DataParser
from .data_cleaner import DataCleaner
from .scraper_config import ScraperConfig, scraper_config
from .zhcw_scraper import ZhcwScraper
from .c500_scraper import C500Scraper
from .c500_scraper_enhanced import C500ScraperEnhanced

__all__ = [
    'BaseScraper',
    'DataParser', 
    'DataCleaner',
    'ScraperConfig',
    'scraper_config',
    'ZhcwScraper',
    'C500Scraper',
    'C500ScraperEnhanced',
]

__version__ = '1.0.0'
__author__ = '彩虹数据开发团队' 