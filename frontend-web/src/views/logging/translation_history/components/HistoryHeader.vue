<template>
  <div class="page-header">
    <div class="header-left">
      <h1 class="page-title">识别记录</h1>
      <span class="record-count" v-if="!loading">共 {{ total }} 条记录</span>
    </div>
    <div class="header-actions">
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
  keyword: string
  loading: boolean
  total: number
}>()

const emit = defineEmits<{
  (e: 'update:keyword', val: string): void
  (e: 'search'): void
}>()

const internalKeyword = computed({
  get: () => props.keyword,
  set: (val) => emit('update:keyword', val)
})

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

    .keyword-input { width: 100%; }
  }
}
</style>
