<template>
  <div class="page-header">
    <div class="header-left">
      <h1 class="page-title">识别记录</h1>
      <span class="record-count" v-if="!loading">共 {{ total }} 条记录</span>
    </div>
    <div class="header-actions">
      <el-date-picker
        v-model="internalDateRange"
        type="daterange"
        range-separator="—"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        :shortcuts="dateShortcuts"
        @change="handleSearch"
        class="date-picker"
        size="default"
      />
      <el-input
        v-model="internalKeyword"
        placeholder="搜索识别内容..."
        class="keyword-input"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        :prefix-icon="Search"
        size="default"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps<{
  dateRange: string[]
  keyword: string
  loading: boolean
  total: number
}>()

const emit = defineEmits<{
  (e: 'update:dateRange', val: string[]): void
  (e: 'update:keyword', val: string): void
  (e: 'search'): void
}>()

const internalDateRange = computed({
  get: () => props.dateRange,
  set: (val) => emit('update:dateRange', val)
})

const internalKeyword = computed({
  get: () => props.keyword,
  set: (val) => emit('update:keyword', val)
})

const dateShortcuts = [
  { text: '今天', value: () => { const d = new Date(); return [d, d] } },
  { text: '最近7天', value: () => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 6); return [s, e] } },
  { text: '最近30天', value: () => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 29); return [s, e] } },
]

const handleSearch = () => {
  emit('search')
}
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;

  .page-title {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
  }

  .record-count {
    font-size: 13px;
    color: #9ca3af;
    font-weight: 500;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;

  .date-picker {
    width: 280px;
  }

  .keyword-input {
    width: 220px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;

    .date-picker, .keyword-input { width: 100%; }
  }
}
</style>
