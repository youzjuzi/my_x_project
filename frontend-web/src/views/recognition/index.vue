<template>
  <div class="recognition-container">
    <div class="page-shell">
      <RecognitionHeader
        :selected-mode="selectedMode"
        :is-camera-active="isCameraActive"
        :connection-text="connectionText"
        @back="handleExit"
        @start-camera="startCamera"
        @stop-camera="stopCamera"
        @change-mode="changeMode"
      />

      <el-row :gutter="18" class="main-layout">
        <el-col :span="16" :xs="24">
          <VideoPanel
            :is-camera-active="isCameraActive"
            :connection-state="connectionState"
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
            :command-mode-active="commandModeActive"
            :command-candidate="commandCandidate"
            :command-candidate-progress="commandCandidateProgress"
            :pinyin-buffer="pinyinBuffer"
            :cached-buffer="cachedBuffer"
            :deleted-cache-char="deletedCacheChar"
            :deleted-cache-tick="deletedCacheTick"
            :delete-progress-tick="deleteProgressTick"
            :delete-progress-value="deleteProgressValue"
            :stability-progress="stabilityProgress"
            @start="startCamera"
            @stop="stopCamera"
          />
        </el-col>

        <el-col :span="8" :xs="24">
          <InteractionPanel
            :gesture-stream="gestureStream"
            :hanzi-candidate="hanziCandidate"
            :candidates="hanziCandidates"
            :candidate-index="candidateIndex"
            :pending-words="pendingWords"
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
import useUserStore from '@/store/modules/user'
import { saveHistory } from '@/api/translationHistory'

const router = useRouter()
const userStore = useUserStore()

const {
  isCameraActive,
  connectionState,
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
  commandModeActive,
  commandCandidate,
  commandCandidateProgress,
} = useRecognitionSession()

const pendingWords = ref('')
const finalSentence = ref('')
const polishedResult = ref('')
const isSubmitting = ref(false)
const exitDialogVisible = ref(false)

watch(
  () => actionTick.value,
  () => {
    if (actionType.value === 'CONFIRM' && actionToast.value) {
      // CONFIRM：词语暂存到已接受词语，等待 SUBMIT 统一发送
      pendingWords.value += actionToast.value
      return
    }

    if (actionType.value === 'CLEAR') {
      // CLEAR：清除已暂存（接受）的词语，但保留已提交的最终句子
      pendingWords.value = ''
      ElMessage.warning('已清空暂存词语')
      return
    }

    if (actionType.value === 'SUBMIT') {
      handleSubmit()
    }
  }
)

const handleSubmit = async () => {
  if (!pendingWords.value || isSubmitting.value) {
    return
  }

  isSubmitting.value = true
  const wordsToSubmit = pendingWords.value
  pendingWords.value = ''

  try {
    const response = await fetch('http://127.0.0.1:8002/webrtc/polish', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: wordsToSubmit })
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || '网络请求失败')
    }

    const result = await response.json()
    if (result && result.polishedText) {
      finalSentence.value += result.polishedText + ' '
      polishedResult.value = result.polishedText
      ElMessage.success('AI 润色成功')
      saveHistory({
        userId: userStore.userId,
        originalWords: wordsToSubmit,
        resultSentence: result.polishedText,
        isAiPolished: 1
      }).catch(err => console.error('保存历史记录失败:', err))
    } else {
      // 容错：如果未返回结果直接拼接原词
      finalSentence.value += wordsToSubmit + ' '
      saveHistory({
        userId: userStore.userId,
        originalWords: wordsToSubmit,
        resultSentence: wordsToSubmit,
        isAiPolished: 0
      }).catch(err => console.error('保存降级历史记录失败:', err))
    }
  } catch (error) {
    console.error('提交失败:', error)
    // 失败时把词语还回暂存区
    pendingWords.value = wordsToSubmit + pendingWords.value
    ElMessage.warning('提交失败，词语已还原')
  } finally {
    isSubmitting.value = false
  }
}

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
  pendingWords.value = ''
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
