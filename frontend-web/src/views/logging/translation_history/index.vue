<template>
  <div class="history-page">
    <HistoryHeader
      v-model:dateRange="dateRange"
      v-model:keyword="keyword"
      :loading="loading"
      :total="total"
      @search="handleSearch"
    />

    <div class="content-body">
      <div class="sidebar-mini">
        <MiniCalendar
          v-model:heatmapYear="heatmapYear"
          v-model:heatmapMonth="heatmapMonth"
          :activityDates="activityDates"
          :dateRange="dateRange"
          :isCurrentMonth="isCurrentMonth"
          @changeMonth="fetchActivityDates"
          @selectDate="handleCalendarClick"
        />

        <QuickFilters
          :activeFilter="activeFilter"
          @filterChange="applyQuickFilter"
        />
      </div>

      <HistoryList
        :historyList="groupedRecords"
        :loading="loading"
        :total="total"
        v-model:pageNo="pageNo"
        :pageSize="pageSize"
        @pageChange="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getHistoryList, getActivityDates } from '@/api/translationHistory'
import useUserStore from '@/store/modules/user'

import HistoryHeader from './components/HistoryHeader.vue'
import MiniCalendar from './components/MiniCalendar.vue'
import QuickFilters from './components/QuickFilters.vue'
import HistoryList from './components/HistoryList.vue'

const userStore = useUserStore()

interface HistoryItem {
  createTime: string
  originalWords: string
  resultSentence: string
  isAiPolished: number
}

// ==================== 数据 ====================
const historyList = ref<HistoryItem[]>([])
const loading = ref(false)
const pageNo = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref<string[]>([])
const keyword = ref('')
const activeFilter = ref('all')

// 日历
const now = new Date()
const heatmapYear = ref(now.getFullYear())
const heatmapMonth = ref(now.getMonth() + 1)
const activityDates = ref<string[]>([])

// ==================== 计算属性 ====================
const isCurrentMonth = computed(() => {
  const n = new Date()
  return heatmapYear.value === n.getFullYear() && heatmapMonth.value === n.getMonth() + 1
})

/** 按日期分组 */
const groupedRecords = computed(() => {
  const groups: { date: string; dateLabel: string; items: HistoryItem[] }[] = []
  const map = new Map<string, HistoryItem[]>()

  for (const item of historyList.value) {
    const dateStr = item.createTime ? item.createTime.substring(0, 10) : '未知日期'
    if (!map.has(dateStr)) {
      map.set(dateStr, [])
    }
    map.get(dateStr)!.push(item)
  }

  for (const [date, items] of map) {
    groups.push({
      date,
      dateLabel: formatDateLabel(date),
      items
    })
  }

  return groups
})

// ==================== 方法 ====================
const fetchHistory = async () => {
  if (!userStore.userId) return
  loading.value = true
  try {
    const res = await getHistoryList({
      userId: userStore.userId,
      pageNo: pageNo.value,
      pageSize: pageSize.value,
      startDate: dateRange.value?.[0] || undefined,
      endDate: dateRange.value?.[1] || undefined,
      keyword: keyword.value || undefined
    })
    if (res?.data) {
      historyList.value = res.data.rows || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchActivityDates = async () => {
  if (!userStore.userId) return
  try {
    const res = await getActivityDates({
      userId: userStore.userId,
      year: heatmapYear.value,
      month: heatmapMonth.value
    })
    activityDates.value = res?.data || []
  } catch (error) {
    console.error('获取活动日期失败:', error)
  }
}

const handleSearch = () => {
  pageNo.value = 1
  activeFilter.value = 'custom'
  fetchHistory()
}

const handlePageChange = () => {
  fetchHistory()
  // 滚动到顶部
  document.querySelector('.record-list')?.scrollTo({ top: 0, behavior: 'smooth' })
}

const applyQuickFilter = (f: { key: string; label: string }) => {
  activeFilter.value = f.key
  keyword.value = ''

  const today = new Date()
  const todayStr = today.toISOString().substring(0, 10)

  if (f.key === 'all') {
    dateRange.value = []
  } else if (f.key === 'today') {
    dateRange.value = [todayStr, todayStr]
  } else if (f.key === 'week') {
    const weekStart = new Date(today)
    weekStart.setDate(today.getDate() - today.getDay())
    dateRange.value = [weekStart.toISOString().substring(0, 10), todayStr]
  } else if (f.key === 'ai') {
    dateRange.value = []
    // AI 筛选暂用关键词方式，后续可加 isAiPolished 参数
  }

  pageNo.value = 1
  fetchHistory()
}

const handleCalendarClick = (day: number) => {
  const d = `${heatmapYear.value}-${String(heatmapMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  dateRange.value = [d, d]
  activeFilter.value = 'custom'
  pageNo.value = 1
  fetchHistory()
}

/** 日期标签（今天 / 昨天 / 具体日期） */
const formatDateLabel = (dateStr: string) => {
  if (!dateStr || dateStr === '未知日期') return dateStr
  const today = new Date()
  const todayStr = today.toISOString().substring(0, 10)
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  const yesterdayStr = yesterday.toISOString().substring(0, 10)

  if (dateStr === todayStr) return '📍 今天'
  if (dateStr === yesterdayStr) return '昨天'

  // "4月2日 周三"
  const d = new Date(dateStr)
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${weekDays[d.getDay()]}`
}

// ==================== 生命周期 ====================
onMounted(() => {
  fetchHistory()
  fetchActivityDates()
})
</script>

<style scoped lang="scss">
.history-page {
  min-height: calc(100vh - 84px);
  padding: 24px 32px;
  background: #f5f7fa;
}

.content-body {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.sidebar-mini {
  width: 240px;
  flex-shrink: 0;
  position: sticky;
  top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 992px) {
  .content-body {
    flex-direction: column;
  }

  .sidebar-mini {
    width: 100%;
    position: static;
    flex-direction: row;
    overflow-x: auto;
    
    :deep(.mini-calendar) { min-width: 240px; }
    :deep(.quick-filters) { min-width: 200px; flex: 1; }
  }
}

@media (max-width: 768px) {
  .history-page {
    padding: 16px;
  }

  .sidebar-mini {
    flex-direction: column;
  }
}
</style>
