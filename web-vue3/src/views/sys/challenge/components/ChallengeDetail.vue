<template>
  <el-dialog v-model="visible" title="挑战详情" width="60%" @close="handleClose">
    <div class="detail-content" v-if="challenge">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="挑战ID" :span="2">
          {{ challenge.challengeId }}
        </el-descriptions-item>
        <el-descriptions-item label="用户">
          <div class="user-info">
            <span class="username">{{ challenge.username || '未知用户' }}</span>
            <el-text type="info" size="small" style="margin-left: 8px">
              (ID: {{ challenge.userId }})
            </el-text>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="挑战模式">
          <el-tag :type="challenge.mode === 'random' ? 'primary' : 'success'">
            {{ challenge.mode === 'random' ? '随机挑战' : '题库挑战' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="题库ID" v-if="challenge.questionSetId">
          {{ challenge.questionSetId }}
        </el-descriptions-item>
        <el-descriptions-item label="得分">
          <span class="score-text">{{ challenge.score || 0 }} 分</span>
        </el-descriptions-item>
        <el-descriptions-item label="完成情况">
          {{ challenge.completedCount || 0 }} / {{ challenge.totalCount || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="准确率">
          <el-tag :type="getAccuracyTagType(challenge)">
            {{ getAccuracy(challenge) }}%
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="使用时间">
          {{ formatTime(challenge.timeUsed || 0) }}
        </el-descriptions-item>
        <el-descriptions-item label="时间限制">
          {{ formatTime(challenge.timeLimit || 0) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(challenge.status)">
            {{ getStatusText(challenge.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="挑战时间" :span="2">
          {{ formatDateTime(challenge.createTime) }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间" :span="2" v-if="challenge.finishTime">
          {{ formatDateTime(challenge.finishTime) }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  challenge: any | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

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
    minute: '2-digit',
    second: '2-digit'
  })
}

const getAccuracy = (challenge: any) => {
  if (!challenge.totalCount || challenge.totalCount === 0) return 0
  const accuracy = ((challenge.completedCount || 0) / challenge.totalCount) * 100
  return Math.round(accuracy)
}

const getAccuracyTagType = (challenge: any) => {
  const accuracy = getAccuracy(challenge)
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
.detail-content {
  .score-text {
    font-size: 18px;
    font-weight: bold;
    color: #6956FF;
  }
}
</style>

