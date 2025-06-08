<template>
  <div class="statistics-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <span class="title-icon">📈</span>
        统计分析
      </h2>
      <p class="page-description">
        双色球号码频率统计、冷热分析等数据分析功能
      </p>
    </div>

    <!-- 统计类型选择 -->
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-icon">🎯</span>
          <span class="header-title">分析类型</span>
        </div>
      </template>
      
      <el-radio-group v-model="activeTab" size="large">
        <el-radio-button label="frequency">号码频率</el-radio-button>
        <el-radio-button label="hot_cold">冷热分析</el-radio-button>
        <el-radio-button label="overview">统计概览</el-radio-button>
        <el-radio-button label="advanced">高级分析</el-radio-button>
      </el-radio-group>
      
      <div class="filter-controls">
        <el-select v-model="ballTypeFilter" placeholder="选择球类型" style="width: 120px">
          <el-option label="全部" value="all" />
          <el-option label="红球" value="red" />
          <el-option label="蓝球" value="blue" />
        </el-select>
        
        <el-button type="primary" @click="refreshData" :loading="loading">
          刷新数据
        </el-button>
      </div>
    </el-card>

    <!-- 号码频率统计 -->
    <div v-if="activeTab === 'frequency'">
      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-icon">📊</span>
            <span class="header-title">号码出现频率</span>
          </div>
        </template>
        
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <div v-else-if="frequencyData.length > 0">
          <el-table
            :data="frequencyData"
            stripe
            border
            style="width: 100%"
            :default-sort="{ prop: 'appear_count', order: 'descending' }"
          >
            <el-table-column prop="ball_number" label="号码" width="80" align="center">
              <template #default="scope">
                <span 
                  class="ball" 
                  :class="scope.row.ball_type === 'red' ? 'red-ball' : 'blue-ball'"
                >
                  {{ scope.row.ball_number }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="ball_type" label="类型" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.ball_type === 'red' ? 'danger' : 'primary'">
                  {{ scope.row.ball_type === 'red' ? '红球' : '蓝球' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="appear_count" label="出现次数" width="100" align="center" sortable />
            <el-table-column prop="avg_interval" label="平均间隔" width="100" align="center" sortable />
            <el-table-column prop="max_interval" label="最大间隔" width="100" align="center" sortable />
            <el-table-column prop="last_appear_issue" label="最后出现期号" align="center" />
            <el-table-column label="频率条" align="center">
              <template #default="scope">
                <div class="frequency-bar">
                  <div 
                    class="frequency-fill"
                    :style="{ width: getFrequencyPercentage(scope.row.appear_count) + '%' }"
                    :class="scope.row.ball_type === 'red' ? 'red-freq' : 'blue-freq'"
                  ></div>
                  <span class="frequency-text">{{ scope.row.appear_count }}</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div v-else class="empty-data">
          <el-empty description="暂无统计数据">
            <el-button type="primary" @click="refreshData">
              加载数据
            </el-button>
          </el-empty>
        </div>
      </el-card>
    </div>

    <!-- 冷热分析 -->
    <div v-if="activeTab === 'hot_cold'">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="stats-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="header-icon">🔥</span>
                <span class="header-title">热门号码 TOP 10</span>
              </div>
            </template>
            
            <div class="hot-cold-list">
              <div 
                v-for="(item, index) in hotNumbers" 
                :key="item.ball_number"
                class="number-item hot-item"
              >
                <div class="rank">{{ index + 1 }}</div>
                <span 
                  class="ball" 
                  :class="item.ball_type === 'red' ? 'red-ball' : 'blue-ball'"
                >
                  {{ item.ball_number }}
                </span>
                <div class="count">{{ item.appear_count }}次</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="stats-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="header-icon">❄️</span>
                <span class="header-title">冷门号码 TOP 10</span>
              </div>
            </template>
            
            <div class="hot-cold-list">
              <div 
                v-for="(item, index) in coldNumbers" 
                :key="item.ball_number"
                class="number-item cold-item"
              >
                <div class="rank">{{ index + 1 }}</div>
                <span 
                  class="ball" 
                  :class="item.ball_type === 'red' ? 'red-ball' : 'blue-ball'"
                >
                  {{ item.ball_number }}
                </span>
                <div class="count">{{ item.appear_count }}次</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 统计概览 -->
    <div v-if="activeTab === 'overview'">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon">📊</div>
              <div class="overview-content">
                <div class="overview-title">总开奖期数</div>
                <div class="overview-value">{{ overviewStats.totalDraws }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon">🔴</div>
              <div class="overview-content">
                <div class="overview-title">红球统计</div>
                <div class="overview-value">33个号码</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon">🔵</div>
              <div class="overview-content">
                <div class="overview-title">蓝球统计</div>
                <div class="overview-value">16个号码</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="stats-summary" shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span class="header-icon">📋</span>
            <span class="header-title">数据摘要</span>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="数据更新时间">
            {{ new Date().toLocaleString('zh-CN') }}
          </el-descriptions-item>
          <el-descriptions-item label="统计项目">
            {{ frequencyData.length }} 个号码
          </el-descriptions-item>
          <el-descriptions-item label="红球最热号码">
            <span v-if="topRedBall" class="ball red-ball">
              {{ topRedBall.ball_number }}
            </span>
            <span v-if="topRedBall">({{ topRedBall.appear_count }}次)</span>
          </el-descriptions-item>
          <el-descriptions-item label="蓝球最热号码">
            <span v-if="topBlueBall" class="ball blue-ball">
              {{ topBlueBall.ball_number }}
            </span>
            <span v-if="topBlueBall">({{ topBlueBall.appear_count }}次)</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 高级分析 -->
    <div v-if="activeTab === 'advanced'">
      <el-card class="filter-card" shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span class="header-icon">🔬</span>
            <span class="header-title">高级分析类型</span>
          </div>
        </template>
        
        <el-radio-group v-model="advancedType" size="large">
          <el-radio-button label="consecutive">连号分析</el-radio-button>
          <el-radio-button label="ac_value">AC值分析</el-radio-button>
          <el-radio-button label="span">跨度分析</el-radio-button>
          <el-radio-button label="interval">间隔分析</el-radio-button>
          <el-radio-button label="repeat">重复分析</el-radio-button>
        </el-radio-group>
        
        <!-- 功能说明 -->
        <div class="analysis-description">
          <el-alert 
            :title="getAnalysisDescription(advancedType).title"
            :description="getAnalysisDescription(advancedType).description"
            type="info" 
            show-icon 
            :closable="false"
            style="margin-top: 15px;"
          />
        </div>
        
        <div class="filter-controls" style="margin-top: 15px;">
          <div class="parameter-group">
            <label class="parameter-label">分析期数:</label>
            <el-input-number 
              v-model="analysisLimit" 
              :min="10" 
              :max="500" 
              placeholder="分析期数"
              style="width: 150px;"
            />
            <span class="parameter-desc">选择要分析的开奖期数（建议50-200期）</span>
          </div>
          
          <div v-if="advancedType === 'interval'" class="parameter-group">
            <label class="parameter-label">目标号码:</label>
            <el-select v-model="intervalBallType" placeholder="球类型" style="width: 100px; margin-right: 10px;">
              <el-option label="红球" value="red" />
              <el-option label="蓝球" value="blue" />
            </el-select>
            <el-input-number 
              v-model="intervalBallNumber" 
              :min="1" 
              :max="intervalBallType === 'red' ? 33 : 16"
              placeholder="球号"
              style="width: 100px;"
            />
            <span class="parameter-desc">
              选择要分析的具体号码（红球1-33，蓝球1-16）
            </span>
          </div>
          
          <el-button type="primary" @click="loadAdvancedAnalysis" :loading="advancedLoading">
            开始分析
          </el-button>
        </div>
      </el-card>

      <!-- 连号分析结果 -->
      <div v-if="advancedType === 'consecutive' && consecutiveData">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="analysis-card clickable-card" shadow="hover" @click="filterConsecutivePatterns('two')">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🔗</span>
                  <span class="header-title">两连号</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ consecutiveData.two_consecutive }}</div>
                <div class="stat-desc">次 ({{ consecutiveData.probabilities.two_consecutive }}%)</div>
                <div class="click-hint">点击查看详情</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="analysis-card clickable-card" shadow="hover" @click="filterConsecutivePatterns('three')">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🔗</span>
                  <span class="header-title">三连号</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ consecutiveData.three_consecutive }}</div>
                <div class="stat-desc">次 ({{ consecutiveData.probabilities.three_consecutive }}%)</div>
                <div class="click-hint">点击查看详情</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="analysis-card clickable-card" shadow="hover" @click="filterConsecutivePatterns('four')">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🔗</span>
                  <span class="header-title">四连号及以上</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ consecutiveData.four_consecutive }}</div>
                <div class="stat-desc">次 ({{ consecutiveData.probabilities.four_consecutive }}%)</div>
                <div class="click-hint">点击查看详情</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="pattern-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📋</span>
              <span class="header-title">
                {{ getConsecutiveDetailTitle() }}
                <span v-if="consecutiveFilter !== 'all'" style="color: #409eff; font-size: 14px;">
                  ({{ getFilteredConsecutivePatterns().length }}条记录)
                </span>
              </span>
              <el-button-group size="small">
                <el-button 
                  :type="consecutiveFilter === 'all' ? 'primary' : ''"
                  @click="consecutiveFilter = 'all'"
                  size="small"
                >
                  全部
                </el-button>
                <el-button 
                  :type="consecutiveFilter === 'two' ? 'primary' : ''"
                  @click="consecutiveFilter = 'two'"
                  size="small"
                >
                  两连号
                </el-button>
                <el-button 
                  :type="consecutiveFilter === 'three' ? 'primary' : ''"
                  @click="consecutiveFilter = 'three'"
                  size="small"
                >
                  三连号
                </el-button>
                <el-button 
                  :type="consecutiveFilter === 'four' ? 'primary' : ''"
                  @click="consecutiveFilter = 'four'"
                  size="small"
                >
                  四连号+
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <div v-if="getFilteredConsecutivePatterns().length === 0" class="empty-data">
            <el-empty description="暂无此类型的连号数据" />
          </div>
          
          <el-table v-else :data="getFilteredConsecutivePatterns().slice(0, 20)" stripe>
            <el-table-column prop="issue" label="期号" width="100" align="center" />
            <el-table-column prop="draw_date" label="开奖日期" width="110" align="center" />
            <el-table-column label="红球号码" width="220" align="center">
              <template #default="scope">
                <div class="ball-group-compact">
                  <span 
                    v-for="ball in scope.row.red_balls" 
                    :key="ball" 
                    class="ball red-ball-small"
                  >
                    {{ ball }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="连号组合" align="center">
              <template #default="scope">
                <div class="consecutive-groups">
                  <el-tag 
                    v-for="(group, index) in scope.row.consecutive_groups" 
                    :key="index"
                    :type="getConsecutiveTagType(group)"
                    size="small"
                    style="margin-right: 5px;"
                  >
                    {{ group.join('-') }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="连号类型" width="100" align="center">
              <template #default="scope">
                <el-tag 
                  v-for="(group, index) in scope.row.consecutive_groups" 
                  :key="index"
                  :type="getConsecutiveTagType(group)"
                  size="small"
                  style="margin-right: 3px;"
                >
                  {{ group.length }}连号
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-if="getFilteredConsecutivePatterns().length > 20" style="text-align: center; margin-top: 15px;">
            <el-text type="info">
              显示前20条记录，共{{ getFilteredConsecutivePatterns().length }}条
            </el-text>
          </div>
        </el-card>
      </div>

      <!-- AC值分析结果 -->
      <div v-if="advancedType === 'ac_value' && acValueData">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📊</span>
                  <span class="header-title">平均AC值</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ acValueData.average_ac }}</div>
                <div class="stat-desc">平均离散度</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📈</span>
                  <span class="header-title">最大AC值</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ acValueData.max_ac }}</div>
                <div class="stat-desc">最高离散度</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📉</span>
                  <span class="header-title">最小AC值</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ acValueData.min_ac }}</div>
                <div class="stat-desc">最低离散度</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🎯</span>
                  <span class="header-title">分析期数</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ acValueData.total_periods }}</div>
                <div class="stat-desc">总期数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="distribution-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📊</span>
              <span class="header-title">AC值分布</span>
            </div>
          </template>
          
          <el-table :data="Object.entries(acValueData.ac_probability).map(([ac, prob]) => ({ ac_value: ac, probability: prob, count: acValueData.ac_distribution[ac] }))" stripe>
            <el-table-column prop="ac_value" label="AC值" width="100" align="center" />
            <el-table-column prop="count" label="出现次数" width="120" align="center" />
            <el-table-column prop="probability" label="出现概率(%)" width="150" align="center" />
            <el-table-column label="概率条" align="center">
              <template #default="scope">
                <div class="probability-bar">
                  <div 
                    class="probability-fill"
                    :style="{ width: scope.row.probability + '%' }"
                  ></div>
                  <span class="probability-text">{{ scope.row.probability }}%</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 跨度分析结果 -->
      <div v-if="advancedType === 'span' && spanData">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📏</span>
                  <span class="header-title">平均跨度</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ spanData.average_span }}</div>
                <div class="stat-desc">平均值</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📈</span>
                  <span class="header-title">最大跨度</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ spanData.max_span }}</div>
                <div class="stat-desc">最大值</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📉</span>
                  <span class="header-title">最小跨度</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ spanData.min_span }}</div>
                <div class="stat-desc">最小值</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🎯</span>
                  <span class="header-title">分析期数</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ spanData.total_periods }}</div>
                <div class="stat-desc">总期数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 间隔分析结果 -->
      <div v-if="advancedType === 'interval' && intervalData">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">⏱️</span>
                  <span class="header-title">平均间隔</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ intervalData.average_interval }}</div>
                <div class="stat-desc">期</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">📅</span>
                  <span class="header-title">当前间隔</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ intervalData.current_interval }}</div>
                <div class="stat-desc">期未出现</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🎯</span>
                  <span class="header-title">出现次数</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ intervalData.appear_count }}</div>
                <div class="stat-desc">次</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 重复分析结果 -->
      <div v-if="advancedType === 'repeat' && repeatData">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">🔄</span>
                  <span class="header-title">无重复</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ repeatData.no_repeat_periods }}</div>
                <div class="stat-desc">次 ({{ repeatData.probabilities.no_repeat }}%)</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">1️⃣</span>
                  <span class="header-title">重复1球</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ repeatData.repeat_patterns.one_ball_repeat }}</div>
                <div class="stat-desc">次 ({{ repeatData.probabilities.one_ball_repeat }}%)</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">2️⃣</span>
                  <span class="header-title">重复2球</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ repeatData.repeat_patterns.two_balls_repeat }}</div>
                <div class="stat-desc">次 ({{ repeatData.probabilities.two_balls_repeat }}%)</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="analysis-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="header-icon">3️⃣</span>
                  <span class="header-title">重复3球或以上</span>
                </div>
              </template>
              <div class="analysis-stat">
                <div class="stat-value">{{ repeatData.repeat_patterns.three_balls_repeat + repeatData.repeat_patterns.more_balls_repeat }}</div>
                <div class="stat-desc">次 ({{ (repeatData.probabilities.three_balls_repeat + repeatData.probabilities.more_balls_repeat).toFixed(2) }}%)</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// API配置
