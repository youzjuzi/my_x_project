<template>
  <el-dialog v-model="visible" title="我的挑战记录" width="80%" @close="handleClose">
    <div class="history-content">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.mode"
          placeholder="挑战模式"
          clearable
          style="width: 200px"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="RefreshRight" @click="handleReset">重置</el-button>
      </div>

      <!-- 表格 -->
      <el-table
        :data="historyList"
        v-loading="loading"
        border
        style="width: 100%"
      >
        <el-table-column type="index" width="60" align="center" label="#" />
        <el-table-column prop="challengeId" label="挑战ID" min-width="200" show-overflow-tooltip />
        <el-table-column label="挑战模式" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.mode === 'random' ? 'primary' : 'success'">
              {{ row.mode === 'random' ? '随机挑战' : '题库挑战' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="得分" width="100" align="center">
          <template #default="{ row }">
            <span class="score-text">{{ row.score || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="完成情况" width="150" align="center">
          <template #default="{ row }">
            <span>{{ row.completedCount || 0 }} / {{ row.totalCount || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="使用时间" width="120" align="center">
          <template #default="{ row }">
            {{ formatTime(row.timeUsed || 0) }}
          </template>
        </el-table-column>
        <el-table-column label="准确率" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getAccuracyTagType(row)">
              {{ getAccuracy(row) }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="挑战时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getChallengeHistory } from '@/api/challenge'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const historyList = ref<any[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({
  mode: ''
})

// 获取挑战历史
const fetchHistory = async () => {
  loading.value = true
  try {
    const res = await getChallengeHistory({
      pageNo: currentPage.value,
      pageSize: pageSize.value
    })
    const data = res.data || { total: 0, rows: [] }
    historyList.value = data.rows || []
    total.value = Number(data.total) || 0
  } catch (error) {
    console.error('获取挑战历史失败', error)
    ElMessage.error('获取挑战历史失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchHistory()
}

const handleReset = () => {
  searchForm.mode = ''
  currentPage.value = 1
  fetchHistory()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchHistory()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchHistory()
}

const handleClose = () => {
  emit('update:modelValue', false)
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '—'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAccuracy = (row: any) => {
  if (!row.totalCount || row.totalCount === 0) return 0
  const accuracy = ((row.completedCount || 0) / row.totalCount) * 100
  return Math.round(accuracy)
}

const getAccuracyTagType = (row: any) => {
  const accuracy = getAccuracy(row)
  if (accuracy >= 90) return 'success'
  if (accuracy >= 70) return 'warning'
  if (accuracy >= 50) return 'info'
  return 'danger'
}

const getStatusText = (status: number) => {
  const map: Record<number, string> = {
    0: '进行中',
    1: '已完成',
    2: '已放弃'
  }
  return map[status] || '未知'
}

const getStatusTagType = (status: number) => {
  const map: Record<number, string> = {
    0: 'warning',
    1: 'success',
    2: 'info'
  }
  return map[status] || 'info'
}

watch(() => props.modelValue, (val) => {
  if (val) {
    fetchHistory()
  }
})
</script>

<style scoped lang="scss">
.history-content {
  .search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }

  .score-text {
    font-size: 18px;
    font-weight: bold;
    color: #6956FF;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

