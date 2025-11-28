<template>
  <div class="challenge-container">
    <el-row :gutter="24" class="game-layout">

      <el-col :span="10" :xs="24">
        <div class="task-panel">

          <div class="mode-switch" v-if="!isPlaying">
            <el-radio-group v-model="currentMode" size="large" @change="handleModeChange">
              <el-radio-button label="english">🔤 英文拼写</el-radio-button>
              <el-radio-button label="number">🔢 数字挑战</el-radio-button>
              <el-radio-button label="chinese">🀄 中文拼音</el-radio-button>
            </el-radio-group>
          </div>

          <div class="stats-bar">
            <div class="stat-item">
              <span class="label">得分</span>
              <span class="value score">{{ score }}</span>
            </div>
            <div class="stat-item">
              <span class="label">倒计时</span>
              <span class="value time" :class="{ warning: timeLeft <= 10 }">{{ timeLeft }}s</span>
            </div>
          </div>

          <div class="word-display-area">
            <div class="word-progress">
              第 {{ currentWordIndex + 1 }} / {{ totalWords }} 关
            </div>

            <div v-if="currentMode === 'chinese'" class="chinese-char">
              {{ currentWordOriginal }}
            </div>

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
          </div>

          <div class="hint-area" v-if="isPlaying">
            <p class="hint-text">
              {{ currentMode === 'chinese' ? '请打出对应拼音手势：' : '请做出手势：' }}
            </p>
            <div class="hint-card">
              <div class="target-char">{{ currentTargetChar }}</div>
              <img :src="getHintImage(currentTargetChar)" class="hint-img" />
            </div>
          </div>

          <div class="control-area">
            <el-button
              v-if="!isPlaying"
              type="primary"
              size="large"
              class="start-btn"
              @click="startGame"
            >
              <el-icon class="mr-2"><VideoPlay /></el-icon> 开始{{ modeName }}挑战
            </el-button>
            <el-button v-else type="danger" plain @click="stopGame">结束</el-button>
          </div>
        </div>
      </el-col>

      <el-col :span="14" :xs="24">
        <div class="camera-panel">
          <div class="video-wrapper">
            <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
            <div class="overlay" v-if="!isPlaying">
              <el-icon :size="60" color="#fff"><Trophy /></el-icon>
              <p>选择模式，开始挑战！</p>
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

    <el-dialog v-model="showResult" title="挑战结束" width="30%" center>
      <div class="result-content">
        <h2>{{ score }} 分</h2>
        <p>模式：{{ modeName }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showResult = false">再来一次</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { VideoPlay, Trophy } from '@element-plus/icons-vue'
import { pinyin } from 'pinyin-pro' // 引入拼音库

// --- 状态定义 ---
const isPlaying = ref(false)
const currentMode = ref('chinese') // english, number, chinese
const score = ref(0)
const timeLeft = ref(60)
const showResult = ref(false)
const timer = ref(null)

// --- 题库数据 ---
const banks = {
  english: ['HELLO', 'WORLD', 'JAVA', 'VUE', 'YOLO'],
  number: ['520', '1314', '666', '123', '2025'], // 数字题库
  chinese: ['你好', '世界', '手语', '挑战', '加油'] // 中文题库
}

// 游戏运行时状态
const currentWordIndex = ref(0)
const matchedCount = ref(0)
const lastDetectedChar = ref('')
const recognitionTimer = ref(null) // 识别循环的定时器

// --- 核心计算属性 ---

// 1. 当前模式的名称
const modeName = computed(() => {
  const map = { english: '英文', number: '数字', chinese: '中文' }
  return map[currentMode.value]
})

// 2. 当前题目总数
const totalWords = computed(() => banks[currentMode.value].length)

// 3. 当前原始题目 (例如: "HELLO" 或 "你好")
const currentWordOriginal = computed(() => {
  return banks[currentMode.value][currentWordIndex.value]
})

// 4. 将题目转换为“待打序列”
// - 英文/数字模式：直接 split 成数组
// - 中文模式：转换成大写拼音数组 (你好 -> ['N','I','H','A','O'])
const currentTargetSequence = computed(() => {
  const word = currentWordOriginal.value
  if (currentMode.value === 'chinese') {
    // 使用 pinyin-pro 将汉字转为不带音调的大写拼音，去空格
    // '你好' -> 'NI HAO' -> 'NIHAO' -> ['N','I','H','A','O']
    const py = pinyin(word, { toneType: 'none', type: 'string' }).toUpperCase().replace(/\s+/g, '')
    return py.split('')
  } else {
    return word.split('')
  }
})

// 5. 当前需要打的字符
const currentTargetChar = computed(() => {
  return currentTargetSequence.value[matchedCount.value]
})

// --- 游戏逻辑 ---

const startGame = () => {
  // 先停止之前的游戏（如果存在）
  stopGame()
  
  isPlaying.value = true
  score.value = 0
  timeLeft.value = 60
  currentWordIndex.value = 0
  matchedCount.value = 0
  lastDetectedChar.value = ''

  timer.value = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) gameOver()
  }, 1000)

  mockRecognitionLoop()
}

