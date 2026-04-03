import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { createRecognitionWebRtcClient } from '@/services/webrtcClient'
import { usePassedChars } from './usePassedChars'

export const LETTERS = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i))
export const NUMBERS = Array.from({ length: 10 }, (_, i) => String(i))
export const COMMANDS = [
  { value: 'CONFIRM', label: '确认', description: '双手同时张开五指', hint: '双手掌心展开，对准镜头保持稳定' },
  { value: 'DELETE', label: '删除', description: '双手食指同时向下', hint: '双手其余手指收起，食指朝下保持稳定' },
  { value: 'CLEAR', label: '清空', description: '双手同时握拳', hint: '双手握拳并保持，触发一次清空手势' },
  { value: 'NEXT', label: '下一个', description: '双手食指同时向上', hint: '双手其余手指收起，食指朝上保持稳定' },
  { value: 'SUBMIT', label: '提交', description: '双手同时竖起大拇指', hint: '双手竖起拇指，其余手指收拢后保持稳定' },
]
export const REQUIRED_COUNT = 3

const LETTER_ITEMS = LETTERS.map((value) => ({ value, label: value }))
const NUMBER_ITEMS = NUMBERS.map((value) => ({ value, label: value }))
const COMMAND_VALUE_SET = new Set(COMMANDS.map((item) => item.value))
const COMMAND_LABEL_MAP = Object.fromEntries(COMMANDS.map((item) => [item.value, item.label]))

function findItem(items, value) {
  return items.find((item) => item.value === value) || items[0]
}

function getCommandLabel(token) {
  return COMMAND_LABEL_MAP[token] || token
}

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

  const currentCharList = computed(() => {
    if (activeMode.value === 'numbers') return NUMBER_ITEMS
    if (activeMode.value === 'commands') return COMMANDS
    return LETTER_ITEMS
  })

  const totalCount = computed(() => currentCharList.value.length)

  const targetConfig = computed(() => {
    const fallback = { value: targetChar.value, label: targetChar.value, description: '', hint: '' }
    return findItem(currentCharList.value, targetChar.value) || fallback
  })

  const webrtcMode = computed(() => {
    if (activeMode.value === 'numbers') return 'digits'
    if (activeMode.value === 'commands') return 'commands'
    return 'letters'
  })

  const referenceImageUrl = computed(() => {
    if (activeMode.value === 'commands') {
      return ''
    }

    const value = targetConfig.value.value
    return activeMode.value === 'letters'
      ? `https://avatar.youzilite.us.kg/letter/${value}.png`
      : `https://avatar.youzilite.us.kg/number/${value}.png`
  })

  const referenceTitle = computed(() => targetConfig.value.label)

  const referenceHint = computed(() => {
    if (activeMode.value === 'commands') {
      return targetConfig.value.description || '请根据提示完成双手功能手势。'
    }
    return '请参照图片做出对应手势，对准摄像头保持稳定'
  })

  const referenceDescription = computed(() => {
    if (activeMode.value === 'commands') {
      return targetConfig.value.hint || ''
    }
    return ''
  })

  watch(isPassed, (passed) => {
    if (!passed) return
    markPassed(targetChar.value, activeMode.value)
    showCelebration.value = true
    ElMessage.success(`${targetConfig.value.label} 已掌握！点击下一个继续`)
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
    const rawDisplayToken = String(payload.spellingBuffer || payload.commandGesture || payload.commandCandidate || '')
    pinyinBuffer.value = activeMode.value === 'commands' ? getCommandLabel(rawDisplayToken) : rawDisplayToken
    stabilityProgress.value = Number(payload.stabilityProgress || payload.commandCandidateProgress || 0)
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
      stream?.getTracks().forEach((t) => t.stop())
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
    localStream.value?.getTracks().forEach((t) => t.stop())
    localStream.value = null
  }

  const switchMode = (mode) => {
    activeMode.value = mode
    targetChar.value = currentCharList.value[0]?.value || 'A'
    resetPracticeState()

    if (webrtcClient) {
      try { webrtcClient.setMode(webrtcMode.value) }
      catch (err) { console.error(err) }
    }
  }

  const selectChar = (char) => {
    targetChar.value = char
    resetPracticeState()
  }

  const nextChar = () => {
    const list = currentCharList.value
    const currentIndex = list.findIndex((item) => item.value === targetChar.value)
    const nextIndex = currentIndex >= 0 ? (currentIndex + 1) % list.length : 0
    targetChar.value = list[nextIndex]?.value || targetChar.value
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
    const rawTarget = route.query.target
    if (!rawTarget) {
      return
    }

    const target = String(rawTarget).toUpperCase()
    if (COMMAND_VALUE_SET.has(target)) {
      activeMode.value = 'commands'
      targetChar.value = target
      return
    }

    if (NUMBERS.includes(target)) {
      activeMode.value = 'numbers'
      targetChar.value = target
      return
    }

    activeMode.value = 'letters'
    targetChar.value = target
  }

  return {
    activeMode,
    targetChar,
    currentCharList,
    totalCount,
    targetLabel: referenceTitle,
    referenceImageUrl,
    referenceHint,
    referenceDescription,
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
