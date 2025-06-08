<template>
  <div class="home-container">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1 class="title">
          <span class="rainbow-icon">🌈</span>
          欢迎来到彩虹数据
        </h1>
        <p class="subtitle">
          中国福利彩票双色球历史数据分析学习平台
        </p>
        <el-alert
          title="学习平台说明"
          type="info"
          description="本网站专注于数据分析技术学习，通过双色球历史数据进行统计分析实践。所有预测功能仅供娱乐，不构成投注建议。"
          show-icon
          :closable="false"
          class="banner-alert"
        />
      </div>
    </div>

    <!-- 最新开奖结果 -->
    <div class="latest-result-section">
      <el-card class="result-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-icon">🎯</span>
            <span class="header-title">最新开奖结果</span>
            <el-button 
              type="primary" 
              size="small" 
              @click="refreshLatest"
              :loading="loadingLatest"
            >
              刷新
            </el-button>
          </div>
        </template>
        
        <div v-if="latestResult" class="result-display">
          <div class="result-info">
            <p class="issue-info">
              <strong>期号：</strong>{{ latestResult.issue }}
              <strong style="margin-left: 20px;">开奖日期：</strong>{{ latestResult.draw_date }}
            </p>
          </div>
          
          <div class="balls-display">
            <div class="red-balls">
              <span class="balls-label">红球</span>
              <div class="balls-container">
                <span 
                  v-for="ball in getRedBalls(latestResult)" 
                  :key="ball"
                  class="ball red-ball"
                >
                  {{ ball }}
                </span>
              </div>
            </div>
            
            <div class="blue-balls">
              <span class="balls-label">蓝球</span>
              <div class="balls-container">
                <span class="ball blue-ball">
                  {{ latestResult.blue_ball }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="!loadingLatest" class="no-data">
          <el-empty description="暂无开奖数据">
            <el-button type="primary" @click="refreshLatest">加载数据</el-button>
          </el-empty>
        </div>
        
        <div v-else class="loading-data">
          <el-skeleton :rows="3" animated />
        </div>
      </el-card>
    </div>

    <!-- 功能导航 -->
    <div class="navigation-section">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="nav in navigationItems" :key="nav.key">
          <el-card 
            class="nav-card" 
            shadow="hover" 
            @click="handleNavigate(nav.key)"
            :class="{ 'clickable': true }"
          >
            <div class="nav-content">
              <div class="nav-icon">{{ nav.icon }}</div>
              <h3 class="nav-title">{{ nav.title }}</h3>
              <p class="nav-description">{{ nav.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 数据概览 -->
    <div class="overview-section">
      <el-card class="overview-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-icon">📊</span>
            <span class="header-title">数据概览</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6" v-for="stat in overviewStats" :key="stat.key">
            <div class="stat-item">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 免责声明 -->
    <div class="disclaimer-section">
      <el-alert
        title="⚠️ 重要免责声明"
        type="warning"
        :closable="false"
        show-icon
      >
        <p>
          <strong>本网站仅用于数据分析技术学习目的：</strong>
        </p>
        <ul>
          <li>所有数据分析和预测功能纯属学习实践，不具有任何实用性</li>
          <li>彩票开奖结果完全随机，历史数据无法预测未来结果</li>
          <li>请勿将任何预测结果作为投注依据</li>
          <li>请理性对待彩票，适度娱乐</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['navigate'])

// 响应式数据
const latestResult = ref(null)
const loadingLatest = ref(false)
const overviewStats = ref([
  { key: 'total', label: '总期数', value: '--' },
  { key: 'red_balls', label: '红球范围', value: '1-33' },
  { key: 'blue_balls', label: '蓝球范围', value: '1-16' },
  { key: 'update', label: '数据更新', value: '--' }
])

// 导航项配置
const navigationItems = [
  {
    key: 'history',
    icon: '📋',
    title: '历史开奖',
    description: '查看双色球历史开奖记录，支持多条件筛选'
  },
  {
    key: 'statistics',
    icon: '📈',
    title: '统计分析',
    description: '号码频率、冷热分析、走势图等统计功能'
  },
  {
    key: 'prediction',
    icon: '🎮',
    title: '娱乐预测',
    description: '基于统计算法的娱乐性预测（仅供学习）'
  },
  {
    key: 'history',
    icon: '📖',
    title: '学习记录',
    description: '记录您的数据分析学习轨迹'
  }
]

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 方法
const getRedBalls = (result) => {
  return [
    result.red_ball_1,
    result.red_ball_2,
    result.red_ball_3,
    result.red_ball_4,
    result.red_ball_5,
    result.red_ball_6
  ].sort((a, b) => a - b)
}

const refreshLatest = async () => {
  loadingLatest.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/results/latest/`)
    if (response.data.code === 200 && response.data.data) {
      latestResult.value = response.data.data
      ElMessage.success('最新开奖数据加载成功')
    } else {
      ElMessage.info('暂无开奖数据')
    }
  } catch (error) {
    console.error('获取最新开奖数据失败:', error)
    ElMessage.error('获取数据失败，请检查后端服务是否启动')
  } finally {
    loadingLatest.value = false
  }
}

const loadOverviewStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/results/`)
    if (response.data && Array.isArray(response.data.results)) {
      overviewStats.value[0].value = response.data.count || response.data.results.length
      overviewStats.value[3].value = '刚刚'
    }
  } catch (error) {
    console.error('获取概览数据失败:', error)
  }
}

