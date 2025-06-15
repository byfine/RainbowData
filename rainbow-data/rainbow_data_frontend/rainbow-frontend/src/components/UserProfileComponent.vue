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
    
    <!-- 收藏管理 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="favorites-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-icon">⭐</span>
              <span class="header-title">我的收藏</span>
              <el-button type="primary" size="small" @click="showAddFavoriteDialog = true">
                添加收藏
              </el-button>
            </div>
          </template>
          
          <div v-if="favorites.length === 0" class="empty-state">
            <el-empty description="暂无收藏内容">
              <el-button type="primary" @click="showAddFavoriteDialog = true">添加第一个收藏</el-button>
            </el-empty>
          </div>
          
          <div v-else>
            <el-tabs v-model="activeFavoriteTab" @tab-click="handleFavoriteTabClick">
              <el-tab-pane label="全部" name="all">
                <div class="favorite-list">
                  <div v-for="favorite in favorites" :key="favorite.id" class="favorite-item">
                    <div class="favorite-content">
                      <h4>{{ favorite.title }}</h4>
                      <div class="favorite-balls" v-if="getFavoriteNumbers(favorite)">
                        <div class="balls-row">
                          <span class="balls-label">红球：</span>
                          <div class="balls-container">
                            <span
                              v-for="ball in getFavoriteNumbers(favorite).red_balls"
                              :key="ball"
                              class="ball red-ball"
                            >
                              {{ ball }}
                            </span>
                          </div>
                        </div>
                        <div class="balls-row">
                          <span class="balls-label">蓝球：</span>
                          <span class="ball blue-ball">
                            {{ getFavoriteNumbers(favorite).blue_ball }}
                          </span>
                        </div>
                      </div>
                      <p class="favorite-summary">{{ favorite.content_summary }}</p>
                      <div class="favorite-meta">
                        <el-tag size="small">{{ favorite.favorite_type_display }}</el-tag>
                        <span class="view-count">查看 {{ favorite.view_count }} 次</span>
                        <span class="create-time">{{ formatDateTime(favorite.created_at) }}</span>
                      </div>
                    </div>
                    <div class="favorite-actions">
                      <el-button type="danger" size="small" @click="handleDeleteFavorite(favorite.id)">
                        删除
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="开奖结果" name="lottery_result">
                <div class="favorite-list">
                  <div v-for="favorite in favorites.filter(f => f.favorite_type === 'lottery_result')" :key="favorite.id" class="favorite-item">
                    <div class="favorite-content">
                      <h4>{{ favorite.title }}</h4>
                      <div class="favorite-balls" v-if="getLotteryNumbers(favorite)">
                        <div class="balls-row">
                          <span class="balls-label">红球：</span>
                          <div class="balls-container">
                            <span
                              v-for="ball in getLotteryNumbers(favorite).red_balls"
                              :key="ball"
                              class="ball red-ball"
                            >
                              {{ ball }}
                            </span>
                          </div>
                        </div>
                        <div class="balls-row">
                          <span class="balls-label">蓝球：</span>
                          <span class="ball blue-ball">
                            {{ getLotteryNumbers(favorite).blue_ball }}
                          </span>
                        </div>
                      </div>
                      <p class="favorite-summary">{{ favorite.content_summary }}</p>
                      <div class="favorite-meta">
                        <el-tag size="small">{{ favorite.favorite_type_display }}</el-tag>
                        <span class="view-count">查看 {{ favorite.view_count }} 次</span>
                        <span class="create-time">{{ formatDateTime(favorite.created_at) }}</span>
                      </div>
                    </div>
                    <div class="favorite-actions">
                      <el-button type="danger" size="small" @click="handleDeleteFavorite(favorite.id)">
                        删除
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="预测记录" name="prediction">
                <div class="favorite-list">
                  <div v-for="favorite in favorites.filter(f => f.favorite_type === 'prediction')" :key="favorite.id" class="favorite-item">
                    <div class="favorite-content">
                      <h4>{{ favorite.title }}</h4>
                      <div class="favorite-balls" v-if="getPredictionNumbers(favorite)">
                        <div class="balls-row">
                          <span class="balls-label">红球：</span>
                          <div class="balls-container">
                            <span
                              v-for="ball in getPredictionNumbers(favorite).red_balls"
                              :key="ball"
                              class="ball red-ball"
                            >
                              {{ ball }}
                            </span>
                          </div>
                        </div>
                        <div class="balls-row">
                          <span class="balls-label">蓝球：</span>
                          <span class="ball blue-ball">
                            {{ getPredictionNumbers(favorite).blue_ball }}
                          </span>
                        </div>
                      </div>
                      <p class="favorite-summary">{{ favorite.content_summary }}</p>
                      <div class="favorite-meta">
                        <el-tag size="small">{{ favorite.favorite_type_display }}</el-tag>
                        <span class="view-count">查看 {{ favorite.view_count }} 次</span>
                        <span class="create-time">{{ formatDateTime(favorite.created_at) }}</span>
                      </div>
                    </div>
                    <div class="favorite-actions">
                      <el-button type="danger" size="small" @click="handleDeleteFavorite(favorite.id)">
                        删除
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="号码组合" name="number_set">
                <div class="favorite-list">
                  <div v-for="favorite in favorites.filter(f => f.favorite_type === 'number_set')" :key="favorite.id" class="favorite-item">
                    <div class="favorite-content">
                      <h4>{{ favorite.title }}</h4>
                      <div class="favorite-balls" v-if="getNumberSetNumbers(favorite)">
                        <div class="balls-row">
                          <span class="balls-label">红球：</span>
                          <div class="balls-container">
                            <span
                              v-for="ball in getNumberSetNumbers(favorite).red_balls"
                              :key="ball"
                              class="ball red-ball"
                            >
                              {{ ball }}
                            </span>
                          </div>
                        </div>
                        <div class="balls-row">
                          <span class="balls-label">蓝球：</span>
                          <span class="ball blue-ball">
                            {{ getNumberSetNumbers(favorite).blue_ball }}
                          </span>
                        </div>
                      </div>
                      <p class="favorite-summary">{{ favorite.content_summary }}</p>
                      <div class="favorite-meta">
                        <el-tag size="small">{{ favorite.favorite_type_display }}</el-tag>
                        <span class="view-count">查看 {{ favorite.view_count }} 次</span>
                        <span class="create-time">{{ formatDateTime(favorite.created_at) }}</span>
                      </div>
                    </div>
                    <div class="favorite-actions">
                      <el-button type="danger" size="small" @click="handleDeleteFavorite(favorite.id)">
                        删除
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加收藏对话框 -->
    <el-dialog v-model="showAddFavoriteDialog" title="添加收藏" width="600px">
      <el-form :model="favoriteForm" :rules="favoriteRules" ref="favoriteFormRef" label-width="100px">
        <el-form-item label="收藏类型" prop="favorite_type">
          <el-select v-model="favoriteForm.favorite_type" placeholder="请选择收藏类型" @change="handleFavoriteTypeChange">
            <el-option label="号码组合" value="number_set" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="收藏标题" prop="title">
          <el-input v-model="favoriteForm.title" placeholder="请输入收藏标题" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="favoriteForm.description" type="textarea" rows="3" placeholder="请输入描述信息" />
        </el-form-item>
        
        <!-- 号码组合输入 -->
        <div v-if="favoriteForm.favorite_type === 'number_set'">
          <el-form-item label="红球号码" prop="red_balls">
            <div class="number-input-group">
              <el-input-number
                v-for="(ball, index) in favoriteForm.red_balls"
                :key="index"
                v-model="favoriteForm.red_balls[index]"
                :min="1"
                :max="33"
                size="small"
                style="width: 80px; margin-right: 8px;"
              />
            </div>
            <div class="form-tip">
              <el-text size="small" type="info">💡 输入6个不重复的红球号码(1-33)</el-text>
            </div>
          </el-form-item>
          
          <el-form-item label="蓝球号码" prop="blue_ball">
            <el-input-number
              v-model="favoriteForm.blue_ball"
              :min="1"
              :max="16"
              size="small"
              style="width: 80px;"
            />
            <div class="form-tip">
              <el-text size="small" type="info">💡 输入1个蓝球号码(1-16)</el-text>
            </div>
          </el-form-item>
        </div>
        
        <!-- 暂无号码组合时的提示 -->
        <div v-else class="empty-tip">
          <el-alert 
            title="请选择号码组合类型" 
            type="info" 
            description="收藏功能目前支持自定义号码组合收藏。历史开奖和预测记录可以在相应页面直接收藏。"
            :closable="false"
          />
        </div>
        
        <el-form-item label="标签">
          <el-input v-model="favoriteTagInput" placeholder="输入标签后按回车添加" @keyup.enter="addFavoriteTag" />
          <div class="tags-container" style="margin-top: 8px;">
            <el-tag
              v-for="tag in favoriteForm.tags"
              :key="tag"
              closable
              @close="removeFavoriteTag(tag)"
              style="margin-right: 8px;"
            >
              {{ tag }}
            </el-tag>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="favoriteForm.is_public">公开收藏</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddFavoriteDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitFavorite" :loading="favoriteSubmitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
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

