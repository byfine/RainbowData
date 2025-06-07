# 彩虹数据 - 双色球数据分析学习网站开发规范

## 项目概述

### 1.1 项目名称
**彩虹数据 (RainbowData)** - 中国福利彩票双色球历史数据分析学习系统

### 1.2 项目目标
- 收集、存储和分析中国福利彩票双色球历史开奖数据，用于学习数据分析技术
- 提供丰富的统计分析功能，帮助理解数据分布和规律
- 为用户提供友好的Web界面进行数据查询和统计分析
- 构建简洁、实用的"彩虹数据"学习平台

### 1.3 项目特点
- 以数据分析和统计学习为主要目标
- 多维度统计分析功能
- 响应式Web设计
- 简洁实用的架构设计
- 娱乐性预测功能

### 1.4 项目定位与免责声明
- **学习目的**：本项目纯粹用于数据分析技术学习和统计知识实践
- **非商业性质**：不以盈利为目的，不提供任何形式的付费服务
- **娱乐性质**：预测功能仅供娱乐，不构成任何投注建议
- **免责声明**：彩票开奖结果完全随机，历史数据不能预测未来结果，用户需理性对待

## 功能需求

### 2.1 核心功能模块

#### 2.1.1 数据管理模块
- **历史数据导入**：支持批量导入双色球历史开奖数据
- **数据实时同步**：定时爬取最新开奖结果
- **数据验证**：确保数据完整性和准确性
- **数据备份**：定期备份历史数据

#### 2.1.2 数据分析模块
- **基础统计分析**：
  - 号码出现频率统计
  - 冷热号码分析
  - 奇偶比例分析
  - 大小比例分析
  - 和值分布分析
- **高级分析功能**：
  - 号码连号分析
  - 重复号码分析
  - 间隔期数分析
  - 跨度分析
  - AC值分析

#### 2.1.3 娱乐预测模块
- **简单预测算法**（仅供娱乐）：
  - 频率统计分析
  - 趋势分析
  - 简单的机器学习算法（如线性回归）
  - ⚠️ **重要提醒**：预测结果仅供娱乐，不具有实际指导意义
- **预测结果展示**：
  - 号码推荐（标注娱乐性质）
  - 统计学概率说明
  - 预测准确率跟踪（用于学习算法效果）

#### 2.1.4 用户管理模块
- **用户注册/登录**：邮箱注册
- **用户权限管理**：普通用户、管理员
- **个人中心**：用户资料、分析历史、收藏功能
- **学习记录**：数据分析学习轨迹、个人统计报告

#### 2.1.5 数据展示模块
- **开奖结果展示**：最新开奖、历史开奖查询
- **图表可视化**：走势图、分布图、统计图表
- **报表生成**：数据分析报告、预测报告

### 2.2 辅助功能模块

#### 2.2.1 系统管理
- **后台管理界面**：数据管理、用户管理、系统配置
- **日志管理**：操作日志、错误日志、访问日志
- **系统监控**：性能监控、数据库监控、API监控

#### 2.2.2 API服务
- **RESTful API**：提供数据查询和预测服务
- **API文档**：完整的API使用说明
- **API限流**：防止恶意请求和过度使用

## 技术架构

### 3.1 整体架构（简化版）
```
前端(Vue.js) → Web服务器(Django) → 数据库(MySQL) → 缓存(Redis)
                    ↓
               定时任务(Django Cron)
```

### 3.2 后端技术栈
- **Web框架**：Django 4.2+
- **数据库**：MySQL 8.0+
- **ORM**：Django ORM
- **缓存**：Redis 7.0+（可选，用于提升查询性能）
- **定时任务**：Django-cron（数据同步）
- **Web服务器**：Django开发服务器（开发期）/ Gunicorn（生产环境）
- **API框架**：Django REST Framework

### 3.3 前端技术栈
- **前端框架**：Vue.js 3.x
- **UI组件库**：Element Plus
- **图表库**：ECharts
- **HTTP客户端**：Axios
- **构建工具**：Vite