const handleNavigate = (page) => {
  emit('navigate', page)
}

// 组件挂载时加载数据
onMounted(() => {
  refreshLatest()
  loadOverviewStats()
})
</script>

<style scoped>
.home-container {
  max-width: 100%;
}

/* 欢迎横幅样式 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  text-align: center;
}

.banner-content .title {
  font-size: 36px;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.rainbow-icon {
  font-size: 42px;
  margin-right: 15px;
}

.subtitle {
  font-size: 18px;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.banner-alert {
  margin-top: 20px;
  text-align: left;
}

/* 最新开奖结果样式 */
.latest-result-section {
  margin-bottom: 30px;
}

.result-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-icon {
  font-size: 20px;
  margin-right: 8px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  flex: 1;
}

.result-display {
  text-align: center;
}

.result-info {
  margin-bottom: 20px;
  font-size: 16px;
  color: #666;
}

.balls-display {
  display: flex;
  justify-content: space-around;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.red-balls, .blue-balls {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.balls-label {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #666;
}

.balls-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.ball {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: white;
}

.red-ball {
  background: linear-gradient(45deg, #ff6b6b, #ff5252);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

.blue-ball {
  background: linear-gradient(45deg, #4dabf7, #339af0);
  box-shadow: 0 4px 8px rgba(77, 171, 247, 0.3);
}

/* 功能导航样式 */
.navigation-section {
  margin-bottom: 30px;
}

.nav-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  margin-bottom: 20px;
}

.nav-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.nav-content {
  text-align: center;
  padding: 20px 10px;
}

.nav-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.nav-title {
  font-size: 18px;
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.nav-description {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

/* 数据概览样式 */
.overview-section {
  margin-bottom: 30px;
}

.overview-card {
  border-radius: 12px;
}

.stat-item {
  text-align: center;
  padding: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 免责声明样式 */
.disclaimer-section {
  margin-top: 30px;
}

.disclaimer-section ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.disclaimer-section li {
  margin-bottom: 5px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .banner-content .title {
    font-size: 28px;
  }
  
  .rainbow-icon {
    font-size: 32px;
    margin-right: 10px;
  }
  
  .balls-display {
    flex-direction: column;
    gap: 15px;
  }
  
  .ball {
    width: 35px;
    height: 35px;
    font-size: 14px;
  }
  
  .nav-icon {
    font-size: 36px;
  }
}
</style> 