const stopGame = () => {
  clearInterval(timer.value)
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

// 模拟识别 (对接后端 WebSocket 时替换这里)
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
    // 模拟识别成功 (实际逻辑：如果后端返回的 label === target)
    if (Math.random() > 0.6) {
      lastDetectedChar.value = target
      handleMatchSuccess()
    } else {
      lastDetectedChar.value = '?'
    }
    mockRecognitionLoop()
  }, 800)
}

const handleModeChange = () => {
  // 切换模式时，如果游戏正在运行，先停止
  if (isPlaying.value) {
    stopGame()
  }
}

const handleMatchSuccess = () => {
  if (!isPlaying.value) return // 确保游戏还在进行中
  
  matchedCount.value++
  score.value += 10

  // 检查是否拼完当前词
  if (matchedCount.value >= currentTargetSequence.value.length) {
    if (currentWordIndex.value < totalWords.value - 1) {
      setTimeout(() => {
        if (!isPlaying.value) return // 再次检查
        currentWordIndex.value++
        matchedCount.value = 0
      }, 500)
    } else {
      gameOver()
    }
  }
}

// 获取提示图 URL
const getHintImage = (char) => {
  // 数字处理
  if (/\d/.test(char)) {
    // 假设你有一些数字手势图，或者使用网络资源
    // 这里暂时用一个通用图占位，建议自己存一套 0-9.png 到 assets
    return `https://cdn-icons-png.flaticon.com/512/3564/35640${char}.png`
  }
  // 字母处理
  return `https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/American_Sign_Language_letter_${char}.svg/1200px-American_Sign_Language_letter_${char}.svg.png`
}

onUnmounted(() => {
  clearInterval(timer.value)
  if (recognitionTimer.value) {
    clearTimeout(recognitionTimer.value)
    recognitionTimer.value = null
  }
})
</script>

<style scoped lang="scss">
/* 保持你原有的样式基础，增加以下几点 */

.mode-switch {
  text-align: center;
  margin-bottom: 30px;
}

.chinese-char {
  font-size: 48px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
  letter-spacing: 8px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 其他样式复用上一个回答的 scss 即可 */
.challenge-container { padding: 24px; min-height: calc(100vh - 84px); background-color: #f5f7fa; }
.task-panel { background: #fff; border-radius: 16px; padding: 30px; min-height: 600px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); display: flex; flex-direction: column; }
.stats-bar { display: flex; justify-content: space-between; margin-bottom: 20px; .stat-item { display: flex; flex-direction: column; align-items: center; .value { font-size: 24px; font-weight: bold; } .score { color: #6956FF; } } }
.word-display-area { text-align: center; margin-bottom: 30px; .letter-container { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; } .letter-box { width: 50px; height: 50px; border: 2px solid #E4E7ED; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: #C0C4CC; &.active { border-color: #6956FF; color: #6956FF; transform: scale(1.1); } &.matched { background-color: #67C23A; border-color: #67C23A; color: #fff; } } }
.hint-area { background: #F2F3F5; border-radius: 12px; padding: 15px; text-align: center; margin-top: auto; .hint-card { display: flex; align-items: center; justify-content: center; gap: 15px; .target-char { font-size: 32px; font-weight: bold; } .hint-img { height: 60px; object-fit: contain; } } }
.control-area { margin-top: 20px; text-align: center; }
.camera-panel { background: #000; border-radius: 16px; height: 600px; overflow: hidden; position: relative; .video-wrapper { width: 100%; height: 100%; .camera-feed { width: 100%; height: 100%; object-fit: cover; } .overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.6); color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; } .recognition-feedback { position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 20px; color: #fff; backdrop-filter: blur(5px); } } }
</style>