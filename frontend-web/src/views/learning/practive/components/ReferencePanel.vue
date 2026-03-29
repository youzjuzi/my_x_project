<template>
  <div class="reference-panel">
    <div class="panel-label">标准手势</div>
    <div class="char-display">{{ targetChar }}</div>

    <div class="reference-image-wrap">
      <el-image
        :src="referenceImageUrl"
        fit="contain"
        class="reference-image"
      >
        <template #error>
          <div class="image-error">
            <el-icon :size="40"><Picture /></el-icon>
            <p>图片加载中...</p>
          </div>
        </template>
      </el-image>
    </div>

    <p class="reference-hint">请参照图片做出对应手势，对准摄像头保持稳定</p>
  </div>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'

defineProps({
  targetChar: { type: String, default: 'A' },
  referenceImageUrl: { type: String, default: '' },
})
</script>

<style scoped lang="scss">
.reference-panel {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 20px 16px;
  border-radius: 22px;
  background: #fff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 14px 32px rgba(28, 43, 36, 0.06);
  gap: 10px;
}

.panel-label {
  padding: 4px 12px;
  border-radius: 999px;
  background: #edf4f0;
  color: #245c42;
  font-size: 12px;
  font-weight: 600;
  align-self: flex-start;
}

.char-display {
  font-size: 80px;
  font-weight: 900;
  color: #16312a;
  line-height: 1;
  letter-spacing: -0.02em;
}

.reference-image-wrap {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reference-image {
  width: 100%;
  height: 100%;

  :deep(img) {
    object-fit: contain;
    max-height: 100%;
  }
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #a0b0aa;
  font-size: 13px;
}

.reference-hint {
  margin: 0;
  font-size: 12px;
  color: #7a9088;
  text-align: center;
  line-height: 1.6;
}
</style>
