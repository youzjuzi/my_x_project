<template>
  <div class="quick-filters">
    <div class="filter-title">快速筛选</div>
    <button
      v-for="f in quickFilters"
      :key="f.key"
      class="filter-chip"
      :class="{ active: activeFilter === f.key }"
      @click="applyQuickFilter(f)"
    >
      {{ f.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  activeFilter: string
}>()

const emit = defineEmits<{
  (e: 'filterChange', filter: { key: string; label: string }): void
}>()

const quickFilters = [
  { key: 'all', label: '全部' },
  { key: 'today', label: '今天' },
  { key: 'week', label: '本周' },
  { key: 'ai', label: '仅AI润色' },
]

const applyQuickFilter = (f: { key: string; label: string }) => {
  emit('filterChange', f)
}
</script>

<style scoped lang="scss">
.quick-filters {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);

  .filter-title {
    font-size: 12px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
  }

  .filter-chip {
    display: inline-block;
    padding: 6px 14px;
    margin: 0 6px 6px 0;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid #e5e7eb;
    background: #fff;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #6366f1;
      color: #6366f1;
    }

    &.active {
      background: #6366f1;
      border-color: #6366f1;
      color: #fff;
    }
  }
}
</style>
