<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
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
  SwitchButton,
  Monitor
} from '@element-plus/icons-vue'

// 导入组件
import HomeComponent from './components/HomeComponent.vue'
import HistoryComponent from './components/HistoryComponent.vue'
import StatisticsComponent from './components/StatisticsComponent.vue'
import PredictionComponent from './components/PredictionComponent.vue'
import LoginComponent from './components/LoginComponent.vue'
import RegisterComponent from './components/RegisterComponent.vue'
import UserProfileComponent from './components/UserProfileComponent.vue'
import CrawlerComponent from './components/CrawlerComponent.vue'

// 响应式数据
const activeIndex = ref('home')
const isAuthenticated = ref(false)
const currentUser = ref(null)
const showAuthDialog = ref(false)
const authMode = ref('login') // 'login' 或 'register'
const hasAdminPermission = ref(false)

// 页面标题映射
const pageTitleMap = {
  'home': '首页',
  'history': '历史开奖',
  'statistics': '统计分析',
  'prediction': '娱乐预测',
  'crawler': '爬虫管理',
  'profile': '个人中心'
}

// 更新页面标题
const updatePageTitle = (page) => {
  const pageTitle = pageTitleMap[page] || '首页'
  document.title = `${pageTitle} - 彩虹数据`
}

// 强制显示所有菜单项的函数
const forceShowAllMenuItems = () => {
  nextTick(() => {
    // 多种选择器确保找到所有菜单项
    const selectors = [
      '.el-menu-demo .el-menu-item',
      '.el-menu--horizontal .el-menu-item',
      '.el-menu.el-menu--horizontal .el-menu-item'
    ]
    
    selectors.forEach(selector => {
      const menuItems = document.querySelectorAll(selector)
      menuItems.forEach((item, index) => {
        // 强制设置显示样式
        item.style.setProperty('display', 'flex', 'important')
        item.style.setProperty('visibility', 'visible', 'important')
        item.style.setProperty('opacity', '1', 'important')
        item.style.setProperty('position', 'static', 'important')
        item.style.setProperty('transform', 'none', 'important')
        item.style.setProperty('left', 'auto', 'important')
        item.style.setProperty('right', 'auto', 'important')
        item.style.setProperty('top', 'auto', 'important')
        item.style.setProperty('bottom', 'auto', 'important')
        item.style.setProperty('width', 'auto', 'important')
        item.style.setProperty('height', 'auto', 'important')
        item.style.setProperty('max-width', 'none', 'important')
        item.style.setProperty('overflow', 'visible', 'important')
        
        // 移除可能的隐藏类
        item.classList.remove('hidden', 'collapse', 'el-menu-item--hidden')
      })
    })
    
    // 额外检查：如果还有隐藏的菜单项，再次强制显示
    setTimeout(() => {
      const hiddenItems = document.querySelectorAll('.el-menu-demo .el-menu-item[style*="display: none"], .el-menu-demo .el-menu-item[style*="visibility: hidden"]')
      hiddenItems.forEach(item => {
        item.style.setProperty('display', 'flex', 'important')
        item.style.setProperty('visibility', 'visible', 'important')
        item.style.setProperty('opacity', '1', 'important')
      })
    }, 100)
  })
}

// 方法
const handleSelect = (key) => {
  if (key === 'profile' && !isAuthenticated.value) {
    showAuthDialog.value = true
    authMode.value = 'login'
    return
  }
  activeIndex.value = key
  // 更新页面标题
  updatePageTitle(key)
  // 页面切换后强制显示所有菜单项
  forceShowAllMenuItems()
}

const handleNavigate = (page) => {
  if (page === 'profile' && !isAuthenticated.value) {
    showAuthDialog.value = true
    authMode.value = 'login'
    return
  }
  activeIndex.value = page
  // 更新页面标题
  updatePageTitle(page)
  // 页面切换后强制显示所有菜单项
  forceShowAllMenuItems()
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
    // 更新页面标题
    updatePageTitle('home')
    
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
    // 更新页面标题
    updatePageTitle('home')
    ElMessage.success('已退出登录')
  }
}

