import { computed, ref, type Ref } from 'vue'
import { pinyin } from 'pinyin-pro'
import { ElMessage } from 'element-plus'
import { submitChallenge } from '@/api/challenge'
import { createRecognitionWebRtcClient } from '@/services/webrtcClient'

function normalizeDetectedToken(token: string) {
  return String(token || '').trim().toUpperCase()
}

export function useChallengeGame(challengeTimeRef?: Ref<number>) {
  const isPlaying = ref(false)
  const currentMode = ref<'english' | 'number' | 'chinese'>('chinese')
  const score = ref(0)
  const timeLeft = ref(60)
  const showResult = ref(false)
  const showPauseDialog = ref(false)
  const timer = ref<NodeJS.Timeout | null>(null)

  const currentQuestionList = ref<any[]>([])
  const currentWordIndex = ref(0)
  const matchedCount = ref(0)
  const lastDetectedChar = ref('')
  const currentQuestion = ref<any>(null)
  const challengeId = ref<string>('')
  const challengeTime = challengeTimeRef || ref(60)

  const localStream = ref<MediaStream | null>(null)
  const connectionState = ref('idle')
  const isRecognitionReady = ref(false)
  const stabilityProgress = ref(0)
  const overlayResult = ref<any>(null)

  const isAdvancingQuestion = ref(false)

  let webrtcClient: ReturnType<typeof createRecognitionWebRtcClient> | null = null

  const totalWords = computed(() => currentQuestionList.value.length)

  const currentWordOriginal = computed(() => {
    if (!currentQuestion.value) return ''
    return String(currentQuestion.value.content || '')
  })

  const currentTargetSequence = computed(() => {
    const word = currentWordOriginal.value
    if (!word) return []

    if (currentMode.value === 'chinese') {
      return pinyin(word, { toneType: 'none', type: 'string' })
        .toUpperCase()
        .replace(/\s+/g, '')
        .split('')
    }

    if (currentMode.value === 'number') {
      return String(word).replace(/\s+/g, '').split('')
    }

    return String(word).toUpperCase().replace(/\s+/g, '').split('')
  })

  const currentTargetChar = computed(() => {
    return currentTargetSequence.value[matchedCount.value] || ''
  })

  const completedCount = computed(() => {
    if (!currentQuestion.value) return 0
    return Math.min(currentWordIndex.value, totalWords.value)
  })

  const recognitionMode = computed(() => {
    return currentMode.value === 'number' ? 'digits' : 'letters'
  })

  const updateCurrentMode = () => {
    if (!currentQuestion.value) return
    const type = currentQuestion.value.type
    if (type === 1) {
      currentMode.value = 'english'
    } else if (type === 2) {
      currentMode.value = 'chinese'
    } else if (type === 3) {
      currentMode.value = 'number'
    }

    if (webrtcClient) {
      try {
        webrtcClient.setMode(recognitionMode.value)
      } catch (error) {
        console.error('挑战识别模式切换失败', error)
      }
    }
  }

  const resetRecognitionState = () => {
    isRecognitionReady.value = false
    stabilityProgress.value = 0
    overlayResult.value = null
    lastDetectedChar.value = ''
  }

  const teardownRecognition = (releaseStream = true) => {
    if (webrtcClient) {
      webrtcClient.disconnect()
      webrtcClient = null
    }
    connectionState.value = 'idle'
    resetRecognitionState()

    if (releaseStream && localStream.value) {
      localStream.value.getTracks().forEach((track) => track.stop())
      localStream.value = null
    }
  }

  const handleRecognitionMatch = (token: string) => {
    if (!isPlaying.value || isAdvancingQuestion.value) {
      return
    }

    const normalizedToken = normalizeDetectedToken(token)
    if (!normalizedToken) {
      return
    }

    lastDetectedChar.value = normalizedToken

    if (normalizedToken !== normalizeDetectedToken(currentTargetChar.value)) {
      return
    }

    matchedCount.value += 1
    score.value += 10

    if (matchedCount.value < currentTargetSequence.value.length) {
      return
    }

    if (currentWordIndex.value >= totalWords.value - 1) {
      void gameOver()
      return
    }

    isAdvancingQuestion.value = true
    window.setTimeout(() => {
      if (!isPlaying.value) {
        isAdvancingQuestion.value = false
        return
      }
      currentWordIndex.value += 1
      matchedCount.value = 0
      currentQuestion.value = currentQuestionList.value[currentWordIndex.value]
      updateCurrentMode()
      lastDetectedChar.value = ''
      stabilityProgress.value = 0
      overlayResult.value = null
      isAdvancingQuestion.value = false
    }, 450)
  }

  const handleServerMessage = (payload: any) => {
    if (!payload || typeof payload !== 'object') {
      return
    }

    if (payload.type === 'error') {
      ElMessage.error(payload.message || '挑战识别服务异常')
      return
    }

    if (payload.type === 'mode_changed') {
      return
    }

    if (payload.type !== 'result') {
      return
    }

    isRecognitionReady.value = true
    overlayResult.value = payload
    stabilityProgress.value = Number(payload.stabilityProgress || 0)

    const inProgressToken = normalizeDetectedToken(payload.spellingBuffer || payload.text || '')
    if (inProgressToken) {
      lastDetectedChar.value = inProgressToken
    }

    if (payload.actionPerformed && payload.actionType === 'STABLE_MATCH') {
      const matchedToken = normalizeDetectedToken(payload.practiceMatchedToken || payload.actionToast || '')
      if (matchedToken) {
        handleRecognitionMatch(matchedToken)
      }
      stabilityProgress.value = 0
    }
  }

  const ensureRecognitionConnected = async () => {
    if (webrtcClient && localStream.value) {
      try {
        webrtcClient.setMode(recognitionMode.value)
      } catch (error) {
        console.error('挑战识别模式同步失败', error)
      }
      return true
    }

    let stream: MediaStream | null = null
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 960, height: 540, facingMode: 'user' },
        audio: false,
      })

      localStream.value = stream
      connectionState.value = 'connecting'
      resetRecognitionState()

      webrtcClient = createRecognitionWebRtcClient({
        mediaStream: stream,
        scene: 'challenge',
        mode: recognitionMode.value,
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
      return true
    } catch (error: any) {
      console.error('挑战识别连接失败', error)
      stream?.getTracks().forEach((track) => track.stop())
      localStream.value = null
      connectionState.value = 'idle'
      webrtcClient = null
      ElMessage.error(error?.message || '挑战识别连接失败')
      return false
    }
  }

  const startTimer = () => {
    if (timer.value) {
      clearInterval(timer.value)
    }
    timer.value = setInterval(() => {
      timeLeft.value -= 1
      if (timeLeft.value <= 0) {
        void gameOver()
      }
    }, 1000)
  }

  const startGame = async () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }

    showPauseDialog.value = false
    showResult.value = false
    isAdvancingQuestion.value = false
    score.value = 0
    timeLeft.value = challengeTime.value
    currentWordIndex.value = 0
    matchedCount.value = 0
    currentQuestion.value = currentQuestionList.value[0] || null
    lastDetectedChar.value = ''
    updateCurrentMode()

    const connected = await ensureRecognitionConnected()
    if (!connected) {
      isPlaying.value = false
      return false
    }

    isPlaying.value = true
    startTimer()
    return true
  }

  const stopGame = (showPause = true) => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }

    isPlaying.value = false
    isAdvancingQuestion.value = false
    lastDetectedChar.value = ''

    if (!showPause) {
      teardownRecognition(true)
      return
    }

    showPauseDialog.value = true
  }

  const resumeGame = async () => {
    showPauseDialog.value = false

    const connected = await ensureRecognitionConnected()
    if (!connected) {
      return false
    }

    isPlaying.value = true
    startTimer()
    return true
  }

  const abandonChallenge = async () => {
    teardownRecognition(true)

    if (challengeId.value) {
      try {
        await submitChallenge({
          challengeId: challengeId.value,
          score: score.value,
          completedCount: completedCount.value,
          timeUsed: challengeTime.value - timeLeft.value,
          status: 2,
        })
        console.log('挑战已标记为放弃')
      } catch (error) {
        console.error('放弃挑战失败', error)
      } finally {
        challengeId.value = ''
      }
    }
  }

  const gameOver = async () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }

    isPlaying.value = false
    isAdvancingQuestion.value = false
    teardownRecognition(true)

    if (challengeId.value) {
      try {
        await submitChallenge({
          challengeId: challengeId.value,
          score: score.value,
          completedCount: Math.min(completedCount.value + (matchedCount.value >= currentTargetSequence.value.length && currentTargetSequence.value.length > 0 ? 1 : 0), totalWords.value),
          timeUsed: challengeTime.value - timeLeft.value,
        })
      } catch (error) {
        console.error('提交挑战结果失败', error)
      } finally {
        challengeId.value = ''
      }
    }

    showResult.value = true
  }

  const getRank = (accuracy: number) => {
    if (accuracy >= 0.9) return '优秀'
    if (accuracy >= 0.7) return '良好'
    if (accuracy >= 0.5) return '及格'
    return '一般'
  }

  return {
    isPlaying,
    currentMode,
    score,
    timeLeft,
    showResult,
    showPauseDialog,
    currentQuestionList,
    currentWordIndex,
    matchedCount,
    lastDetectedChar,
    currentQuestion,
    challengeId,
    localStream,
    connectionState,
    isRecognitionReady,
    stabilityProgress,
    overlayResult,
    totalWords,
    completedCount,
    currentWordOriginal,
    currentTargetSequence,
    currentTargetChar,
    startGame,
    stopGame,
    resumeGame,
    abandonChallenge,
    gameOver,
    updateCurrentMode,
    getRank,
  }
}

