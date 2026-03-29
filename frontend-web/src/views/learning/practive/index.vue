<template>
  <div class="practice-container">
    <PracticeHeader
      :active-mode="activeMode"
      :target-char="targetChar"
      :current-char-list="currentCharList"
      :is-camera-active="isCameraActive"
      @back="goBack"
      @switch-mode="switchMode"
      @select-char="selectChar"
      @start-camera="startCamera"
      @stop-camera="stopCamera"
    />

    <div class="stage">
      <!-- 左侧：摄像头画面 + 稳定度 HUD -->
      <CameraPanel
        :stream="localStream"
        :is-camera-active="isCameraActive"
        :is-recognition-ready="isRecognitionReady"
        :connection-state="connectionState"
        :pinyin-buffer="pinyinBuffer"
        :stability-progress="stabilityProgress"
        :hit-count="hitCount"
        :required-count="REQUIRED_COUNT"
        :overlay-result="overlayResult"
        @start-camera="startCamera"
      />

      <!-- 右侧：参考图 -->
      <ReferencePanel
        :target-char="targetChar"
        :reference-image-url="referenceImageUrl"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PracticeHeader from './components/PracticeHeader.vue'
import CameraPanel from './components/CameraPanel.vue'
import ReferencePanel from './components/ReferencePanel.vue'
import { usePracticeSession, REQUIRED_COUNT } from './composables/usePracticeSession'

const {
  activeMode,
  targetChar,
  currentCharList,
  referenceImageUrl,
  isCameraActive,
  connectionState,
  isRecognitionReady,
  localStream,
  pinyinBuffer,
  stabilityProgress,
  overlayResult,
  hitCount,
  isPassed,
  startCamera,
  stopCamera,
  switchMode,
  selectChar,
  goBack,
  initFromRoute,
} = usePracticeSession()

onMounted(() => {
  initFromRoute()
})
</script>

<style scoped lang="scss">
.practice-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 84px);
  padding: 14px 20px 18px;
  background-color: #edf2f0;
  background-image:
    radial-gradient(at 0% 0%, rgba(200, 230, 215, 0.4) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(195, 225, 205, 0.3) 0px, transparent 50%),
    radial-gradient(rgba(45, 105, 80, 0.05) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 24px 24px;
  gap: 12px;
}

.stage {
  display: flex;
  gap: 12px;
  flex: 1;
  min-height: 0;
}

@media (max-width: 768px) {
  .practice-container { padding: 10px 12px 14px; }
  .stage { flex-direction: column; }
}
</style>