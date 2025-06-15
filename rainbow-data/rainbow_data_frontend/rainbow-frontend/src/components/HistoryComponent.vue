<template>
  <div class="history-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">📋</span>
        历史开奖记录
      </h2>
      <p class="page-description">
        查看双色球历史开奖数据，支持按期号、日期等条件筛选
      </p>
    </div>

    <!-- 查询筛选条件 -->
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">🔍</span>
          <span class="header-title">查询条件</span>
        </div>
      </template>
      
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="期号">
          <el-input
            v-model="queryForm.issue"
            placeholder="输入期号，如：2024001"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="queryForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 250px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 开奖记录列表 -->
    <el-card class="results-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">📊</span>
          <span class="header-title">开奖记录</span>
          <div class="header-actions">
            <el-button size="small" @click="refreshData" :loading="loading">
              刷新数据
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 数据表格 -->
            <el-table
        :data="tableData"
        :loading="loading"
        stripe
        border
        style="width: 100%; table-layout: fixed;"
        :default-sort="{ prop: 'draw_date', order: 'descending' }"
        @sort-change="handleSortChange"
        class="history-table"
        ref="historyTable"
      >
        <el-table-column
          prop="issue"
          label="期号"
          width="120"
          sortable
          align="center"
          header-align="center"
          :resizable="false"
        />
        
        <el-table-column
          prop="draw_date"
          label="开奖日期"
          width="120"
          sortable
          align="center"
          header-align="center"
          :resizable="false"
        />
        
        <el-table-column
          label="红球"
          width="300"
          align="center"
          header-align="center"
          :resizable="false"
        >
          <template #default="scope">
            <div class="balls-display">
              <span
                v-for="ball in getRedBalls(scope.row)"
                :key="ball"
                class="ball red-ball"
              >
                {{ ball }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="blue_ball"
          label="蓝球"
          width="80"
          align="center"
          header-align="center"
          :resizable="false"
        >
          <template #default="scope">
            <span class="ball blue-ball">
              {{ scope.row.blue_ball }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column
          label="操作"
          width="160"
          align="center"
          header-align="center"
          :resizable="false"
        >
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="viewDetails(scope.row)"
            >
              详情
            </el-button>
            <el-button
              size="small"
              type="warning"
              @click="addToFavorites(scope.row)"
              :disabled="!isAuthenticated"
            >
              <el-icon><Star /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页组件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <!-- 空数据状态 -->
      <div v-if="!loading && tableData.length === 0" class="empty-data">
        <el-empty description="暂无开奖数据">
          <el-button type="primary" @click="refreshData">
            加载数据
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 开奖详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="开奖详情"
      width="500px"
      :before-close="handleCloseDetail"
    >
      <div v-if="selectedResult" class="detail-content">
        <div class="detail-item">
          <label>期号：</label>
          <span>{{ selectedResult.issue }}</span>
        </div>
        <div class="detail-item">
          <label>开奖日期：</label>
          <span>{{ selectedResult.draw_date }}</span>
        </div>
        <div class="detail-item">
          <label>红球：</label>
          <div class="balls-container">
            <span
              v-for="ball in getRedBalls(selectedResult)"
              :key="ball"
              class="ball red-ball"
            >
              {{ ball }}
            </span>
          </div>
        </div>
        <div class="detail-item">
          <label>蓝球：</label>
          <span class="ball blue-ball">
            {{ selectedResult.blue_ball }}
          </span>
        </div>
        <div class="detail-item">
          <label>创建时间：</label>
          <span>{{ formatDateTime(selectedResult.created_at) }}</span>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Star } from '@element-plus/icons-vue'
import axios from 'axios'

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const detailDialogVisible = ref(false)
const selectedResult = ref(null)

// 接收父组件传递的认证状态
const props = defineProps({
  isAuthenticated: {
    type: Boolean,
    default: false
  }
})

// 查询表单
const queryForm = reactive({
  issue: '',
  dateRange: []
})

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 排序数据
const sortData = reactive({
  prop: 'draw_date',
  order: 'descending'
})

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

const formatDateTime = (dateTimeStr) => {
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}

const buildQueryParams = () => {
  const params = {
    page: pagination.page,
    page_size: pagination.pageSize
  }
  
  // 添加搜索条件
  if (queryForm.issue) {
    params.issue = queryForm.issue
  }
  
  if (queryForm.dateRange && queryForm.dateRange.length === 2) {
    params.start_date = queryForm.dateRange[0]
    params.end_date = queryForm.dateRange[1]
  }
  
  // 添加排序
  if (sortData.prop) {
    const ordering = sortData.order === 'descending' ? `-${sortData.prop}` : sortData.prop
    params.ordering = ordering
  }
  
  return params
}

const loadData = async () => {
  loading.value = true
  try {
    const params = buildQueryParams()
    
    let url = `${API_BASE_URL}/api/v1/results/`
    
    // 如果有日期范围查询，使用专门的API
    if (params.start_date && params.end_date) {
      url = `${API_BASE_URL}/api/v1/results/date_range/`
    }
    
    const response = await axios.get(url, { params })
    
    if (response.data) {
      // 处理不同的响应格式
      if (response.data.results) {
        // DRF分页格式
        tableData.value = response.data.results
        pagination.total = response.data.count || 0
      } else if (response.data.data && response.data.data.results) {
        // 自定义API格式
        tableData.value = response.data.data.results
        pagination.total = response.data.data.count || 0
      } else if (Array.isArray(response.data)) {
        // 简单数组格式
        tableData.value = response.data
        pagination.total = response.data.length
      } else {
        tableData.value = []
        pagination.total = 0
      }
      
      ElMessage.success(`加载成功，共 ${pagination.total} 条记录`)
      
      // 数据加载完成后修复表格布局
      fixTableLayout()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请检查后端服务')
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1 // 重置到第一页
  loadData()
}

const handleReset = () => {
  queryForm.issue = ''
  queryForm.dateRange = []
  pagination.page = 1
  loadData()
}

const refreshData = () => {
  loadData()
}

const handleSizeChange = (newSize) => {
  pagination.pageSize = newSize
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (newPage) => {
  pagination.page = newPage
  loadData()
}

const handleSortChange = ({ prop, order }) => {
  sortData.prop = prop
  sortData.order = order
  pagination.page = 1
  loadData()
}

const viewDetails = (row) => {
  selectedResult.value = row
  detailDialogVisible.value = true
}

const handleCloseDetail = () => {
  detailDialogVisible.value = false
  selectedResult.value = null
}

// 快捷收藏功能
const addToFavorites = async (lotteryResult) => {
  if (!props.isAuthenticated) {
    ElMessage.warning('请先登录后再收藏')
    return
  }
  
  try {
    // 先检查是否已经收藏过
    const checkResponse = await axios.get(`${API_BASE_URL}/api/v1/favorites/`)
    if (checkResponse.status === 200) {
      const existingFavorites = checkResponse.data.results || checkResponse.data
      const existingFavorite = existingFavorites.find(fav => 
        fav.favorite_type === 'lottery_result' && fav.object_id === lotteryResult.id
      )
      
      if (existingFavorite) {
        ElMessage.warning(`期号 ${lotteryResult.issue} 已经收藏过了`)
        return
      }
    }
    
    const submitData = {
      favorite_type: 'lottery_result',
      object_id: lotteryResult.id,
      title: `期号 ${lotteryResult.issue} - ${lotteryResult.draw_date}`,
      description: `红球: ${getRedBalls(lotteryResult).join(', ')} 蓝球: ${lotteryResult.blue_ball}`,
      tags: ['开奖结果', lotteryResult.issue],
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
        ElMessage.warning('该开奖结果已经收藏过了')
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

// 表格布局修复方法（核心解决方案）
const fixTableLayout = () => {
  nextTick(() => {
    setTimeout(() => {
      const table = document.querySelector('.history-table')
      if (table) {
        // 强制设置表格为固定布局 - 这是核心解决方案
        table.style.tableLayout = 'fixed'
        table.style.width = '100%'
        
        // 设置表头和表体的布局
        const headerTable = table.querySelector('.el-table__header table')
        const bodyTable = table.querySelector('.el-table__body table')
        
        if (headerTable) {
          headerTable.style.tableLayout = 'fixed'
          headerTable.style.width = '100%'
        }
        
        if (bodyTable) {
          bodyTable.style.tableLayout = 'fixed'
          bodyTable.style.width = '100%'
        }
        
        // 设置列宽度 - 确保表头和表体列宽一致
        const colWidths = ['120px', '120px', '300px', '80px', '160px']
        
        const headerCols = table.querySelectorAll('.el-table__header colgroup col')
        headerCols.forEach((col, index) => {
          if (colWidths[index]) {
            col.style.width = colWidths[index]
          }
        })
        
        const bodyCols = table.querySelectorAll('.el-table__body colgroup col')
        bodyCols.forEach((col, index) => {
          if (colWidths[index]) {
            col.style.width = colWidths[index]
          }
        })
        
        // 额外确保文字对齐
        const headers = table.querySelectorAll('.el-table__header th')
        headers.forEach(th => {
          th.style.textAlign = 'center'
          const cell = th.querySelector('.cell')
          if (cell) {
            cell.style.textAlign = 'center'
          }
        })
        
        const bodyTds = table.querySelectorAll('.el-table__body td')
        bodyTds.forEach(td => {
          td.style.textAlign = 'center'
        })
      }
    }, 150)
  })
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
  
  // 挂载后修复表格布局
  setTimeout(() => {
    fixTableLayout()
  }, 300)
})
</script>

<style scoped>
.history-container {
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
.filter-card, .results-card {
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
  gap: 10px;
}

/* 球号样式 */
.balls-display {
  display: flex;
  gap: 5px;
  justify-content: center;
  flex-wrap: wrap;
}

.balls-container {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.ball {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
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

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
}

/* 空数据样式 */
.empty-data {
  text-align: center;
  padding: 40px 20px;
}

/* 详情对话框样式 */
.detail-content {
  padding: 10px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 16px;
}

.detail-item label {
  font-weight: bold;
  width: 100px;
  color: #666;
}

.detail-item .balls-container {
  margin-left: 10px;
}

.detail-item .ball {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

/* 表格固定布局样式 - 核心解决方案 */
.history-table {
  width: 100% !important;
  table-layout: fixed !important;
}

.history-table :deep(.el-table__header),
.history-table :deep(.el-table__body) {
  width: 100% !important;
  table-layout: fixed !important;
}

.history-table :deep(.el-table__header table),
.history-table :deep(.el-table__body table) {
  width: 100% !important;
  table-layout: fixed !important;
}

/* 确保列宽度一致 - 关键修复 */
.history-table :deep(colgroup col:nth-child(1)) {
  width: 120px !important;
}

.history-table :deep(colgroup col:nth-child(2)) {
  width: 120px !important;
}

.history-table :deep(colgroup col:nth-child(3)) {
  width: 300px !important;
}

.history-table :deep(colgroup col:nth-child(4)) {
  width: 80px !important;
}

.history-table :deep(colgroup col:nth-child(5)) {
  width: 160px !important;
}

/* 文字居中和内边距 */
.history-table :deep(.el-table__header th) {
  text-align: center !important;
  padding: 12px 0 !important;
}

.history-table :deep(.el-table__header th .cell) {
  text-align: center !important;
}

.history-table :deep(.el-table__body td) {
  text-align: center !important;
  padding: 12px 0 !important;
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
  
  .filter-form {
    gap: 15px;
  }
  
  .balls-display {
    gap: 4px;
  }
  
  .ball {
    width: 26px;
    height: 26px;
    font-size: 11px;
  }
  
  .header-actions {
    gap: 8px;
  }
  
  .header-actions .el-button {
    padding: 8px 16px;
  }
  
  .detail-item .ball {
    width: 30px;
    height: 30px;
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
  
  .filter-form {
    flex-direction: column;
    gap: 10px;
  }
  
  .filter-form .el-form-item {
    margin-bottom: 15px;
  }
  
  .filter-form .el-button {
    width: 100%;
    margin-top: 10px;
  }
  
  .header-actions {
    justify-content: center;
    gap: 8px;
    margin-top: 10px;
  }
  
  .header-actions .el-button {
    flex: 1;
    font-size: 12px;
    padding: 6px 8px;
  }
  
  .balls-display {
    gap: 2px;
    justify-content: center;
  }
  
  .balls-container {
    gap: 2px;
    justify-content: center;
  }
  
  .ball {
    width: 22px;
    height: 22px;
    font-size: 9px;
  }
  
  .pagination-container {
    margin-top: 15px;
    padding: 15px 0;
  }
  
  .empty-data {
    padding: 30px 15px;
  }
  
  .detail-content {
    padding: 5px 0;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 12px;
    font-size: 14px;
  }
  
  .detail-item label {
    width: auto;
    margin-bottom: 5px;
    font-size: 13px;
  }
  
  .detail-item .ball {
    width: 26px;
    height: 26px;
    font-size: 11px;
  }
  
  .detail-item .balls-container {
    margin-left: 0;
    margin-top: 5px;
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
  
  .filter-form .el-form-item {
    margin-bottom: 12px;
  }
  
  .header-actions .el-button {
    font-size: 11px;
    padding: 5px 6px;
  }
  
  .ball {
    width: 18px;
    height: 18px;
    font-size: 8px;
  }
  
  .balls-display {
    gap: 1px;
  }
  
  .balls-container {
    gap: 1px;
  }
  
  .empty-data {
    padding: 25px 10px;
  }
  
  .detail-item {
    font-size: 12px;
    margin-bottom: 10px;
  }
  
  .detail-item label {
    font-size: 11px;
  }
  
  .detail-item .ball {
    width: 20px;
    height: 20px;
    font-size: 9px;
  }
  
  .pagination-container {
    margin-top: 10px;
    padding: 10px 0;
  }
}
</style>

<style>
/* 全局表格布局修复 - 确保在所有情况下生效 */
.history-table {
  table-layout: fixed !important;
  width: 100% !important;
}

.history-table .el-table__header,
.history-table .el-table__body {
  width: 100% !important;
}

.history-table .el-table__header table,
.history-table .el-table__body table {
  table-layout: fixed !important;
  width: 100% !important;
}

/* 关键：强制列宽一致 */
.history-table colgroup col:nth-child(1) { width: 120px !important; }
.history-table colgroup col:nth-child(2) { width: 120px !important; }
.history-table colgroup col:nth-child(3) { width: 300px !important; }
.history-table colgroup col:nth-child(4) { width: 80px !important; }
.history-table colgroup col:nth-child(5) { width: 160px !important; }

/* 文字居中 */
.history-table .el-table__header th {
  text-align: center !important;
}

.history-table .el-table__header th .cell {
  text-align: center !important;
}

.history-table .el-table__body td {
  text-align: center !important;
}
</style> 