<template>
  <div class="prediction-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">🎮</span>
        娱乐预测
      </h2>
      <p class="page-description">
        基于统计算法的娱乐性预测功能（仅供学习，不具有实用性）
      </p>
    </div>

    <!-- 重要免责声明 -->
    <el-alert
      title="⚠️ 重要免责声明"
      type="warning"
      :closable="false"
      show-icon
      class="disclaimer-alert"
    >
      <p><strong>本预测功能仅用于数据分析技术学习：</strong></p>
      <ul>
        <li>预测结果纯属娱乐，不具有任何实用性或准确性</li>
        <li>彩票开奖结果完全随机，无法通过历史数据预测</li>
        <li>请勿将预测结果作为任何投注依据</li>
        <li>使用本功能即表示您理解并同意以上声明</li>
      </ul>
    </el-alert>

    <!-- 预测参数选择 -->
    <el-card class="prediction-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">⚙️</span>
          <span class="header-title">预测参数设置</span>
        </div>
      </template>
      
      <el-form :model="predictionForm" label-width="120px">
        <el-form-item label="预测算法">
          <el-select v-model="predictionForm.algorithm" placeholder="选择预测算法">
            <el-option label="频率统计" value="frequency" />
            <el-option label="趋势分析" value="trend" />
            <el-option label="线性回归" value="regression" />
            <el-option label="组合算法" value="ensemble" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="预测期号">
          <el-input
            v-model="predictionForm.targetIssue"
            placeholder="输入预测期号，如：2024101"
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="generatePrediction" 
            :loading="loading"
            size="large"
          >
            <span class="button-icon">🎲</span>
            生成娱乐预测
          </el-button>
          
          <el-button @click="resetForm" size="large">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预测结果展示 -->
    <el-card v-if="predictionResult" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">🎯</span>
          <span class="header-title">预测结果</span>
          <div class="header-actions">
            <el-tag type="warning" size="small">仅供娱乐</el-tag>
            <el-button 
              v-if="isAuthenticated"
              size="small" 
              type="warning" 
              @click="addPredictionToFavorites(predictionResult)"
            >
              <el-icon><Star /></el-icon>
              收藏此预测
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="prediction-display">
        <div class="prediction-info">
          <p><strong>预测期号：</strong>{{ predictionResult.target_issue }}</p>
          <p><strong>使用算法：</strong>{{ getAlgorithmName(predictionResult.algorithm) }}</p>
          <p><strong>置信度：</strong>{{ predictionResult.confidence }}%（仅为算法参数，无实际意义）</p>
        </div>
        
        <div class="predicted-numbers">
          <div class="numbers-section">
            <h3 class="section-title">预测红球</h3>
            <div class="balls-container">
              <span
                v-for="ball in predictionResult.predicted_red_balls"
                :key="ball"
                class="ball red-ball"
              >
                {{ ball }}
              </span>
            </div>
          </div>
          
          <div class="numbers-section">
            <h3 class="section-title">预测蓝球</h3>
            <div class="balls-container">
              <span class="ball blue-ball">
                {{ predictionResult.predicted_blue_ball }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="prediction-note">
          <el-alert
            title="学习提示"
            type="info"
            :closable="false"
            show-icon
          >
            这是一个基于{{ getAlgorithmName(predictionResult.algorithm) }}的示例预测。
            实际上，彩票号码是完全随机的，任何预测都不具有实际价值。
            本功能旨在演示数据分析算法的应用。
          </el-alert>
        </div>
      </div>
    </el-card>

    <!-- 预测历史记录 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">📋</span>
          <span class="header-title">预测历史记录</span>
          <el-button v-if="isAuthenticated" size="small" @click="loadPredictionHistory" :loading="loadingHistory">
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 未登录用户显示登录引导 -->
      <div v-if="!isAuthenticated" class="login-guide">
        <el-alert
          title="登录后可保存预测历史记录"
          type="info"
          :closable="false"
          show-icon
        >
          <p>登录后，您的预测记录会自动保存，最多保留最近50条记录，方便您跟踪学习进度。</p>
        </el-alert>
        
        <div class="login-buttons">
          <el-button type="primary" @click="$emit('show-login')">
            立即登录
          </el-button>
          <el-button @click="$emit('show-register')">
            免费注册
          </el-button>
        </div>
      </div>
      
      <!-- 登录用户显示历史记录 -->
      <div v-else>
        <div v-if="loadingHistory" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="predictionHistory.length > 0">
          <div class="history-info">
            <el-tag type="success" size="small">
              已保存 {{ predictionHistory.length }} 条记录 (最多50条)
            </el-tag>
          </div>
          
          <el-table
            :data="predictionHistory"
            stripe
            style="width: 100%; margin-top: 15px; table-layout: fixed;"
            class="fixed-header-table"
          >
            <el-table-column prop="target_issue" label="预测期号" width="120" align="center" :resizable="false" show-overflow-tooltip />
            <el-table-column prop="algorithm" label="算法" width="100" align="center" :resizable="false" show-overflow-tooltip>
              <template #default="scope">
                {{ getAlgorithmName(scope.row.algorithm) }}
              </template>
            </el-table-column>
            <el-table-column label="预测红球" align="center" :resizable="false" show-overflow-tooltip>
              <template #default="scope">
                <div class="balls-display">
                  <span
                    v-for="ball in scope.row.predicted_red_balls"
                    :key="ball"
                    class="ball red-ball small"
                  >
                    {{ ball }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_blue_ball" label="预测蓝球" width="80" align="center" :resizable="false" show-overflow-tooltip>
              <template #default="scope">
                <span class="ball blue-ball small">
                  {{ scope.row.predicted_blue_ball }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="80" align="center" :resizable="false" show-overflow-tooltip>
              <template #default="scope">
                {{ scope.row.confidence }}%
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="150" align="center" :resizable="false" show-overflow-tooltip>
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" :resizable="false">
              <template #default="scope">
                <el-button
                  size="small"
                  type="warning"
                  @click="addPredictionToFavorites(scope.row)"
                >
                  <el-icon><Star /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div v-else class="empty-data">
          <el-empty description="暂无预测记录">
            <el-button type="primary" @click="generatePrediction">
              生成第一个预测
            </el-button>
          </el-empty>
        </div>
      </div>
    </el-card>

    <!-- 算法说明 -->
    <el-card class="algorithm-info" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">📚</span>
          <span class="header-title">算法说明</span>
        </div>
      </template>
      
      <el-collapse>
        <el-collapse-item title="频率统计算法" name="frequency">
          <p>基于历史开奖数据中号码出现的频率进行预测。选择出现频率较高的号码作为预测结果。</p>
          <p><strong>注意：</strong>这种方法在理论上没有预测价值，因为每次开奖都是独立事件。</p>
        </el-collapse-item>
        
        <el-collapse-item title="趋势分析算法" name="trend">
          <p>分析号码出现的时间趋势，预测可能"该出现"的号码。</p>
          <p><strong>注意：</strong>彩票不存在"趋势"，每个号码在每次开奖中的概率都相同。</p>
        </el-collapse-item>
        
        <el-collapse-item title="线性回归算法" name="regression">
          <p>使用机器学习中的线性回归方法，基于历史数据进行预测。</p>
          <p><strong>注意：</strong>随机事件无法通过回归分析预测，这只是算法演示。</p>
        </el-collapse-item>
        
        <el-collapse-item title="组合算法" name="ensemble">
          <p>结合多种算法的结果，使用加权平均等方法得出最终预测。</p>
          <p><strong>注意：</strong>多个无效算法的组合仍然无效，但可以学习集成学习的概念。</p>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Star } from '@element-plus/icons-vue'
import axios from 'axios'

// 定义组件事件
const emit = defineEmits(['show-login', 'show-register'])

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const loadingHistory = ref(false)
const predictionResult = ref(null)
const predictionHistory = ref([])

// 用户认证状态
const isAuthenticated = computed(() => {
  return localStorage.getItem('token') && localStorage.getItem('user')
})

// 预测表单
const predictionForm = reactive({
  algorithm: 'frequency',
  targetIssue: ''
})

// 算法名称映射
const algorithmNames = {
  frequency: '频率统计',
  trend: '趋势分析',
  regression: '线性回归',
  ensemble: '组合算法'
}

// 方法
const getAlgorithmName = (algorithm) => {
  return algorithmNames[algorithm] || algorithm
}

const formatDateTime = (dateTimeStr) => {
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}

const generatePrediction = async () => {
  if (!predictionForm.targetIssue) {
    ElMessage.warning('请输入预测期号')
    return
  }

  loading.value = true
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/predictions/generate/`, {
      algorithm: predictionForm.algorithm,
      target_issue: predictionForm.targetIssue
    })
    
    if (response.data.code === 200 && response.data.data) {
      predictionResult.value = response.data.data
      
      // 根据用户状态显示不同消息
      if (response.data.user_status === 'authenticated') {
        ElMessage.success('娱乐预测生成成功，已保存到您的历史记录！')
        // 刷新历史记录
        loadPredictionHistory()
      } else {
        ElMessage.success('娱乐预测生成成功！登录后可保存历史记录。')
        // 显示登录提示
        if (response.data.login_hint) {
          setTimeout(() => {
            ElMessage.info(response.data.login_hint)
          }, 2000)
        }
      }
    } else {
      ElMessage.error(response.data.message || '预测生成失败')
    }
  } catch (error) {
    console.error('生成预测失败:', error)
    if (error.response && error.response.status === 401) {
      ElMessage.warning('请先登录后再使用预测功能')
    } else {
      ElMessage.error('生成预测失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}

const loadPredictionHistory = async () => {
  // 只有登录用户才加载历史记录
  if (!isAuthenticated.value) {
    predictionHistory.value = []
    return
  }

  loadingHistory.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/predictions/`)
    
    if (response.data && Array.isArray(response.data.results)) {
      predictionHistory.value = response.data.results
    } else if (response.data && Array.isArray(response.data)) {
      predictionHistory.value = response.data
    } else {
      predictionHistory.value = []
    }
  } catch (error) {
    console.error('加载预测历史失败:', error)
    predictionHistory.value = []
    if (error.response && error.response.status === 401) {
      ElMessage.warning('请登录后查看历史记录')
    }
  } finally {
    loadingHistory.value = false
  }
}

