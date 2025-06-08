<template>
  <div class="login-container">
    <!-- 登录表单卡片 -->
    <el-card class="login-card" shadow="always">
      <template #header>
        <div class="card-header">
          <span class="header-icon">🔐</span>
          <span class="header-title">用户登录</span>
        </div>
      </template>
      
      <el-form 
        :model="loginForm" 
        :rules="loginRules" 
        ref="loginFormRef"
        label-width="80px"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="loading"
            style="width: 100%"
            size="large"
          >
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="login-footer">
            <span>还没有账户？</span>
            <el-button type="text" @click="$emit('switch-to-register')">
              立即注册
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['login-success', 'switch-to-register'])

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const loginFormRef = ref()

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 表单验证
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // 调用登录API
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login/`, {
      username: loginForm.username,
      password: loginForm.password
    })
    
    if (response.data.code === 200) {
      // 登录成功
      const { user, token } = response.data.data
      
      // 保存用户信息和Token到localStorage
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', token)
      
      // 设置axios默认请求头
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
      
      ElMessage.success('登录成功！')
      
      // 触发登录成功事件
      emit('login-success', { user, token })
      
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
    
  } catch (error) {
    console.error('登录失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        // 显示字段验证错误
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '登录失败')
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (loginFormRef.value) {
    loginFormRef.value.resetFields()
  }
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.header-icon {
  font-size: 24px;
  margin-right: 8px;
}

.header-title {
  font-family: 'Microsoft YaHei', sans-serif;
}

.login-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.login-footer .el-button {
  padding: 0;
  margin-left: 5px;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }
  
  .login-card {
    margin: 0;
  }
}
</style> 