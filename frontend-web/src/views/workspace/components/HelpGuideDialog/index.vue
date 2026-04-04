<template>
  <el-dialog
    v-model="dialogVisible"
    :width="720"
    :show-close="true"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    class="help-guide-dialog"
    align-center
  >
    <!-- 对话框头部：标题 + 副标题 -->
    <template #header>
      <div class="dialog-header">
        <div class="icon-wrapper">
          <el-icon :size="26"><QuestionFilled /></el-icon>
        </div>
        <div>
          <h3 class="dialog-title">使用指南</h3>
          <p class="dialog-caption">了解如何使用手语识别工作台</p>
        </div>
      </div>
    </template>

    <!-- Tab 切换器 + 内容区 -->
    <div class="dialog-body">
      <!-- 药丸式 Tab 切换器 -->
      <div class="tab-switcher">
        <button
          v-for="tab in HELP_TABS"
          :key="tab.key"
          class="tab-pill"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-emoji">{{ tab.emoji }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- 内容区：固定高度，内部滚动 -->
      <div class="tab-content-area">
        <transition name="tab-fade" mode="out-in">
          <component :is="currentTabComponent" :key="activeTab" />
        </transition>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button class="close-btn" round @click="dialogVisible = false">
          我知道了
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { HELP_TABS } from './helpData'
import TabQuickStart from './tabs/TabQuickStart.vue'
import TabAlphabet from './tabs/TabAlphabet.vue'
import TabCommands from './tabs/TabCommands.vue'
import TabPinyin from './tabs/TabPinyin.vue'
import TabFaq from './tabs/TabFaq.vue'

/* ======================== Props / Emit ======================== */
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

/* ======================== Tab 状态 ======================== */
const activeTab = ref('quickstart')

/** Tab key -> 组件映射，用于动态组件切换 */
const TAB_COMPONENTS = {
  quickstart: markRaw(TabQuickStart),
  alphabet: markRaw(TabAlphabet),
  commands: markRaw(TabCommands),
  pinyin: markRaw(TabPinyin),
  faq: markRaw(TabFaq),
}

const currentTabComponent = computed(() => TAB_COMPONENTS[activeTab.value])
</script>

<style lang="scss" scoped>
/* ======================== 对话框全局样式覆写 ======================== */
:deep(.help-guide-dialog) {
  .el-dialog {
    overflow: hidden;
    border: none;
    border-radius: 26px;
    box-shadow: 0 28px 80px rgba(16, 34, 29, 0.18);
  }

  .el-dialog__header {
    padding: 0;
    margin: 0;
  }

  .el-dialog__body,
  .el-dialog__footer {
    padding: 0;
  }

  /* 关闭按钮样式 */
  .el-dialog__headerbtn {
    top: 20px;
    right: 20px;

    .el-dialog__close {
      color: rgba(255, 255, 255, 0.7);
      font-size: 18px;

      &:hover {
        color: #fff;
      }
    }
  }
}

/* ======================== 头部 ======================== */
.dialog-header {
  padding: 28px 30px 22px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: linear-gradient(135deg, #1d6247 0%, #295c4c 100%);
}

.icon-wrapper {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  color: #fff;
  background: rgba(255, 255, 255, 0.14);
}

.dialog-title {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
}

.dialog-caption {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.78);
}

/* ======================== 对话框主体 ======================== */
.dialog-body {
  padding: 0;
}

/* ======================== Tab 切换器 ======================== */
.tab-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 24px 0;
  overflow-x: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.tab-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(33, 109, 75, 0.12);
  background: #f4f7f5;
  color: #4a6b5f;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.25s ease;
  outline: none;

  .tab-emoji {
    font-size: 14px;
  }

  &:hover {
    background: #eaf3ee;
    border-color: rgba(33, 109, 75, 0.25);
  }

  &.active {
    background: #216d4b;
    color: #fff;
    border-color: #216d4b;
    box-shadow: 0 4px 14px rgba(33, 109, 75, 0.25);
  }
}

/* ======================== 内容区 ======================== */
.tab-content-area {
  height: 460px;
  overflow-y: auto;
  padding: 20px 24px 24px;
  scrollbar-width: thin;
  scrollbar-color: rgba(33, 109, 75, 0.15) transparent;

  &::-webkit-scrollbar {
    width: 5px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(33, 109, 75, 0.15);
    border-radius: 10px;
  }
}

/* Tab 切换动画 */
.tab-fade-enter-active,
.tab-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tab-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.tab-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ======================== 底部 ======================== */
.dialog-footer {
  padding: 10px 30px 26px;
  display: flex;
  justify-content: flex-end;
}

.close-btn {
  min-height: 42px;
  padding: 0 24px;
  border-radius: 999px;
  color: #29443d;
  border: 1px solid #d7e2dc;
  background: #fff;
}
</style>
