<template>
  <div class="crawler-management">
    <!-- 页面标题 -->
    <div class="header">
      <h2>🕷️ 爬虫数据管理</h2>
      <p class="subtitle">自动化数据获取和管理系统</p>
    </div>

    <!-- 权限检查提示 -->
    <div v-if="!hasPermission" class="permission-notice">
      <el-alert 
        title="权限不足" 
        type="warning" 
        description="爬虫管理功能需要管理员权限。请联系管理员获取权限。"
        :closable="false"
        show-icon>
      </el-alert>
    </div>

    <!-- 爬虫管理主界面 -->
    <div v-else class="crawler-content">
      <!-- 爬虫控制面板 -->
      <el-card class="control-panel" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>🎛️ 爬虫控制面板</span>
            <el-button 
              type="info" 
              @click="refreshStatus" 
              :loading="isRefreshing"
              size="small">
              刷新状态
            </el-button>
          </div>
        </template>

        <!-- 任务启动控制 -->
        <div class="control-section">
          <h4>🚀 任务启动控制</h4>
          <div class="control-buttons">
            <el-form :inline="true" class="start-form">
              <el-form-item label="数据源:">
                <el-select v-model="startForm.sourceId" placeholder="选择数据源" style="width: 200px">
                  <el-option
                    v-for="source in dataSources"
                    :key="source.id"
                    :label="source.name"
                    :value="source.id"
                    :disabled="!source.is_enabled"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="任务类型:">
                <el-select v-model="startForm.taskType" placeholder="选择任务类型" style="width: 180px">
                  <el-option label="手动爬取" value="manual_crawl" />
                  <el-option label="最新数据同步" value="latest_sync" />
                  <el-option label="增量同步" value="incremental_sync" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="startCrawler" 
                  :loading="isStarting"
                  :disabled="!startForm.sourceId"
                  size="large">
                  启动爬虫
                </el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 运行中任务控制 -->
          <div v-if="runningTasks.length > 0" class="running-tasks">
            <h5>正在运行的任务:</h5>
            <div class="task-list">
              <el-tag 
                v-for="task in runningTasks" 
                :key="task.task_id"
                type="primary"
                closable
                @close="stopTask(task.task_id)"
                class="task-tag">
                {{ task.task_id }} ({{ getTaskTypeName(task.task_type) }})
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 状态统计显示 -->
        <div class="status-display">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="status-item">
                <el-tag :type="systemStatus === 'healthy' ? 'success' : 'danger'" size="large">
                  {{ systemStatus === 'healthy' ? '正常' : '异常' }}
                </el-tag>
                <p class="status-label">系统状态</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <el-tag type="primary" size="large">{{ taskStats.running || 0 }}</el-tag>
                <p class="status-label">运行任务</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <el-tag type="success" size="large">{{ taskStats.success || 0 }}</el-tag>
                <p class="status-label">成功任务</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <el-tag type="danger" size="large">{{ taskStats.failed || 0 }}</el-tag>
                <p class="status-label">失败任务</p>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 数据源管理 -->
      <el-card class="datasource-panel" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>🗂️ 数据源管理</span>
            <div class="header-actions">
              <el-button type="primary" size="small" @click="refreshDataSources">
                刷新
              </el-button>
              <el-button type="success" size="small" @click="showAddDataSourceDialog = true">
                添加数据源
              </el-button>
            </div>
          </div>
        </template>

        <el-table :data="dataSources" style="width: 100%; table-layout: fixed;" v-loading="loadingDataSources" class="fixed-header-table">
          <el-table-column prop="name" label="数据源名称" width="200" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              <el-tag :type="scope.row.is_enabled ? 'primary' : 'info'">
                {{ scope.row.name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source_type" label="类型" width="120" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              <el-tag type="info" size="small">{{ scope.row.source_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="base_url" label="URL" show-overflow-tooltip :resizable="false">
            <template #default="scope">
              <span>{{ scope.row.base_url }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_enabled" label="状态" width="120" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'">
                {{ scope.row.is_enabled ? '启用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_success_time" label="最后成功" width="160" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              {{ formatDateTime(scope.row.last_success_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" :resizable="false">
            <template #default="scope">
              <el-button
                size="small"
                :type="scope.row.is_enabled ? 'warning' : 'success'"
                @click="toggleDataSource(scope.row)">
                {{ scope.row.is_enabled ? '停用' : '启用' }}
              </el-button>
              <el-button
                size="small"
                type="primary"
                @click="editDataSource(scope.row)">
                编辑
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 爬取日志 -->
      <el-card class="log-panel" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>📋 爬取日志</span>
            <div class="header-actions">
              <el-select v-model="logFilter" placeholder="筛选状态" style="width: 120px; margin-right: 10px">
                <el-option label="全部" value="" />
                <el-option label="等待中" value="pending" />
                <el-option label="运行中" value="running" />
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
              <el-button type="primary" size="small" @click="refreshLogs">
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <el-table :data="crawlLogs" style="width: 100%; table-layout: fixed;" v-loading="loadingLogs" class="fixed-header-table">
          <el-table-column prop="task_id" label="任务ID" width="160" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              <el-link type="primary" @click="viewLogDetail(scope.row)">
                {{ scope.row.task_id }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="task_type" label="任务类型" width="120" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              <el-tag size="small">{{ getTaskTypeName(scope.row.task_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="data_source_name" label="数据源" width="140" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.data_source?.name || '未知' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              <el-tag :type="getLogStatusType(scope.row.status)" size="small">
                {{ getLogStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="160" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              {{ formatDateTime(scope.row.start_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="duration_seconds" label="耗时" width="100" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.duration_seconds ? scope.row.duration_seconds + 's' : '--' }}
            </template>
          </el-table-column>
          <el-table-column prop="records_found" label="发现/创建" width="120" :resizable="false" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.records_found || 0 }} / {{ scope.row.records_created || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" :resizable="false">
            <template #default="scope">
              <el-button
                v-if="scope.row.status === 'running'"
                size="small"
                type="danger"
                @click="stopTask(scope.row.task_id)">
                停止
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="logPagination.page"
            v-model:page-size="logPagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :small="false"
            :disabled="loadingLogs"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            :total="logPagination.total"
            @size-change="handleLogSizeChange"
            @current-change="handleLogPageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 日志详情对话框 -->
    <el-dialog v-model="showLogDetail" title="爬取日志详情" width="60%">
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ selectedLog.task_id }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ getTaskTypeName(selectedLog.task_type) }}</el-descriptions-item>
          <el-descriptions-item label="数据源">{{ selectedLog.data_source?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getLogStatusType(selectedLog.status)">
              {{ getLogStatusText(selectedLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDateTime(selectedLog.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDateTime(selectedLog.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="执行耗时">{{ selectedLog.duration_seconds }}秒</el-descriptions-item>
          <el-descriptions-item label="记录统计">
            发现: {{ selectedLog.records_found }}, 创建: {{ selectedLog.records_created }}, 更新: {{ selectedLog.records_updated }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedLog.error_message" class="error-section">
          <h4>错误信息:</h4>
          <el-alert type="error" :closable="false">
            {{ selectedLog.error_message }}
          </el-alert>
        </div>
        
        <div v-if="selectedLog.logs && selectedLog.logs.length > 0" class="logs-section">
          <h4>执行日志:</h4>
          <div class="log-content">
            <div v-for="(log, index) in selectedLog.logs" :key="index" class="log-line">
              {{ log }}
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 添加数据源对话框 -->
    <el-dialog v-model="showAddDataSourceDialog" title="添加数据源" width="50%">
      <el-form :model="dataSourceForm" :rules="dataSourceRules" ref="dataSourceFormRef" label-width="120px">
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="数据源类型" prop="source_type">
          <el-select v-model="dataSourceForm.source_type" placeholder="选择数据源类型">
            <el-option label="网站" value="website" />
            <el-option label="API" value="api" />
            <el-option label="文件" value="file" />
          </el-select>
        </el-form-item>
        <el-form-item label="基础URL" prop="base_url">
          <el-input v-model="dataSourceForm.base_url" placeholder="请输入基础URL" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="dataSourceForm.priority" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_enabled">
          <el-switch v-model="dataSourceForm.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDataSourceDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddDataSource" :loading="submittingDataSource">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 免责声明 -->
    <el-card class="disclaimer" shadow="never">
      <div class="disclaimer-content">
        <el-alert
          title="免责声明"
          type="info"
          :closable="false"
          show-icon>
          <template #default>
            <p>
              <strong>📋 重要提醒：</strong> 本爬虫系统仅用于学术研究和技术学习目的。使用时请遵守相关网站的使用条款和robots.txt规则，合理控制请求频率，避免对目标网站造成过大负担。
            </p>
          </template>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

export default {
  name: 'CrawlerComponent',
  setup() {
    // API配置
    const API_BASE_URL = 'http://127.0.0.1:8001'
    
    // 响应式数据
    const hasPermission = ref(true) // 基于文档，权限集成已完成
    const isStarting = ref(false)
    const isStopping = ref(false)
    const isSyncing = ref(false)
    const isRefreshing = ref(false)
    const loadingDataSources = ref(false)
    const loadingLogs = ref(false)
    const submittingDataSource = ref(false)
    
    // 任务相关
    const runningTasks = ref([])
    const taskStats = ref({})
    const systemStatus = ref('healthy')
    
    // 数据源相关
    const dataSources = ref([])
    const showAddDataSourceDialog = ref(false)
    const dataSourceForm = ref({
      name: '',
      source_type: 'website',
      base_url: '',
      priority: 5,
      is_enabled: true
    })
    const dataSourceFormRef = ref()
    const dataSourceRules = {
      name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
      source_type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }],
      base_url: [{ required: true, message: '请输入基础URL', trigger: 'blur' }]
    }
    
    // 爬取日志相关
    const crawlLogs = ref([])
    const logFilter = ref('')
    const showLogDetail = ref(false)
    const selectedLog = ref(null)
    const logPagination = ref({
      page: 1,
      pageSize: 20,
      total: 0
    })
    
    // 启动表单
    const startForm = ref({
      sourceId: null,
      taskType: 'manual_crawl'
    })
    
    // 定时器
    let statusTimer = null
    
    // 计算属性
    const filteredLogs = computed(() => {
      if (!logFilter.value) return crawlLogs.value
      return crawlLogs.value.filter(log => log.status === logFilter.value)
    })
    
    // 方法定义
    const startCrawler = async () => {
      if (!startForm.value.sourceId) {
        ElMessage.warning('请选择数据源')
        return
      }
      
      isStarting.value = true
      try {
        const response = await axios.post(`${API_BASE_URL}/api/v1/crawler/`, {
          action: 'start',
          source_id: startForm.value.sourceId,
          task_type: startForm.value.taskType
        })
        
        if (response.data.code === 200) {
          ElMessage.success('爬虫任务已启动')
          refreshStatus() // 刷新状态
          refreshLogs() // 刷新日志
        } else {
          ElMessage.error(response.data.message || '启动失败')
        }
      } catch (error) {
        console.error('启动爬虫失败:', error)
        ElMessage.error('启动失败，请检查网络连接')
      } finally {
        isStarting.value = false
      }
    }
    
    const stopTask = async (taskId) => {
      try {
        await ElMessageBox.confirm('确定要停止这个任务吗？', '确认停止', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await axios.post(`${API_BASE_URL}/api/v1/crawler/`, {
          action: 'stop',
          task_id: taskId
        })
        
        if (response.data.code === 200) {
          ElMessage.success('任务已停止')
          refreshStatus()
          refreshLogs()
        } else {
          ElMessage.error(response.data.message || '停止失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('停止任务失败:', error)
          ElMessage.error('停止失败，请检查网络连接')
        }
      }
    }
    
    const refreshStatus = async () => {
      isRefreshing.value = true
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/crawler/`)
        
        if (response.data.code === 200) {
          const data = response.data.data
          runningTasks.value = data.running_tasks || []
          taskStats.value = data.task_stats || {}
          systemStatus.value = data.system_status || 'healthy'
        }
      } catch (error) {
        console.error('刷新状态失败:', error)
      } finally {
        isRefreshing.value = false
      }
    }
    
    const refreshDataSources = async () => {
      loadingDataSources.value = true
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/datasources/`)
        
        if (response.data.results) {
          dataSources.value = response.data.results
        } else if (response.data.data) {
          dataSources.value = response.data.data
        } else {
          dataSources.value = []
        }
      } catch (error) {
        console.error('加载数据源失败:', error)
        ElMessage.error('加载数据源失败')
      } finally {
        loadingDataSources.value = false
      }
    }
    
    const refreshLogs = async () => {
      loadingLogs.value = true
      try {
        const params = {
          page: logPagination.value.page,
          page_size: logPagination.value.pageSize
        }
        
        if (logFilter.value) {
          params.status = logFilter.value
        }
        
        const response = await axios.get(`${API_BASE_URL}/api/v1/crawler/logs/`, { params })
        
        if (response.data.results) {
          crawlLogs.value = response.data.results
          logPagination.value.total = response.data.count || 0
        } else if (response.data.data) {
          crawlLogs.value = response.data.data.logs || []
          logPagination.value.total = response.data.data.count || 0
        }
      } catch (error) {
        console.error('加载日志失败:', error)
        ElMessage.error('加载日志失败')
      } finally {
        loadingLogs.value = false
      }
    }
    
    const toggleDataSource = async (dataSource) => {
      try {
        const response = await axios.patch(`${API_BASE_URL}/api/v1/datasources/${dataSource.id}/`, {
          is_enabled: !dataSource.is_enabled
        })
        
        if (response.status === 200) {
          ElMessage.success(`数据源已${dataSource.is_enabled ? '停用' : '启用'}`)
          refreshDataSources()
        }
      } catch (error) {
        console.error('切换数据源状态失败:', error)
        ElMessage.error('操作失败')
      }
    }
    
    const editDataSource = (dataSource) => {
      // 编辑功能可以后续实现
      ElMessage.info('编辑功能开发中...')
    }
    
    const handleAddDataSource = async () => {
      if (!dataSourceFormRef.value) return
      
      try {
        await dataSourceFormRef.value.validate()
        
        submittingDataSource.value = true
        
        const response = await axios.post(`${API_BASE_URL}/api/v1/datasources/`, dataSourceForm.value)
        
        if (response.status === 201) {
          ElMessage.success('数据源添加成功')
          showAddDataSourceDialog.value = false
          resetDataSourceForm()
          refreshDataSources()
        }
      } catch (error) {
        console.error('添加数据源失败:', error)
        ElMessage.error('添加失败')
      } finally {
        submittingDataSource.value = false
      }
    }
    
    const resetDataSourceForm = () => {
      dataSourceForm.value = {
        name: '',
        source_type: 'website',
        base_url: '',
        priority: 5,
        is_enabled: true
      }
    }
    
    const viewLogDetail = async (log) => {
      selectedLog.value = log
      showLogDetail.value = true
      
      // 如果需要获取详细日志，可以调用详情API
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/crawler/logs/${log.id}/`)
        if (response.data.data) {
          selectedLog.value = response.data.data
        }
      } catch (error) {
        console.error('获取日志详情失败:', error)
      }
    }
    
    const handleLogSizeChange = (newSize) => {
      logPagination.value.pageSize = newSize
      logPagination.value.page = 1
      refreshLogs()
    }
    
    const handleLogPageChange = (newPage) => {
      logPagination.value.page = newPage
      refreshLogs()
    }
    
    // 工具方法
    const getLogStatusType = (status) => {
      const statusMap = {
        'success': 'success',
        'running': 'primary',
        'failed': 'danger',
        'pending': 'warning',
        'cancelled': 'info'
      }
      return statusMap[status] || 'info'
    }
    
    const getLogStatusText = (status) => {
      const statusMap = {
        'success': '成功',
        'running': '运行中',
        'failed': '失败',
        'pending': '等待中',
        'cancelled': '已取消'
      }
      return statusMap[status] || '未知'
    }
    
    const getTaskTypeName = (taskType) => {
      const typeMap = {
        'manual_crawl': '手动爬取',
        'latest_sync': '最新同步',
        'incremental_sync': '增量同步',
        'full_sync': '全量同步',
        'scheduled_crawl': '定时爬取'
      }
      return typeMap[taskType] || taskType
    }
    
    const formatDateTime = (dateTime) => {
      if (!dateTime) return '--'
      return new Date(dateTime).toLocaleString('zh-CN')
    }
    
    // 定时刷新状态
    const startStatusTimer = () => {
      statusTimer = setInterval(() => {
        refreshStatus()
      }, 10000) // 每10秒刷新一次
    }
    
    const stopStatusTimer = () => {
      if (statusTimer) {
        clearInterval(statusTimer)
        statusTimer = null
      }
    }
    
    // 生命周期
    onMounted(() => {
      console.log('爬虫管理组件已加载')
      refreshDataSources()
      refreshLogs()
      refreshStatus()
      startStatusTimer() // 启动定时刷新
    })
    
    onUnmounted(() => {
      stopStatusTimer() // 清理定时器
    })
    
    return {
      hasPermission,
      isStarting,
      isStopping,
      isSyncing,
      isRefreshing,
      loadingDataSources,
      loadingLogs,
      submittingDataSource,
      runningTasks,
      taskStats,
      systemStatus,
      dataSources,
      crawlLogs,
      logFilter,
      showLogDetail,
      selectedLog,
      logPagination,
      startForm,
      showAddDataSourceDialog,
      dataSourceForm,
      dataSourceFormRef,
      dataSourceRules,
      filteredLogs,
      startCrawler,
      stopTask,
      refreshStatus,
      refreshDataSources,
      refreshLogs,
      toggleDataSource,
      editDataSource,
      handleAddDataSource,
      resetDataSourceForm,
      viewLogDetail,
      handleLogSizeChange,
      handleLogPageChange,
      getLogStatusType,
      getLogStatusText,
      getTaskTypeName,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.crawler-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 16px;
}

.crawler-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-section {
  margin-bottom: 20px;
}

.control-section h4 {
  margin-bottom: 15px;
  color: #606266;
}

.control-buttons {
  margin-bottom: 20px;
}

.start-form {
  margin-bottom: 15px;
}

.running-tasks {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.running-tasks h5 {
  margin-bottom: 10px;
  color: #606266;
}

.task-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.task-tag {
  margin: 0;
}

.status-display {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.status-item {
  text-align: center;
}

.status-item .el-tag {
  font-size: 18px;
  padding: 8px 16px;
  font-weight: bold;
}

.status-label {
  margin-top: 10px;
  color: #7f8c8d;
  font-size: 14px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.log-detail {
  padding: 20px;
}

.error-section, .logs-section {
  margin-top: 20px;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
}

.log-line {
  margin-bottom: 5px;
  line-height: 1.4;
}

.disclaimer {
  margin-top: 30px;
  border: 1px solid #e1f5fe;
  background-color: #f8f9fa;
}

.disclaimer-content p {
  margin-bottom: 10px;
  line-height: 1.6;
}

.permission-notice {
  margin-bottom: 20px;
}

/* 响应式设计 */
/* 平板端适配 (768px - 1024px) */
@media (max-width: 1024px) and (min-width: 768px) {
  .crawler-management {
    padding: 15px;
    max-width: 100%;
  }
  
  .header h2 {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-actions {
    gap: 8px;
  }
  
  .header-actions .el-button {
    padding: 8px 12px;
  }
  
  .status-display {
    padding: 15px;
  }
  
  .status-item .el-tag {
    font-size: 16px;
    padding: 6px 12px;
  }
  
  .task-list {
    gap: 8px;
  }
  
  .log-content {
    max-height: 250px;
    padding: 12px;
    font-size: 13px;
  }
}

/* 移动端适配 (< 768px) */
@media (max-width: 768px) {
  .crawler-management {
    padding: 10px;
    max-width: 100%;
  }
  
  .header {
    margin-bottom: 20px;
  }
  
  .header h2 {
    font-size: 20px;
    margin-bottom: 8px;
  }
  
  .subtitle {
    font-size: 13px;
  }
  
  .crawler-content {
    gap: 15px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
    gap: 6px;
  }
  
  .header-actions .el-button {
    flex: 1;
    padding: 6px 8px;
    font-size: 12px;
  }
  
  .control-section {
    margin-bottom: 15px;
  }
  
  .control-section h4 {
    margin-bottom: 10px;
    font-size: 16px;
  }
  
  .control-buttons {
    margin-bottom: 15px;
  }
  
  .control-buttons .el-button {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .start-form {
    margin-bottom: 12px;
  }
  
  .start-form .el-form-item {
    margin-bottom: 12px;
  }
  
  .start-form .el-select,
  .start-form .el-input-number {
    width: 100%;
  }
  
  .running-tasks {
    padding: 12px;
  }
  
  .running-tasks h5 {
    margin-bottom: 8px;
    font-size: 14px;
  }
  
  .task-list {
    gap: 6px;
  }
  
  .task-tag {
    font-size: 11px;
    padding: 4px 8px;
  }
  
  .status-display {
    padding: 12px;
  }
  
  .status-item .el-tag {
    font-size: 14px;
    padding: 6px 10px;
  }
  
  .status-label {
    margin-top: 8px;
    font-size: 12px;
  }
  
  .log-content {
    max-height: 200px;
    padding: 10px;
    font-size: 11px;
  }
  
  .log-line {
    margin-bottom: 3px;
  }
  
  .log-detail {
    padding: 15px;
  }
  
  .pagination-wrapper {
    margin-top: 15px;
    text-align: center;
  }
  
  .disclaimer {
    margin-top: 20px;
  }
  
  .disclaimer-content p {
    margin-bottom: 8px;
    font-size: 12px;
    line-height: 1.5;
  }
  
  .permission-notice {
    margin-bottom: 15px;
  }
  
  .crawler-management .el-table {
    font-size: 12px;
  }
  
  .crawler-management .el-table .el-table__cell {
    padding: 8px 0;
  }
  
  .el-dialog__body {
    padding: 15px 20px;
  }
  
  .el-form-item__label {
    font-size: 13px;
  }
}

/* 小屏移动端适配 (< 480px) */
@media (max-width: 480px) {
  .crawler-management {
    padding: 8px;
  }
  
  .header h2 {
    font-size: 18px;
  }
  
  .subtitle {
    font-size: 12px;
  }
  
  .crawler-content {
    gap: 12px;
  }
  
  .card-header {
    font-size: 13px;
  }
  
  .header-actions .el-button {
    padding: 5px 6px;
    font-size: 11px;
  }
  
  .control-section h4 {
    font-size: 14px;
  }
  
  .control-buttons .el-button {
    margin-bottom: 6px;
    font-size: 12px;
  }
  
  .start-form .el-form-item {
    margin-bottom: 10px;
  }
  
  .running-tasks {
    padding: 10px;
  }
  
  .running-tasks h5 {
    font-size: 13px;
  }
  
  .task-tag {
    font-size: 10px;
    padding: 3px 6px;
  }
  
  .status-display {
    padding: 10px;
  }
  
  .status-item .el-tag {
    font-size: 12px;
    padding: 4px 8px;
  }
  
  .status-label {
    font-size: 11px;
  }
  
  .log-content {
    max-height: 150px;
    padding: 8px;
    font-size: 10px;
  }
  
  .log-detail {
    padding: 12px;
  }
  
  .disclaimer-content p {
    font-size: 11px;
  }
  
  .crawler-management .el-table {
    font-size: 11px;
  }
  
  .crawler-management .el-table .el-table__cell {
    padding: 6px 0;
  }
  
  .el-dialog__body {
    padding: 12px 15px;
  }
  
  .el-form-item__label {
    font-size: 12px;
  }
}
</style> 