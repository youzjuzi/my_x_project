import { ref, computed, type Ref } from 'vue'
import { pinyin } from 'pinyin-pro'
import { ElMessage } from 'element-plus'
import { submitChallenge } from '@/api/challenge'

export function useChallengeGame(challengeTimeRef?: Ref<number>) {
  // --- 游戏状态 ---
  const isPlaying = ref(false)
  const currentMode = ref<'english' | 'number' | 'chinese'>('chinese')
  const score = ref(0)
  const timeLeft = ref(60)
  const showResult = ref(false)
  const showPauseDialog = ref(false)
  const timer = ref<NodeJS.Timeout | null>(null)
  const recognitionTimer = ref<NodeJS.Timeout | null>(null)

  // --- 题目数据 ---
  const currentQuestionList = ref<any[]>([])
  const currentWordIndex = ref(0)
  const matchedCount = ref(0)
  const lastDetectedChar = ref('')
  const currentQuestion = ref<any>(null)
  const challengeId = ref<string>('')
  
  // 使用传入的 challengeTime 或创建新的
  const challengeTime = challengeTimeRef || ref(60)

  // --- 计算属性 ---
  const totalWords = computed(() => currentQuestionList.value.length)

  const currentWordOriginal = computed(() => {
    if (!currentQuestion.value) return ''
    return currentQuestion.value.content
  })

  const currentTargetSequence = computed(() => {
    const word = currentWordOriginal.value
    if (currentMode.value === 'chinese') {
      const py = pinyin(word, { toneType: 'none', type: 'string' }).toUpperCase().replace(/\s+/g, '')
      return py.split('')
    } else {
      return word.split('')
    }
  })

  const currentTargetChar = computed(() => {
    return currentTargetSequence.value[matchedCount.value]
  })

  // 更新当前模式
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
  }

  // 开始游戏
  const startGame = () => {
    // 清理之前的定时器
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
    if (recognitionTimer.value) {
      clearTimeout(recognitionTimer.value)
      recognitionTimer.value = null
    }
    
    isPlaying.value = true
    score.value = 0
    timeLeft.value = challengeTime.value
    currentWordIndex.value = 0
    matchedCount.value = 0
    lastDetectedChar.value = ''
    currentQuestion.value = currentQuestionList.value[0]
    updateCurrentMode()

    timer.value = setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) gameOver()
    }, 1000)

    mockRecognitionLoop()
  }

  // 停止游戏
  const stopGame = (showPause = true) => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
    if (recognitionTimer.value) {
      clearTimeout(recognitionTimer.value)
      recognitionTimer.value = null
    }
    isPlaying.value = false
    lastDetectedChar.value = ''
    
    if (showPause) {
      showPauseDialog.value = true
    }
  }

  // 继续挑战
  const resumeGame = () => {
    showPauseDialog.value = false
    isPlaying.value = true
    
    timer.value = setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) gameOver()
    }, 1000)
    
    mockRecognitionLoop()
  }

  // 放弃挑战
  const abandonChallenge = async () => {
    if (challengeId.value) {
      try {
        await submitChallenge({
          challengeId: challengeId.value,
          score: score.value,
          completedCount: currentWordIndex.value + 1,
          timeUsed: challengeTime.value - timeLeft.value,
          status: 2
        })
        console.log('挑战已标记为放弃')
      } catch (error) {
        console.error('放弃挑战失败', error)
      }
    }
  }

  // 游戏结束
  const gameOver = async () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
    if (recognitionTimer.value) {
      clearTimeout(recognitionTimer.value)
      recognitionTimer.value = null
    }
    isPlaying.value = false
    lastDetectedChar.value = ''
    
    if (challengeId.value) {
      try {
        await submitChallenge({
          challengeId: challengeId.value,
          score: score.value,
          completedCount: currentWordIndex.value + 1,
          timeUsed: challengeTime.value - timeLeft.value
        })
      } catch (error) {
        console.error('提交挑战结果失败', error)
      }
    }
    
    showResult.value = true
  }

  // 模拟识别循环
  const mockRecognitionLoop = () => {
    if (!isPlaying.value) {
      recognitionTimer.value = null
      return
    }
    recognitionTimer.value = setTimeout(() => {
      if (!isPlaying.value) {
        recognitionTimer.value = null
        return
      }
      const target = currentTargetChar.value
      // 模拟识别：80%正确率，20%错误率
      if (Math.random() > 0.2) {
        lastDetectedChar.value = target
        handleMatchSuccess()
      } else {
        lastDetectedChar.value = '?'
      }
      mockRecognitionLoop()
    }, 800)
  }

  // 匹配成功处理
  const handleMatchSuccess = () => {
    if (!isPlaying.value) return
    
    matchedCount.value++
    score.value += 10

    if (matchedCount.value >= currentTargetSequence.value.length) {
      if (currentWordIndex.value < totalWords.value - 1) {
        setTimeout(() => {
          if (!isPlaying.value) return
          currentWordIndex.value++
          matchedCount.value = 0
          currentQuestion.value = currentQuestionList.value[currentWordIndex.value]
          updateCurrentMode()
        }, 500)
      } else {
        gameOver()
      }
    }
  }

  // 获取等级
  const getRank = (accuracy: number) => {
    if (accuracy >= 0.9) return '优秀'
    if (accuracy >= 0.7) return '良好'
    if (accuracy >= 0.5) return '及格'
    return '一般'
  }

  return {
    // 状态
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
    // 计算属性
    totalWords,
    currentWordOriginal,
    currentTargetSequence,
    currentTargetChar,
    // 方法
    startGame,
    stopGame,
    resumeGame,
    abandonChallenge,
    gameOver,
    handleMatchSuccess,
    updateCurrentMode,
    getRank
  }
}

