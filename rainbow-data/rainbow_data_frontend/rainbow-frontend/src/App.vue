<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { 
  HomeFilled, 
  DocumentCopy, 
  TrendCharts, 
  MagicStick,
  User,
  UserFilled,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'

// 导入组件
import HomeComponent from './components/HomeComponent.vue'
import HistoryComponent from './components/HistoryComponent.vue'
import StatisticsComponent from './components/StatisticsComponent.vue'
import PredictionComponent from './components/PredictionComponent.vue'
import LoginComponent from './components/LoginComponent.vue'
import RegisterComponent from './components/RegisterComponent.vue'
import UserProfileComponent from './components/UserProfileComponent.vue'

// 响应式数据
const activeIndex = ref('home')
const isAuthenticated = ref(false)
const currentUser = ref(null)
const showAuthDialog = ref(false)
const authMode = ref('login') // 'login' 或 'register'

// 方法
const handleSelect = (key) => {
  if (key === 'profile' && !isAuthenticated.value) {
    showAuthDialog.value = true
    authMode.value = 'login'
    return
  }
  activeIndex.value = key
}

const handleNavigate = (page) => {
  if (page === 'profile' && !isAuthenticated.value) {
    showAuthDialog.value = true
    authMode.value = 'login'
    return
  }
  activeIndex.value = page
}

const handleLogin = () => {
  showAuthDialog.value = true
  authMode.value = 'login'
}

const handleRegister = () => {
  showAuthDialog.value = true
  authMode.value = 'register'
}

const handleLogout = async () => {
  try {
    // 调用登出API
    await axios.post('http://127.0.0.1:8001/api/v1/auth/logout/')
    
    // 清除本地存储
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    
    // 更新状态
    isAuthenticated.value = false
    currentUser.value = null
    activeIndex.value = 'home'
    
    ElMessage.success('已成功退出登录')
  } catch (error) {
    console.error('登出失败:', error)
    // 即使API调用失败，也清除本地状态
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    isAuthenticated.value = false
    currentUser.value = null
    activeIndex.value = 'home'
    ElMessage.success('已退出登录')
  }
}

const onLoginSuccess = ({ user, token }) => {
  // 保存用户信息和Token
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)
  axios.defaults.headers.common['Authorization'] = `Token ${token}`
  
  // 更新状态
  isAuthenticated.value = true
  currentUser.value = user
  showAuthDialog.value = false
  
  ElMessage.success(`欢迎回来，${user.username}！`)
}

const onRegisterSuccess = ({ user, token }) => {
  // 注册成功后自动登录
  onLoginSuccess({ user, token })
}

const switchAuthMode = (mode) => {
  authMode.value = mode
}

const handleUserCommand = (command) => {
  if (command === 'profile') {
    activeIndex.value = 'profile'
  } else if (command === 'logout') {
    handleLogout()
  }
}

const checkAuthStatus = () => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
      isAuthenticated.value = true
      currentUser.value = user
    } catch (error) {
      console.error('解析用户信息失败:', error)
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }
}

// 组件挂载时
onMounted(() => {
  console.log('🌈 彩虹数据应用已启动')
  checkAuthStatus()
})
</script>

