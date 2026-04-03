<template>
  <div class="page-container">
    <div class="sidebar">
      <div class="calendar-wrapper">
        <h3 class="calendar-title">📅 练习日历</h3>
        <el-calendar v-model="currentDate" class="custom-calendar">
          <template #date-cell="{ data }">
            <div 
              class="date-cell" 
              :class="{ 'is-active': isActivityDate(data.day) }"
              @click="handleDateClick(data.day)"
            >
              <span>{{ data.day.split('-').slice(2).join('') }}</span>
              <div v-if="isActivityDate(data.day)" class="activity-dot"></div>
            </div>
          </template>
        </el-calendar>
      </div>
    </div>

    <div class="main-content">
      <h2 class="page-title">👋 我的手语练习日记</h2>
      
      <!-- 简约搜索栏 -->
      <div class="search-bar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="handleSearch"
          class="date-picker"
        />
        
        <el-input
          v-model="keyword"
          placeholder="搜索关键词..."
          class="keyword-input"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>

      <div class="timeline-wrapper">
        <el-timeline>
          <el-timeline-item
            v-for="(item, index) in historyList"
            :key="index"
            :timestamp="item.createTime"
            placement="top"
            :type="item.isAiPolished ? 'success' : 'primary'"
            :hollow="true"
          >
            <el-card class="history-card" shadow="hover">
              <div class="card-content">
                
                <div class="left-part">
                  <div class="label">我的手语动作</div>
                  <div class="tags-wrapper">
                    <el-tag 
                      v-for="(word, i) in parseWords(item.originalWords)" 
                      :key="i"
                      class="sign-tag"
                      effect="light"
                    >
                      {{ word }}
                    </el-tag>
                  </div>
                </div>

                <div class="middle-part">
                  <el-icon :size="20" color="#909399"><Right /></el-icon>
                  <div class="ai-badge" v-if="item.isAiPolished">
                    <el-icon><MagicStick /></el-icon> AI
                  </div>
                </div>

                <div class="right-part">
                  <div class="label">翻译结果</div>
                  <div class="result-text">{{ item.resultSentence }}</div>
                </div>
                
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Right, MagicStick, Search } from '@element-plus/icons-vue'
import { getHistoryList, getActivityDates } from '@/api/translationHistory'
import useUserStore from '@/store/modules/user' 

const userStore = useUserStore()

interface HistoryItem {
  createTime: string;
  originalWords: string; // JSON string
  resultSentence: string;
  isAiPolished: number; // 0 or 1
}

const historyList = ref<HistoryItem[]>([])
const loading = ref(false)

// 分页参数
const pageNo = ref(1)
const pageSize = ref(20)
const total = ref(0) // 虽然目前还没做分页组件，但预留着

// 搜索参数
const dateRange = ref<string[]>([])
const keyword = ref('')

// 日历相关
const currentDate = ref(new Date())
const activityDates = ref<string[]>([])

// 获取活动日期
const fetchActivityDates = async () => {
  if (!userStore.userId) return
  try {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth() + 1
    const res = await getActivityDates({ userId: userStore.userId, year, month })
    if (res && res.data) {
      activityDates.value = res.data
    }
  } catch (error) {
    console.error('获取活动日期失败:', error)
  }
}

// 监听月份变化
watch(currentDate, (newVal, oldVal) => {
  if (newVal.getMonth() !== oldVal?.getMonth() || newVal.getFullYear() !== oldVal?.getFullYear()) {
    fetchActivityDates()
  }
})

const isActivityDate = (day: string) => {
  return activityDates.value.includes(day)
}

const handleDateClick = (day: string) => {
  // 只有点击有记录的日期才触发筛选? 或者不管有没有都触发?
  // 用户需求：点击日历上的某一天 -> 右侧时间轴自动滚动到那一天，或者只显示那一天的记录。
  // 这里实现：只显示那一天的记录
  dateRange.value = [day, day]
  handleSearch()
}

const handleSearch = () => {
  pageNo.value = 1
  fetchHistory()
}

const fetchHistory = async () => {
  if (!userStore.userId) return
  
  loading.value = true
  try {
    const res = await getHistoryList({
      userId: userStore.userId,
      pageNo: pageNo.value,
      pageSize: pageSize.value,
      startDate: dateRange.value ? dateRange.value[0] : undefined,
      endDate: dateRange.value ? dateRange.value[1] : undefined,
      keyword: keyword.value
    })
    
    // 后端返回结构 { total: xx, rows: [...] }
    if (res && res.data) {
      historyList.value = res.data.rows || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

const parseWords = (rawValue: string) => {
  const text = String(rawValue ?? '').trim()
  if (!text) {
    return []
  }

  try {
    const parsed = JSON.parse(text)
    if (Array.isArray(parsed)) {
      return parsed.map(item => String(item))
    }
    return [String(parsed)]
  } catch (error) {
    return [text]
  }
}

onMounted(() => {
  fetchHistory()
  fetchActivityDates()
})
</script>

<style scoped>
.page-container {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
}

.sidebar {
  width: 320px;
  flex-shrink: 0;
}

.calendar-wrapper {
  background: white;
  border-radius: 12px;
  padding: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.calendar-title {
  text-align: center;
  margin: 10px 0;
  color: #303133;
  font-size: 16px;
}

.custom-calendar :deep(.el-calendar__header) {
  padding: 10px;
  font-size: 14px;
}

.custom-calendar :deep(.el-calendar__body) {
  padding: 10px;
}

.custom-calendar :deep(.el-calendar-table td) {
  border: none;
}

.custom-calendar :deep(.el-calendar-table td.is-selected) {
  background-color: transparent;
}

.custom-calendar :deep(.el-calendar-table .el-calendar-day) {
  height: 40px;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.date-cell {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.date-cell:hover {
  background-color: #f2f6fc;
}

.date-cell.is-active {
  font-weight: bold;
  color: #409eff;
}

.activity-dot {
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  background-color: #409eff;
  border-radius: 50%;
}

.main-content {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  min-height: 600px;
}

.timeline-wrapper {
  padding: 0 20px;
}

/* Original styles below */
.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}
.search-bar {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
}
.date-picker {
  width: 250px !important;
}
.keyword-input {
  width: 250px;
}
.history-card {
  border-radius: 12px;
}
.card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.left-part, .right-part {
  flex: 1; /* 左右等宽 */
  padding: 0 10px;
}
.middle-part {
  width: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}
.sign-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}
.result-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.ai-badge {
  font-size: 10px;
  color: #67c23a;
  background: #f0f9eb;
  padding: 2px 6px;
  border-radius: 10px;
  margin-top: 4px;
  display: flex;
  align-items: center;
}
</style>
