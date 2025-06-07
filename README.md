# 彩虹数据 (RainbowData) - 双色球数据分析学习平台

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![Vue.js](https://img.shields.io/badge/vue.js-3.x-green.svg)

## 📖 项目简介

彩虹数据是一个基于Django + Vue.js的双色球历史数据分析学习平台，专注于数据分析技术学习和统计知识实践。

**⚠️ 重要声明：本项目纯粹用于学习目的，预测结果仅供娱乐，不构成任何投注建议！**

## 🚀 技术栈

### 后端技术
- **Framework**: Django 4.2.22
- **Database**: MySQL 8.0.42
- **API**: Django REST Framework 3.16.0
- **Documentation**: drf-spectacular 0.28.0
- **Data Analysis**: NumPy, Pandas, Scikit-learn

### 前端技术
- **Framework**: Vue.js 3.x
- **Build Tool**: Vite
- **UI Library**: Element Plus
- **Charts**: ECharts
- **HTTP Client**: Axios

## 🎯 核心功能

- 📊 **数据分析**: 号码频率统计、冷热号分析、趋势分析
- 📈 **数据可视化**: 走势图、分布图、统计图表
- 🎮 **娱乐预测**: 基于统计学的号码推荐（仅供娱乐）
- 👤 **用户管理**: 注册登录、个人中心、学习记录
- 📱 **响应式设计**: 支持PC和移动端访问

## 🛠️ 开发环境

### 系统要求
- Windows 10/11
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 项目结构
```
rainbow-data/
├── rainbow_data_backend/     # Django后端项目
│   ├── rainbow_data/        # Django配置
│   ├── manage.py           # Django管理脚本
│   └── venv/               # Python虚拟环境
├── rainbow_data_frontend/   # Vue.js前端项目
│   └── rainbow-frontend/   # Vite项目目录
├── Requirements/           # 需求文档
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明
```

## 🚀 快速开始

### 后端启动
```bash
cd rainbow_data_backend
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

### 前端启动
```bash
cd rainbow_data_frontend/rainbow-frontend
npm install
npm run dev
```

### 访问地址
- **后端管理**: http://127.0.0.1:8000/admin/
- **前端界面**: http://localhost:5173/
- **API文档**: http://127.0.0.1:8000/api/docs/

## 📊 数据库配置

```sql
-- 创建数据库
CREATE DATABASE rainbow_data_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'BaiFan'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON rainbow_data_db.* TO 'BaiFan'@'localhost';
FLUSH PRIVILEGES;
```

## 🔧 开发进度

- [x] ✅ 开发环境搭建
- [x] ✅ Django后端框架
- [x] ✅ Vue.js前端框架
- [x] ✅ MySQL数据库配置
- [ ] 🚧 数据模型设计
- [ ] 🚧 API接口开发
- [ ] 🚧 前端界面开发
- [ ] 🚧 数据分析功能

## 📝 学习记录

本项目的详细开发过程记录在 `.cursor/myfiles/diary/debug.md` 文件中，包含：
- 环境搭建步骤
- 遇到的问题和解决方案
- 技术学习心得
- 开发里程碑

## 📄 文档

- [需求规范 (RD1.md)](Requirements/RD1.md)
- [开发清单 (RD2.md)](Requirements/RD2.md)
- [开发日志 (debug.md)](.cursor/myfiles/diary/debug.md)

## ⚖️ 免责声明

1. **学习目的**: 本项目仅用于数据分析技术学习
2. **非商业性质**: 不提供任何付费服务
3. **娱乐性质**: 预测功能仅供娱乐参考
4. **随机性提醒**: 彩票开奖完全随机，历史数据无法预测未来

## 📞 联系方式

- **开发者**: BaiFan
- **邮箱**: fan.bai@garena.com
- **项目地址**: [GitHub Repository URL]

---

**🌈 让数据分析变得有趣！Happy Coding! 🚀** 