const API_BASE_URL = 'http://127.0.0.1:8001'

// 响应式数据
const loading = ref(false)
const activeTab = ref('frequency')
const ballTypeFilter = ref('all')
const frequencyData = ref([])
const overviewStats = ref({
  totalDraws: 0
})

// 高级分析相关数据
const advancedLoading = ref(false)
const advancedType = ref('consecutive')
const analysisLimit = ref(50)
const intervalBallType = ref('red')
const intervalBallNumber = ref(1)
const consecutiveData = ref(null)
const acValueData = ref(null)
const spanData = ref(null)
const intervalData = ref(null)
const repeatData = ref(null)

// 连号分析筛选
const consecutiveFilter = ref('all')

// 计算属性
const hotNumbers = computed(() => {
  const filtered = ballTypeFilter.value === 'all' 
    ? frequencyData.value 
    : frequencyData.value.filter(item => item.ball_type === ballTypeFilter.value)
  
  return filtered
    .sort((a, b) => b.appear_count - a.appear_count)
    .slice(0, 10)
})

const coldNumbers = computed(() => {
  const filtered = ballTypeFilter.value === 'all' 
    ? frequencyData.value 
    : frequencyData.value.filter(item => item.ball_type === ballTypeFilter.value)
  
  return filtered
    .sort((a, b) => a.appear_count - b.appear_count)
    .slice(0, 10)
})

