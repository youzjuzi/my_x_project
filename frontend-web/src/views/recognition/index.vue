<template>
  <div class="recognition-container">
    <div class="page-shell">
      <RecognitionHeader
        :selected-mode="selectedMode"
        :is-camera-active="isCameraActive"
        :connection-text="connectionText"
        @back="handleExit"
        @change-mode="changeMode"
        @start-camera="startCamera"
        @stop-camera="stopCamera"
      />

      <el-row :gutter="18" class="main-layout">
        <el-col :span="16" :xs="24">
          <VideoPanel
            :is-camera-active="isCameraActive"
            :is-recognition-ready="isRecognitionReady"
            :input-fps="inputFps"
            :processed-fps="processedFps"
            :latency="latency"
            :video-stream="localStream"
            :overlay-result="overlayResult"
            :action-toast="actionToast"
            :action-title="actionTitle"
            :action-type="actionType"
            :action-tick="actionTick"
            @start="startCamera"
            @stop="stopCamera"
          />
        </el-col>

        <el-col :span="8" :xs="24">
          <InteractionPanel
            :gesture-stream="gestureStream"
            :pinyin-buffer="pinyinBuffer"
            :cached-buffer="cachedBuffer"
            :hanzi-candidate="hanziCandidate"
            :candidates="hanziCandidates"
            :candidate-index="candidateIndex"
            :deleted-cache-char="deletedCacheChar"
            :deleted-cache-tick="deletedCacheTick"
            :delete-progress-tick="deleteProgressTick"
            :delete-progress-value="deleteProgressValue"
            :stability-progress="stabilityProgress"
            :final-sentence="finalSentence"
            @copy="copyResult"
            @clear="clearAll"
            @speak="speakResult"
          />
        </el-col>
      </el-row>
    </div>

    <ExitConfirmDialog
      v-model="exitDialogVisible"
      @confirm="confirmExit"
      @cancel="exitDialogVisible = false"
    />
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RecognitionHeader from './components/RecognitionHeader.vue'
import VideoPanel from './components/VideoPanel.vue'
import InteractionPanel from './components/InteractionPanel.vue'
import ExitConfirmDialog from './components/ExitConfirmDialog.vue'
import { useRecognitionSession } from './composables/useRecognitionSession'

const router = useRouter()

const {
  isCameraActive,
  connectionText,
  selectedMode,
  inputFps,
  processedFps,
  latency,
  gestureStream,
  pinyinBuffer,
  cachedBuffer,
  hanziCandidate,
  hanziCandidates,
  candidateIndex,
  deletedCacheChar,
  deletedCacheTick,
  deleteProgressTick,
  deleteProgressValue,
  stabilityProgress,
  localStream,
  overlayResult,
  isRecognitionReady,
  actionToast,
  actionTitle,
  actionType,
  actionTick,
  clearActionToast,
  startCamera,
  stopCamera,
  changeMode,
} = useRecognitionSession()

const finalSentence = ref('')
const exitDialogVisible = ref(false)

watch(
  () => actionTick.value,
  () => {
    if (actionType.value !== 'CONFIRM' || !actionToast.value) {
      return
    }

    finalSentence.value += actionToast.value
  }
)

const handleExit = () => {
  if (isCameraActive.value) {
    exitDialogVisible.value = true
    return
  }

  navigateBack()
}

const confirmExit = () => {
  stopCamera()
  exitDialogVisible.value = false
  navigateBack()
}

const navigateBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
    return
  }

  router.push('/')
}

const clearAll = () => {
  finalSentence.value = ''
}

const copyResult = async () => {
  if (!finalSentence.value) {
    return
  }

  await navigator.clipboard.writeText(finalSentence.value)
  ElMessage.success('已复制')
}

const speakResult = () => {
  ElMessage.info('语音播报暂未实现')
}

onBeforeUnmount(() => {
  clearActionToast()
  stopCamera()
})
</script>

<style scoped lang="scss">
.recognition-container {
  min-height: calc(100vh - 84px);
  padding: 16px 20px 18px;
  background: #f8faf9;
  overflow: hidden;
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.main-layout {
  margin: 0;
}

@media (max-width: 992px) {
  .recognition-container {
    padding: 16px;
    overflow: auto;
  }
}

@media (max-width: 767px) {
  .recognition-container {
    min-height: auto;
    padding: 14px;
  }
}
</style>
