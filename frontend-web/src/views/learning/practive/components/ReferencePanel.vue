<template>
  <div class="reference-panel">
    <div class="panel-label">标准手势</div>
    <div class="char-display">{{ targetLabel }}</div>

    <div class="reference-image-wrap">
      <el-image
        v-if="referenceImageUrl"
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

      <div v-else class="command-guide-card">
        <div class="command-guide-title">动作提示</div>
        <p class="command-guide-main">{{ referenceHint }}</p>
        <p v-if="referenceDescription" class="command-guide-sub">{{ referenceDescription }}</p>
      </div>
    </div>

    <p v-if="referenceImageUrl" class="reference-hint">{{ referenceHint }}</p>
  </div>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'

defineProps({
  targetLabel: { type: String, default: 'A' },
  referenceImageUrl: { type: String, default: '' },
  referenceHint: { type: String, default: '' },
  referenceDescription: { type: String, default: '' },
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
  font-size: 56px;
  font-weight: 900;
  color: #16312a;
  line-height: 1;
  letter-spacing: -0.02em;
  text-align: center;
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

.command-guide-card {
  width: 100%;
  padding: 20px 18px;
  border-radius: 22px;
  background:
    radial-gradient(circle at top left, rgba(215, 238, 227, 0.95), rgba(241, 247, 244, 0.98));
  border: 1px solid rgba(33, 109, 75, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.command-guide-title {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(33, 109, 75, 0.1);
  color: #216d4b;
  font-size: 12px;
  font-weight: 700;
}

.command-guide-main {
  margin: 14px 0 8px;
  font-size: 18px;
  line-height: 1.5;
  color: #17312b;
  font-weight: 800;
}

.command-guide-sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #5d746c;
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
