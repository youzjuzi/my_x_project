<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    width="450px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    class="pause-dialog"
  >
    <template #header>
      <div class="pause-dialog-header">
        <el-icon :size="32" color="#409EFF"><VideoPlay /></el-icon>
        <h3>挑战已暂停</h3>
      </div>
    </template>
    <div class="pause-dialog-content">
      <p class="pause-tip">请选择下一步操作</p>
      <div class="pause-buttons">
        <el-button 
          type="primary" 
          size="large" 
          @click="$emit('resume')"
          class="pause-btn resume-btn"
        >
          <el-icon><VideoPlay /></el-icon>
          <span>继续挑战</span>
        </el-button>
        <el-button 
          type="warning" 
          size="large" 
          @click="$emit('restart')"
          class="pause-btn restart-btn"
        >
          <el-icon><Refresh /></el-icon>
          <span>重新开始</span>
        </el-button>
        <el-button 
          type="info" 
          size="large" 
          @click="$emit('return')"
          class="pause-btn return-btn"
        >
          <el-icon><Back /></el-icon>
          <span>返回配置</span>
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { VideoPlay, Refresh, Back } from '@element-plus/icons-vue'

defineProps<{
  modelValue: boolean
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
  'resume': []
  'restart': []
  'return': []
}>()
</script>

<style scoped lang="scss">
:deep(.pause-dialog) {
  .el-dialog__header {
    padding: 30px 30px 20px 30px;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .el-dialog__body {
    padding: 30px;
  }
}

.pause-dialog-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  
  h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }
}

.pause-dialog-content {
  text-align: center;
  
  .pause-tip {
    font-size: 15px;
    color: #909399;
    margin: 0 0 30px 0;
    line-height: 1.5;
  }
  
  .pause-buttons {
    display: flex;
    flex-direction: column;
    gap: 16px;
    
    .pause-btn {
      width: 100%;
      height: 50px;
      font-size: 16px;
      font-weight: 500;
      border-radius: 8px;
      transition: all 0.3s;
      padding: 0;
      
      :deep(.el-button__inner) {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        height: 100%;
      }
      
      .el-icon {
        font-size: 18px;
        flex-shrink: 0;
      }
      
      span {
        flex-shrink: 0;
      }
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      &.resume-btn {
        background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
        border: none;
        
        &:hover {
          background: linear-gradient(135deg, #66b1ff 0%, #409EFF 100%);
        }
      }
      
      &.restart-btn {
        background: linear-gradient(135deg, #E6A23C 0%, #f0c78a 100%);
        border: none;
        
        &:hover {
          background: linear-gradient(135deg, #f0c78a 0%, #E6A23C 100%);
        }
      }
      
      &.return-btn {
        background: linear-gradient(135deg, #909399 0%, #b3b6bb 100%);
        border: none;
        
        &:hover {
          background: linear-gradient(135deg, #b3b6bb 0%, #909399 100%);
        }
      }
    }
  }
}
</style>

