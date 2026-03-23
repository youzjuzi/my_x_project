<template>
  <el-dialog
    v-model="dialogVisible"
    :width="420"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    class="exit-confirm-dialog"
    align-center
    @close="handleClose"
  >
    <template #header>
      <div class="dialog-header">
        <div class="icon-wrapper">
          <el-icon :size="24"><SwitchButton /></el-icon>
        </div>
        <div>
          <h3 class="dialog-title">结束本次识别</h3>
          <p class="dialog-caption">离开当前页面前，请确认是否关闭摄像头</p>
        </div>
      </div>
    </template>

    <div class="dialog-content">
      <p class="dialog-message">当前摄像头正在使用中，退出页面后会自动关闭摄像头并结束识别。</p>
      <p class="dialog-subtitle">如果你只是想暂停采集，建议先在页面中点击“关闭摄像头”。</p>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button class="cancel-btn" @click="handleCancel">
          继续留在此页
        </el-button>
        <el-button type="primary" class="confirm-btn" @click="handleConfirm">
          退出并关闭摄像头
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { SwitchButton } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const handleConfirm = () => {
  emit('confirm')
  dialogVisible.value = false
}

const handleCancel = () => {
  emit('cancel')
  dialogVisible.value = false
}

const handleClose = () => {
  emit('cancel')
}
</script>

<style lang="scss" scoped>
:deep(.exit-confirm-dialog) {
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
    color: #fff;
  }

  .dialog-caption {
    margin: 0;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.78);
  }

  .dialog-content {
    padding: 28px 30px 10px;
  }

  .dialog-message {
    margin: 0 0 10px;
    font-size: 16px;
    line-height: 1.7;
    color: #1f332d;
    font-weight: 600;
  }

  .dialog-subtitle {
    margin: 0;
    font-size: 14px;
    line-height: 1.7;
    color: #6d7f78;
  }

  .dialog-footer {
    padding: 20px 30px 30px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }

  .cancel-btn,
  .confirm-btn {
    min-height: 42px;
    padding: 0 18px;
    border-radius: 999px;
  }

  .cancel-btn {
    color: #29443d;
    border: 1px solid #d7e2dc;
    background: #fff;
  }

  .confirm-btn {
    border: none;
    background: linear-gradient(135deg, #1d6247 0%, #2f7f5d 100%);
  }
}
</style>
