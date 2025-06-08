<template>
  <div class="profile-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">👤</span>
        个人中心
      </h2>
      <p class="page-description">
        管理您的个人信息和账户设置
      </p>
    </div>

    <el-row :gutter="20">
      <!-- 用户信息卡片 -->
      <el-col :xs="24" :md="12">
        <el-card class="profile-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📋</span>
              <span class="header-title">基本信息</span>
              <el-button 
                type="text" 
                @click="editMode = !editMode"
                :icon="editMode ? 'Close' : 'Edit'"
              >
                {{ editMode ? '取消' : '编辑' }}
              </el-button>
            </div>
          </template>
          
          <div v-if="!editMode" class="profile-info">
            <div class="info-item">
              <label>用户名：</label>
              <span>{{ userInfo.username }}</span>
            </div>
            <div class="info-item">
              <label>邮箱：</label>
              <span>{{ userInfo.email }}</span>
            </div>
            <div class="info-item">
              <label>姓名：</label>
              <span>{{ userInfo.first_name || '未设置' }}</span>
            </div>
            <div class="info-item">
              <label>注册时间：</label>
              <span>{{ formatDateTime(userInfo.date_joined) }}</span>
            </div>
            <div class="info-item">
              <label>最后登录：</label>
              <span>{{ formatDateTime(userInfo.last_login) }}</span>
            </div>
          </div>
          
          <el-form 
            v-else
            :model="editForm" 
            :rules="editRules" 
            ref="editFormRef"
            label-width="80px"
          >
            <el-form-item label="用户名">
              <el-input v-model="editForm.username" disabled />
              <div class="form-tip">用户名不可修改</div>
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="editForm.email" />
            </el-form-item>
            
            <el-form-item label="姓名" prop="first_name">
              <el-input v-model="editForm.first_name" placeholder="请输入真实姓名" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="updateLoading">
                保存修改
              </el-button>
              <el-button @click="cancelEdit">
                取消
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 密码修改卡片 -->
      <el-col :xs="24" :md="12">
        <el-card class="password-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">🔒</span>
              <span class="header-title">修改密码</span>
            </div>
          </template>
          
          <el-form 
            :model="passwordForm" 
            :rules="passwordRules" 
            ref="passwordFormRef"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                placeholder="请输入当前密码"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码（至少8个字符）"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 账户统计信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📊</span>
              <span class="header-title">学习统计</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="12" :sm="6" v-for="stat in userStats" :key="stat.key">
              <div class="stat-item">
                <div class="stat-icon">{{ stat.icon }}</div>
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const editMode = ref(false)
const updateLoading = ref(false)
const passwordLoading = ref(false)
const editFormRef = ref()
const passwordFormRef = ref()

// 用户信息
const userInfo = ref({
  username: '',
  email: '',
  first_name: '',
  date_joined: '',
  last_login: ''
})

// 编辑表单
const editForm = reactive({
  username: '',
  email: '',
  first_name: ''
})

// 密码修改表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 用户统计数据
const userStats = ref([
  { key: 'predictions', icon: '🎮', label: '预测次数', value: '0' },
  { key: 'analyses', icon: '📈', label: '分析次数', value: '0' },
  { key: 'login_days', icon: '📅', label: '登录天数', value: '0' },
  { key: 'study_time', icon: '⏰', label: '学习时长', value: '0小时' }
])

