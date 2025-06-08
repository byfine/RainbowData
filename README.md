# 🌈 彩虹数据 (RainbowData)

**中国福利彩票双色球历史数据分析学习系统**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目简介

彩虹数据是一个用于**数据分析技术学习**的双色球历史开奖数据分析平台。本项目纯粹用于学习目的，帮助开发者掌握：

- 🔍 **数据统计分析**：频率分析、趋势分析、模式识别
- 🎯 **机器学习应用**：预测算法、特征工程、模型评估
- 🖥️ **全栈Web开发**：前后端分离、RESTful API、响应式设计
- 🗄️ **数据库设计**：关系型数据库、索引优化、数据建模

> ⚠️ **重要声明**：本项目仅供学习研究，预测功能纯属娱乐，不构成任何投注建议。彩票开奖结果完全随机，请理性对待。

## ✨ 核心功能

### 🎮 智能预测系统
- **匿名体验**：未登录用户可直接体验预测功能
- **个人历史**：登录用户享受个性化历史记录（最多50条）
- **多种算法**：频率统计、趋势分析、线性回归、组合算法

### 📊 高级数据分析
- **连号分析**：检测连续号码出现规律
- **AC值分析**：号码组合离散程度计算
- **跨度分析**：红球分布范围统计
- **间隔分析**：特定号码出现间隔研究
- **重复分析**：连续期数重复号码统计

### 👤 用户体验优化
- **渐进式增强**：免费试用 → 注册获得更多功能
- **数据安全**：用户数据完全隔离，按需限制存储
- **响应式设计**：支持桌面端和移动端

### 🕷️ 智能数据获取 (规划中)
- **多数据源爬虫**：福彩官网、第三方网站
- **自动同步**：定时获取最新开奖数据
- **数据验证**：多源交叉验证确保准确性

## 🏗️ 技术架构

### 后端技术栈
- **框架**：Django 4.2+ / Django REST Framework
- **数据库**：MySQL 8.0+
- **缓存**：Redis 7.0+ (可选)
- **异步任务**：Celery + Redis (爬虫功能)
- **数据分析**：pandas, numpy, scikit-learn

### 前端技术栈
- **框架**：Vue.js 3.x (Composition API)
- **UI组件**：Element Plus
- **图表库**：ECharts (规划中)
- **构建工具**：Vite
- **HTTP客户端**：Axios

### 数据库设计
```sql
-- 核心数据表
lottery_results     # 开奖记录
statistics         # 统计分析
predictions        # 预测记录 (按用户隔离)
user_profiles      # 用户扩展信息
crawl_logs         # 爬虫执行记录
data_sources       # 数据源配置
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Git

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/rainbow-data.git
cd rainbow-data
```

### 2. 后端环境搭建
```bash
# 创建虚拟环境
cd rainbow_data_backend
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate
# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库 (修改 settings.py)
# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 导入样例数据 (可选)
python manage.py import_lottery_data sample_data.csv

# 启动后端服务
python manage.py runserver 0.0.0.0:8001
```

### 3. 前端环境搭建
```bash
# 安装前端依赖
cd rainbow_data_frontend/rainbow-frontend
npm install

# 启动前端开发服务器
npm run dev
```

### 4. 访问应用
- **前端界面**：http://localhost:5173
- **后端API**：http://localhost:8001
- **API文档**：http://localhost:8001/api/docs/
- **管理后台**：http://localhost:8001/admin/

## 📊 项目进度

### 当前完成度：约70% 🎉

- ✅ **开发环境搭建** (100%)
- ✅ **数据库设计** (100%)
- ✅ **基础API接口** (100%)
- ✅ **用户认证系统** (85%)
- ✅ **前端基础界面** (85%)
- ✅ **智能预测系统** (90%) - **最新突破**
- ✅ **高级数据分析** (75%)
- 🚧 **可视化图表** (规划中)
- 🚧 **爬虫数据获取** (规划中)
- 🚧 **系统优化部署** (规划中)

### 最新重大更新 (2025年6月)

#### 🎯 预测功能用户体验重大优化
- **智能双模式**：匿名用户可体验，登录用户享受完整功能
- **数据安全优化**：用户预测记录完全隔离，每用户最多50条
- **用户引导体系**：从试用到注册的平滑转换
- **渐进式增强**：业界标准的用户体验设计

## 🤝 贡献指南

欢迎参与项目开发！请查看：
- [开发文档](Requirements/RD1.md) - 详细的需求规范
- [任务清单](Requirements/RD2.md) - 开发任务CheckList
- [调试日志](.cursor/myfiles/diary/debug.md) - 开发过程记录

### 开发流程
1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/new-feature`)
3. 提交更改 (`git commit -m 'Add new feature'`)
4. 推送到分支 (`git push origin feature/new-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

1. **学习目的**：本项目纯粹用于数据分析技术学习和研究
2. **非商业性质**：不提供任何形式的付费服务或商业用途
3. **预测娱乐性**：所有预测功能仅供娱乐，不具有实际指导意义
4. **随机性说明**：彩票开奖结果完全随机，历史数据无法预测未来
5. **理性对待**：请用户理性对待，不要将预测结果作为投注依据


---

**🌈 彩虹数据** - 让数据分析学习更有趣！ ✨ 