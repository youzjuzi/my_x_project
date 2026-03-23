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
          开启摄像头后，这里会显示最近识别到的片段。
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
          <span class="tip">本阶段先只做展示，暂不接候选词逻辑</span>
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
          <span v-if="candidates.length === 0" class="no-candidate">暂无候选词</span>
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
          <p class="result-label">输出内容</p>
          <div class="result-text">{{ finalSentence || '识别后的完整文字会显示在这里。' }}</div>
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
import { Aim, ChatLineSquare, EditPen, Microphone } from '@element-plus/icons-vue'

defineProps({
  gestureStream: {
    type: Array,
    default: () => [],
  },
  pinyinBuffer: {
    type: String,
    default: '',
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
  margin-bottom: 10px;
  padding: 12px 14px;
  border-radius: 16px;
  background: #f4f7f5;
  border: 1px solid #e3ece7;
}

.pinyin-text {
  font-size: 18px;
  font-weight: 700;
  color: #17312b;
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

@media (max-width: 767px) {
  .interaction-panel {
    margin-top: 12px;
  }

  .panel-section {
    padding: 14px;
    border-radius: 18px;
  }

  .section-header,
  .candidates-header {
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