const topRedBall = computed(() => {
  const redBalls = frequencyData.value.filter(item => item.ball_type === 'red')
  return redBalls.length > 0 
    ? redBalls.reduce((max, current) => current.appear_count > max.appear_count ? current : max)
    : null
})

const topBlueBall = computed(() => {
  const blueBalls = frequencyData.value.filter(item => item.ball_type === 'blue')
  return blueBalls.length > 0 
    ? blueBalls.reduce((max, current) => current.appear_count > max.appear_count ? current : max)
    : null
})

// 方法
const getFrequencyPercentage = (count) => {
  const maxCount = Math.max(...frequencyData.value.map(item => item.appear_count))
  return maxCount > 0 ? (count / maxCount) * 100 : 0
}

const loadFrequencyData = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/statistics/frequency/`, {
      params: {
        ball_type: ballTypeFilter.value
      }
    })
    
    if (response.data.code === 200 && response.data.data) {
      frequencyData.value = response.data.data.statistics || []
      ElMessage.success('频率数据加载成功')
    } else {
      frequencyData.value = []
      ElMessage.info('暂无统计数据')
    }
  } catch (error) {
    console.error('加载频率数据失败:', error)
    ElMessage.error('加载数据失败，请检查后端服务')
    frequencyData.value = []
  } finally {
    loading.value = false
  }
}

const loadOverviewData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/results/`)
    if (response.data && response.data.count) {
      overviewStats.value.totalDraws = response.data.count
    }
  } catch (error) {
    console.error('加载概览数据失败:', error)
  }
}

