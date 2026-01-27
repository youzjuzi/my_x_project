<template>
  <div class="challenge-manage-page">
    <!-- 搜索组件 -->
    <ChallengeSearch
      :model-value="searchForm"
      @update:model-value="updateSearchForm"
      @search="handleSearch"
      @reset="handleReset"
    />

    <!-- 表格组件 -->
    <ChallengeTable
      :table-data="tableData"
      :loading="loading"
      :total="total"
      :current-page="currentPage"
      :page-size="pageSize"
      @update:current-page="currentPage = $event"
      @update:page-size="pageSize = $event; currentPage = 1"
      @refresh="fetchData"
      @view="handleView"
    />

    <!-- 详情对话框 -->
    <ChallengeDetail
      v-model="detailVisible"
      :challenge="selectedChallenge"
    />
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'challenge_history' // ⚠️ 必须与路由 name 完全一致！
})

import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ChallengeSearch from './components/ChallengeSearch.vue'
import ChallengeTable from './components/ChallengeTable.vue'
import ChallengeDetail from './components/ChallengeDetail.vue'
import { getAllChallengeHistory } from '@/api/challenge'

// 搜索表单
const searchForm = reactive({
  userId: null as number | null,
  mode: null as string | null,
  status: null as number | null
})

// 监听搜索表单变化
const updateSearchForm = (value: any) => {
  searchForm.userId = value.userId !== undefined && value.userId !== null ? value.userId : null
  searchForm.mode = value.mode !== undefined && value.mode !== null && value.mode !== '' ? value.mode : null
  searchForm.status = value.status !== undefined && value.status !== null ? value.status : null
}

// 表格数据
const tableData = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 详情对话框
const detailVisible = ref(false)
const selectedChallenge = ref<any>(null)

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {
      pageNo: currentPage.value,
      pageSize: pageSize.value
    }
    
    // 只有当值不为 null 和 undefined 时才添加到参数中
    if (searchForm.userId != null) {
      params.userId = searchForm.userId
    }
    if (searchForm.mode != null && searchForm.mode !== '') {
      params.mode = searchForm.mode
    }
    if (searchForm.status != null) {
      params.status = searchForm.status
    }

    console.log('查询参数:', params) // 调试日志

    const res = await getAllChallengeHistory(params)
    const data = res.data || { total: 0, rows: [] }
    tableData.value = data.rows || []
    total.value = Number(data.total) || 0
  } catch (error) {
    console.error('获取挑战记录失败', error)
    ElMessage.error('获取挑战记录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  // 清空搜索条件
  searchForm.userId = null
  searchForm.mode = null
  searchForm.status = null
  currentPage.value = 1
  fetchData()
}

const handleView = (row: any) => {
  selectedChallenge.value = row
  detailVisible.value = true
}

// 初始化
onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.challenge-manage-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}
</style>
