<template>
  <div class="interaction-panel">
    <div class="panel-section capture-section">
      <div class="section-header">
        <div class="header-title">
          <el-icon><Aim /></el-icon>
          <span>识别过程</span>
        </div>
        <span class="section-meta">{{ gestureStream.length }} 条</span>
      </div>

      <div class="gesture-stream">
        <transition-group name="list">
          <div
            v-for="(item, index) in gestureStream"
            :key="item.id"
            class="gesture-bubble"
            :class="{ latest: index === gestureStream.length - 1 }"
          >
            {{ item.char }}
          </div>
        </transition-group>
        <div v-if="gestureStream.length === 0" class="empty-tip">
          开启摄像头后，识别到的字符会按顺序显示在这里。
        </div>
      </div>
    </div>

    <div class="panel-section sequence-section">
      <div class="section-header">
        <div class="header-title">
          <el-icon><EditPen /></el-icon>
          <span>当前拼写</span>
        </div>
        <span class="section-meta">{{ stabilityPercent }}%</span>
      </div>

      <div class="input-display">
        <div class="pinyin-track" :style="trackStyle"></div>
        <span
          class="pinyin-text"
          :class="{ animating: hasInput }"
          :style="pinyinStyle"
        >
          {{ pinyinBuffer || '等待输入' }}
        </span>
      </div>

      <div class="cache-display">
        <div class="cache-header">
          <span class="label">稳定缓存</span>
          <span class="tip">字符稳定后会追加到这里，删除动作会作用于最后一个字符。</span>
        </div>
        <div class="cache-value" :class="{ empty: !hasCacheContent }">
          <template v-if="hasCacheContent">
            <span
              v-for="(char, index) in cacheChars"
              :key="`cache-${index}-${char}`"
              class="cache-char"
            >
              {{ char }}
            </span>
            <span
              v-if="deletedCacheChar"
              :key="`deleted-${deletedCacheTick}`"
              class="cache-char deleting"
            >
              {{ deletedCacheChar }}
            </span>
          </template>
          <span v-else>暂无已锁定字符</span>
          <div
            v-if="rewindTrackVisible"
            class="cache-delete-track"
            :style="rewindTrackStyle"
          ></div>
        </div>
      </div>

      <div class="candidates-area">
        <div class="candidates-header">
          <span class="label">候选内容</span>
          <span class="tip">后续可在这里扩展候选词或拼写建议。</span>
        </div>
        <div class="tags-wrapper">
          <el-tag
            v-for="(word, idx) in candidates"
            :key="idx"
            class="candidate-tag"
            effect="plain"
            round
            size="small"
            @click="$emit('select-candidate', word)"
          >
            {{ word }}
          </el-tag>
          <span v-if="candidates.length === 0" class="no-candidate">暂无候选内容</span>
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
          <p class="result-label">已确认内容</p>
          <div class="result-text">{{ finalSentence || '已确认的内容会显示在这里。' }}</div>
        </div>

        <div class="result-toolbar">
          <el-button type="primary" plain size="small" round @click="$emit('speak')" :disabled="!finalSentence">
            <el-icon><Microphone /></el-icon>
            朗读结果
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { Aim, ChatLineSquare, EditPen, Microphone } from '@element-plus/icons-vue'

const props = defineProps({
  gestureStream: {
    type: Array,
    default: () => [],
  },
  pinyinBuffer: {
    type: String,
    default: '',
  },
  cachedBuffer: {
    type: String,
    default: '',
  },
  deletedCacheChar: {
    type: String,
    default: '',
  },
  deletedCacheTick: {
    type: Number,
    default: 0,
  },
  deleteProgressTick: {
    type: Number,
    default: 0,
  },
  deleteProgressValue: {
    type: Number,
    default: 0,
  },
  stabilityProgress: {
    type: Number,
    default: 0,
  },
  candidates: {
    type: Array,
    default: () => [],
  },
  finalSentence: {
    type: String,
    default: '',
  },
})

defineEmits(['select-candidate', 'copy', 'clear', 'speak'])

const normalizedProgress = computed(() => {
  const value = Number(props.stabilityProgress || 0)
  return Math.max(0, Math.min(1, value))
})

