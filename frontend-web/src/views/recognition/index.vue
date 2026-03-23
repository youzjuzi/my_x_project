<template>
  <div class="recognition-container">
    <div class="page-shell">
      <div class="hero-row">
        <div class="nav-header">
          <div class="back-capsule" @click="handleExit" aria-label="返回">
            <div class="icon-wrap">
              <el-icon><ArrowLeft /></el-icon>
            </div>
          </div>
        </div>

        <div class="page-intro">
          <div class="intro-main">
            <p class="eyebrow">手势识别</p>
            <h1>通过摄像头实时识别手势内容</h1>
            <p class="description">
              当前页面已接入 WebRTC 推理服务，支持数字与字母两种模式切换，现阶段优先展示实时摄像头画面、识别框，以及最基础的识别过程与当前拼写。
            </p>
          </div>

          <div class="intro-actions">
            <div class="mode-switch">
              <el-button
                :type="selectedMode === 'digits' ? 'primary' : 'default'"
                plain
                class="mode-button"
                @click="changeMode('digits')"
              >
                数字模式
              </el-button>
              <el-button
                :type="selectedMode === 'letters' ? 'primary' : 'default'"
                plain
                class="mode-button"
                @click="changeMode('letters')"
              >
                字母模式
              </el-button>
            </div>

            <div class="intro-badge">
              <span class="status-dot" :class="{ active: isCameraActive }"></span>
              {{ isCameraActive ? connectionText : '等待开启摄像头' }}
            </div>

            <el-button
              v-if="!isCameraActive"
              type="primary"
              class="hero-action"
              @click="startCamera"
            >
              开启摄像头
            </el-button>

            <el-button
              v-else
              type="danger"
              plain
              class="hero-action"
              @click="stopCamera"
            >
              关闭摄像头
            </el-button>
          </div>
        </div>
      </div>

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
            :switch-toast="switchToast"
            @start="startCamera"
            @stop="stopCamera"
          />
        </el-col>

        <el-col :span="8" :xs="24">
          <InteractionPanel
            :gesture-stream="gestureStream"
            :pinyin-buffer="pinyinBuffer"
            :cached-buffer="cachedBuffer"
            :stability-progress="stabilityProgress"
            :candidates="candidates"
            :final-sentence="finalSentence"
            @select-candidate="selectCandidate"
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
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import VideoPanel from './components/VideoPanel.vue'
import InteractionPanel from './components/InteractionPanel.vue'
import ExitConfirmDialog from './components/ExitConfirmDialog.vue'
import { createRecognitionWebRtcClient } from './services/webrtcClient'

const router = useRouter()

const isCameraActive = ref(false)
const connectionState = ref('idle')
const selectedMode = ref('digits')
const inputFps = ref(0)
const processedFps = ref(0)
const latency = ref(0)
const gestureStream = ref([])
const pinyinBuffer = ref('')
const cachedBuffer = ref('')
const stabilityProgress = ref(0)
const candidates = ref([])
const finalSentence = ref('')
const exitDialogVisible = ref(false)
const localStream = ref(null)
const overlayResult = ref(null)
const isRecognitionReady = ref(false)
const switchToast = ref('')

let webrtcClient = null
let switchToastTimer = null

const modeLabelMap = {
  digits: '数字',
  letters: '字母',
}

const connectionText = computed(() => {
  const modeLabel = modeLabelMap[selectedMode.value] || selectedMode.value

  if (connectionState.value === 'connected') {
    return `WebRTC 已连接 · ${modeLabel}模式`
  }

  if (connectionState.value === 'connecting') {
    return `WebRTC 连接中 · ${modeLabel}模式`
  }

  return `摄像头已开启 · ${modeLabel}模式`
})

const resetDisplayState = () => {
  inputFps.value = 0
  processedFps.value = 0
  latency.value = 0
  overlayResult.value = null
  gestureStream.value = []
  pinyinBuffer.value = ''
  cachedBuffer.value = ''
  stabilityProgress.value = 0
  isRecognitionReady.value = false
}

const clearSwitchToast = () => {
  if (switchToastTimer) {
    window.clearTimeout(switchToastTimer)
    switchToastTimer = null
  }
  switchToast.value = ''
}

const showSwitchToast = (mode) => {
  const modeLabel = modeLabelMap[mode] || mode
  clearSwitchToast()
  switchToast.value = `已切换到${modeLabel}模式`
  switchToastTimer = window.setTimeout(() => {
    switchToast.value = ''
    switchToastTimer = null
  }, 1500)
}

const mapProcessItems = (items) => {
  if (!Array.isArray(items)) {
    return []
  }

  return items.map((item, index) => ({
    id: `${index}-${item}`,
    char: item,
  }))
}

const handleServerMessage = (payload) => {
  if (!payload || typeof payload !== 'object') {
    return
  }

  if (payload.type === 'error') {
    ElMessage.error(payload.message || '识别服务返回错误')
    return
  }

  if (payload.type === 'mode_changed') {
    selectedMode.value = payload.mode || selectedMode.value
    resetDisplayState()
    return
  }

  if (payload.type !== 'result') {
    return
  }

  if (payload.modeChangedByCommand) {
    isRecognitionReady.value = true
    inputFps.value = Number(payload.inputFps || 0)
    processedFps.value = Number(payload.processedFps || 0)
    latency.value = Number(payload.latencyMs || 0)
    selectedMode.value = payload.mode || selectedMode.value
    gestureStream.value = []
    pinyinBuffer.value = ''
    cachedBuffer.value = ''
    stabilityProgress.value = 0
    candidates.value = []
    finalSentence.value = ''
    overlayResult.value = null
    showSwitchToast(selectedMode.value)
    return
  }

  overlayResult.value = payload
  isRecognitionReady.value = true
  inputFps.value = Number(payload.inputFps || 0)
  processedFps.value = Number(payload.processedFps || 0)
  latency.value = Number(payload.latencyMs || 0)
  gestureStream.value = mapProcessItems(payload.processItems)
  pinyinBuffer.value = String(payload.spellingBuffer || '')
  cachedBuffer.value = String(payload.cachedBuffer || '')
  stabilityProgress.value = Number(payload.stabilityProgress || 0)
}

