<template>
  <div class="mini-calendar">
    <div class="cal-header">
      <button class="cal-nav-btn" @click="prevMonth">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <span class="cal-month-label">{{ heatmapYear }}年{{ heatmapMonth }}月</span>
      <button class="cal-nav-btn" @click="nextMonth" :disabled="isCurrentMonth">
        <el-icon><ArrowRight /></el-icon>
      </button>
    </div>
    <div class="cal-weekdays">
      <span v-for="d in ['日','一','二','三','四','五','六']" :key="d">{{ d }}</span>
    </div>
    <div class="cal-grid">
      <div v-for="n in firstDayOfWeek" :key="'e'+n" class="cal-cell empty"></div>
      <div
        v-for="day in daysInMonth"
        :key="day"
        class="cal-cell"
        :class="{
          active: activitySet.has(fmtDate(day)),
          today: isTodayCell(day),
          selected: isSelectedDay(day)
        }"
        @click="handleCalendarClick(day)"
      >
        {{ day }}
      </div>
    </div>
    <div class="cal-legend">
      <span class="legend-dot active-dot"></span>
      <span class="legend-text">有记录</span>
      <template v-if="localRange.length === 2 && localRange[0] && localRange[1]">
        <span class="legend-clear" @click="clearSelection">清除</span>
      </template>
      <span class="legend-count">{{ activityDates.length }} 天活跃</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  heatmapYear: number
  heatmapMonth: number
  activityDates: string[]
  dateRange: string[]
  isCurrentMonth: boolean
}>()

const emit = defineEmits<{
  (e: 'update:heatmapYear', val: number): void
  (e: 'update:heatmapMonth', val: number): void
  (e: 'changeMonth'): void
  (e: 'update:dateRange', val: string[]): void
}>()

const activitySet = computed(() => new Set(props.activityDates))
const daysInMonth = computed(() => new Date(props.heatmapYear, props.heatmapMonth, 0).getDate())
const firstDayOfWeek = computed(() => new Date(props.heatmapYear, props.heatmapMonth - 1, 1).getDay())

const rangeStart = ref<string | null>(null)
const localRange = computed<string[]>(() => props.dateRange || [])

// 外部（QuickFilters）改变 dateRange 时重置内部选择状态
watch(() => props.dateRange, ([s, e]) => {
  if (rangeStart.value && (!s || !e || rangeStart.value < s || rangeStart.value > e)) {
    rangeStart.value = null
  }
})

const prevMonth = () => {
  if (props.heatmapMonth === 1) { 
    emit('update:heatmapYear', props.heatmapYear - 1)
    emit('update:heatmapMonth', 12) 
  } else { 
    emit('update:heatmapMonth', props.heatmapMonth - 1) 
  }
  emit('changeMonth')
}

const nextMonth = () => {
  if (props.isCurrentMonth) return
  if (props.heatmapMonth === 12) { 
    emit('update:heatmapYear', props.heatmapYear + 1)
    emit('update:heatmapMonth', 1) 
  } else { 
    emit('update:heatmapMonth', props.heatmapMonth + 1) 
  }
  emit('changeMonth')
}

const fmtDate = (day: number) => {
  return `${props.heatmapYear}-${String(props.heatmapMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

const isTodayCell = (day: number) => {
  const n = new Date()
  return props.heatmapYear === n.getFullYear() && props.heatmapMonth === n.getMonth() + 1 && day === n.getDate()
}

const isSelectedDay = (day: number) => {
  if (!props.dateRange || props.dateRange.length < 2) return false
  const d = fmtDate(day)
  return d >= props.dateRange[0] && d <= props.dateRange[1]
}

const handleCalendarClick = (day: number) => {
  const dayStr = fmtDate(day)
  const [s, e] = localRange.value

  if (!s && !e) {
    // 无选中 → 选中该天
    rangeStart.value = dayStr
    emit('update:dateRange', [dayStr, dayStr])
    return
  }

  // 有选中
  if (dayStr === s || dayStr === e) {
    // 点击边界 → 清除
    clearSelection()
    return
  }

  if (dayStr > s && dayStr < e) {
    // 点击范围内非边界 → 重新开始
    rangeStart.value = dayStr
    emit('update:dateRange', [dayStr, dayStr])
    return
  }

  // 点击范围外 → 扩展
  const anchor = rangeStart.value || s
  const sorted = [anchor, dayStr].sort()
  rangeStart.value = anchor
  emit('update:dateRange', sorted)
}

const clearSelection = () => {
  rangeStart.value = null
  emit('update:dateRange', [])
}
</script>

<style scoped lang="scss">
.mini-calendar {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.cal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;

  .cal-month-label {
    font-size: 14px;
    font-weight: 700;
    color: #1f2937;
  }

  .cal-nav-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
    border-radius: 6px;
    color: #6b7280;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover:not(:disabled) { background: #f3f4f6; color: #1f2937; }
    &:disabled { opacity: 0.3; cursor: not-allowed; }
  }
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 4px;

  span {
    text-align: center;
    font-size: 10px;
    font-weight: 600;
    color: #9ca3af;
    padding: 4px 0;
  }
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
  color: #6b7280;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;

  &.empty { cursor: default; }

  &:hover:not(.empty) {
    background: #f3f4f6;
  }

  &.active {
    background: #dbeafe;
    color: #2563eb;
    font-weight: 700;
  }

  &.today {
    border: 1.5px solid #6366f1;
    font-weight: 700;
  }

  &.selected {
    background: #6366f1;
    color: #fff;
    font-weight: 700;
  }

  &.selected.active {
    background: #4f46e5;
  }
}

.cal-legend {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #f3f4f6;
  font-size: 11px;
  color: #9ca3af;

  .active-dot {
    width: 8px;
    height: 8px;
    border-radius: 3px;
    background: #dbeafe;
    border: 1px solid #93c5fd;
    flex-shrink: 0;
  }

  .legend-count {
    margin-left: auto;
    font-weight: 600;
    color: #6b7280;
  }

  .legend-clear {
    margin-left: auto;
    font-size: 11px;
    color: #6366f1;
    cursor: pointer;
    font-weight: 600;

    &:hover { text-decoration: underline; }
  }
}
</style>
