<template>
  <el-card class="config-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="header-title">🎯 挑战配置</span>
      </div>
    </template>
    
    <div class="config-content">
      <!-- 挑战模式选择 -->
      <div class="config-section">
        <div class="section-title">选择挑战模式</div>
        <el-radio-group :model-value="config.challengeMode" @update:model-value="updateConfig('challengeMode', $event)" size="large" class="mode-group">
          <el-radio-button label="random">
            <el-icon><Refresh /></el-icon>
            <span>随机挑战</span>
          </el-radio-button>
          <el-radio-button label="questionSet">
            <el-icon><Collection /></el-icon>
            <span>选择题库</span>
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 题库选择（仅在选择题库模式时显示） -->
      <div class="config-section" v-if="config.challengeMode === 'questionSet'">
        <div class="section-title">选择题库</div>
        <el-select
          :model-value="config.selectedQuestionSetId"
          @update:model-value="updateConfig('selectedQuestionSetId', $event)"
          placeholder="请选择题库"
          size="large"
          style="width: 100%"
          clearable
        >
          <el-option
            v-for="set in questionSetList"
            :key="set.id"
            :label="set.name"
            :value="set.id"
          >
            <div class="question-set-option">
              <span>{{ set.name }}</span>
              <el-tag 
                size="small" 
                :type="(set.questionCount || 0) >= 5 ? 'info' : 'warning'" 
                style="margin-left: 8px"
              >
                {{ set.questionCount || 0 }} 道题
              </el-tag>
            </div>
          </el-option>
        </el-select>
        <div v-if="selectedQuestionSet" class="question-set-info">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="题库描述">
              {{ selectedQuestionSet.description || '暂无描述' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <!-- 随机选择选项 -->
        <div class="random-option" style="margin-top: 16px">
          <el-checkbox :model-value="config.randomFromQuestionSet" @update:model-value="updateConfig('randomFromQuestionSet', $event)" size="large">
            <span>从题库中随机选择题目</span>
          </el-checkbox>
          <div class="option-tip">
            <el-text type="info" size="small">
              开启后将从题库中随机选择指定数量的题目，否则按顺序选择
            </el-text>
          </div>
        </div>
      </div>

      <!-- 题目类型选择（仅在随机挑战模式显示） -->
      <div class="config-section" v-if="config.challengeMode === 'random'">
        <div class="section-title">选择题目类型</div>
        <el-checkbox-group :model-value="config.selectedTypes" @update:model-value="updateConfig('selectedTypes', $event)" class="type-group">
          <el-checkbox label="1" size="large">
            <el-icon><Document /></el-icon>
            <span>单词</span>
          </el-checkbox>
          <el-checkbox label="2" size="large">
            <el-icon><EditPen /></el-icon>
            <span>中文</span>
          </el-checkbox>
          <el-checkbox label="3" size="large">
            <el-icon><Money /></el-icon>
            <span>数字</span>
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 难度选择（仅在随机挑战模式显示） -->
      <div class="config-section" v-if="config.challengeMode === 'random'">
        <div class="section-title">难度等级（可选）</div>
        <el-checkbox-group :model-value="config.selectedDifficulties" @update:model-value="updateConfig('selectedDifficulties', $event)" class="difficulty-group">
          <el-checkbox label="1" size="large">
            <el-tag type="success" size="small">简单</el-tag>
          </el-checkbox>
          <el-checkbox label="2" size="large">
            <el-tag type="warning" size="small">中等</el-tag>
          </el-checkbox>
          <el-checkbox label="3" size="large">
            <el-tag type="danger" size="small">困难</el-tag>
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 题目数量设置 -->
      <div class="config-section">
        <div class="section-title">题目数量</div>
        <template v-if="config.challengeMode === 'questionSet' && !config.randomFromQuestionSet">
          <div class="question-count-display">
            <el-text type="info" size="large">
              将使用题库中的所有题目（共 {{ selectedQuestionSet?.questionCount || 0 }} 道题）
            </el-text>
          </div>
        </template>
        <template v-else>
          <el-slider
            :model-value="config.questionCount"
            @update:model-value="updateConfig('questionCount', $event)"
            :min="getMinQuestionCount"
            :max="getMaxQuestionCount"
            :step="5"
            show-stops
            show-input
            :show-input-controls="false"
            :disabled="getMaxQuestionCount < 5"
            style="width: 100%"
          />
          <div class="slider-tip" v-if="getMaxQuestionCount < 5">
            <el-text type="warning" size="small">
              所选题库题目数量不足（{{ getMaxQuestionCount }} 道），无法进行挑战
            </el-text>
          </div>
          <div class="slider-tip" v-else>
            {{ config.challengeMode === 'questionSet' ? '将从题库中' : '将' }}选择 {{ config.questionCount }} 道题目进行挑战
          </div>
        </template>
      </div>

      <!-- 挑战时间设置 -->
      <div class="config-section">
        <div class="section-title">挑战时间（秒）</div>
        <el-slider
          :model-value="config.challengeTime"
          @update:model-value="updateConfig('challengeTime', $event)"
          :min="30"
          :max="300"
          :step="10"
          show-stops
          show-input
          :show-input-controls="false"
          style="width: 100%"
        />
        <div class="slider-tip">
          挑战时间：{{ formatTime(config.challengeTime) }}（{{ Math.floor(config.challengeTime / 60) }} 分 {{ config.challengeTime % 60 }} 秒）
        </div>
      </div>

      <!-- 开始按钮 -->
      <div class="config-actions">
        <el-button
          type="primary"
          size="large"
          :icon="VideoPlay"
          :disabled="!canStart"
          @click="$emit('start')"
          style="width: 200px"
        >
          开始挑战
        </el-button>
        <div v-if="!canStart" class="error-tip">
          {{ errorTip }}
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { VideoPlay, Refresh, Collection, Document, EditPen, Money } from '@element-plus/icons-vue'

const props = defineProps<{
  config: {
    challengeMode: 'random' | 'questionSet'
    selectedQuestionSetId: number | null
    randomFromQuestionSet: boolean
    selectedTypes: string[]
    selectedDifficulties: string[]
    questionCount: number
    challengeTime: number
  }
  questionSetList: any[]
}>()

const emit = defineEmits<{
  'update:config': [key: string, value: any]
  'start': []
}>()

const selectedQuestionSet = computed(() => {
  if (!props.config.selectedQuestionSetId) return null
  return props.questionSetList.find(set => set.id === props.config.selectedQuestionSetId)
})

const canStart = computed(() => {
  if (props.config.challengeMode === 'questionSet' && !props.config.selectedQuestionSetId) {
    return false
  }
  if (props.config.challengeMode === 'random' && props.config.selectedTypes.length === 0) {
    return false
  }
  // 检查题库题目数量是否足够
  if (props.config.challengeMode === 'questionSet' && selectedQuestionSet.value) {
    const count = selectedQuestionSet.value.questionCount || 0
    if (count < 5) {
      return false
    }
    // 如果随机选择，检查题目数量是否足够
    if (props.config.randomFromQuestionSet && count < props.config.questionCount) {
      return false
    }
  }
  return true
})

const errorTip = computed(() => {
  if (props.config.challengeMode === 'questionSet' && !props.config.selectedQuestionSetId) {
    return '请选择题库'
  }
  if (props.config.challengeMode === 'random' && props.config.selectedTypes.length === 0) {
    return '请至少选择一种题目类型'
  }
  if (props.config.challengeMode === 'questionSet' && selectedQuestionSet.value) {
    const count = selectedQuestionSet.value.questionCount || 0
    if (count < 5) {
      return '所选题库题目数量不足（至少需要5道题）'
    }
    if (props.config.randomFromQuestionSet && count < props.config.questionCount) {
      return `所选题库只有 ${count} 道题，无法选择 ${props.config.questionCount} 道题`
    }
  }
  return ''
})

// 获取题目数量的最小值
const getMinQuestionCount = computed(() => {
  return 5
})

// 获取题目数量的最大值
const getMaxQuestionCount = computed(() => {
  if (props.config.challengeMode === 'questionSet' && selectedQuestionSet.value) {
    const count = selectedQuestionSet.value.questionCount || 0
    // 如果题库题目数量小于5，返回5（最小值），否则返回实际数量
    return Math.max(count, 5)
  }
  return 50 // 随机模式默认最大值50
})

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const updateConfig = (key: string, value: any) => {
  emit('update:config', key, value)
}

// 监听题库选择和不随机选项的变化，自动设置题目数量
watch(
  () => [props.config.selectedQuestionSetId, props.config.randomFromQuestionSet],
  ([newSetId, newRandom]) => {
    if (props.config.challengeMode === 'questionSet' && newSetId && !newRandom) {
      const set = selectedQuestionSet.value
      if (set && set.questionCount) {
        // 当选择题库且不随机时，自动设置为题库的题目数量
        emit('update:config', 'questionCount', set.questionCount)
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.config-card {
  max-width: 800px;
  margin: 0 auto;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .config-content {
    .config-section {
      margin-bottom: 32px;
      
      .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #606266;
        margin-bottom: 16px;
      }
      
      .mode-group,
      .type-group,
      .difficulty-group {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
      
      .question-set-info {
        margin-top: 12px;
      }
      
      .random-option {
        padding: 12px;
        background: #f5f7fa;
        border-radius: 8px;
        
        .option-tip {
          margin-top: 8px;
          padding-left: 24px;
        }
      }
      
      .question-count-display {
        padding: 16px;
        background: #f0f2f5;
        border-radius: 8px;
        text-align: center;
      }
      
      .slider-tip {
        margin-top: 8px;
        font-size: 12px;
        color: #909399;
        text-align: center;
      }
    }
    
    .config-actions {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      margin-top: 32px;
      
      .error-tip {
        font-size: 12px;
        color: #f56c6c;
      }
    }
  }
}

.question-set-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>