const disconnectWebRtc = () => {
  if (!webrtcClient) {
    connectionState.value = 'idle'
    return
  }

  webrtcClient.disconnect()
  webrtcClient = null
  connectionState.value = 'idle'
}

const connectWebRtc = async (stream) => {
  disconnectWebRtc()
  connectionState.value = 'connecting'

  webrtcClient = createRecognitionWebRtcClient({
    mediaStream: stream,
    mode: selectedMode.value,
    onResult: handleServerMessage,
    onOpen: () => {
      connectionState.value = 'connected'
    },
    onClose: () => {
      connectionState.value = 'idle'
      webrtcClient = null
    },
    onConnectionStateChange: (state) => {
      connectionState.value = state
    },
    onError: (error) => {
      console.error(error)
    },
  })

  await webrtcClient.connect()
}

const startCamera = async () => {
  let stream = null

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' },
      audio: false,
    })

    localStream.value = stream
    isCameraActive.value = true
    resetDisplayState()

    await connectWebRtc(stream)
  } catch (error) {
    console.error(error)
    if (stream) {
      stream.getTracks().forEach((track) => {
        track.stop()
      })
    }
    isCameraActive.value = false
    localStream.value = null
    resetDisplayState()
    connectionState.value = 'idle'
    ElMessage.error(error?.message || '无法开启摄像头或连接 WebRTC 服务')
  }
}

const stopCamera = () => {
  disconnectWebRtc()
  isCameraActive.value = false
  resetDisplayState()
  clearSwitchToast()

  if (localStream.value) {
    localStream.value.getTracks().forEach((track) => {
      track.stop()
    })
    localStream.value = null
  }
}

const changeMode = async (mode) => {
  if (selectedMode.value === mode) {
    return
  }

  selectedMode.value = mode
  resetDisplayState()

  if (!webrtcClient) {
    return
  }

  try {
    webrtcClient.setMode(mode)
  } catch (error) {
    console.error(error)
    ElMessage.error(error?.message || '模式切换失败')
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

const selectCandidate = (word) => {
  finalSentence.value += word
  pinyinBuffer.value = ''
  candidates.value = []
  gestureStream.value = []
  stabilityProgress.value = 0
}

const clearAll = () => {
  finalSentence.value = ''
  pinyinBuffer.value = ''
  gestureStream.value = []
  stabilityProgress.value = 0
}

const copyResult = async () => {
  if (!finalSentence.value) {
    return
  }

  await navigator.clipboard.writeText(finalSentence.value)
  ElMessage.success('识别结果已复制')
}

const speakResult = () => {
  ElMessage.info('朗读功能暂未接入')
}

onBeforeUnmount(() => {
  clearSwitchToast()
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

.hero-row {
  display: flex;
  align-items: stretch;
  gap: 10px;
  margin-bottom: 10px;
}

.nav-header {
  flex-shrink: 0;
}

.back-capsule {
  height: 100%;
  min-width: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(26, 64, 50, 0.08);
  box-shadow: 0 6px 18px rgba(28, 43, 36, 0.05);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  user-select: none;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(28, 43, 36, 0.1);
  }
}

.icon-wrap {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #edf4f1;
  color: #22463b;
  font-size: 15px;
}

.page-intro {
  flex: 1;
  padding: 12px 16px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 10px 26px rgba(28, 43, 36, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.intro-main {
  min-width: 0;
}

.intro-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.mode-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.mode-button {
  min-width: 92px;
}

.eyebrow {
  margin: 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #688178;
}

.page-intro h1 {
  margin: 4px 0;
  font-size: 24px;
  line-height: 1.15;
  color: #16312a;
}

.description {
  margin: 0;
  max-width: 760px;
  font-size: 13px;
  line-height: 1.5;
  color: #5d7169;
}

.intro-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  background: #eef5f1;
  color: #24463d;
  font-size: 12px;
  font-weight: 700;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c7d0cc;

  &.active {
    background: #25a165;
    box-shadow: 0 0 0 4px rgba(37, 161, 101, 0.12);
  }
}

.hero-action {
  min-width: 124px;
  height: 36px;
  border-radius: 999px;
}

.main-layout {
  margin: 0;
}

@media (max-width: 992px) {
  .recognition-container {
    padding: 16px;
    overflow: auto;
  }

  .hero-row {
    flex-direction: column;
  }

  .page-intro {
    flex-direction: column;
    align-items: stretch;
  }

  .intro-actions {
    width: 100%;
    justify-content: space-between;
  }

  .page-intro h1 {
    font-size: 22px;
  }
}

@media (max-width: 767px) {
  .recognition-container {
    min-height: auto;
    padding: 14px;
  }

  .nav-header {
    align-self: flex-start;
  }

  .page-intro {
    padding: 14px;
    border-radius: 18px;
  }

  .page-intro h1 {
    font-size: 20px;
  }

  .description {
    font-size: 13px;
  }

  .intro-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .mode-switch {
    width: 100%;
  }

  .mode-button,
  .hero-action {
    width: 100%;
  }

  .intro-badge {
    justify-content: center;
  }
}
</style>
