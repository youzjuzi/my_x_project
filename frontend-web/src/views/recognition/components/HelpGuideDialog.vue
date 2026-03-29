<template>
  <el-dialog
    v-model="dialogVisible"
    :width="600"
    :show-close="true"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    class="help-guide-dialog"
    align-center
  >
    <template #header>
      <div class="dialog-header">
        <div class="icon-wrapper">
          <el-icon :size="26"><QuestionFilled /></el-icon>
        </div>
        <div>
          <h3 class="dialog-title">使用指南</h3>
          <p class="dialog-caption">了解如何使用手语识别功能</p>
        </div>
      </div>
    </template>

    <!-- 占位内容区域，后续填充手势说明 -->
    <div class="dialog-body">
      <p class="coming-soon">手势指南内容即将上线，敬请期待 🙌</p>
    </div>

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
import { computed } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'

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
</script>

<style lang="scss" scoped>
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

  .dialog-body {
    padding: 36px 30px;
    min-height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .coming-soon {
    margin: 0;
    font-size: 15px;
    color: #7a908a;
    line-height: 1.7;
  }

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
}
</style>