// 表单验证规则
const editRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 密码验证函数
const validateNewPassword = (rule, value, callback) => {
  if (value.length < 8) {
    callback(new Error('新密码至少8个字符'))
  } else if (!/^[a-zA-Z0-9]+$/.test(value)) {
    callback(new Error('密码只能包含数字和字母'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: validateNewPassword, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 方法
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '未知'
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}

const loadUserProfile = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/user/profile/`)
    
    if (response.data.code === 200) {
      userInfo.value = response.data.data
      // 同步到编辑表单
      editForm.username = userInfo.value.username
      editForm.email = userInfo.value.email
      editForm.first_name = userInfo.value.first_name
    } else {
      ElMessage.error('加载用户信息失败')
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败，请检查网络连接')
  }
}

const handleUpdateProfile = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    updateLoading.value = true
    
    const response = await axios.put(`${API_BASE_URL}/api/v1/user/profile/`, {
      email: editForm.email,
      first_name: editForm.first_name
    })
    
    if (response.data.code === 200) {
      userInfo.value = response.data.data
      editMode.value = false
      ElMessage.success('个人信息更新成功！')
    } else {
      ElMessage.error(response.data.message || '更新失败')
    }
    
  } catch (error) {
    console.error('更新个人信息失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '更新失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    updateLoading.value = false
  }
}

const cancelEdit = () => {
  editMode.value = false
  // 恢复原始数据
  editForm.username = userInfo.value.username
  editForm.email = userInfo.value.email
  editForm.first_name = userInfo.value.first_name
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    
    // 确认对话框
    await ElMessageBox.confirm(
      '修改密码后需要重新登录，确定要继续吗？',
      '确认修改密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    passwordLoading.value = true
    
    const response = await axios.post(`${API_BASE_URL}/api/v1/user/change-password/`, {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    
    if (response.data.code === 200) {
      ElMessage.success('密码修改成功！请重新登录。')
      
      // 清除本地存储的用户信息
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      
      // 重置表单
      resetPasswordForm()
      
      // 触发重新登录（这里可以发送事件给父组件）
      setTimeout(() => {
        window.location.reload()
      }, 1500)
      
    } else {
      ElMessage.error(response.data.message || '密码修改失败')
    }
    
  } catch (error) {
    if (error === 'cancel') {
      return // 用户取消操作
    }
    
    console.error('修改密码失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '密码修改失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    passwordLoading.value = false
  }
}

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const loadUserStats = async () => {
  try {
    // TODO: 等待后端API开发完成后调用真实API
    // const response = await axios.get(`${API_BASE_URL}/api/v1/user/stats/`)
    
    // 新用户默认显示0值，移除假数据
    userStats.value = [
      { key: 'predictions', icon: '🎮', label: '预测次数', value: '0' },
      { key: 'analyses', icon: '📈', label: '分析次数', value: '0' },
      { key: 'login_days', icon: '📅', label: '登录天数', value: '1' },
      { key: 'study_time', icon: '⏰', label: '学习时长', value: '0小时' }
    ]
  } catch (error) {
    console.error('加载用户统计失败:', error)
    // 错误时也显示默认的0值
    userStats.value = [
      { key: 'predictions', icon: '🎮', label: '预测次数', value: '0' },
      { key: 'analyses', icon: '📈', label: '分析次数', value: '0' },
      { key: 'login_days', icon: '📅', label: '登录天数', value: '1' },
      { key: 'study_time', icon: '⏰', label: '学习时长', value: '0小时' }
    ]
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserProfile()
  loadUserStats()
})
</script>

<style scoped>
.profile-container {
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

/* 卡片样式 */
.profile-card,
.password-card,
.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: bold;
  color: #2c3e50;
}

.header-icon {
  font-size: 20px;
  margin-right: 8px;
}

.header-title {
  flex: 1;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 用户信息展示样式 */
.profile-info {
  line-height: 1.8;
}

.info-item {
  display: flex;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  font-weight: bold;
  color: #666;
  width: 100px;
  flex-shrink: 0;
}

.info-item span {
  color: #333;
  flex: 1;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

/* 统计卡片样式 */
.stat-item {
  text-align: center;
  padding: 20px 10px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .info-item {
    flex-direction: column;
  }
  
  .info-item label {
    width: auto;
    margin-bottom: 5px;
  }
  
  .stat-item {
    margin-bottom: 15px;
  }
}
</style> 