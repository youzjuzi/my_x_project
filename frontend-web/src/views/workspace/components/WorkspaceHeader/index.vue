<template>
  <HelpGuideDialog v-model="helpVisible" />

  <!-- 控制栏：工作台标识在左，帮助和模式切换在右 -->
  <div class="control-bar">
    <!-- 左侧：工作台当前模块标识（带绿点表示当前页），点击跳首页 -->
    <div class="workspace-chip" role="button" tabindex="0" aria-label="返回首页" @click="goHome" @keydown.enter="goHome">
      <span class="chip-dot" />
      工作台
    </div>

    <!-- 竖分隔线 -->
    <div class="bar-divider" />

    <!-- 右侧：功能按键区（帮助 + 模式切换） -->
    <div class="bar-actions">
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
        <!-- hover 时旋转 180° 提示可切换 -->
        <div class="mode-toggle-icon">
          <el-icon><Switch /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Switch, QuestionFilled } from '@element-plus/icons-vue'
import HelpGuideDialog from '../../../recognition/components/HelpGuideDialog.vue'

const router = useRouter()
const helpVisible = ref(false)

/* 点击工作台带回后台首页 */
const goHome = () => router.push('/')

const props = defineProps({
  selectedMode: {
    type: String,
    default: 'letters',
  },
})

const emit = defineEmits(['change-mode'])

const handleModeToggle = () => {
  const next = props.selectedMode === 'digits' ? 'letters' : 'digits'
  emit('change-mode', next)
}
</script>

<style scoped lang="scss">
/* 控制栏主容器（宽度由右列决定，左边缘自然与拼音/识别结果卡片对齐） */
.control-bar {
  padding: 10px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(18, 42, 35, 0.1);
  box-shadow:
    0 2px 4px rgba(28, 43, 36, 0.04),
    0 8px 24px rgba(28, 43, 36, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  overflow: hidden;
  /* 极窄时允许换行，防止按钮溢出 */
  flex-wrap: wrap;
}

/* 左侧：工作台标识 chip（绿点 + 背景带绿意，指示当前模块） */
.workspace-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(237, 247, 242, 0.9) 0%, rgba(232, 244, 239, 0.9) 100%);
  border: 1px solid rgba(45, 105, 80, 0.18);
  color: #1a3d30;
  font-size: 13px;
  font-weight: 700;
  user-select: none;
  white-space: nowrap;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(33, 109, 75, 0.12);
    border-color: rgba(45, 105, 80, 0.35);
  }

  &:active {
    transform: translateY(0);
  }
}

/* 当前页指示绿点 */
.chip-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #25a165;
  box-shadow: 0 0 0 3px rgba(37, 161, 101, 0.18);
  flex-shrink: 0;
  animation: dot-pulse 2.4s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(37, 161, 101, 0.18); }
  50%       { box-shadow: 0 0 0 5px rgba(37, 161, 101, 0.08); }
}

/* 竖分隔线 */
.bar-divider {
  width: 1px;
  height: 20px;
  background: linear-gradient(to bottom, transparent, rgba(45, 105, 80, 0.15), transparent);
  flex-shrink: 0;
}

/* 右侧：帮助 + 模式按钮区 */
.bar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.help-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #edf7f2 0%, #e8f4ef 100%);
  border: 1px solid rgba(33, 109, 75, 0.15);
  color: #216d4b;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
  white-space: nowrap; /* 禁止折行 */
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  .el-icon {
    font-size: 16px;
    flex-shrink: 0;
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
  gap: 6px;
  padding: 6px 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #edf7f2 0%, #e8f4ef 100%);
  border: 1px solid rgba(33, 109, 75, 0.15);
  cursor: pointer;
  user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(33, 109, 75, 0.12);
    border-color: rgba(33, 109, 75, 0.35);

    /* hover 时箭头旋转 180°，提示「可切换」 */
    .mode-toggle-icon {
      transform: rotate(180deg);
    }
  }

  &:active {
    transform: translateY(0);
  }
}

.mode-toggle-icon {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: rgba(33, 109, 75, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #216d4b;
  font-size: 13px;
  flex-shrink: 0;
  /* 旋转动画过渡 */
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.mode-icon-block {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #216d4b;
  color: #fff;
  font-size: 11px;
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
  font-size: 9px;
  color: #688178;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  white-space: nowrap;
}

.mode-name {
  font-size: 13px;
  font-weight: 800;
  color: #16312a;
  line-height: 1.2;
  white-space: nowrap;
}

@media (max-width: 767px) {
  .control-bar {
    padding: 14px;
    border-radius: 18px;
  }

  .mode-display {
    width: 100%;
  }
}
</style>
