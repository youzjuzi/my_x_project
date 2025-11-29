<template>
  <div class="challenge-container">
    <!-- 顶部操作栏 -->
    <div class="top-actions" v-if="showConfig">
      <el-button type="info" :icon="Clock" @click="showHistoryDialog = true">
        查看挑战记录
      </el-button>
    </div>

    <!-- 配置界面 -->
    <ChallengeConfig
      v-if="showConfig"
      :config="config"
      :question-set-list="questionSetList"
      @update:config="handleConfigUpdate"
      @start="handleStartChallenge"
    />

    <!-- 游戏界面 -->
    <ChallengeGame
      v-if="!showConfig"
      :is-playing="isPlaying"
      :challenge-mode="challengeMode"
      :current-mode="currentMode"
      :current-question-set-name="currentQuestionSetName"
      :score="score"
      :current-word-index="currentWordIndex"
      :total-words="totalWords"
      :time-left="timeLeft"
      :current-word-original="currentWordOriginal"
      :current-target-sequence="currentTargetSequence"
      :matched-count="matchedCount"
      :current-target-char="currentTargetChar"
      :last-detected-char="lastDetectedChar"
      :current-question="currentQuestion"
      @start-game="startGame"
      @stop-game="stopGame"
    />

    <!-- 结果对话框 -->
    <ChallengeResult
      v-model="showResult"
      :score="score"
      :completed-count="currentWordIndex + 1"
      :total-count="totalWords"
      :challenge-mode="challengeMode"
      :time-used="challengeTime - timeLeft"
      :accuracy="totalWords > 0 ? (currentWordIndex + 1) / totalWords : 0"
      :rank="getRank((currentWordIndex + 1) / totalWords)"
      @back-to-config="handleBackToConfig"
      @restart="handleRestart"
    />

    <!-- 挑战记录对话框 -->
    <ChallengeHistory v-model="showHistoryDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch, onMounted } from 'vue'
import { Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { pinyin } from 'pinyin-pro'
import ChallengeConfig from './components/ChallengeConfig.vue'
import ChallengeGame from './components/ChallengeGame.vue'
import ChallengeResult from './components/ChallengeResult.vue'
import ChallengeHistory from './components/ChallengeHistory.vue'
import questionSetManage from '@/api/questionSetManage'
import { queryQuestions, startChallenge, submitChallenge } from '@/api/challenge'

// --- 配置状态 ---
const showConfig = ref(true)
const showHistoryDialog = ref(false)
const challengeMode = ref<'random' | 'questionSet'>('random')
const selectedQuestionSetId = ref<number | null>(null)
const randomFromQuestionSet = ref(true)
const selectedTypes = ref<string[]>(['1', '2', '3'])
const selectedDifficulties = ref<string[]>(['1', '2', '3'])
const questionCount = ref(20)
const challengeTime = ref(60)

// 配置对象（用于传递给组件）
const config = computed(() => ({
  challengeMode: challengeMode.value,
  selectedQuestionSetId: selectedQuestionSetId.value,
  randomFromQuestionSet: randomFromQuestionSet.value,
  selectedTypes: selectedTypes.value,
  selectedDifficulties: selectedDifficulties.value,
  questionCount: questionCount.value,
  challengeTime: challengeTime.value
}))

// --- 游戏状态 ---
const isPlaying = ref(false)
const currentMode = ref<'english' | 'number' | 'chinese'>('chinese')
const score = ref(0)
const timeLeft = ref(60)
const showResult = ref(false)
const timer = ref<NodeJS.Timeout | null>(null)

// --- 题目数据 ---
const currentQuestionList = ref<any[]>([])
const currentWordIndex = ref(0)
const matchedCount = ref(0)
const lastDetectedChar = ref('')
const recognitionTimer = ref<NodeJS.Timeout | null>(null)
const currentQuestion = ref<any>(null)
const challengeId = ref<string>('')

// --- 题库数据 ---
const questionSetList = ref<any[]>([])

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

const currentQuestionSetName = computed(() => {
  const set = questionSetList.value.find(s => s.id === selectedQuestionSetId.value)
  return set?.name || ''
})

// --- 方法 ---
const handleConfigUpdate = (key: string, value: any) => {
  switch (key) {
    case 'challengeMode':
      challengeMode.value = value
      break
    case 'selectedQuestionSetId':
      selectedQuestionSetId.value = value
      break
    case 'randomFromQuestionSet':
      randomFromQuestionSet.value = value
      break
    case 'selectedTypes':
      selectedTypes.value = value
      break
    case 'selectedDifficulties':
      selectedDifficulties.value = value
      break
    case 'questionCount':
      questionCount.value = value
      break
    case 'challengeTime':
      challengeTime.value = value
      break
  }
}

// 加载题库列表
const loadQuestionSets = async () => {
  try {
    const res = await questionSetManage.getAllQuestionSets()
    if (res.data) {
      // 为每个题库获取题目数量
      const setsWithCount = await Promise.all(
        res.data.map(async (set: any) => {
          try {
            const questionIdsRes = await questionSetManage.getQuestionIdsByQuestionSetId(set.id)
            const questionCount = questionIdsRes.data?.length || 0
            return {
              ...set,
              questionCount
            }
          } catch (error) {
            console.error(`获取题库 ${set.id} 的题目数量失败`, error)
            return {
              ...set,
              questionCount: 0
            }
          }
        })
      )
      questionSetList.value = setsWithCount
    }
  } catch (error) {
    console.error('加载题库列表失败', error)
  }
}

// 加载题目
const loadQuestions = async () => {
  try {
    const params: any = {
      mode: challengeMode.value,
      count: questionCount.value,
      random: challengeMode.value === 'questionSet' ? randomFromQuestionSet.value : true
    }

    if (challengeMode.value === 'random') {
      params.types = selectedTypes.value.join(',')
      if (selectedDifficulties.value.length > 0) {
        params.difficulties = selectedDifficulties.value.join(',')
      }
    } else if (challengeMode.value === 'questionSet' && selectedQuestionSetId.value) {
      params.questionSetId = selectedQuestionSetId.value
    }

    const res = await queryQuestions(params)
    const data = res.data || {}
    const questions = data.questions || []

    if (questions.length === 0) {
      ElMessage.warning('没有符合条件的题目，请调整筛选条件')
      return false
    }

    currentQuestionList.value = questions
    currentWordIndex.value = 0
    currentQuestion.value = questions[0]
    updateCurrentMode()

    return true
  } catch (error) {
    console.error('加载题目失败', error)
    ElMessage.error('加载题目失败，请稍后重试')
    return false
  }
}

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

const handleStartChallenge = async () => {
  if (!(await loadQuestions())) {
    return
  }

  // 调用后端接口开始挑战
  try {
    const questionIds = currentQuestionList.value.map(q => q.id)
    const res = await startChallenge({
      mode: challengeMode.value,
      questionSetId: challengeMode.value === 'questionSet' ? selectedQuestionSetId.value : null,
      questionIds,
      timeLimit: challengeTime.value
    })

    const data = res.data || {}
    challengeId.value = data.challengeId || ''
    
    showConfig.value = false
    setTimeout(() => {
      startGame()
    }, 100)
  } catch (error) {
    console.error('开始挑战失败', error)
    ElMessage.error('开始挑战失败，请稍后重试')
  }
}

const startGame = () => {
  stopGame()
  
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

const stopGame = () => {
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
}

const gameOver = async () => {
  stopGame()
  
  // 提交挑战结果
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
    // 模拟识别成功
    if (Math.random() > 0.6) {
      lastDetectedChar.value = target
      handleMatchSuccess()
    } else {
      lastDetectedChar.value = '?'
    }
    mockRecognitionLoop()
  }, 800)
}

const handleMatchSuccess = () => {
  if (!isPlaying.value) return
  
  matchedCount.value++
  score.value += 10

  // 检查是否拼完当前词
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

const handleBackToConfig = () => {
  showResult.value = false
  showConfig.value = true
  stopGame()
  currentQuestionList.value = []
  challengeId.value = ''
}

const handleRestart = async () => {
  showResult.value = false
  if (await loadQuestions()) {
    // 重新开始挑战
    try {
      const questionIds = currentQuestionList.value.map(q => q.id)
      const res = await startChallenge({
        mode: challengeMode.value,
        questionSetId: challengeMode.value === 'questionSet' ? selectedQuestionSetId.value : null,
        questionIds,
        timeLimit: challengeTime.value
      })
      const data = res.data || {}
      challengeId.value = data.challengeId || ''
      startGame()
    } catch (error) {
      console.error('重新开始挑战失败', error)
      ElMessage.error('重新开始挑战失败，请稍后重试')
    }
  }
}

const getRank = (accuracy: number) => {
  if (accuracy >= 0.9) return '优秀'
  if (accuracy >= 0.7) return '良好'
  if (accuracy >= 0.5) return '及格'
  return '一般'
}

// 初始化
onMounted(() => {
  loadQuestionSets()
})

onUnmounted(() => {
  stopGame()
})
</script>

<style scoped lang="scss">
.challenge-container {
  padding: 24px;
  min-height: calc(100vh - 84px);
  background-color: #f5f7fa;
}

.top-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}
</style>