### 3.4 数据分析技术栈
- **科学计算**：NumPy, Pandas
- **机器学习**：Scikit-learn（基础算法）
- **数据可视化**：Matplotlib（后端图表生成）
- **统计分析**：SciPy（基础统计功能）

### 3.5 部署技术栈（简化版）
- **操作系统**：Ubuntu 22.04 LTS
- **容器化**：Docker（可选）
- **Web服务器**：Nginx（反向代理）
- **进程管理**：Systemd / Supervisor
- **监控**：基础日志监控

## 数据库设计

### 4.1 数据表结构

#### 4.1.1 开奖记录表 (lottery_results)
```sql
CREATE TABLE lottery_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    issue VARCHAR(20) NOT NULL UNIQUE COMMENT '期号',
    draw_date DATE NOT NULL COMMENT '开奖日期',
    red_ball_1 TINYINT NOT NULL COMMENT '红球1',
    red_ball_2 TINYINT NOT NULL COMMENT '红球2',
    red_ball_3 TINYINT NOT NULL COMMENT '红球3',
    red_ball_4 TINYINT NOT NULL COMMENT '红球4',
    red_ball_5 TINYINT NOT NULL COMMENT '红球5',
    red_ball_6 TINYINT NOT NULL COMMENT '红球6',
    blue_ball TINYINT NOT NULL COMMENT '蓝球',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_draw_date (draw_date),
    INDEX idx_issue (issue)
);
```

#### 4.1.2 统计分析表 (statistics)
```sql
CREATE TABLE statistics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ball_number TINYINT NOT NULL COMMENT '球号',
    ball_type ENUM('red', 'blue') NOT NULL COMMENT '球类型',
    appear_count INT DEFAULT 0 COMMENT '出现次数',
    last_appear_issue VARCHAR(20) COMMENT '最后出现期号',
    max_interval INT DEFAULT 0 COMMENT '最大间隔',
    avg_interval DECIMAL(10,2) DEFAULT 0 COMMENT '平均间隔',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_ball_type_number (ball_number, ball_type)
);
```

#### 4.1.3 用户表 (users)
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('normal', 'admin') DEFAULT 'normal',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 4.1.4 预测记录表 (predictions)
```sql
CREATE TABLE predictions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    algorithm VARCHAR(50) NOT NULL COMMENT '预测算法',
    target_issue VARCHAR(20) NOT NULL COMMENT '预测期号',
    predicted_numbers JSON NOT NULL COMMENT '预测号码',
    confidence DECIMAL(5,2) COMMENT '置信度',
    is_accurate BOOLEAN COMMENT '是否准确',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4.2 数据索引优化
- 为常用查询字段创建索引
- 组合索引优化复杂查询
- 定期分析和优化慢查询

### 4.3 数据分区策略
- 按年份对历史数据进行分区
- 提高大数据量查询性能

## API设计

### 5.1 API基础规范
- **协议**：HTTPS
- **格式**：JSON
- **认证**：JWT Token
- **版本控制**：URL版本号 `/api/v1/`

### 5.2 核心API接口

#### 5.2.1 开奖数据API
```
GET /api/v1/lottery/results/          # 获取开奖结果列表
GET /api/v1/lottery/results/{issue}/  # 获取指定期号结果
GET /api/v1/lottery/latest/           # 获取最新开奖结果
```

#### 5.2.2 统计分析API
```
GET /api/v1/statistics/frequency/     # 号码频率统计
GET /api/v1/statistics/trends/        # 趋势分析
GET /api/v1/statistics/patterns/      # 模式分析
```

#### 5.2.3 娱乐预测API
```
POST /api/v1/predictions/generate/    # 生成娱乐预测
GET /api/v1/predictions/history/      # 预测历史（学习记录）
GET /api/v1/predictions/accuracy/     # 算法学习效果统计
```

#### 5.2.4 用户管理API
```
POST /api/v1/auth/register/           # 用户注册
POST /api/v1/auth/login/              # 用户登录
GET /api/v1/user/profile/             # 用户资料
PUT /api/v1/user/profile/             # 更新资料
```

### 5.3 API响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": "2024-01-01T10:00:00Z"
}
```