// 收藏相关数据
const favorites = ref([])
const activeFavoriteTab = ref('all')
const showAddFavoriteDialog = ref(false)
const favoriteSubmitting = ref(false)
const favoriteTagInput = ref('')
const favoriteFormRef = ref()

// 收藏表单数据
const favoriteForm = reactive({
  favorite_type: 'number_set', // 默认选择号码组合
  title: '',
  description: '',
  red_balls: [1, 2, 3, 4, 5, 6],
  blue_ball: 1,
  tags: [],
  is_public: false
})

// 数据选择相关
const lotteryResults = ref([])
const userPredictions = ref([])

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

// 收藏表单验证规则
const favoriteRules = {
  favorite_type: [
    { required: true, message: '请选择收藏类型', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入收藏标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  object_id: [
    { 
      validator: (rule, value, callback) => {
        if (favoriteForm.favorite_type !== 'number_set' && !value) {
          callback(new Error('请输入对象ID'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 工具函数
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  
  const date = new Date(dateTimeString)
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
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
    // 调用真实的用户统计API
    const response = await axios.get(`${API_BASE_URL}/api/v1/user/stats/`)
    
    if (response.data.code === 200) {
      userStats.value = response.data.data.basic_stats
    } else {
      // API调用失败时使用默认值
      userStats.value = [
        { key: 'predictions', icon: '🎮', label: '预测次数', value: '0' },
        { key: 'analyses', icon: '📈', label: '分析次数', value: '0' },
        { key: 'login_days', icon: '📅', label: '登录天数', value: '1' },
        { key: 'study_time', icon: '⏰', label: '学习时长', value: '0小时' }
      ]
    }
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

const loadFavorites = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/favorites/`)
    if (response.status === 200) {
      // 正确处理分页响应格式
      const responseData = response.data
      if (responseData.results) {
        // 分页格式：{count: 12, results: [...]}
        favorites.value = responseData.results
      } else if (Array.isArray(responseData)) {
        // 数组格式：[...]
        favorites.value = responseData
      } else {
        favorites.value = []
        console.warn('意外的收藏数据格式:', responseData)
      }
    }
  } catch (error) {
    console.error('加载收藏失败:', error)
    if (error.response && error.response.status === 401) {
      ElMessage.warning('请先登录后查看收藏')
    } else {
      ElMessage.error('加载收藏失败，请稍后重试')
    }
  }
}

const handleFavoriteTabClick = (tab) => {
  console.log('切换收藏标签:', tab.name)
}

const handleDeleteFavorite = async (favoriteId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个收藏吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await axios.delete(`${API_BASE_URL}/api/v1/favorites/${favoriteId}/`)
    
    if (response.status === 204) {
      ElMessage.success('删除成功')
      // 重新加载收藏列表
      loadFavorites()
    } else {
      ElMessage.error('删除失败')
    }
    
  } catch (error) {
    if (error === 'cancel') {
      return // 用户取消操作
    }
    
    console.error('删除收藏失败:', error)
    ElMessage.error('删除失败，请稍后重试')
  }
}

const handleFavoriteTypeChange = () => {
  // 号码组合类型切换时重置号码
  if (favoriteForm.favorite_type === 'number_set') {
    favoriteForm.red_balls = [1, 2, 3, 4, 5, 6]
    favoriteForm.blue_ball = 1
  }
}

const addFavoriteTag = (tag) => {
  const tagToAdd = tag || favoriteTagInput.value.trim()
  if (tagToAdd && !favoriteForm.tags.includes(tagToAdd)) {
    favoriteForm.tags.push(tagToAdd)
    favoriteTagInput.value = ''
  }
}

const removeFavoriteTag = (tag) => {
  const index = favoriteForm.tags.indexOf(tag)
  if (index > -1) {
    favoriteForm.tags.splice(index, 1)
  }
}

const resetFavoriteForm = () => {
  favoriteForm.favorite_type = 'number_set'
  favoriteForm.title = ''
  favoriteForm.description = ''
  favoriteForm.red_balls = [1, 2, 3, 4, 5, 6]
  favoriteForm.blue_ball = 1
  favoriteForm.tags = []
  favoriteForm.is_public = false
  favoriteTagInput.value = ''
}

// 号码解析函数
const getFavoriteNumbers = (favorite) => {
  if (favorite.favorite_type === 'lottery_result') {
    return getLotteryNumbers(favorite)
  } else if (favorite.favorite_type === 'prediction') {
    return getPredictionNumbers(favorite)
  } else if (favorite.favorite_type === 'number_set') {
    return getNumberSetNumbers(favorite)
  }
  return null
}

const getLotteryNumbers = (favorite) => {
  try {
    // 从description中解析号码 "红球: 5, 10, 11, 15, 19, 30 蓝球: 13"
    const description = favorite.description
    if (!description) return null
    
    const redBallMatch = description.match(/红球:\s*([0-9,\s]+)/)
    const blueBallMatch = description.match(/蓝球:\s*(\d+)/)
    
    if (redBallMatch && blueBallMatch) {
      const redBalls = redBallMatch[1]
        .split(',')
        .map(ball => parseInt(ball.trim()))
        .filter(ball => !isNaN(ball))
        .sort((a, b) => a - b)
      
      const blueBall = parseInt(blueBallMatch[1])
      
      return {
        red_balls: redBalls,
        blue_ball: blueBall
      }
    }
  } catch (error) {
    console.error('解析开奖结果号码失败:', error)
  }
  return null
}

const getPredictionNumbers = (favorite) => {
  try {
    // 从description中解析号码 "红球: 01, 05, 12 蓝球: 08 (置信度: 75%)"
    const description = favorite.description
    if (!description) return null
    
    const redBallMatch = description.match(/红球:\s*([0-9,\s]+)/)
    const blueBallMatch = description.match(/蓝球:\s*(\d+)/)
    
    if (redBallMatch && blueBallMatch) {
      const redBalls = redBallMatch[1]
        .split(',')
        .map(ball => parseInt(ball.trim()))
        .filter(ball => !isNaN(ball))
        .sort((a, b) => a - b)
      
      const blueBall = parseInt(blueBallMatch[1])
      
      return {
        red_balls: redBalls,
        blue_ball: blueBall
      }
    }
  } catch (error) {
    console.error('解析预测记录号码失败:', error)
  }
  return null
}

const getNumberSetNumbers = (favorite) => {
  try {
    // 从content_data中获取号码
    if (favorite.content_data && favorite.content_data.red_balls && favorite.content_data.blue_ball) {
      return {
        red_balls: favorite.content_data.red_balls.sort((a, b) => a - b),
        blue_ball: favorite.content_data.blue_ball
      }
    }
  } catch (error) {
    console.error('解析号码组合失败:', error)
  }
  return null
}

const handleSubmitFavorite = async () => {
  if (!favoriteFormRef.value) return
  
  try {
    await favoriteFormRef.value.validate()
    
    favoriteSubmitting.value = true
    
    // 构建提交数据 - 现在只支持号码组合
    const submitData = {
      favorite_type: favoriteForm.favorite_type,
      title: favoriteForm.title,
      description: favoriteForm.description,
      is_public: favoriteForm.is_public,
      tags: favoriteForm.tags,
      content_data: {
        red_balls: favoriteForm.red_balls,
        blue_ball: favoriteForm.blue_ball
      }
    }
    
    const response = await axios.post(`${API_BASE_URL}/api/v1/favorites/`, submitData)
    
    // Django DRF创建成功返回201状态码
    if (response.status === 201) {
      ElMessage.success('添加收藏成功！')
      showAddFavoriteDialog.value = false
      resetFavoriteForm()
      loadFavorites()
    } else {
      ElMessage.error('添加收藏失败')
    }
    
  } catch (error) {
    console.error('添加收藏失败:', error)
    
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
  } finally {
    favoriteSubmitting.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserProfile()
  loadUserStats()
  loadFavorites()
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
/* 平板端适配 (768px - 1024px) */
@media (max-width: 1024px) and (min-width: 768px) {
  .page-title {
    font-size: 26px;
  }
  
  .title-icon {
    font-size: 30px;
  }
  
  .stat-item {
    padding: 18px 8px;
  }
  
  .stat-icon {
    font-size: 28px;
    margin-bottom: 8px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .stat-label {
    font-size: 13px;
  }
  
  .info-item {
    margin-bottom: 12px;
    padding: 8px 0;
  }
  
  .favorite-item {
    padding: 12px;
    margin-bottom: 8px;
  }
  
  .favorite-content h4 {
    font-size: 15px;
  }
  
  .favorite-summary {
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
  
  .user-stats {
    gap: 10px;
  }
  
  .stat-item {
    margin-bottom: 10px;
    padding: 15px 8px;
  }
  
  .stat-icon {
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .info-item {
    flex-direction: column;
    margin-bottom: 10px;
    padding: 6px 0;
  }
  
  .info-item label {
    width: auto;
    margin-bottom: 5px;
    font-size: 13px;
  }
  
  .info-item span {
    font-size: 14px;
  }
  
  .form-tip {
    font-size: 11px;
  }
  
  .favorite-list {
    min-height: 150px;
  }
  
  .favorite-item {
    padding: 10px;
    margin-bottom: 8px;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .favorite-content {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .favorite-content h4 {
    font-size: 14px;
    margin-bottom: 6px;
  }
  
  .favorite-summary {
    font-size: 12px;
    margin-bottom: 8px;
  }
  
  .favorite-meta {
    font-size: 11px;
  }
  
  .favorite-actions {
    align-self: flex-end;
  }
  
  .favorite-actions .el-button {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  .add-favorite-btn {
    width: 100%;
    margin-top: 10px;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
  
  .el-dialog__body {
    padding: 15px 20px;
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
  
  .user-stats {
    gap: 8px;
  }
  
  .stat-item {
    padding: 12px 6px;
  }
  
  .stat-icon {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .stat-value {
    font-size: 16px;
  }
  
  .stat-label {
    font-size: 11px;
  }
  
  .info-item {
    margin-bottom: 8px;
    padding: 4px 0;
  }
  
  .info-item label {
    font-size: 12px;
  }
  
  .info-item span {
    font-size: 13px;
  }
  
  .form-tip {
    font-size: 10px;
  }
  
  .favorite-item {
    padding: 8px;
    margin-bottom: 6px;
  }
  
  .favorite-content h4 {
    font-size: 13px;
    margin-bottom: 4px;
  }
  
  .favorite-summary {
    font-size: 11px;
    margin-bottom: 6px;
  }
  
  .favorite-meta {
    font-size: 10px;
  }
  
  .favorite-actions .el-button {
    padding: 3px 6px;
    font-size: 10px;
  }
  
  .el-form-item {
    margin-bottom: 12px;
  }
  
  .el-dialog__body {
    padding: 12px 15px;
  }
}

/* 收藏相关样式 */
.favorites-card {
  margin-bottom: 20px;
}

.favorite-list {
  min-height: 200px;
}

.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.favorite-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.favorite-content {
  flex: 1;
}

.favorite-content h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.favorite-summary {
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.favorite-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.favorite-actions {
  flex-shrink: 0;
  margin-left: 15px;
}

/* 收藏中的红蓝球样式 */
.favorite-balls {
  margin: 10px 0;
}

.balls-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.balls-label {
  font-size: 14px;
  color: #666;
  font-weight: bold;
  min-width: 50px;
  margin-right: 8px;
}

.balls-container {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.ball {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 11px;
  color: white;
}

.red-ball {
  background: linear-gradient(45deg, #ff6b6b, #ff5252);
  box-shadow: 0 2px 4px rgba(255, 107, 107, 0.3);
}

.blue-ball {
  background: linear-gradient(45deg, #4dabf7, #339af0);
  box-shadow: 0 2px 4px rgba(77, 171, 247, 0.3);
}

.view-count,
.create-time {
  font-size: 12px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

/* 收藏表单样式 */
.number-input-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.form-tip {
  margin-top: 4px;
}

.form-tip .el-text {
  font-size: 12px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.empty-tip {
  margin: 20px 0;
}
</style> 