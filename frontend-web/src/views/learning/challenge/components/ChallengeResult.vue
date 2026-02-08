<template>
  <el-dialog v-model="visible" title="挑战结束" width="400px" center>
    <div class="result-content">
      <div class="result-score">
        <el-icon :size="60" color="#6956FF"><Trophy /></el-icon>
        <h2>{{ score }} 分</h2>
      </div>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="完成题目">{{ completedCount }} / {{ totalCount }}</el-descriptions-item>
        <el-descriptions-item label="挑战模式">
          {{ challengeMode === 'random' ? '随机挑战' : '题库挑战' }}
        </el-descriptions-item>
        <el-descriptions-item label="使用时间">{{ formatTime(timeUsed) }}</el-descriptions-item>
        <el-descriptions-item label="准确率">
          <el-tag :type="getAccuracyTagType(accuracy)">
            {{ Math.round(accuracy * 100) }}%
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="评级">
          <el-tag :type="getRankTagType(rank)">
            {{ rank }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
    <template #footer>
      <el-button @click="handleBackToConfig">返回配置</el-button>
      <el-button type="primary" @click="handleRestart">再来一次</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Trophy } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  score: number
  completedCount: number
  totalCount: number
  challengeMode: 'random' | 'questionSet'
  timeUsed: number
  accuracy: number
  rank: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'back-to-config': []
  'restart': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getAccuracyTagType = (accuracy: number) => {
  if (accuracy >= 0.9) return 'success'
  if (accuracy >= 0.7) return 'warning'
  if (accuracy >= 0.5) return 'info'
  return 'danger'
}

const getRankTagType = (rank: string) => {
  const map: Record<string, string> = {
    '优秀': 'success',
    '良好': 'warning',
    '及格': 'info',
    '一般': 'danger'
  }
  return map[rank] || 'info'
}

const handleBackToConfig = () => {
  emit('back-to-config')
  visible.value = false
}

const handleRestart = () => {
  emit('restart')
  visible.value = false
}
</script>

<style scoped lang="scss">
.result-content {
  text-align: center;
  
  .result-score {
    margin-bottom: 24px;
    
    h2 {
      margin: 16px 0 0;
      font-size: 36px;
      color: #6956FF;
    }
  }
}
</style>

