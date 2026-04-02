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

  // ========== 已掌握字符 localStorage 管理 ==========
  const { markPassed, isCharPassed, getPassedCount } = usePassedChars()

  // ========== 字符选择状态 ==========
  const activeMode = ref('letters')   // 'letters' | 'numbers'
  const targetChar = ref('A')         // 当前练习的目标字符

  // ========== 摄像头 & WebRTC 状态 ==========
  const isCameraActive = ref(false)
  const connectionState = ref('idle')
  const isRecognitionReady = ref(false)
  const localStream = ref(null)

  // ========== 识别状态（复用 AI 后端推流数据） ==========
  const pinyinBuffer = ref('')        // 当前正在检测的字符（AI 推来的 spellingBuffer）
  const stabilityProgress = ref(0)   // 稳定度 0-1（AI 推来的 stabilityProgress）
  const overlayResult = ref(null)    // 检测框数据，传给 CameraPanel 绘制

  // ========== 练习判定状态 ==========
  const hitCount = ref(0)     // 连续正确次数
  const isPassed = ref(false) // 是否已过关

  let webrtcClient = null

  // ========== 字符列表 ==========
  const currentCharList = computed(() =>
    activeMode.value === 'letters' ? LETTERS : NUMBERS
  )

  // WebRTC mode 与 activeMode 的映射
  const webrtcMode = computed(() =>
    activeMode.value === 'numbers' ? 'digits' : 'letters'
  )

  // 参考图 URL，复用 glossary 里的 Cloudflare CDN
  const referenceImageUrl = computed(() => {
    const isLetter = LETTERS.includes(targetChar.value)
    return isLetter
      ? `https://avatar.youzilite.us.kg/letter/${targetChar.value}.png`
      : `https://avatar.youzilite.us.kg/number/${targetChar.value}.png`
  })

  // ========== 监听过关：存储 + 简单提示 ==========
  watch(isPassed, (passed) => {
    if (!passed) return
    // 写入 localStorage（临时存储）
    markPassed(targetChar.value, activeMode.value)
    // 底部简单提示
    ElMessage.success(`${targetChar.value} 已掌握！点击下一个字符继续`)
  })

  // ========== 练习判定 ==========
  const checkHit = (confirmedChar) => {
    if (!confirmedChar) return

    // 统一大写比对（AI 返回的字母通常是大写）
    const matched = confirmedChar.toUpperCase() === targetChar.value.toUpperCase()
    if (matched) {
      hitCount.value = Math.min(hitCount.value + 1, REQUIRED_COUNT)
      if (hitCount.value >= REQUIRED_COUNT) {
        isPassed.value = true
      }
    } else {
      // 识别到了别的字符，重置
      hitCount.value = 0
    }
  }

  const resetPracticeState = () => {
    hitCount.value = 0
    isPassed.value = false
    pinyinBuffer.value = ''
    stabilityProgress.value = 0
    isRecognitionReady.value = false
    overlayResult.value = null
  }

  // ========== 处理 AI 推送消息 ==========
  const handleServerMessage = (payload) => {
    if (!payload || typeof payload !== 'object') return
    if (payload.type === 'error') {
      ElMessage.error(payload.message || '识别服务异常')
      return
    }
    if (payload.type !== 'result') return

    isRecognitionReady.value = true

    if (payload.actionPerformed) {
      // CONFIRM：AI 确认了一个字符
      if (payload.actionType === 'CONFIRM') {
        const confirmed = payload.actionToast || ''
        checkHit(confirmed)
      }
      // 动作执行后清空稳定度状态
      pinyinBuffer.value = ''
      stabilityProgress.value = 0
      overlayResult.value = null
      return
    }

    // 普通识别帧：更新当前检测状态
    overlayResult.value = payload
    pinyinBuffer.value = String(payload.spellingBuffer || '')
    stabilityProgress.value = Number(payload.stabilityProgress || 0)
  }

  // ========== WebRTC 连接管理 ==========
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

  // ========== 开启 / 关闭摄像头 ==========
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

  // ========== 字符 / 模式切换 ==========
  const switchMode = (mode) => {
    activeMode.value = mode
    targetChar.value = mode === 'letters' ? 'A' : '0'
    hitCount.value = 0
    isPassed.value = false

    // 通知 AI 后端切换模式
    if (webrtcClient) {
      try { webrtcClient.setMode(mode === 'numbers' ? 'digits' : 'letters') }
      catch (err) { console.error(err) }
    }
  }

  const selectChar = (char) => {
    targetChar.value = char
    hitCount.value = 0
    isPassed.value = false
    pinyinBuffer.value = ''
    stabilityProgress.value = 0
  }

  // ========== 返回导航 ==========
  const goBack = () => {
    stopCamera()
    router.go(-1)
  }

  // ========== 读取 URL 参数初始化 ==========
  const initFromRoute = () => {
    const target = route.query.target
    if (target) {
      targetChar.value = String(target).toUpperCase()
      activeMode.value = NUMBERS.includes(target) ? 'numbers' : 'letters'
    }
  }

  return {
    // 字符状态
    activeMode,
    targetChar,
    currentCharList,
    referenceImageUrl,
    // 摄像头 & WebRTC
    isCameraActive,
    connectionState,
    isRecognitionReady,
    localStream,
    // 识别状态
    pinyinBuffer,
    stabilityProgress,
    overlayResult,
    // 练习判定
    hitCount,
    isPassed,
    // 已掌握信息（供 Header 查询）
    isCharPassed,
    getPassedCount,
    // 方法
    startCamera,
    stopCamera,
    switchMode,
    selectChar,
    goBack,
    initFromRoute,
  }
}
