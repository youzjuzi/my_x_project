<template>
  <div class="interaction-panel">
    <!-- 实时捕捉流 -->
    <div class="panel-section">
      <div class="section-header">
        <el-icon><Aim /></el-icon> 实时捕捉流
      </div>
      <div class="gesture-stream">
        <transition-group name="list">
          <div
            v-for="(item, index) in gestureStream"
            :key="item.id"
            class="gesture-bubble"
            :class="{ 'latest': index === gestureStream.length - 1 }"
          >
            {{ item.char }}
          </div>
        </transition-group>
        <div v-if="gestureStream.length === 0" class="empty-tip">等待手势输入...</div>
      </div>
    </div>

    <!-- 拼音序列 -->
    <div class="panel-section">
      <div class="section-header">
        <el-icon><EditPen /></el-icon> 拼音序列
      </div>
      <div class="input-display">
        <span class="pinyin-text">{{ pinyinBuffer || '_' }}</span>
        <span class="cursor blink">|</span>
      </div>
      <div class="candidates-area">
        <div class="label">AI 联想:</div>
        <div class="tags-wrapper">
          <el-tag
            v-for="(word, idx) in candidates"
            :key="idx"
            class="candidate-tag"
            effect="light"
            @click="$emit('select-candidate', word)"
          >
            {{ word }}
          </el-tag>
          <span v-if="candidates.length === 0" class="no-candidate">...</span>
        </div>
      </div>
    </div>

    <!-- 翻译结果 -->
    <div class="panel-section result-section">
      <div class="section-header">
        <el-icon><ChatLineSquare /></el-icon> 翻译结果
        <div class="actions">
          <el-button
            link
            type="primary"
            icon="CopyDocument"
            @click="$emit('copy')"
            :disabled="!finalSentence"
          ></el-button>
          <el-button
            link
            type="danger"
            icon="Delete"
            @click="$emit('clear')"
            :disabled="!finalSentence"
          ></el-button>
        </div>
      </div>
      <div class="final-result-card">
        <div class="result-text">{{ finalSentence || '翻译内容将显示在这里...' }}</div>
        <div class="speak-btn" @click="$emit('speak')" v-if="finalSentence">
          <el-icon><Microphone /></el-icon> 朗读
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Aim, EditPen, ChatLineSquare, CopyDocument, Delete, Microphone } from '@element-plus/icons-vue'

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
  height: 640px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-section {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    font-weight: 600;
    color: #606266;
    margin-bottom: 15px;

    .el-icon {
      margin-right: 6px;
      font-size: 16px;
      color: #6956FF;
    }

    .actions {
      display: flex;
      gap: 4px;
    }
  }

  &.result-section {
    flex: 1;
    display: flex;
    flex-direction: column;

    .final-result-card {
      flex: 1;
    }
  }
}

.gesture-stream {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  min-height: 50px;
  align-items: center;
  padding-bottom: 5px;

  .gesture-bubble {
    width: 40px;
    height: 40px;
    background: #F2F0FF;
    color: #6956FF;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    flex-shrink: 0;
    transition: all 0.3s;

    &.latest {
      background: #6956FF;
      color: #fff;
      transform: scale(1.1);
      box-shadow: 0 4px 10px rgba(105, 86, 255, 0.3);
    }
  }

  .empty-tip {
    color: #C0C4CC;
    font-size: 13px;
    font-style: italic;
  }
}

.input-display {
  background: #f9fafc;
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #6956FF;
  font-family: 'Consolas', monospace;
  font-size: 18px;
  color: #303133;
  margin-bottom: 15px;

  .cursor {
    color: #6956FF;
    animation: blink 1s infinite;
  }
}

.candidates-area {
  display: flex;
  align-items: center;
  gap: 10px;

  .label {
    font-size: 12px;
    color: #909399;
  }

  .tags-wrapper {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .candidate-tag {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-2px);
      border-color: #6956FF;
      color: #6956FF;
    }
  }

  .no-candidate {
    color: #E4E7ED;
  }
}

.final-result-card {
  background: linear-gradient(180deg, #F9FAFC 0%, #fff 100%);
  border: 1px solid #EBEEF5;
  border-radius: 12px;
  padding: 20px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  .result-text {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    line-height: 1.6;
  }

  .speak-btn {
    align-self: flex-end;
    background: #fff;
    color: #606266;
    border: 1px solid #DCDFE6;
    padding: 6px 15px;
    border-radius: 20px;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all 0.2s;

    &:hover {
      border-color: #6956FF;
      color: #6956FF;
    }
  }
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>

