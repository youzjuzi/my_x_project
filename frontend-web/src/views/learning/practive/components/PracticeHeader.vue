<template>
  <div class="top-bar">
    <div class="back-btn" @click="$emit('back')" aria-label="返回">
      <el-icon><ArrowLeft /></el-icon>
    </div>

    <div class="char-selector">
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
        <button
          class="mode-tab"
          :class="{ active: activeMode === 'commands' }"
          @click="$emit('switch-mode', 'commands')"
        >功能手势</button>
      </div>

      <div class="char-list">
        <button
          v-for="item in currentCharList"
          :key="item.value"
          class="char-chip"
          :class="{ active: targetChar === item.value, passed: isCharPassed(item.value, activeMode), wide: item.label.length > 2 }"
          @click="$emit('select-char', item.value)"
        >
          {{ item.label }}
          <span v-if="isCharPassed(item.value, activeMode)" class="passed-dot" aria-label="已掌握" />
        </button>
      </div>

      <div class="camera-badge">
        <span class="status-dot" :class="{ active: isCameraActive }"></span>
        {{ isCameraActive ? '识别中' : '等待开启' }}
      </div>

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
  activeMode:      { type: String, default: 'letters' },
  targetChar:      { type: String, default: 'A' },
  currentCharList: { type: Array, default: () => [] },
  isCameraActive:  { type: Boolean, default: false },
  isCharPassed:    { type: Function, default: () => false },
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
  position: relative;
  min-width: 34px;
  height: 34px;
  padding: 0 10px;
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

  &.passed:not(.active) {
    background: #dcf0e6;
    border-color: rgba(34, 197, 94, 0.35);
    color: #166534;
  }

  &.wide {
    min-width: 64px;
    font-size: 13px;
  }
}

.passed-dot {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.25);
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