const stabilityPercent = computed(() => Math.round(normalizedProgress.value * 100))
const hasInput = computed(() => Boolean(props.pinyinBuffer))
const cacheChars = computed(() => Array.from(props.cachedBuffer || ''))
const hasCacheContent = computed(() => cacheChars.value.length > 0 || Boolean(props.deletedCacheChar))
const rewindTrackVisible = ref(false)
const rewindTrackScale = ref(0)
let rewindTrackTimer = null

const pinyinStyle = computed(() => {
  const progress = normalizedProgress.value
  const hue = Math.round(140 - progress * 140)
  const translateY = Math.round(progress * -8)
  const scale = 1 + progress * 0.08
  const glow = 10 + progress * 18
  return {
    color: `hsl(${hue} 72% 42%)`,
    transform: `translateY(${translateY}px) scale(${scale})`,
    textShadow: `0 0 ${glow}px rgba(221, 76, 76, ${0.12 + progress * 0.28})`,
  }
})

const trackStyle = computed(() => ({
  transform: `scaleX(${normalizedProgress.value})`,
}))

const rewindTrackStyle = computed(() => ({
  transform: `scaleX(${rewindTrackScale.value})`,
}))

const clearRewindTrackTimer = () => {
  if (!rewindTrackTimer) {
    return
  }

  window.clearTimeout(rewindTrackTimer)
  rewindTrackTimer = null
}

watch(
  () => props.deleteProgressTick,
  () => {
    clearRewindTrackTimer()

    const progress = Math.max(0, Math.min(1, Number(props.deleteProgressValue || 0)))

    if (progress <= 0) {
      rewindTrackVisible.value = false
      rewindTrackScale.value = 0
      return
    }

    rewindTrackVisible.value = true
    rewindTrackScale.value = progress

    window.requestAnimationFrame(() => {
      rewindTrackScale.value = 0
    })

    rewindTrackTimer = window.setTimeout(() => {
      rewindTrackVisible.value = false
      rewindTrackTimer = null
    }, 1000)
  }
)

onBeforeUnmount(() => {
  clearRewindTrackTimer()
})
</script>

<style lang="scss" scoped>
.interaction-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-section {
  padding: 14px 16px;
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
  min-height: 52px;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
}

.gesture-bubble {
  min-width: 38px;
  height: 38px;
  padding: 0 12px;
  flex-shrink: 0;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf4ef;
  color: #226145;
  font-size: 16px;
  font-weight: 800;

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

.input-display {
  position: relative;
  margin-bottom: 10px;
  padding: 12px 14px;
  border-radius: 16px;
  background: #f4f7f5;
  border: 1px solid #e3ece7;
  overflow: hidden;
}

.pinyin-track {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 4px;
  transform-origin: left center;
  background: linear-gradient(90deg, #2f9f68 0%, #f0b54b 55%, #d74a4a 100%);
  transition: transform 0.12s linear;
}

.pinyin-text {
  position: relative;
  z-index: 1;
  display: inline-block;
  font-size: 18px;
  font-weight: 800;
  color: #17312b;
  transition: color 0.12s linear, transform 0.12s linear, text-shadow 0.12s linear;

  &.animating {
    will-change: transform, color, text-shadow;
  }
}

.cache-display {
  margin-bottom: 10px;
  padding: 10px 12px;
  border-radius: 16px;
  background: #fbfcfb;
  border: 1px solid #e3ece7;
}

.cache-header {
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.cache-value {
  position: relative;
  min-height: 40px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #ecf4ef;
  color: #226145;
  font-size: 18px;
  font-weight: 800;
  word-break: break-all;
  overflow: hidden;

  &.empty {
    color: #8a9893;
    font-weight: 600;
  }
}

.cache-delete-track {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 4px;
  transform-origin: right center;
  background: linear-gradient(90deg, #2f9f68 0%, #f0b54b 55%, #d74a4a 100%);
  transition: transform 1s ease-out;
  box-shadow: 0 0 18px rgba(215, 74, 74, 0.2);
}

.cache-char {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 0.9em;
}

.cache-char.deleting {
  color: #d74a4a;
  text-shadow: 0 0 16px rgba(215, 74, 74, 0.28);
  animation: reverseDelete 1s ease forwards;
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

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.candidate-tag {
  cursor: pointer;
}

.no-candidate {
  font-size: 12px;
  color: #97a5a0;
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
