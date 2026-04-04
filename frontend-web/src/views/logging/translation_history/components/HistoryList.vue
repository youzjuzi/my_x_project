<template>
  <div class="record-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-skeleton">
      <div v-for="i in 5" :key="i" class="skeleton-card">
        <div class="skeleton-line wide"></div>
        <div class="skeleton-line narrow"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="historyList.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <h3>暂无识别记录</h3>
      <p>去工作台开始手语识别，记录会自动出现在这里</p>
      <el-button type="primary" round @click="$router.push('/workspace')">
        前往工作台
      </el-button>
    </div>

    <!-- 记录列表 -->
    <template v-else>
      <div v-for="group in historyList" :key="group.date" class="date-group">
        <div class="group-header">
          <span class="group-date">{{ group.dateLabel }}</span>
          <span class="group-count">{{ group.items.length }} 条</span>
        </div>

        <div
          v-for="(item, idx) in group.items"
          :key="idx"
          class="record-card"
          :class="{ 'ai-polished': item.isAiPolished }"
        >
          <div class="card-time">
            <span class="time-text">{{ formatTime(item.createTime) }}</span>
            <span v-if="item.isAiPolished" class="ai-tag">
              <el-icon :size="12"><MagicStick /></el-icon>
              AI润色
            </span>
          </div>

          <div class="card-body">
            <div class="input-section">
              <div class="section-label">手语输入</div>
              <div class="word-tags">
                <span
                  v-for="(word, wi) in parseWords(item.originalWords)"
                  :key="wi"
                  class="word-tag"
                >{{ word }}</span>
              </div>
            </div>

            <div class="arrow-section">
              <div class="arrow-line"></div>
              <div class="arrow-head">
                <el-icon :size="16"><Right /></el-icon>
              </div>
            </div>

            <div class="result-section">
              <div class="section-label">翻译结果</div>
              <div class="result-text">{{ item.resultSentence }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination-wrap" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="internalPageNo"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="handlePageChange"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Right, MagicStick } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps<{
  historyList: { date: string; dateLabel: string; items: any[] }[]
  loading: boolean
  total: number
  pageNo: number
  pageSize: number
}>()

const emit = defineEmits<{
  (e: 'update:pageNo', val: number): void
  (e: 'pageChange'): void
}>()

const internalPageNo = computed({
  get: () => props.pageNo,
  set: (val) => emit('update:pageNo', val)
})

const handlePageChange = () => {
  emit('pageChange')
}

const parseWords = (rawValue: string) => {
  const text = String(rawValue ?? '').trim()
  if (!text) return []
  try {
    const parsed = JSON.parse(text)
    if (Array.isArray(parsed)) return parsed.map(item => String(item))
    return [String(parsed)]
  } catch {
    return [text]
  }
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const match = timeStr.match(/(\d{2}):(\d{2})/)
  return match ? `${match[1]}:${match[2]}` : timeStr
}
</script>

<style scoped lang="scss">
.record-list {
  flex: 1;
  min-width: 0;
}

.date-group {
  margin-bottom: 24px;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;

  .group-date {
    font-size: 15px;
    font-weight: 700;
    color: #1f2937;
  }

  .group-count {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 500;
  }
}

.record-card {
  background: #fff;
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transform: translateY(-1px);
  }

  &.ai-polished {
    border-left: 3px solid #10b981;
  }
}

.card-time {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;

  .time-text {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
  }

  .ai-tag {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 10px;
    font-weight: 600;
    color: #10b981;
    background: rgba(16, 185, 129, 0.08);
    padding: 2px 8px;
    border-radius: 999px;
  }
}

.card-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.input-section, .result-section {
  flex: 1;
  min-width: 0;
}

.section-label {
  font-size: 10px;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 6px;
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;

  .word-tag {
    display: inline-block;
    padding: 4px 12px;
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    color: #2563eb;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
}

.arrow-section {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  color: #d1d5db;

  .arrow-line {
    width: 24px;
    height: 1px;
    background: #e5e7eb;
  }

  .arrow-head {
    display: flex;
    color: #9ca3af;
  }
}

.result-text {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.4;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 24px 0 8px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;

  .empty-icon {
    font-size: 56px;
    margin-bottom: 16px;
  }

  h3 {
    margin: 0 0 8px;
    font-size: 18px;
    font-weight: 600;
    color: #374151;
  }

  p {
    margin: 0 0 20px;
    font-size: 14px;
    color: #9ca3af;
  }
}

.loading-skeleton {
  .skeleton-card {
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 10px;
  }

  .skeleton-line {
    height: 16px;
    border-radius: 8px;
    background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    margin-bottom: 10px;

    &.wide { width: 80%; }
    &.narrow { width: 40%; }
  }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@media (max-width: 768px) {
  .card-body {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .arrow-section {
    transform: rotate(90deg);
    align-self: center;
  }
}
</style>