const resetForm = () => {
  predictionForm.algorithm = 'frequency'
  predictionForm.targetIssue = ''
  predictionResult.value = null
}

// 快捷收藏预测记录功能
const addPredictionToFavorites = async (prediction) => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录后再收藏')
    return
  }
  
  try {
    // 先检查是否已经收藏过
    const checkResponse = await axios.get(`${API_BASE_URL}/api/v1/favorites/`)
    if (checkResponse.status === 200) {
      const existingFavorites = checkResponse.data.results || checkResponse.data
      const existingFavorite = existingFavorites.find(fav => 
        fav.favorite_type === 'prediction' && fav.object_id === prediction.id
      )
      
      if (existingFavorite) {
        ElMessage.warning(`预测记录 ${prediction.target_issue} 已经收藏过了`)
        return
      }
    }
    
    const submitData = {
      favorite_type: 'prediction',
      object_id: prediction.id,
      title: `预测 ${prediction.target_issue} - ${getAlgorithmName(prediction.algorithm)}`,
      description: `红球: ${prediction.predicted_red_balls.join(', ')} 蓝球: ${prediction.predicted_blue_ball} (置信度: ${prediction.confidence}%)`,
      tags: ['预测记录', prediction.algorithm, prediction.target_issue],
      is_public: false
    }
    
    const response = await axios.post(`${API_BASE_URL}/api/v1/favorites/`, submitData)
    
    // Django DRF创建成功返回201状态码
    if (response.status === 201) {
      ElMessage.success('收藏成功！')
    } else {
      ElMessage.error('收藏失败')
    }
    
  } catch (error) {
    console.error('收藏失败:', error)
    
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      if (status === 401) {
        ElMessage.error('请先登录后再收藏')
      } else if (status === 400) {
        // 显示验证错误信息
        const errorData = error.response.data
        if (errorData && typeof errorData === 'object') {
          const errors = Object.values(errorData).flat()
          ElMessage.error(`收藏失败: ${errors.join(', ')}`)
        } else {
          ElMessage.error('收藏数据格式错误')
        }
      } else if (status === 500) {
        // 500错误通常是重复收藏导致的IntegrityError
        ElMessage.warning('该预测记录已经收藏过了')
      } else {
        ElMessage.error(`收藏失败 (${status})`)
      }
    } else if (error.request) {
      // 网络错误
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      // 其他错误
      ElMessage.error('收藏失败，请稍后重试')
    }
  }
}

