<template>
  <div class="challenge-container">
    <!-- 配置界面：选择挑战模式和题库 -->
    <el-card v-if="showConfig" class="config-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="header-title">🎯 挑战配置</span>
        </div>
      </template>
      
      <div class="config-content">
        <!-- 挑战模式选择 -->
        <div class="config-section">
          <div class="section-title">选择挑战模式</div>
          <el-radio-group v-model="challengeMode" size="large" class="mode-group">
            <el-radio-button label="random">
              <el-icon><Refresh /></el-icon>
              <span>随机挑战</span>
            </el-radio-button>
            <el-radio-button label="questionSet">
              <el-icon><Collection /></el-icon>
              <span>选择题库</span>
            </el-radio-button>
          </el-radio-group>
        </div>

        <!-- 题库选择（仅在选择题库模式时显示） -->
        <div class="config-section" v-if="challengeMode === 'questionSet'">
          <div class="section-title">选择题库</div>
          <el-select
            v-model="selectedQuestionSetId"
            placeholder="请选择题库"
            size="large"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="set in questionSetList"
              :key="set.id"
              :label="set.name"
              :value="set.id"
            >
              <div class="question-set-option">
                <span>{{ set.name }}</span>
                <el-tag size="small" type="info" style="margin-left: 8px">
                  {{ set.questionCount }} 道题
                </el-tag>
              </div>
            </el-option>
          </el-select>
          <div v-if="selectedQuestionSet" class="question-set-info">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="题库描述">
                {{ selectedQuestionSet.description || '暂无描述' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <!-- 随机选择选项 -->
          <div class="random-option" style="margin-top: 16px">
            <el-checkbox v-model="randomFromQuestionSet" size="large">
              <span>从题库中随机选择题目</span>
            </el-checkbox>
            <div class="option-tip">
              <el-text type="info" size="small">
                开启后将从题库中随机选择指定数量的题目，否则按顺序选择
              </el-text>
            </div>
          </div>
        </div>

        <!-- 题目类型选择（仅在随机挑战模式显示） -->
        <div class="config-section" v-if="challengeMode === 'random'">
          <div class="section-title">选择题目类型</div>
          <el-checkbox-group v-model="selectedTypes" class="type-group">
            <el-checkbox label="1" size="large">
              <el-icon><Document /></el-icon>
              <span>单词</span>
            </el-checkbox>
            <el-checkbox label="2" size="large">
              <el-icon><EditPen /></el-icon>
              <span>中文</span>
            </el-checkbox>
            <el-checkbox label="3" size="large">
              <el-icon><Money /></el-icon>
              <span>数字</span>
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 难度选择（仅在随机挑战模式显示） -->
        <div class="config-section" v-if="challengeMode === 'random'">
          <div class="section-title">难度等级（可选）</div>
          <el-checkbox-group v-model="selectedDifficulties" class="difficulty-group">
            <el-checkbox label="1" size="large">
              <el-tag type="success" size="small">简单</el-tag>
            </el-checkbox>
            <el-checkbox label="2" size="large">
              <el-tag type="warning" size="small">中等</el-tag>
            </el-checkbox>
            <el-checkbox label="3" size="large">
              <el-tag type="danger" size="small">困难</el-tag>
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 题目数量设置 -->
        <div class="config-section">
          <div class="section-title">题目数量</div>
          <template v-if="challengeMode === 'questionSet' && !randomFromQuestionSet">
            <!-- 题库模式且不随机：显示题库总题数，不可调整 -->
            <div class="question-count-display">
              <el-text type="info" size="large">
                将使用题库中的所有题目（共 {{ selectedQuestionSet?.questionCount || 0 }} 道题）
              </el-text>
            </div>
          </template>
          <template v-else>
            <!-- 随机挑战模式 或 题库模式且随机：可以设置数量 -->
            <el-slider
              v-model="questionCount"
              :min="5"
              :max="challengeMode === 'questionSet' && selectedQuestionSet ? selectedQuestionSet.questionCount : 50"
              :step="5"
              show-stops
              show-input
              :show-input-controls="false"
              :disabled="challengeMode === 'questionSet' && !randomFromQuestionSet"
              style="width: 100%"
            />
            <div class="slider-tip">
              {{ challengeMode === 'questionSet' ? '将从题库中' : '将' }}选择 {{ questionCount }} 道题目进行挑战
            </div>
          </template>
        </div>

        <!-- 挑战时间设置 -->
        <div class="config-section">
          <div class="section-title">挑战时间（秒）</div>
          <el-slider
            v-model="challengeTime"
            :min="30"
            :max="300"
            :step="10"
            show-stops
            show-input
            :show-input-controls="false"
            style="width: 100%"
          />
          <div class="slider-tip">
            挑战时间：{{ formatTime(challengeTime) }}（{{ Math.floor(challengeTime / 60) }} 分 {{ challengeTime % 60 }} 秒）
          </div>
        </div>

        <!-- 开始按钮 -->
        <div class="config-actions">
          <el-button
            type="primary"
            size="large"
            :icon="VideoPlay"
            :disabled="!canStart"
            @click="handleStartChallenge"
            style="width: 200px"
          >
            开始挑战
          </el-button>
          <div v-if="!canStart" class="error-tip">
            {{ getErrorTip() }}
          </div>
        </div>
      </div>
    </el-card>

    <!-- 游戏界面 -->
    <el-row v-if="!showConfig" :gutter="24" class="game-layout">
      <el-col :span="10" :xs="24">
        <div class="task-panel">
          <!-- 模式显示 -->
          <div class="mode-display" v-if="isPlaying">
            <el-tag :type="getModeTagType(currentMode)" size="large">
              {{ getModeText(currentMode) }}
            </el-tag>
            <el-tag v-if="challengeMode === 'questionSet'" type="info" size="large" style="margin-left: 8px">
              {{ currentQuestionSetName }}
            </el-tag>
          </div>

          <!-- 统计信息 -->
          <div class="stats-bar">
            <div class="stat-item">
              <span class="label">得分</span>
              <span class="value score">{{ score }}</span>
            </div>
            <div class="stat-item">
              <span class="label">进度</span>
              <span class="value progress">{{ currentWordIndex + 1 }} / {{ totalWords }}</span>
            </div>
            <div class="stat-item">
              <span class="label">倒计时</span>
              <span class="value time" :class="{ warning: timeLeft <= 10 }">
                {{ formatTime(timeLeft) }}
              </span>
            </div>
          </div>

          <!-- 题目显示区域 -->
          <div class="word-display-area">
            <div class="word-progress">
              第 {{ currentWordIndex + 1 }} / {{ totalWords }} 题
            </div>

            <!-- 中文模式显示汉字 -->
            <div v-if="currentMode === 'chinese'" class="chinese-char">
              {{ currentWordOriginal }}
            </div>

            <!-- 字母/数字容器 -->
            <div class="letter-container">
              <div
                v-for="(char, index) in currentTargetSequence"
                :key="index"
                class="letter-box"
                :class="{
                  'matched': index < matchedCount,
                  'active': index === matchedCount
                }"
              >
                {{ char }}
              </div>
            </div>

            <!-- 题目信息 -->
            <div v-if="currentQuestion" class="question-info">
              <el-tag :type="getDifficultyTagType(currentQuestion.difficulty)" size="small">
                {{ getDifficultyText(currentQuestion.difficulty) }}
              </el-tag>
              <el-tag :type="getTypeTagType(currentQuestion.type)" size="small" style="margin-left: 8px">
                {{ getTypeText(currentQuestion.type) }}
              </el-tag>
            </div>
          </div>

          <!-- 提示区域 -->
          <div class="hint-area" v-if="isPlaying">
            <p class="hint-text">
              {{ currentMode === 'chinese' ? '请打出对应拼音手势：' : '请做出手势：' }}
            </p>
            <div class="hint-card">
              <div class="target-char">{{ currentTargetChar }}</div>
              <img :src="getHintImage(currentTargetChar)" class="hint-img" />
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="control-area">
            <el-button
              v-if="!isPlaying && !showConfig"
              type="primary"
              size="large"
              class="start-btn"
              @click="startGame"
            >
              <el-icon class="mr-2"><VideoPlay /></el-icon> 开始挑战
            </el-button>
            <el-button v-else-if="isPlaying" type="danger" plain @click="stopGame">
              结束挑战
            </el-button>
          </div>
        </div>
      </el-col>

      <el-col :span="14" :xs="24">
        <div class="camera-panel">
          <div class="video-wrapper">
            <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
            <div class="overlay" v-if="!isPlaying">
              <el-icon :size="60" color="#fff"><Trophy /></el-icon>
              <p>准备开始挑战！</p>
            </div>
            <div class="recognition-feedback" v-if="isPlaying">
              <div class="detected-tag">
                识别中: <span class="highlight">{{ lastDetectedChar || '...' }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 结果对话框 -->
    <el-dialog v-model="showResult" title="挑战结束" width="400px" center>
      <div class="result-content">
        <div class="result-score">
          <el-icon :size="60" color="#6956FF"><Trophy /></el-icon>
          <h2>{{ score }} 分</h2>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="完成题目">{{ currentWordIndex }} / {{ totalWords }}</el-descriptions-item>
          <el-descriptions-item label="挑战模式">
            {{ challengeMode === 'random' ? '随机挑战' : '题库挑战' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用时间">{{ formatTime(challengeTime - timeLeft) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="handleBackToConfig">返回配置</el-button>
        <el-button type="primary" @click="handleRestart">再来一次</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue'
import { VideoPlay, Trophy, Refresh, Collection, Document, EditPen, Money } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { pinyin } from 'pinyin-pro'

// --- 配置状态 ---
const showConfig = ref(true)
const challengeMode = ref<'random' | 'questionSet'>('random')
const selectedQuestionSetId = ref<number | null>(null)
const randomFromQuestionSet = ref(true) // 从题库中随机选择
const selectedTypes = ref<string[]>(['1', '2', '3']) // 默认全选
const selectedDifficulties = ref<string[]>(['1', '2', '3']) // 默认全选
const questionCount = ref(20)
const challengeTime = ref(60) // 挑战时间（秒）

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

// --- 模拟题库数据 ---
const mockQuestionSets = [
  {
    id: 1,
    name: '基础词汇',
    description: '包含常用单词和基础词汇',
    questionCount: 30,
    status: 1
  },
  {
    id: 2,
    name: '数字练习',
    description: '0-9999 数字手语练习',
    questionCount: 25,
    status: 1
  },
  {
    id: 3,
    name: '日常用语',
    description: '日常交流常用中文词汇',
    questionCount: 40,
    status: 1
  },
  {
    id: 4,
    name: '综合挑战',
    description: '混合类型题目，适合进阶练习',
    questionCount: 50,
    status: 1
  }
]

const questionSetList = ref(mockQuestionSets)

// --- 模拟题目数据 ---
const mockQuestions = {
  // 类型1：单词
  word: [
    { id: 1, content: 'HELLO', type: 1, difficulty: 1, pinyin: null },
    { id: 2, content: 'WORLD', type: 1, difficulty: 1, pinyin: null },
    { id: 3, content: 'JAVA', type: 1, difficulty: 2, pinyin: null },
    { id: 4, content: 'VUE', type: 1, difficulty: 2, pinyin: null },
    { id: 5, content: 'YOLO', type: 1, difficulty: 3, pinyin: null },
    { id: 6, content: 'PYTHON', type: 1, difficulty: 2, pinyin: null },
    { id: 7, content: 'REACT', type: 1, difficulty: 2, pinyin: null },
    { id: 8, content: 'NODE', type: 1, difficulty: 1, pinyin: null },
    { id: 9, content: 'HTML', type: 1, difficulty: 1, pinyin: null },
    { id: 10, content: 'CSS', type: 1, difficulty: 1, pinyin: null }
  ],
  // 类型2：中文
  chinese: [
    { id: 11, content: '你好', type: 2, difficulty: 1, pinyin: 'ni hao' },
    { id: 12, content: '世界', type: 2, difficulty: 1, pinyin: 'shi jie' },
    { id: 13, content: '手语', type: 2, difficulty: 2, pinyin: 'shou yu' },
    { id: 14, content: '挑战', type: 2, difficulty: 2, pinyin: 'tiao zhan' },
    { id: 15, content: '加油', type: 2, difficulty: 1, pinyin: 'jia you' },
    { id: 16, content: '学习', type: 2, difficulty: 1, pinyin: 'xue xi' },
    { id: 17, content: '成功', type: 2, difficulty: 2, pinyin: 'cheng gong' },
    { id: 18, content: '努力', type: 2, difficulty: 2, pinyin: 'nu li' },
    { id: 19, content: '梦想', type: 2, difficulty: 3, pinyin: 'meng xiang' },
    { id: 20, content: '未来', type: 2, difficulty: 2, pinyin: 'wei lai' }
  ],
  // 类型3：数字
  number: [
    { id: 21, content: '520', type: 3, difficulty: 1, pinyin: null },
    { id: 22, content: '1314', type: 3, difficulty: 2, pinyin: null },
    { id: 23, content: '666', type: 3, difficulty: 1, pinyin: null },
    { id: 24, content: '123', type: 3, difficulty: 1, pinyin: null },
    { id: 25, content: '2025', type: 3, difficulty: 2, pinyin: null },
    { id: 26, content: '888', type: 3, difficulty: 1, pinyin: null },
    { id: 27, content: '999', type: 3, difficulty: 1, pinyin: null },
    { id: 28, content: '100', type: 3, difficulty: 1, pinyin: null },
    { id: 29, content: '2024', type: 3, difficulty: 2, pinyin: null },
    { id: 30, content: '365', type: 3, difficulty: 2, pinyin: null }
  ]
}

// --- 计算属性 ---
const selectedQuestionSet = computed(() => {
  if (!selectedQuestionSetId.value) return null
  return questionSetList.value.find(set => set.id === selectedQuestionSetId.value)
})

const canStart = computed(() => {
  if (challengeMode.value === 'questionSet' && !selectedQuestionSetId.value) {
    return false
  }
  if (selectedTypes.value.length === 0) {
    return false
  }
  return true
})

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
  return selectedQuestionSet.value?.name || ''
})

// --- 方法 ---
const getErrorTip = () => {
  if (challengeMode.value === 'questionSet' && !selectedQuestionSetId.value) {
    return '请选择题库'
  }
  if (challengeMode.value === 'random' && selectedTypes.value.length === 0) {
    return '请至少选择一种题目类型'
  }
  return ''
}

const getModeText = (mode: string) => {
  const map: Record<string, string> = {
    english: '英文拼写',
    number: '数字挑战',
    chinese: '中文拼音'
  }
  return map[mode] || mode
}

const getModeTagType = (mode: string) => {
  const map: Record<string, string> = {
    english: 'primary',
    number: 'warning',
    chinese: 'success'
  }
  return map[mode] || 'info'
}

const getTypeText = (type: number) => {
  const map: Record<number, string> = {
    1: '单词',
    2: '中文',
    3: '数字'
  }
  return map[type] || '未知'
}

const getTypeTagType = (type: number) => {
  const map: Record<number, string> = {
    1: 'primary',
    2: 'success',
    3: 'warning'
  }
  return map[type] || 'info'
}

const getDifficultyText = (difficulty: number) => {
  const map: Record<number, string> = {
    1: '简单',
    2: '中等',
    3: '困难'
  }
  return map[difficulty] || '未知'
}

const getDifficultyTagType = (difficulty: number) => {
  const map: Record<number, string> = {
    1: 'success',
    2: 'warning',
    3: 'danger'
  }
  return map[difficulty] || 'info'
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 加载题目
const loadQuestions = () => {
  let allQuestions: any[] = []

  if (challengeMode.value === 'random') {
    // 随机挑战模式：根据选择的类型筛选题目
    if (selectedTypes.value.includes('1')) {
      allQuestions = [...allQuestions, ...mockQuestions.word]
    }
    if (selectedTypes.value.includes('2')) {
      allQuestions = [...allQuestions, ...mockQuestions.chinese]
    }
    if (selectedTypes.value.includes('3')) {
      allQuestions = [...allQuestions, ...mockQuestions.number]
    }

    // 根据选择的难度筛选
    if (selectedDifficulties.value.length < 3) {
      allQuestions = allQuestions.filter(q =>
        selectedDifficulties.value.includes(String(q.difficulty))
      )
    }
  } else if (challengeMode.value === 'questionSet' && selectedQuestionSetId.value) {
    // 题库模式：从题库中获取题目（这里模拟，实际应该从后端获取）
    // 暂时使用所有题目作为模拟
    allQuestions = [
      ...mockQuestions.word,
      ...mockQuestions.chinese,
      ...mockQuestions.number
    ]
  }

  // 根据是否随机选择来决定题目顺序
  if (challengeMode.value === 'questionSet' && !randomFromQuestionSet.value) {
    // 按顺序选择（不随机）：使用所有题目
    currentQuestionList.value = allQuestions
  } else {
    // 随机打乱并选择指定数量的题目
    const shuffled = allQuestions.sort(() => Math.random() - 0.5)
    currentQuestionList.value = shuffled.slice(0, questionCount.value)
  }

  if (currentQuestionList.value.length === 0) {
    ElMessage.warning('没有符合条件的题目，请调整筛选条件')
    return false
  }

  // 设置第一题
  currentWordIndex.value = 0
  currentQuestion.value = currentQuestionList.value[0]
  updateCurrentMode()

  return true
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

const handleStartChallenge = () => {
  if (!loadQuestions()) {
    return
  }
  showConfig.value = false
  // 延迟一下，确保界面更新后再开始游戏
  setTimeout(() => {
    startGame()
  }, 100)
}

const startGame = () => {
  stopGame()
  
  isPlaying.value = true
  score.value = 0
  timeLeft.value = challengeTime.value // 使用配置的时间
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

const gameOver = () => {
  stopGame()
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

const getHintImage = (char: string) => {
  if (/\d/.test(char)) {
    return `https://avatar.youzilite.us.kg/number/${char}.png`
  }
  return `https://avatar.youzilite.us.kg/letter/${char}.png`
}

const handleBackToConfig = () => {
  showResult.value = false
  showConfig.value = true
  stopGame()
  currentQuestionList.value = []
}

const handleRestart = () => {
  showResult.value = false
  if (loadQuestions()) {
    startGame()
  }
}

// 监听题库选择变化
watch(selectedQuestionSetId, () => {
  // 可以在这里加载题库信息
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

.config-card {
  max-width: 800px;
  margin: 0 auto;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .config-content {
    .config-section {
      margin-bottom: 32px;
      
      .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #606266;
        margin-bottom: 16px;
      }
      
      .mode-group,
      .type-group,
      .difficulty-group {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
      
      .question-set-info {
        margin-top: 12px;
      }
      
      .random-option {
        padding: 12px;
        background: #f5f7fa;
        border-radius: 8px;
        
        .option-tip {
          margin-top: 8px;
          padding-left: 24px;
        }
      }
      
      .question-count-display {
        padding: 16px;
        background: #f0f2f5;
        border-radius: 8px;
        text-align: center;
      }
      
      .slider-tip {
        margin-top: 8px;
        font-size: 12px;
        color: #909399;
        text-align: center;
      }
    }
    
    .config-actions {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      margin-top: 32px;
      
      .error-tip {
        font-size: 12px;
        color: #f56c6c;
      }
    }
  }
}

.question-set-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.game-layout {
  margin-top: 0;
}

.task-panel {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  min-height: 600px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.mode-display {
  margin-bottom: 20px;
  text-align: center;
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    
    .label {
      font-size: 14px;
      color: #909399;
    }
    
    .value {
      font-size: 28px;
      font-weight: bold;
      
      &.score {
        color: #6956FF;
      }
      
      &.progress {
        color: #67C23A;
      }
      
      &.time {
        color: #E6A23C;
        
        &.warning {
          color: #f56c6c;
          animation: pulse 1s infinite;
        }
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.word-display-area {
  text-align: center;
  margin-bottom: 30px;
  flex: 1;
  
  .word-progress {
    font-size: 14px;
    color: #909399;
    margin-bottom: 20px;
  }
  
  .chinese-char {
    font-size: 48px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 20px;
    letter-spacing: 8px;
    animation: fadeIn 0.5s ease;
  }
  
  .letter-container {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
    
    .letter-box {
      width: 50px;
      height: 50px;
      border: 2px solid #E4E7ED;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: bold;
      color: #C0C4CC;
      transition: all 0.3s;
      
      &.active {
        border-color: #6956FF;
        color: #6956FF;
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(105, 86, 255, 0.3);
      }
      
      &.matched {
        background-color: #67C23A;
        border-color: #67C23A;
        color: #fff;
      }
    }
  }
  
  .question-info {
    margin-top: 16px;
  }
}

.hint-area {
  background: #F2F3F5;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-top: auto;
  
  .hint-text {
    font-size: 14px;
    color: #606266;
    margin-bottom: 16px;
  }
  
  .hint-card {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    
    .target-char {
      font-size: 48px;
      font-weight: bold;
      color: #303133;
    }
    
    .hint-img {
      height: 80px;
      object-fit: contain;
    }
  }
}

.control-area {
  margin-top: 20px;
  text-align: center;
  
  .start-btn {
    width: 200px;
    height: 50px;
    font-size: 16px;
  }
}

.camera-panel {
  background: #000;
  border-radius: 16px;
  height: 600px;
  overflow: hidden;
  position: relative;
  
  .video-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
    
    .camera-feed {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      
      p {
        font-size: 18px;
        margin: 0;
      }
    }
    
    .recognition-feedback {
      position: absolute;
      top: 20px;
      right: 20px;
      background: rgba(0, 0, 0, 0.7);
      padding: 8px 20px;
      border-radius: 20px;
      color: #fff;
      backdrop-filter: blur(5px);
      
      .detected-tag {
        font-size: 14px;
        
        .highlight {
          font-size: 18px;
          font-weight: bold;
          color: #67C23A;
        }
      }
    }
  }
}

.result-content {
  text-align: center;
  padding: 20px 0;
  
  .result-score {
    margin-bottom: 24px;
    
    h2 {
      font-size: 48px;
      color: #6956FF;
      margin: 16px 0 0 0;
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
