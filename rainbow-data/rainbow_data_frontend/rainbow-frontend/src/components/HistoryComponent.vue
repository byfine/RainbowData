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
        style="width: 100%"
        :default-sort="{ prop: 'draw_date', order: 'descending' }"
        @sort-change="handleSortChange"
      >
        <el-table-column
          prop="issue"
          label="期号"
          width="120"
          sortable
          align="center"
        />
        
        <el-table-column
          prop="draw_date"
          label="开奖日期"
          width="120"
          sortable
          align="center"
        />
        
        <el-table-column
          label="红球"
          width="300"
          align="center"
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
        >
          <template #default="scope">
            <span class="ball blue-ball">
              {{ scope.row.blue_ball }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column
          label="操作"
          width="120"
          align="center"
          fixed="right"
        >
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="viewDetails(scope.row)"
            >
              详情
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
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const detailDialogVisible = ref(false)
const selectedResult = ref(null)

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

// 组件挂载时加载数据
onMounted(() => {
  loadData()
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

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .title-icon {
    font-size: 28px;
  }
  
  .balls-display {
    gap: 3px;
  }
  
  .ball {
    width: 24px;
    height: 24px;
    font-size: 10px;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-item label {
    width: auto;
    margin-bottom: 5px;
  }
}
</style> 