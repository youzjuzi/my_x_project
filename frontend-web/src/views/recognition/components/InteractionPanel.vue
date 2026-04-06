<template>
  <div class="interaction-panel">



    <div class="panel-section sequence-section">
      <div class="candidates-header">
        <span class="label">拼音候选</span>
      </div>
      <div class="candidates-content">
        <!-- 有候选词时展示（识别中也会展示上次确认后的候选词） -->
        <template v-if="shouldShowCandidates">
          <div v-if="displayCandidate" class="candidate-preview">
            {{ displayCandidate }}
          </div>
          <div class="tags-wrapper">
            <el-tag
              v-for="(word, idx) in displayCandidates"
              :key="idx"
              class="candidate-tag"
              :class="{ active: idx === displayCandidateIndex }"
              effect="plain"
              round
              size="small"
            >
              <span class="candidate-index">{{ idx + 1 }}</span>
              {{ word }}
            </el-tag>
          </div>
        </template>
        <!-- 缓冲区为空时等待输入 -->
        <span v-else class="no-candidate">等待输入...</span>
      </div>

      <div class="accepted-words-area">
        <div class="candidates-header">
          <span class="label">已确认词语</span>
        </div>
        <div class="accepted-words-content" :class="{ empty: !pendingWords }">
          {{ pendingWords || '暂无内容' }}
        </div>
      </div>
    </div>

    <div class="panel-section result-section">
      <div class="section-header result-header">
        <div class="header-title">
          <el-icon><ChatLineSquare /></el-icon>
          <span>识别结果</span>
        </div>
        <div class="actions">
          <el-button link type="primary" size="small" @click="$emit('copy')" :disabled="!finalSentence">
            复制
          </el-button>
          <el-button link type="danger" size="small" @click="$emit('clear')" :disabled="!finalSentence">
            清空
          </el-button>
        </div>
      </div>

      <div class="final-result-card" :class="{ empty: !finalSentence }">
        <div class="result-content">
          <div class="result-text" :class="{ placeholder: !finalSentence }">
            {{ finalSentence || '等待识别...' }}
          </div>
        </div>

        <div class="result-toolbar">
          <el-button type="primary" plain size="small" round @click="$emit('speak')" :disabled="!finalSentence">
            <el-icon><Microphone /></el-icon>
            播报
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Aim, ChatLineSquare, Microphone } from '@element-plus/icons-vue'

const props = defineProps({
  gestureStream: {
    type: Array,
    default: () => [],
  },
  hanziCandidate: {
    type: String,
    default: '',
  },
  candidates: {
    type: Array,
    default: () => [],
  },
  candidateIndex: {
    type: Number,
    default: 0,
  },
  pendingWords: {
    type: String,
    default: '',
  },
  finalSentence: {
    type: String,
    default: '',
  },
  // 稳定性进度：0 = 无手势/已完成重置，>0 = 手势确认中
  stabilityProgress: {
    type: Number,
    default: 0,
  },
  // 已确认字符缓冲：有内容才允许展示候选
  cachedBuffer: {
    type: String,
    default: '',
  },
})

defineEmits(['copy', 'clear', 'speak'])

/**
 * 缓存上一次确认完成时的候选词状态
 * 目的：识别进行中（进度条在走）时，仍然显示上次确认后的拼音候选词，
 * 而不是显示"识别中..."。只有当新字符确认完成后，才更新候选词。
 */
const lastConfirmedCandidate = ref('')
const lastConfirmedCandidates = ref([])
const lastConfirmedIndex = ref(0)

/**
 * 监听 stabilityProgress 变化：
 * 当进度条从有值变回零（字符确认完成），将当前候选词快照到缓存中
 */
let wasStabilizing = false
watch(
  () => props.stabilityProgress,
  (newVal) => {
    const isStabilizing = newVal >= 0.05
    // 从识别中 → 归零 = 字符确认完成，此时更新缓存的候选词
    if (wasStabilizing && !isStabilizing) {
      lastConfirmedCandidate.value = props.hanziCandidate || ''
      lastConfirmedCandidates.value = [...(props.candidates || [])]
      lastConfirmedIndex.value = props.candidateIndex || 0
    }
    wasStabilizing = isStabilizing
  }
)

// 当不在识别中（进度条没有走）时，也要实时同步候选词（如 NEXT 切换候选等场景）
watch(
  [() => props.hanziCandidate, () => props.candidates, () => props.candidateIndex],
  ([newCandidate, newCandidates, newIndex]) => {
    if (props.stabilityProgress < 0.05 && props.cachedBuffer?.length > 0) {
      lastConfirmedCandidate.value = newCandidate || ''
      lastConfirmedCandidates.value = [...(newCandidates || [])]
      lastConfirmedIndex.value = newIndex || 0
    }
  }
)

/**
 * 用于模板展示的候选词（优先使用缓存版本）
 * 识别中时展示缓存的候选词，不在识别中时展示实时候选词
 */
const displayCandidate = computed(() => {
  if (props.stabilityProgress >= 0.05) {
    return lastConfirmedCandidate.value
  }
  return props.hanziCandidate || ''
})