// 组件挂载时的处理
onMounted(() => {
  // 只有登录用户才加载历史记录
  if (isAuthenticated.value) {
    loadPredictionHistory()
  }
  
  // 自动生成下一期期号
  const today = new Date()
  const year = today.getFullYear()
  const dayOfYear = Math.floor((today - new Date(year, 0, 0)) / (1000 * 60 * 60 * 24))
  const estimatedIssue = Math.floor(dayOfYear / 3) + 1 // 假设每3天一期
  predictionForm.targetIssue = `${year}${String(estimatedIssue).padStart(3, '0')}`
})
</script>

<style scoped>
.prediction-container {
  max-width: 100%;
}

/* 页面头部样式 */
.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  color: #2c3e50;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon {
  font-size: 32px;
  margin-right: 10px;
}

.page-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* 免责声明样式 */
.disclaimer-alert {
  margin-bottom: 20px;
}

.disclaimer-alert ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.disclaimer-alert li {
  margin-bottom: 5px;
  line-height: 1.5;
}

/* 卡片样式 */
.prediction-card, .result-card, .history-card, .algorithm-info {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-icon {
  font-size: 18px;
  margin-right: 8px;
}

.header-title {
  font-size: 16px;
  font-weight: bold;
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 按钮样式 */
.button-icon {
  margin-right: 5px;
}

/* 预测结果样式 */
.prediction-display {
  text-align: center;
}

.prediction-info {
  margin-bottom: 30px;
  font-size: 16px;
  color: #666;
}

.prediction-info p {
  margin: 10px 0;
}

.numbers-section {
  margin: 30px 0;
}

.section-title {
  font-size: 20px;
  color: #2c3e50;
  margin-bottom: 15px;
}

.balls-container {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.balls-display {
  display: flex;
  gap: 5px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 球号样式 */
.ball {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: white;
}

.ball.small {
  width: 24px;
  height: 24px;
  font-size: 12px;
}

.red-ball {
  background: linear-gradient(45deg, #ff6b6b, #ff5252);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

.blue-ball {
  background: linear-gradient(45deg, #4dabf7, #339af0);
  box-shadow: 0 4px 8px rgba(77, 171, 247, 0.3);
}

.prediction-note {
  margin-top: 30px;
}

/* 加载和空数据样式 */
.loading-container, .empty-data {
  text-align: center;
  padding: 40px 20px;
}

/* 响应式设计 */
/* 平板端适配 (768px - 1024px) */
@media (max-width: 1024px) and (min-width: 768px) {
  .page-title {
    font-size: 26px;
  }
  
  .title-icon {
    font-size: 30px;
  }
  
  .ball {
    width: 34px;
    height: 34px;
    font-size: 13px;
  }
  
  .ball.small {
    width: 20px;
    height: 20px;
    font-size: 10px;
  }
  
  .balls-container {
    gap: 6px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .prediction-info {
    margin: 15px 0;
  }
  
  .prediction-meta {
    font-size: 13px;
  }
  
  .accuracy-info {
    font-size: 13px;
  }
}

/* 移动端适配 (< 768px) */
@media (max-width: 768px) {
  .page-title {
    font-size: 20px;
    text-align: center;
  }
  
  .title-icon {
    font-size: 24px;
  }
  
  .page-description {
    font-size: 14px;
    text-align: center;
  }
  
  .prediction-form {
    padding: 15px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-group label {
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .ball {
    width: 30px;
    height: 30px;
    font-size: 12px;
    margin: 1px;
  }
  
  .ball.small {
    width: 18px;
    height: 18px;
    font-size: 9px;
  }
  
  .balls-container {
    gap: 4px;
    justify-content: center;
  }
  
  .section-title {
    font-size: 16px;
    text-align: center;
  }
  
  .prediction-display {
    text-align: center;
    padding: 15px;
  }
  
  .numbers-section {
    margin: 15px 0;
  }
  
  .prediction-info {
    margin: 15px 0;
    text-align: center;
  }
  
  .prediction-meta {
    font-size: 12px;
    margin-bottom: 10px;
  }
  
  .accuracy-info {
    font-size: 12px;
  }
  
  .login-guide {
    padding: 15px;
  }
  
  .login-buttons {
    margin-top: 15px;
  }
  
  .login-buttons .el-button {
    margin: 5px;
    width: calc(50% - 10px);
  }
  
  .history-info {
    margin-bottom: 10px;
    font-size: 12px;
  }
  
  .prediction-card {
    margin-bottom: 15px;
    padding: 12px;
  }
  
  .prediction-note {
    margin-top: 20px;
    padding: 15px;
  }
}

/* 小屏移动端适配 (< 480px) */
@media (max-width: 480px) {
  .page-title {
    font-size: 18px;
  }
  
  .title-icon {
    font-size: 20px;
  }
  
  .page-description {
    font-size: 12px;
  }
  
  .prediction-form {
    padding: 12px;
  }
  
  .form-group {
    margin-bottom: 12px;
  }
  
  .form-group label {
    font-size: 13px;
  }
  
  .ball {
    width: 26px;
    height: 26px;
    font-size: 11px;
  }
  
  .ball.small {
    width: 16px;
    height: 16px;
    font-size: 8px;
  }
  
  .balls-container {
    gap: 3px;
  }
  
  .section-title {
    font-size: 14px;
  }
  
  .prediction-display {
    padding: 12px;
  }
  
  .numbers-section {
    margin: 12px 0;
  }
  
  .prediction-info {
    margin: 12px 0;
  }
  
  .prediction-meta {
    font-size: 11px;
    margin-bottom: 8px;
  }
  
  .accuracy-info {
    font-size: 11px;
  }
  
  .login-guide {
    padding: 12px;
  }
  
  .login-buttons .el-button {
    width: 100%;
    margin: 5px 0;
  }
  
  .history-info {
    font-size: 11px;
  }
  
  .prediction-card {
    margin-bottom: 12px;
    padding: 10px;
  }
  
  .prediction-note {
    margin-top: 15px;
    padding: 12px;
  }
}

/* 登录引导样式 */
.login-guide {
  text-align: center;
  padding: 20px;
}

.login-buttons {
  margin-top: 20px;
}

.login-buttons .el-button {
  margin: 0 10px;
}

/* 历史记录信息样式 */
.history-info {
  margin-bottom: 15px;
  text-align: center;
}
</style> 