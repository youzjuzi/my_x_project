<template>
  <el-card class="table-card" shadow="hover">
    <div class="table-toolbar">
      <div>
        <div class="table-title">挑战记录列表</div>
        <div class="table-subtitle">
          共 {{ total }} 条记录，当前页显示 {{ tableData.length }} 条
        </div>
      </div>
      <el-space>
        <el-button text :icon="RefreshRight" @click="$emit('refresh')">刷新</el-button>
      </el-space>
    </div>

    <el-table :data="tableData" v-loading="loading" border>
      <el-table-column type="index" width="60" align="center" label="#" />
      <el-table-column prop="challengeId" label="挑战ID" min-width="200" show-overflow-tooltip />
      <el-table-column label="用户" width="180" align="center">
        <template #default="{ row }">
          <div class="user-cell">
            <div class="username">{{ row.username || '未知用户' }}</div>
            <el-text type="info" size="small">ID: {{ row.userId }}</el-text>
          </div>
        </template>
      </el-table-column>
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
      <el-table-column label="时间限制" width="120" align="center">
        <template #default="{ row }">
          {{ formatTime(row.timeLimit || 0) }}
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
      <el-table-column prop="finishTime" label="完成时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.finishTime) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center" fixed="right">
        <template #default="{ row }">
          <span class="action-link view-link" @click="$emit('view', row)">查看详情</span>
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
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'

const props = defineProps<{
  tableData: any[]
  loading: boolean
  total: number
  currentPage: number
  pageSize: number
}>()

const emit = defineEmits<{
  'update:currentPage': [value: number]
  'update:pageSize': [value: number]
  'refresh': []
  'view': [row: any]
}>()

const currentPage = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const pageSize = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const handleSizeChange = (val: number) => {
  emit('update:pageSize', val)
  emit('update:currentPage', 1)
}

const handleCurrentChange = (val: number) => {
  emit('update:currentPage', val)
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
</script>

<style scoped lang="scss">
.table-card {
  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .table-title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 4px;
    }
    
    .table-subtitle {
      font-size: 14px;
      color: #909399;
    }
  }
  
  .score-text {
    font-size: 18px;
    font-weight: bold;
    color: #6956FF;
  }
  
  .user-cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    
    .username {
      font-weight: 500;
      color: #303133;
    }
  }
  
  .action-link {
    cursor: pointer;
    color: #409EFF;
    text-decoration: none;
    
    &:hover {
      color: #66b1ff;
      text-decoration: underline;
    }
    
    &.view-link {
      color: #409EFF;
    }
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>

