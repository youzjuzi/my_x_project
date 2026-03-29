<template>
  <div class="top-bar">
    <!-- 返回按钮 -->
    <div class="back-btn" @click="$emit('back')" aria-label="返回">
      <el-icon><ArrowLeft /></el-icon>
    </div>

    <div class="char-selector">
      <!-- 模式切换：字母 / 数字 -->
      <div class="mode-tabs">
        <button
          class="mode-tab"
          :class="{ active: activeMode === 'letters' }"
          @click="$emit('switch-mode', 'letters')"
        >字母</button>
        <button
          class="mode-tab"
          :class="{ active: activeMode === 'numbers' }"
          @click="$emit('switch-mode', 'numbers')"
        >数字</button>
      </div>

      <!-- 字符选择列表 -->
      <div class="char-list">
        <button
          v-for="char in currentCharList"
          :key="char"
          class="char-chip"
          :class="{ active: targetChar === char }"
          @click="$emit('select-char', char)"
        >{{ char }}</button>
      </div>

      <!-- 摄像头状态徽章 -->
      <div class="camera-badge">
        <span class="status-dot" :class="{ active: isCameraActive }"></span>
        {{ isCameraActive ? '识别中' : '等待开启' }}
      </div>

      <!-- 开启/关闭按钮 -->
      <el-button
        v-if="!isCameraActive"
        type="primary"
        class="camera-btn"
        round
        @click="$emit('start-camera')"
      >开启摄像头</el-button>
      <el-button
        v-else
        type="danger"
        plain
        class="camera-btn"
        round
        @click="$emit('stop-camera')"
      >关闭摄像头</el-button>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'

defineProps({
  activeMode:      { type: String,  default: 'letters' },
  targetChar:      { type: String,  default: 'A' },
  currentCharList: { type: Array,   default: () => [] },
  isCameraActive:  { type: Boolean, default: false },
})

defineEmits(['back', 'switch-mode', 'select-char', 'start-camera', 'stop-camera'])
</script>

<style scoped lang="scss">
.top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 6px 18px rgba(28, 43, 36, 0.05);
  flex-shrink: 0;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #edf4f1;
  color: #22463b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s;

  &:hover { background: #daeee5; }
}

.char-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.mode-tabs {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.mode-tab {
  padding: 6px 14px;
  border-radius: 10px;
  border: 1px solid rgba(33, 109, 75, 0.15);
  background: #f4f8f6;
  color: #4d7066;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s;

  &.active {
    background: #216d4b;
    color: #fff;
    border-color: #216d4b;
  }
}

.char-list {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  flex: 1;
  padding-bottom: 2px;
  &::-webkit-scrollbar { height: 0; }
}

.char-chip {
  min-width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid rgba(33, 109, 75, 0.12);
  background: #f4f8f6;
  color: #254d3e;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;

  &:hover {
    background: #daeee5;
    border-color: rgba(33, 109, 75, 0.3);
  }

  &.active {
    background: #216d4b;
    color: #fff;
    border-color: #216d4b;
    box-shadow: 0 4px 12px rgba(33, 109, 75, 0.25);
  }
}

.camera-badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 12px;
  border-radius: 999px;
  background: #eef5f1;
  color: #24463d;
  font-size: 12px;
  font-weight: 700;

  .status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #c7d0cc;
    transition: all 0.3s;

    &.active {
      background: #25a165;
      box-shadow: 0 0 0 3px rgba(37, 161, 101, 0.2);
    }
  }
}

.camera-btn {
  flex-shrink: 0;
  min-width: 110px;
  height: 34px;
}
</style>
