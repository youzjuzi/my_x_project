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
        <h3 class="dialog-title">结束识别</h3>
      </div>
    </template>

    <div class="dialog-content">
      <p class="dialog-message">识别服务正在运行，退出将停止摄像头</p>
      <p class="dialog-subtitle">确定要退出识别页面吗？</p>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button class="cancel-btn" @click="handleCancel">
          取消
        </el-button>
        <el-button type="primary" class="confirm-btn" @click="handleConfirm">
          确定退出
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
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(105, 86, 255, 0.15);
    border: none;
  }

  .el-dialog__header {
    padding: 0;
    margin-bottom: 0;
  }

  .el-dialog__body {
    padding: 0;
  }

  .el-dialog__footer {
    padding: 0;
    border-top: none;
  }

  .dialog-header {
    background: linear-gradient(135deg, #6956FF 0%, #5340E8 100%);
    padding: 32px 32px 24px;
    display: flex;
    align-items: center;
    gap: 16px;

    .icon-wrapper {
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
    }

    .dialog-title {
      margin: 0;
      font-size: 20px;
      font-weight: 700;
      color: #fff;
      letter-spacing: 0.5px;
    }
  }

  .dialog-content {
    padding: 32px;
    text-align: center;

    .dialog-message {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 500;
      color: #303133;
      line-height: 1.6;
    }

    .dialog-subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
      line-height: 1.5;
    }
  }

  .dialog-footer {
    padding: 20px 32px 32px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .cancel-btn {
      padding: 10px 24px;
      border-radius: 10px;
      font-weight: 500;
      border: 1px solid #e4e7ed;
      color: #606266;
      background: #fff;
      transition: all 0.3s;

      &:hover {
        border-color: #c0c4cc;
        background: #f5f7fa;
        color: #303133;
      }
    }

    .confirm-btn {
      padding: 10px 32px;
      border-radius: 10px;
      font-weight: 600;
      background: linear-gradient(135deg, #6956FF 0%, #5340E8 100%);
      border: none;
      color: #fff;
      box-shadow: 0 4px 12px rgba(105, 86, 255, 0.3);
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(105, 86, 255, 0.4);
        background: linear-gradient(135deg, #7c6aff 0%, #6250f0 100%);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}
</style>