const displayCandidates = computed(() => {
  if (props.stabilityProgress >= 0.05) {
    return lastConfirmedCandidates.value
  }
  return props.candidates || []
})

const displayCandidateIndex = computed(() => {
  if (props.stabilityProgress >= 0.05) {
    return lastConfirmedIndex.value
  }
  return props.candidateIndex || 0
})

/**
 * 候选词展示条件（改进版）：
 * - 缓冲区有确认字符（cachedBuffer 非空）
 * - 且有候选词可展示（实时的或缓存的）
 * 识别中时仍然可以展示上次确认后的候选词
 */
const shouldShowCandidates = computed(() => {
  if (!props.cachedBuffer?.length) return false
  // 有实时候选词或有缓存的候选词都可以展示
  return displayCandidates.value.length > 0 || displayCandidate.value
})
</script>

<style lang="scss" scoped>
.interaction-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}

.panel-section {
  padding: 10px 16px 14px;
  border-radius: 22px;
  background: #ffffff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 14px 32px rgba(28, 43, 36, 0.05);
}

.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.header-title {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 15px;
  font-weight: 700;
  color: #18342c;

  .el-icon {
    color: #266c54;
  }
}

.section-meta,
.tip,
.label {
  font-size: 11px;
  color: #76867f;
}

.gesture-stream {
  min-height: 40px; /* 压扁识别流 */
  padding: 8px 12px;
  border-radius: 12px;
  background: #fbfcfb;
  border: 1px solid #e3ece7;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  overflow: hidden;
}

.gesture-bubble {
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  flex-shrink: 0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf4ef;
  color: #226145;
  font-size: 14px;
  font-weight: 700;

  &.latest {
    background: #216d4b;
    color: #fff;
    box-shadow: 0 10px 20px rgba(33, 109, 75, 0.18);
  }
}

.empty-tip {
  font-size: 12px;
  line-height: 1.45;
  color: #879690;
}



.candidates-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.candidates-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.candidates-content {
  padding: 12px 14px;
  border-radius: 12px;
  background: #f4f7f5;
  border: 1px solid #e3ece7;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  /* 固定高度 160px，内容多时可滚动，不会政大布局 */
  height: 160px;
  overflow-y: auto;
}

.candidate-preview {
  padding: 8px 10px;
  border-radius: 8px;
  background: linear-gradient(135deg, #eff7f2 0%, #f9fcfa 100%);
  border: 1px solid #dee9e3;
  color: #17312b;
  font-size: 18px;
  font-weight: 800;
  text-align: center;
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.candidate-tag {
  border-color: rgba(33, 109, 75, 0.12);
  color: #226145;
  background: #f7faf8;
  cursor: default;
  user-select: none;
}

.candidate-tag.active {
  color: #ffffff;
  background: #216d4b;
  border-color: #216d4b;
  box-shadow: 0 10px 18px rgba(33, 109, 75, 0.18);
}

.candidate-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(33, 109, 75, 0.12);
  color: #226145;
  font-size: 10px;
  font-weight: 800;
  margin-right: 4px;
  flex-shrink: 0;
}

.candidate-tag.active .candidate-index {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.no-candidate {
  font-size: 12px;
  color: #97a5a0;
}

.accepted-words-area {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.accepted-words-content {
  padding: 12px 14px;
  border-radius: 12px;
  background: #f4f7f5;
  border: 1px solid #e3ece7;
  color: #17312b;
  font-size: 18px;
  font-weight: 700;
  /* 固定高度，内容多时滚动而不是撑大卡片 */
  height: 52px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  flex-wrap: wrap;

  &.empty {
    color: #8a9893;
    font-size: 14px;
    font-weight: normal;
  }
}

.result-header {
  margin-bottom: 10px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.final-result-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f9fbfa 0%, #ffffff 100%);
  border: 1px solid #e1ebe6;

  &.empty {
    background: linear-gradient(180deg, #f6f8f7 0%, #ffffff 100%);
  }
}

.result-label {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #74857e;
}

.result-text {
  font-size: 20px;
  line-height: 1.55;
  color: #19342d;
  font-weight: 700;

  &.placeholder {
    color: #a4b5ae;
    font-size: 16px;
    font-weight: 400;
  }
}

.result-toolbar {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.2s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes reverseDelete {
  0% {
    opacity: 1;
    transform: translateY(-8px) scale(1.08);
    color: #d74a4a;
  }

  55% {
    opacity: 0.85;
    transform: translateY(2px) scale(0.94);
    color: #f08a5b;
  }

  100% {
    opacity: 0;
    transform: translateY(14px) scale(0.72);
    color: #2f9f68;
  }
}

@media (max-width: 767px) {
  .interaction-panel {
    margin-top: 12px;
  }

  .panel-section {
    padding: 14px;
    border-radius: 18px;
  }

  .section-header,
  .candidates-header,
  .cache-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .result-toolbar {
    justify-content: stretch;
  }

  .result-toolbar :deep(.el-button) {
    width: 100%;
  }
}
</style>