const onLoginSuccess = async ({ user, token }) => {
  // 保存用户信息和Token
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)
  axios.defaults.headers.common['Authorization'] = `Token ${token}`
  
  // 更新状态
  isAuthenticated.value = true
  currentUser.value = user
  showAuthDialog.value = false
  
  // 检查权限
  await checkUserPermissions()
  
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
    updatePageTitle('profile')
    forceShowAllMenuItems()
  } else if (command === 'crawler') {
    activeIndex.value = 'crawler'
    updatePageTitle('crawler')
    forceShowAllMenuItems()
  } else if (command === 'logout') {
    handleLogout()
  }
}

const checkUserPermissions = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8001/api/v1/user/permissions/')
    console.log('权限检查响应:', response.data)
    // 修复权限检查逻辑，使用正确的API响应格式
    const permissionData = response.data.data || {}
    hasAdminPermission.value = permissionData.can_manage_crawler || false
    console.log('爬虫管理权限:', hasAdminPermission.value)
  } catch (error) {
    console.error('权限检查失败:', error)
    // 权限检查失败时，默认为无权限，确保安全
    hasAdminPermission.value = false
  }
}

const checkAuthStatus = async () => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
      isAuthenticated.value = true
      currentUser.value = user
      await checkUserPermissions()
    } catch (error) {
      console.error('解析用户信息失败:', error)
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }
}

// 组件挂载时
onMounted(async () => {
  console.log('🌈 彩虹数据应用已启动')
  await checkAuthStatus()
  // 设置初始页面标题
  updatePageTitle(activeIndex.value)
  // 确保菜单项正确显示
  forceShowAllMenuItems()
  
  // 设置定时器持续检查菜单项显示状态
  setInterval(() => {
    const hiddenItems = document.querySelectorAll('.el-menu-demo .el-menu-item[style*="display: none"], .el-menu-demo .el-menu-item[style*="visibility: hidden"]')
    if (hiddenItems.length > 0) {
      console.log('发现隐藏的菜单项，强制显示')
      forceShowAllMenuItems()
    }
  }, 1000)
})

// 监听activeIndex变化，更新页面标题并确保菜单项始终显示
watch(activeIndex, (newValue) => {
  updatePageTitle(newValue)
  forceShowAllMenuItems()
  // 延迟再次检查
  setTimeout(() => {
    forceShowAllMenuItems()
  }, 200)
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
                  <el-dropdown-item v-if="hasAdminPermission" command="crawler">
                    <el-icon><Monitor /></el-icon>
                    爬虫管理
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
          <HistoryComponent :is-authenticated="isAuthenticated" />
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
        
        <!-- 爬虫管理页面 -->
        <div v-if="activeIndex === 'crawler'" class="page-content">
          <CrawlerComponent />
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
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
}

/* 确保所有页面内容宽度一致 */
* {
  box-sizing: border-box;
}

/* 隐藏不必要的滚动条 */
body {
  overflow-x: hidden;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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
  min-height: 60px;
}

/* 确保导航菜单有足够空间 */
.header-content .el-menu-demo {
  flex: 1;
  max-width: none;
  justify-content: center;
  margin: 0 20px;
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
  display: flex !important;
  flex-wrap: nowrap !important;
}

/* 最强力的菜单项显示控制 */
.el-menu-demo,
.el-menu--horizontal,
.el-menu.el-menu--horizontal {
  overflow: visible !important;
  display: flex !important;
  flex-wrap: nowrap !important;
  width: 100% !important;
  position: relative !important;
  max-width: none !important;
}

/* 强制显示所有菜单项 - 覆盖所有可能的隐藏 */
.el-menu-demo .el-menu-item,
.el-menu--horizontal .el-menu-item,
.el-menu.el-menu--horizontal .el-menu-item {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  position: static !important;
  z-index: 10 !important;
  max-width: none !important;
  width: auto !important;
  height: auto !important;
  overflow: visible !important;
}

/* 针对具体的菜单项索引强制显示 */
.el-menu-demo > .el-menu-item:nth-child(1),
.el-menu-demo > .el-menu-item:nth-child(2), 
.el-menu-demo > .el-menu-item:nth-child(3),
.el-menu-demo > .el-menu-item:nth-child(4) {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: static !important;
  transform: none !important;
  left: auto !important;
  right: auto !important;
  top: auto !important;
  bottom: auto !important;
}

/* 覆盖Element Plus可能的响应式隐藏逻辑 */
.el-menu--horizontal .el-menu-item[style],
.el-menu-demo .el-menu-item[style] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}

