<template>
  <div class="interaction-panel">
    <div class="panel-section capture-section">
      <div class="section-header">
        <div class="header-title">
          <el-icon><Aim /></el-icon>
          <span>识别过程</span>
        </div>
        <span class="section-meta">{{ gestureStream.length }} 条记录</span>
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
          开启摄像头后，这里会显示实时识别到的字母序列。
        </div>
      </div>
    </div>

    <div class="panel-section sequence-section">
      <div class="section-header">
        <div class="header-title">
          <el-icon><EditPen /></el-icon>
          <span>当前拼写</span>
        </div>
      </div>

      <div class="input-display">
        <span class="pinyin-text">{{ pinyinBuffer || '等待输入' }}</span>
      </div>

      <div class="candidates-area">
        <div class="candidates-header">
          <span class="label">候选词</span>
          <span class="tip">点击任一候选词可加入结果</span>
        </div>
        <div class="tags-wrapper">
          <el-tag
            v-for="(word, idx) in candidates"
            :key="idx"
            class="candidate-tag"
            effect="plain"
            round
            @click="$emit('select-candidate', word)"
          >
            {{ word }}
          </el-tag>
          <span v-if="candidates.length === 0" class="no-candidate">当前暂无候选词</span>
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
          <el-button
            link
            type="primary"
            @click="$emit('copy')"
            :disabled="!finalSentence"
          >
            复制
          </el-button>
          <el-button
            link
            type="danger"
            @click="$emit('clear')"
            :disabled="!finalSentence"
          >
            清空
          </el-button>
        </div>
      </div>

      <div class="final-result-card" :class="{ empty: !finalSentence }">
        <div class="result-content">
          <p class="result-label">输出内容</p>
          <div class="result-text">{{ finalSentence || '识别后的文字会显示在这里，方便直接查看、复制或朗读。' }}</div>
        </div>

        <div class="result-toolbar">
          <el-button
            type="primary"
            plain
            round
            @click="$emit('speak')"
            :disabled="!finalSentence"
          >
            <el-icon><Microphone /></el-icon>
            朗读结果
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Aim, EditPen, ChatLineSquare, Microphone } from '@element-plus/icons-vue'

defineProps({
  gestureStream: {
    type: Array,
    default: () => []
  },
  pinyinBuffer: {
    type: String,
    default: ''
  },
  candidates: {
    type: Array,
    default: () => []
  },
  finalSentence: {
    type: String,
    default: ''
  }
})

defineEmits(['select-candidate', 'copy', 'clear', 'speak'])
</script>

<style lang="scss" scoped>
.interaction-panel {
  height: 680px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.panel-section {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 18px 40px rgba(28, 43, 36, 0.06);
}

.capture-section,
.sequence-section {
  flex-shrink: 0;
}

.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-title {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #17312b;

  .el-icon {
    color: #23654b;
  }
}

.section-meta,
.tip,
.label {
  font-size: 12px;
  color: #6f817a;
}

.gesture-stream {
  min-height: 72px;
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-x: auto;
}

.gesture-bubble {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf4ef;
  color: #225d46;
  font-size: 18px;
  font-weight: 800;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease;

  &.latest {
    background: #1f6c4a;
    color: #fff;
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(31, 108, 74, 0.22);
  }
}

.empty-tip {
  font-size: 13px;
  line-height: 1.6;
  color: #8c9a95;
}

.input-display {
  margin-bottom: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: #f4f7f5;
  border: 1px solid #e2ebe6;
}

.pinyin-text {
  font-size: 22px;
  font-weight: 700;
  color: #17312b;
  letter-spacing: 0.03em;
}

.candidates-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.candidates-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.candidate-tag {
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, color 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    color: #1f6c4a;
    border-color: #1f6c4a;
  }
}

.no-candidate {
  font-size: 13px;
  color: #98a5a0;
}

.result-header {
  margin-bottom: 14px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.final-result-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px;
  border-radius: 24px;
  background:
    linear-gradient(180deg, #f8fbf9 0%, #ffffff 100%);
  border: 1px solid #e1ebe5;

  &.empty {
    background:
      linear-gradient(180deg, #f6f8f7 0%, #ffffff 100%);
  }
}

.result-label {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #72837c;
}

.result-text {
  font-size: 24px;
  line-height: 1.7;
  color: #18332c;
  font-weight: 700;
}

.result-toolbar {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.25s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

@media (max-width: 1200px) {
  .interaction-panel {
    height: 640px;
  }
}

@media (max-width: 767px) {
  .interaction-panel {
    height: auto;
    margin-top: 16px;
  }

  .panel-section {
    padding: 18px;
    border-radius: 20px;
  }

  .section-header,
  .candidates-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .final-result-card {
    padding: 20px;
    border-radius: 20px;
  }

  .result-text {
    font-size: 20px;
  }

  .result-toolbar {
    justify-content: stretch;
  }

  .result-toolbar :deep(.el-button) {
    width: 100%;
  }
}
</style>