const refreshData = () => {
  loadFrequencyData()
  loadOverviewData()
}

// 高级分析相关方法
const loadAdvancedAnalysis = async () => {
  advancedLoading.value = true
  
  // 清空之前的分析结果
  consecutiveData.value = null
  acValueData.value = null
  spanData.value = null
  intervalData.value = null
  repeatData.value = null
  
  try {
    let url = ''
    let params = { limit: analysisLimit.value }
    
    switch (advancedType.value) {
      case 'consecutive':
        url = `${API_BASE_URL}/api/v1/statistics/consecutive_analysis/`
        break
      case 'ac_value':
        url = `${API_BASE_URL}/api/v1/statistics/ac_value_analysis/`
        break
      case 'span':
        url = `${API_BASE_URL}/api/v1/statistics/span_analysis/`
        break
      case 'interval':
        url = `${API_BASE_URL}/api/v1/statistics/interval_analysis/`
        params = {
          ...params,
          ball_number: intervalBallNumber.value,
          ball_type: intervalBallType.value
        }
        break
      case 'repeat':
        url = `${API_BASE_URL}/api/v1/statistics/repeat_analysis/`
        break
      default:
        ElMessage.error('未知的分析类型')
        return
    }
    
    const response = await axios.get(url, { params })
    
    if (response.data.code === 200 && response.data.data) {
      switch (advancedType.value) {
        case 'consecutive':
          consecutiveData.value = response.data.data
          break
        case 'ac_value':
          acValueData.value = response.data.data
          break
        case 'span':
          spanData.value = response.data.data
          break
        case 'interval':
          intervalData.value = response.data.data
          break
        case 'repeat':
          repeatData.value = response.data.data
          break
      }
      ElMessage.success(`${getAnalysisTypeName(advancedType.value)}完成`)
    } else {
      ElMessage.error('分析失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('高级分析失败:', error)
    ElMessage.error('分析失败，请检查网络连接和后端服务')
  } finally {
    advancedLoading.value = false
  }
}

const getAnalysisTypeName = (type) => {
  const names = {
    consecutive: '连号分析',
    ac_value: 'AC值分析',
    span: '跨度分析',
    interval: '间隔分析',
    repeat: '重复分析'
  }
  return names[type] || '分析'
}

// 获取分析功能的详细说明
const getAnalysisDescription = (type) => {
  const descriptions = {
    consecutive: {
      title: '连号分析说明',
      description: '分析开奖号码中连续数字的出现情况，如两连号(5,6)、三连号(8,9,10)等。帮助了解连号出现的频率规律。'
    },
    ac_value: {
      title: 'AC值分析说明',
      description: 'AC值是衡量号码组合离散程度的指标。计算方法：将6个红球中任意两个数字的差值去重后统计个数。AC值越大说明号码分布越分散。'
    },
    span: {
      title: '跨度分析说明',
      description: '跨度是指红球中最大号码与最小号码的差值。如红球4,7,16,24,25,33的跨度为33-4=29。了解号码分布的覆盖范围。'
    },
    interval: {
      title: '间隔分析说明',
      description: '分析某个特定号码两次出现之间的间隔期数。可以了解某个号码的"冷热"程度和出现规律。'
    },
    repeat: {
      title: '重复分析说明',
      description: '分析连续两期开奖中出现相同号码的情况。统计无重复、重复1球、2球、3球或以上的概率规律。'
    }
  }
  return descriptions[type] || { title: '分析说明', description: '暂无说明' }
}

// 连号分析相关方法
const filterConsecutivePatterns = (type) => {
  consecutiveFilter.value = type
}

const getFilteredConsecutivePatterns = () => {
  if (!consecutiveData.value || !consecutiveData.value.consecutive_patterns) {
    return []
  }
  
  if (consecutiveFilter.value === 'all') {
    return consecutiveData.value.consecutive_patterns
  }
  
  return consecutiveData.value.consecutive_patterns.filter(pattern => {
    const hasTargetType = pattern.consecutive_groups.some(group => {
      if (consecutiveFilter.value === 'two') return group.length === 2
      if (consecutiveFilter.value === 'three') return group.length === 3
      if (consecutiveFilter.value === 'four') return group.length >= 4
      return false
    })
    return hasTargetType
  })
}

const getConsecutiveDetailTitle = () => {
  const titles = {
    all: '连号模式详情',
    two: '两连号详情',
    three: '三连号详情',
    four: '四连号及以上详情'
  }
  return titles[consecutiveFilter.value] || '连号模式详情'
}

const getConsecutiveTagType = (group) => {
  if (group.length === 2) return 'success'
  if (group.length === 3) return 'warning'
  if (group.length >= 4) return 'danger'
  return 'info'
}

// 监听筛选条件变化
watch([ballTypeFilter], () => {
  if (activeTab.value === 'frequency' || activeTab.value === 'hot_cold') {
    loadFrequencyData()
  }
})

// 组件挂载时加载数据
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.statistics-container {
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
.filter-card, .stats-card, .overview-card, .stats-summary {
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

.filter-controls {
  margin-top: 15px;
  display: flex;
  gap: 15px;
  align-items: center;
}

/* 球号样式 */
.ball {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-flex;
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

/* 频率条样式 */
.frequency-bar {
  position: relative;
  height: 24px;
  background-color: #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.frequency-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  border-radius: 12px;
  transition: width 0.3s ease;
}

.red-freq {
  background: linear-gradient(45deg, rgba(255, 107, 107, 0.3), rgba(255, 82, 82, 0.3));
}

.blue-freq {
  background: linear-gradient(45deg, rgba(77, 171, 247, 0.3), rgba(51, 154, 240, 0.3));
}

.frequency-text {
  position: relative;
  z-index: 1;
  font-size: 12px;
  font-weight: bold;
  color: #666;
}

/* 冷热分析样式 */
.hot-cold-list {
  max-height: 400px;
  overflow-y: auto;
}

.number-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.hot-item {
  background: linear-gradient(45deg, rgba(255, 107, 107, 0.1), rgba(255, 82, 82, 0.1));
  border-left: 3px solid #ff6b6b;
}

.cold-item {
  background: linear-gradient(45deg, rgba(77, 171, 247, 0.1), rgba(51, 154, 240, 0.1));
  border-left: 3px solid #4dabf7;
}

.number-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.rank {
  font-size: 16px;
  font-weight: bold;
  color: #666;
  margin-right: 15px;
  min-width: 20px;
}

.count {
  margin-left: auto;
  font-size: 14px;
  color: #666;
  font-weight: bold;
}

/* 概览卡片样式 */
.overview-item {
  display: flex;
  align-items: center;
  padding: 20px;
}

.overview-icon {
  font-size: 36px;
  margin-right: 15px;
}

.overview-content {
  flex: 1;
}

.overview-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

/* 加载和空数据样式 */
.loading-container, .empty-data {
  text-align: center;
  padding: 40px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .title-icon {
    font-size: 28px;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .overview-item {
    padding: 15px;
  }
  
  .overview-icon {
    font-size: 28px;
  }
  
  .overview-value {
    font-size: 20px;
  }
}

/* 高级分析样式 */
.analysis-card {
  height: 190px;
  margin-bottom: 20px;
}

.analysis-card .el-card__header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  min-height: 60px;
  max-height: 80px;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.analysis-card .el-card__body {
  padding: 0;
  height: calc(100% - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.analysis-stat {
  text-align: center;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px 20px 40px 20px;
  position: relative;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
  line-height: 1;
  display: block;
}

.stat-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.2;
  margin: 0;
}

.pattern-card {
  margin-top: 20px;
}

.distribution-card {
  margin-top: 20px;
}

.probability-bar {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #f5f5f5;
  border-radius: 10px;
  overflow: hidden;
}

.probability-fill {
  height: 100%;
  background: linear-gradient(45deg, #67c23a, #85ce61);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.probability-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: bold;
  color: #333;
}

.ball-group {
  display: flex;
  gap: 5px;
  justify-content: center;
  flex-wrap: wrap;
}

.ball-group-compact {
  display: flex;
  gap: 3px;
  justify-content: center;
  flex-wrap: nowrap;
  align-items: center;
}

.red-ball-small {
  background: linear-gradient(45deg, #ff6b6b, #ff5252);
  box-shadow: 0 2px 4px rgba(255, 107, 107, 0.3);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 11px;
  color: white;
  flex-shrink: 0;
}

.consecutive-groups {
  display: flex;
  gap: 5px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 新增样式 */
.clickable-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.clickable-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
}

.click-hint {
  font-size: 12px;
  color: #999;
  font-style: italic;
  margin-top: 10px;
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
}

.parameter-group {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.parameter-label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
}

.parameter-desc {
  font-size: 12px;
  color: #909399;
  font-style: italic;
  max-width: 400px;
}

.analysis-description {
  margin-top: 15px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.3;
  word-break: keep-all;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.empty-data {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .parameter-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .parameter-label {
    min-width: auto;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style> 