/* 防止菜单项被任何方式隐藏 */
.el-menu-demo .el-menu-item[class*="hidden"],
.el-menu-demo .el-menu-item[class*="collapse"] {
  display: flex !important;
  visibility: visible !important;
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
  color: white !important;
  font-weight: 500;
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

/* 主要内容样式 - 统一宽度 */
.main-container {
  flex: 1;
  background-color: #f5f7fa;
  width: 100vw;
  max-width: 100%;
  min-height: calc(100vh - 120px);
  overflow-x: hidden;
}

.main-content {
  max-width: 1200px;
  width: 1200px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.page-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  box-sizing: border-box;
  min-height: 600px;
  max-width: 1160px;
  margin: 0 auto;
}

/* 确保所有页面内容容器宽度一致 */
.page-content > * {
  max-width: 100%;
  box-sizing: border-box;
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
/* 平板端适配 (768px - 1024px) */
@media (max-width: 1024px) and (min-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .logo-icon {
    font-size: 28px;
  }
  
  .main-content {
    width: 95%;
    max-width: 1024px;
    padding: 15px;
  }
  
  .page-content {
    padding: 15px;
    max-width: 100%;
  }
}

/* 移动端适配 (< 768px) */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 10px;
    align-items: stretch;
  }
  
  .logo {
    margin-bottom: 15px;
    justify-content: center;
    font-size: 20px;
  }
  
  .logo-icon {
    font-size: 24px;
  }
  
  .logo-text {
    font-size: 18px;
  }
  
  .el-menu-demo {
    justify-content: center;
    flex-wrap: wrap !important;
    overflow: visible !important;
    width: 100% !important;
  }
  
  .el-menu-demo .el-menu-item {
    padding: 0 12px;
    font-size: 13px;
    flex-shrink: 0;
    white-space: nowrap;
    display: flex !important;
    visibility: visible !important;
  }
  
  .auth-section {
    margin-left: 0;
    margin-top: 15px;
    display: flex;
    justify-content: center;
  }
  
  .auth-buttons {
    gap: 8px;
  }
  
  .auth-btn {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .main-content {
    width: 95%;
    max-width: 768px;
    padding: 10px;
  }
  
  .page-content {
    padding: 15px;
    border-radius: 6px;
    max-width: 100%;
  }
  
  .footer-content p {
    font-size: 12px;
    margin: 6px 0;
  }
  
  .disclaimer {
    font-size: 11px;
  }
  
  .tech-info {
    font-size: 10px;
  }
}

/* 小屏移动端适配 (< 480px) */
@media (max-width: 480px) {
  .header-content {
    padding: 8px;
  }
  
  .logo {
    font-size: 18px;
    margin-bottom: 12px;
  }
  
  .logo-icon {
    font-size: 20px;
  }
  
  .el-menu-demo {
    overflow-x: auto;
    overflow-y: visible;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  
  .el-menu-demo::-webkit-scrollbar {
    display: none;
  }
  
  .el-menu-demo .el-menu-item {
    padding: 0 8px;
    font-size: 11px;
    flex-shrink: 0;
    min-width: auto;
    display: flex !important;
    visibility: visible !important;
  }
  
  .auth-btn {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  .main-content {
    padding: 8px;
  }
  
  .page-content {
    padding: 12px;
    border-radius: 4px;
  }
}

/* 大屏幕优化 (> 1200px) */
@media (min-width: 1200px) {
  .header-content {
    max-width: 1400px;
  }
  
  .main-content {
    max-width: 1400px;
  }
}
</style>
