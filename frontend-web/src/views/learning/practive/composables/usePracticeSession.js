import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { createRecognitionWebRtcClient } from '@/services/webrtcClient'
import { usePassedChars } from './usePassedChars'

// ========== 字符数据常量 ==========
export const LETTERS = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i)) // A-Z
export const NUMBERS = Array.from({ length: 10 }, (_, i) => String(i))                   // 0-9
export const REQUIRED_COUNT = 3 // 连续识别正确多少次算过关

export function usePracticeSession() {
  const route = useRoute()
  const router = useRouter()

  const { markPassed, isCharPassed, getPassedCount } = usePassedChars()

  const activeMode = ref('letters')
  const targetChar = ref('A')

  const isCameraActive = ref(false)
  const connectionState = ref('idle')
  const isRecognitionReady = ref(false)
  const localStream = ref(null)

  const pinyinBuffer = ref('')
  const stabilityProgress = ref(0)
  const overlayResult = ref(null)

  const hitCount = ref(0)
  const isPassed = ref(false)
  const showCelebration = ref(false)

  let webrtcClient = null

  const currentCharList = computed(() =>
    activeMode.value === 'letters' ? LETTERS : NUMBERS
  )

  const webrtcMode = computed(() =>
    activeMode.value === 'numbers' ? 'digits' : 'letters'
  )

  const referenceImageUrl = computed(() => {
    const isLetter = LETTERS.includes(targetChar.value)
    return isLetter
      ? `https://avatar.youzilite.us.kg/letter/${targetChar.value}.png`
      : `https://avatar.youzilite.us.kg/number/${targetChar.value}.png`
  })

  watch(isPassed, (passed) => {
    if (!passed) return
    markPassed(targetChar.value, activeMode.value)
    showCelebration.value = true
    ElMessage.success(`${targetChar.value} 已掌握！点击下一个字符继续`)
  })

  const checkHit = (matchedToken) => {
    if (!matchedToken) return

    const matched = matchedToken.toUpperCase() === targetChar.value.toUpperCase()
    if (matched) {
      hitCount.value = Math.min(hitCount.value + 1, REQUIRED_COUNT)
      if (hitCount.value >= REQUIRED_COUNT) {
        isPassed.value = true
      }
      return
    }

    hitCount.value = 0
  }

  const resetPracticeState = ({ keepCelebration = false } = {}) => {
    hitCount.value = 0
    isPassed.value = false
    pinyinBuffer.value = ''
    stabilityProgress.value = 0
    isRecognitionReady.value = false
    overlayResult.value = null
    if (!keepCelebration) {
      showCelebration.value = false
    }
  }

  const handleServerMessage = (payload) => {
    if (!payload || typeof payload !== 'object') return
    if (payload.type === 'error') {
      ElMessage.error(payload.message || '识别服务异常')
      return
    }
    if (payload.type !== 'result') return

    isRecognitionReady.value = true

    if (payload.actionPerformed) {
      if (payload.actionType === 'STABLE_MATCH') {
        const matchedToken = payload.practiceMatchedToken || payload.actionToast || ''
        checkHit(matchedToken)
      }
      pinyinBuffer.value = ''
      stabilityProgress.value = 0
      overlayResult.value = null
      return
    }

    overlayResult.value = payload
    pinyinBuffer.value = String(payload.spellingBuffer || '')
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
      scene: 'practice',
      mode: webrtcMode.value,
      onResult: handleServerMessage,
      onOpen: () => { connectionState.value = 'connected' },
      onClose: () => { connectionState.value = 'idle'; webrtcClient = null },
      onConnectionStateChange: (state) => { connectionState.value = state },
      onError: (err) => console.error(err),
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
      resetPracticeState()
      await connectWebRtc(stream)
    } catch (err) {
      console.error(err)
      stream?.getTracks().forEach(t => t.stop())
      isCameraActive.value = false
      localStream.value = null
      connectionState.value = 'idle'
      ElMessage.error(err?.message || '摄像头启动或连接失败')
    }
  }

  const stopCamera = () => {
    disconnectWebRtc()
    isCameraActive.value = false
    resetPracticeState()
    localStream.value?.getTracks().forEach(t => t.stop())
    localStream.value = null
  }

  const switchMode = (mode) => {
    activeMode.value = mode
    targetChar.value = mode === 'letters' ? 'A' : '0'
    resetPracticeState()

    if (webrtcClient) {
      try { webrtcClient.setMode(mode === 'numbers' ? 'digits' : 'letters') }
      catch (err) { console.error(err) }
    }
  }

  const selectChar = (char) => {
    targetChar.value = char
    resetPracticeState()
  }

  const nextChar = () => {
    const list = currentCharList.value
    const currentIndex = list.indexOf(targetChar.value)
    const nextIndex = currentIndex >= 0 ? (currentIndex + 1) % list.length : 0
    targetChar.value = list[nextIndex]
    resetPracticeState()
  }

  const dismissCelebration = () => {
    showCelebration.value = false
  }

  const goBack = () => {
    stopCamera()
    router.go(-1)
  }

  const initFromRoute = () => {
    const target = route.query.target
    if (target) {
      targetChar.value = String(target).toUpperCase()
      activeMode.value = NUMBERS.includes(target) ? 'numbers' : 'letters'
    }
  }

  return {
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
    showCelebration,
    isCharPassed,
    getPassedCount,
    startCamera,
    stopCamera,
    switchMode,
    selectChar,
    nextChar,
    dismissCelebration,
    goBack,
    initFromRoute,
  }
}