## 前端需求

### 6.1 页面结构设计

#### 6.1.1 首页
- 最新开奖结果展示
- 热门号码推荐
- 预测功能入口
- 数据统计概览

#### 6.1.2 历史数据页面
- 开奖历史查询
- 多条件筛选
- 数据导出功能
- 分页显示

#### 6.1.3 统计分析页面
- 可视化图表展示
- 多维度统计分析
- 交互式数据探索
- 自定义分析参数

#### 6.1.4 娱乐预测页面
- 简单预测算法选择
- 预测结果展示（含明显的娱乐性声明）
- 历史预测查看
- 算法学习效果统计

#### 6.1.5 用户中心
- 个人信息管理
- 数据分析学习记录
- 收藏功能
- 个人统计报告

### 6.2 UI/UX设计要求
- 响应式设计，支持移动端
- 现代化扁平化设计风格
- 良好的用户体验和交互
- 数据可视化友好
- 快速加载和流畅操作

## 部署需求

### 7.1 开发环境要求
- **本地开发环境**：Windows 10
- **已安装软件**：Python 3.9+, Node.js 18+
- **需要安装**：Git, MySQL, Redis（可选）, IDE

### 7.2 服务器环境要求（学习环境）
- **操作系统**：Ubuntu 22.04 LTS（全新服务器）
- **CPU**：2核心以上
- **内存**：4GB以上
- **存储**：SSD 50GB以上
- **网络**：基础网络连接即可
- **初始状态**：无任何开发环境，需要完整搭建

### 7.3 软件环境
**本地开发环境（Windows）：**
- **Python**：3.9+（已安装）
- **Node.js**：18+（已安装）
- **Git**：最新版本
- **MySQL**：8.0+
- **IDE**：VS Code 或 PyCharm
- **数据库工具**：MySQL Workbench

**服务器环境（Ubuntu）：**
- **Python**：3.9+
- **Django**：4.2+
- **MySQL**：8.0+
- **Redis**：7.0+（可选）
- **Nginx**：1.18+
- **Git**：最新版本

### 7.4 部署架构（简化版）
```
Internet → Nginx → Django Application → MySQL + Redis(可选)
```

### 7.4 安全配置
- SSL证书配置
- 防火墙设置
- 数据库安全配置
- API限流和防护
- 日志监控和告警

## 开发阶段规划（简化版）

### 8.1 第一阶段：基础架构搭建 (1-2周)
- 项目环境搭建
- 数据库设计和创建
- Django基础框架搭建
- 基础用户认证系统
- Vue.js前端框架搭建

### 8.2 第二阶段：数据管理功能 (1-2周)
- 历史数据导入功能
- 简单的数据获取模块
- 数据验证和清洗
- 基础API接口开发
- 数据展示页面

### 8.3 第三阶段：统计分析功能 (2-3周)
- 基础统计分析算法
- ECharts数据可视化
- 多维度分析功能
- 统计API接口
- 分析结果页面

### 8.4 第四阶段：娱乐预测功能 (1-2周)
- 简单预测算法实现
- 基础机器学习模型
- 预测API接口
- 预测结果展示（含免责声明）
- 准确率跟踪

### 8.5 第五阶段：用户系统完善 (1周)
- 用户权限系统
- 个人中心功能
- 学习记录功能
- 用户体验优化

### 8.6 第六阶段：系统完善和部署 (1周)
- 基础优化
- 安全配置
- 生产环境部署
- 基础监控
- 文档整理

总计：7-11周（根据开发进度调整）

## 数据来源

### 9.1 官方数据源
- 中国福利彩票官方网站
- 各省市福彩中心官网
- 官方API接口（如有）

### 9.2 第三方数据源
- 彩票数据网站
- 开奖结果汇总网站
- 数据服务商API

### 9.3 数据获取策略
- 定时爬虫程序
- 数据验证机制
- 多源数据校验
- 异常数据处理

## 安全考虑

### 10.1 数据安全
- 数据库加密
- 敏感信息脱敏
- 定期数据备份
- 访问权限控制

