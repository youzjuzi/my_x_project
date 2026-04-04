<template>
  <HelpGuideDialog v-model="helpVisible" />
  <div class="hero-row">
    <div class="nav-header">
      <div class="back-capsule" @click="$emit('back')" aria-label="返回">
        <div class="icon-wrap">
          <el-icon><ArrowLeft /></el-icon>
        </div>
      </div>
    </div>

    <div class="page-intro">
      <div class="intro-main">
        <h1>AI 实时手语解析舱 · 让每次挥手都有回音</h1>

      </div>

      <div class="intro-actions">
        <!-- 帮助引导入口按钮 -->
        <div class="help-btn" @click="helpVisible = true" role="button" tabindex="0" aria-label="使用帮助">
          <el-icon><QuestionFilled /></el-icon>
          <span>帮助</span>
        </div>
        <div class="mode-display" @click="handleModeToggle" role="button" tabindex="0" aria-label="切换识别模式">
          <div class="mode-icon-block">{{ selectedMode === 'digits' ? '123' : 'Aa' }}</div>
          <div class="mode-info">
            <span class="mode-hint">点击切换模式</span>
            <span class="mode-name">{{ selectedMode === 'digits' ? '数字识别' : '字母识别' }}</span>
          </div>
          <div class="mode-toggle-icon">
            <el-icon><Switch /></el-icon>
          </div>
        </div>

        <div class="intro-badge">
          <span class="status-dot" :class="{ active: isCameraActive }"></span>
          {{ isCameraActive ? connectionText : '等待开启摄像头' }}
        </div>

        <el-button
          v-if="!isCameraActive"
          type="primary"
          class="hero-action"
          @click="$emit('start-camera')"
        >
          开启摄像头
        </el-button>

        <el-button
          v-else
          type="danger"
          plain
          class="hero-action"
          @click="$emit('stop-camera')"
        >
          关闭摄像头
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ArrowLeft, Switch, QuestionFilled } from '@element-plus/icons-vue'
import HelpGuideDialog from '../../workspace/components/HelpGuideDialog/index.vue'

const helpVisible = ref(false)

const props = defineProps({
  selectedMode: {
    type: String,
    default: 'letters',
  },
  isCameraActive: {
    type: Boolean,
    default: false,
  },
  connectionText: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['back', 'start-camera', 'stop-camera', 'change-mode'])

const handleModeToggle = () => {
  const next = props.selectedMode === 'digits' ? 'letters' : 'digits'
  emit('change-mode', next)
}
</script>

<style scoped lang="scss">
.hero-row {
  display: flex;
  align-items: stretch;
  gap: 10px;
  margin-bottom: 10px;
}

.nav-header {
  flex-shrink: 0;
}

.back-capsule {
  height: 100%;
  min-width: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(26, 64, 50, 0.08);
  box-shadow: 0 6px 18px rgba(28, 43, 36, 0.05);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  user-select: none;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(28, 43, 36, 0.1);
  }
}

.icon-wrap {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #edf4f1;
  color: #22463b;
  font-size: 15px;
}

.page-intro {
  flex: 1;
  padding: 12px 16px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 10px 26px rgba(28, 43, 36, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.intro-main {
  min-width: 0;
}

.intro-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.help-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #edf7f2 0%, #e8f4ef 100%);
  border: 1px solid rgba(33, 109, 75, 0.15);
  color: #216d4b;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  .el-icon {
    font-size: 18px;
  }

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(33, 109, 75, 0.12);
    border-color: rgba(33, 109, 75, 0.35);
  }

  &:active {
    transform: translateY(0);
  }
}

.mode-display {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, #edf7f2 0%, #e8f4ef 100%);
  border: 1px solid rgba(33, 109, 75, 0.15);
  cursor: pointer;
  user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(33, 109, 75, 0.12);
    border-color: rgba(33, 109, 75, 0.35);
  }

  &:active {
    transform: translateY(0);
  }
}

.mode-toggle-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(33, 109, 75, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #216d4b;
  font-size: 14px;
  flex-shrink: 0;
}

.mode-icon-block {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #216d4b;
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: -0.03em;
  flex-shrink: 0;
}

.mode-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mode-hint {
  font-size: 10px;
  color: #688178;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.mode-name {
  font-size: 18px;
  font-weight: 800;
  color: #16312a;
  line-height: 1.1;
}

.eyebrow {
  margin: 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #688178;
}

.page-intro h1 {
  margin: 4px 0;
  font-size: 24px;
  line-height: 1.15;
  color: #16312a;
}

.description {
  margin: 0;
  max-width: 760px;
  font-size: 13px;
  line-height: 1.5;
  color: #5d7169;
}

.intro-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  background: #eef5f1;
  color: #24463d;
  font-size: 12px;
  font-weight: 700;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c7d0cc;

  &.active {
    background: #25a165;
    box-shadow: 0 0 0 4px rgba(37, 161, 101, 0.12);
  }
}

.hero-action {
  min-width: 124px;
  height: 36px;
  border-radius: 999px;
}

@media (max-width: 992px) {
  .hero-row {
    flex-direction: column;
  }

  .page-intro {
    flex-direction: column;
    align-items: stretch;
  }

  .intro-actions {
    width: 100%;
    justify-content: space-between;
  }

  .page-intro h1 {
    font-size: 22px;
  }
}

@media (max-width: 767px) {
  .nav-header {
    align-self: flex-start;
  }

  .page-intro {
    padding: 14px;
    border-radius: 18px;
  }

  .page-intro h1 {
    font-size: 20px;
  }

  .description {
    font-size: 13px;
  }

  .intro-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .mode-display {
    width: 100%;
  }

  .hero-action {
    width: 100%;
  }

  .intro-badge {
    justify-content: center;
  }
}
</style>