<template>
  <div id="app">
    <!-- 页面头部 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🌈</span>
          <span class="logo-text">彩虹数据</span>
        </div>
        
        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeIndex"
          class="el-menu-demo"
          mode="horizontal"
          @select="handleSelect"
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="history">
            <el-icon><DocumentCopy /></el-icon>
            <span>历史开奖</span>
          </el-menu-item>
          <el-menu-item index="statistics">
            <el-icon><TrendCharts /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          <el-menu-item index="prediction">
            <el-icon><MagicStick /></el-icon>
            <span>娱乐预测</span>
          </el-menu-item>
          <el-menu-item v-if="isAuthenticated" index="profile">
            <el-icon><UserFilled /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
        
        <!-- 用户认证区域 -->
        <div class="auth-section">
          <div v-if="!isAuthenticated" class="auth-buttons">
            <el-button type="text" @click="handleLogin" class="auth-btn">
              <el-icon><User /></el-icon>
              登录
            </el-button>
            <el-button type="primary" @click="handleRegister" size="small">
              注册
            </el-button>
          </div>
          
          <div v-else class="user-info">
            <el-dropdown @command="handleUserCommand">
              <span class="user-dropdown">
                <el-icon><UserFilled /></el-icon>
                {{ currentUser.username }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <el-main class="main-content">
        <!-- 首页内容 -->
        <div v-if="activeIndex === 'home'" class="page-content">
          <HomeComponent @navigate="handleNavigate" />
        </div>
        
        <!-- 历史开奖页面 -->
        <div v-if="activeIndex === 'history'" class="page-content">
          <HistoryComponent />
        </div>
        
        <!-- 统计分析页面 -->
        <div v-if="activeIndex === 'statistics'" class="page-content">
          <StatisticsComponent />
        </div>
        
        <!-- 娱乐预测页面 -->
        <div v-if="activeIndex === 'prediction'" class="page-content">
          <PredictionComponent 
            @show-login="handleLogin"
            @show-register="handleRegister"
          />
        </div>
        
        <!-- 个人中心页面 -->
        <div v-if="activeIndex === 'profile'" class="page-content">
          <UserProfileComponent />
        </div>
      </el-main>
    </el-container>
    
    <!-- 用户认证对话框 -->
    <el-dialog
      v-model="showAuthDialog"
      :title="authMode === 'login' ? '用户登录' : '用户注册'"
      width="90%"
      :max-width="authMode === 'login' ? '450px' : '550px'"
      :close-on-click-modal="false"
      center
    >
      <LoginComponent 
        v-if="authMode === 'login'"
        @login-success="onLoginSuccess"
        @switch-to-register="switchAuthMode('register')"
      />
      <RegisterComponent 
        v-else
        @register-success="onRegisterSuccess"
        @switch-to-login="switchAuthMode('login')"
      />
    </el-dialog>

    <!-- 页面底部 -->
    <el-footer class="footer">
      <div class="footer-content">
        <p>
          <strong>🌈 彩虹数据</strong> - 双色球数据分析学习平台
        </p>
        <p class="disclaimer">
          ⚠️ <strong>免责声明</strong>：本网站仅用于数据分析学习，预测功能纯属娱乐，不构成任何投注建议。彩票开奖结果完全随机，请理性对待。
        </p>
        <p class="tech-info">
          技术栈：Vue.js + Django + MySQL | 开发目的：学习数据分析技术
        </p>
      </div>
    </el-footer>
  </div>
</template>

<style scoped>
/* 全局样式 */
#app {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部样式 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  height: auto;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.logo-icon {
  margin-right: 8px;
  font-size: 32px;
}

.logo-text {
  font-family: 'Microsoft YaHei', sans-serif;
}

.el-menu-demo {
  background-color: transparent !important;
  border-bottom: none;
}

/* 认证区域样式 */
.auth-section {
  margin-left: 20px;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-btn {
  color: white !important;
  padding: 8px 16px;
}

.auth-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-info {
  color: white;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-dropdown .el-icon {
  margin-right: 5px;
}

.user-dropdown .el-icon--right {
  margin-left: 5px;
  margin-right: 0;
}

/* 主要内容样式 */
.main-container {
  flex: 1;
  background-color: #f5f7fa;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 底部样式 */
.footer {
  background-color: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
}

.footer-content p {
  margin: 8px 0;
}

.disclaimer {
  color: #f39c12;
  font-size: 14px;
  font-weight: bold;
}

.tech-info {
  color: #95a5a6;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 10px;
  }
  
  .logo {
    margin-bottom: 10px;
  }
  
  .auth-section {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .main-content {
    padding: 10px;
  }
}

@media (max-width: 992px) {
  .header-content {
    flex-wrap: wrap;
  }
  
  .auth-section {
    margin-left: auto;
  }
}
</style>