### 10.2 网络安全
- HTTPS强制加密
- API接口防护
- DDoS攻击防护
- 输入验证和过滤

### 10.3 用户安全
- 密码加密存储
- 登录失败限制
- 会话安全管理
- 隐私信息保护

## 性能要求（学习环境）

### 11.1 响应时间要求
- 页面加载时间：< 5秒
- API响应时间：< 1秒
- 数据查询时间：< 3秒
- 预测计算时间：< 15秒

### 11.2 并发性能要求
- 支持50+并发用户（学习环境足够）
- 峰值QPS：200+
- 基础数据库连接池
- 简单缓存策略

### 11.3 可用性要求
- 系统可用性：95%+（学习环境可接受）
- 基础错误处理
- 简单的故障恢复
- 定期数据备份

## 监控和运维

### 12.1 系统监控
- 服务器性能监控
- 应用程序监控
- 数据库监控
- 网络监控

### 12.2 日志管理
- 应用日志
- 访问日志
- 错误日志
- 审计日志

### 12.3 告警机制
- 邮件告警
- 短信告警
- 钉钉/企微告警
- 监控大屏

## 文档要求

### 13.1 技术文档
- 系统架构文档
- API接口文档
- 数据库设计文档
- 部署运维文档

### 13.2 用户文档
- 用户使用手册
- 功能说明文档
- 常见问题解答
- 视频教程

### 13.3 开发文档
- 代码规范文档
- 开发环境搭建
- 测试用例文档
- 版本发布说明

## 质量保证

### 14.1 代码质量
- 代码审查制度
- 单元测试覆盖率 > 80%
- 集成测试
- 代码静态分析

### 14.2 测试策略
- 功能测试
- 性能测试
- 安全测试
- 兼容性测试

### 14.3 发布管理
- 版本控制策略
- 自动化部署
- 灰度发布
- 回滚机制

## 项目交付物

### 15.1 源代码
- 后端Django项目代码 (`rainbow_data_backend`)
- 前端Vue.js应用代码 (`rainbow_data_frontend`)
- 数据库脚本 (`rainbow_data_db`)
- 配置文件

### 15.2 部署包
- Docker镜像 (`rainbow-data`)
- 部署脚本
- 环境配置
- 初始化数据

### 15.3 文档资料
- 完整技术文档
- 用户使用文档
- 部署运维手册
- 彩虹数据项目总结报告

## 项目命名规范

### 16.1 项目相关命名
- **项目目录名**：`rainbow-data`
- **后端项目名**：`rainbow_data_backend`
- **前端项目名**：`rainbow_data_frontend`  
- **数据库名**：`rainbow_data_db`
- **Git仓库名**：`rainbow-data-analytics`
- **Docker镜像名**：`rainbow-data`

### 16.2 建议域名
- **主域名**：`rainbowdata.com`
- **备选域名**：`rainbow-data.net`、`rainbowdata.cn`

## 新手开发指导

### 17.1 开发工具推荐
- **IDE**: VS Code (推荐新手) / PyCharm Community
- **API测试**: Postman / VS Code REST Client 扩展
- **数据库工具**: MySQL Workbench
- **版本控制**: Git + GitHub
- **文件传输**: WinSCP (Windows到Ubuntu)
- **SSH连接**: PuTTY / Windows Terminal

### 17.2 新手特别注意事项
- **开发环境隔离**：始终在虚拟环境中进行开发
- **版本控制习惯**：频繁提交代码，写清楚commit信息
- **错误排查方法**：仔细阅读错误日志，善用搜索引擎
- **安全意识**：不要在代码中硬编码密码等敏感信息
- **文档记录**：记录开发过程中遇到的问题和解决方案

### 17.3 环境说明
- **本地开发**：Windows 10，已安装Python和Node.js
- **云服务器**：Ubuntu 22.04 LTS，全新环境需要完整搭建
- **数据库**：本地开发用MySQL，生产环境同样使用MySQL

---

**项目名称**：彩虹数据 (RainbowData)  
**文档版本**：v1.0  
**创建日期**：2025年6月  
**更新日期**：2025年6月  
**文档状态**：草案
