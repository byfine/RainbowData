<template>
  <div class="register-container">
    <!-- 注册表单卡片 -->
    <el-card class="register-card" shadow="always">
      <template #header>
        <div class="card-header">
          <span class="header-icon">📝</span>
          <span class="header-title">用户注册</span>
        </div>
      </template>
      
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef"
        label-width="100px"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20个字符）"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱地址"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="first_name">
          <el-input
            v-model="registerForm.first_name"
            placeholder="请输入真实姓名（可选）"
            prefix-icon="Avatar"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少8个字符）"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="password_confirm">
          <el-input
            v-model="registerForm.password_confirm"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="agreeTerms">
            我已阅读并同意
            <el-button type="text" @click="showTermsDialog = true">
              《用户协议》
            </el-button>
            和
            <el-button type="text" @click="showPrivacyDialog = true">
              《隐私政策》
            </el-button>
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister" 
            :loading="loading"
            :disabled="!agreeTerms"
            style="width: 100%"
            size="large"
          >
            <span v-if="!loading">注册</span>
            <span v-else>注册中...</span>
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <div class="register-footer">
            <span>已有账户？</span>
            <el-button type="text" @click="$emit('switch-to-login')">
              立即登录
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 用户协议对话框 -->
    <el-dialog
      v-model="showTermsDialog"
      title="用户协议"
      width="80%"
      max-width="600px"
    >
      <div class="terms-content">
        <h3>彩虹数据学习平台用户协议</h3>
        <p><strong>1. 平台性质</strong></p>
        <p>本平台是一个专注于数据分析技术学习的教育平台，通过双色球历史数据进行统计分析实践。</p>
        
        <p><strong>2. 使用目的</strong></p>
        <p>用户使用本平台仅限于学习数据分析技术，不得用于任何商业或投注目的。</p>
        
        <p><strong>3. 免责声明</strong></p>
        <p>平台提供的所有预测功能纯属娱乐和学习用途，不构成任何投注建议。彩票开奖结果完全随机，历史数据无法预测未来结果。</p>
        
        <p><strong>4. 用户责任</strong></p>
        <p>用户应理性对待彩票，适度娱乐，不得将平台预测结果作为投注依据。</p>
        
        <p><strong>5. 数据安全</strong></p>
        <p>我们承诺保护用户隐私，不会泄露用户个人信息。</p>
      </div>
      <template #footer>
        <el-button @click="showTermsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="showPrivacyDialog"
      title="隐私政策"
      width="80%"
      max-width="600px"
    >
      <div class="privacy-content">
        <h3>隐私政策</h3>
        <p><strong>1. 信息收集</strong></p>
        <p>我们仅收集用户注册时提供的基本信息（用户名、邮箱、姓名）用于账户管理。</p>
        
        <p><strong>2. 信息使用</strong></p>
        <p>收集的信息仅用于：</p>
        <ul>
          <li>提供平台服务</li>
          <li>用户身份验证</li>
          <li>学习记录统计</li>
        </ul>
        
        <p><strong>3. 信息保护</strong></p>
        <p>我们采用适当的技术和管理措施保护用户信息安全，不会向第三方泄露用户个人信息。</p>
        
        <p><strong>4. Cookie使用</strong></p>
        <p>我们使用Cookie来改善用户体验，用户可以通过浏览器设置管理Cookie。</p>
        
        <p><strong>5. 联系我们</strong></p>
        <p>如有隐私相关问题，请通过平台内联系方式与我们联系。</p>
      </div>
      <template #footer>
        <el-button @click="showPrivacyDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['register-success', 'switch-to-login'])

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const registerFormRef = ref()
const agreeTerms = ref(false)
const showTermsDialog = ref(false)
const showPrivacyDialog = ref(false)

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  first_name: '',
  password: '',
  password_confirm: ''
})

// 自定义验证函数
const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateUsername = (rule, value, callback) => {
  if (!/^[a-zA-Z0-9_]{3,20}$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线，长度3-20个字符'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUsername, trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]+$/, message: '密码只能包含数字和字母', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  if (!agreeTerms.value) {
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }
  
  try {
    // 表单验证
    await registerFormRef.value.validate()
    
    loading.value = true
    
    // 调用注册API
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/register/`, {
      username: registerForm.username,
      email: registerForm.email,
      first_name: registerForm.first_name,
      password: registerForm.password,
      password_confirm: registerForm.password_confirm
    })
    
    if (response.data.code === 201) {
      // 注册成功
      const { user, token } = response.data.data
      
      ElMessage.success('注册成功！欢迎加入彩虹数据学习平台！')
      
      // 触发注册成功事件
      emit('register-success', { user, token })
      
    } else {
      ElMessage.error(response.data.message || '注册失败')
    }
    
  } catch (error) {
    console.error('注册失败:', error)
    
    if (error.response && error.response.data) {
      const errorData = error.response.data
      if (errorData.data && typeof errorData.data === 'object') {
        // 显示字段验证错误
        const errors = Object.values(errorData.data).flat()
        ElMessage.error(errors.join(', '))
      } else {
        ElMessage.error(errorData.message || '注册失败')
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
  if (registerFormRef.value) {
    registerFormRef.value.resetFields()
  }
  agreeTerms.value = false
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 500px;
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

.register-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-footer .el-button {
  padding: 0;
  margin-left: 5px;
  font-size: 14px;
}

.terms-content,
.privacy-content {
  line-height: 1.6;
  color: #333;
}

.terms-content h3,
.privacy-content h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.terms-content p,
.privacy-content p {
  margin-bottom: 15px;
}

.terms-content ul,
.privacy-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.terms-content li,
.privacy-content li {
  margin-bottom: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-container {
    padding: 10px;
  }
  
  .register-card {
    margin: 0;
  }
  
  .el-dialog {
    width: 95% !important;
  }
}
</style> 