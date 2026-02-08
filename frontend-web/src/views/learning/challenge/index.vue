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
      @stop-game="() => stopGame(true)"
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

    <!-- 暂停对话框 -->
    <ChallengePauseDialog
      v-model="showPauseDialog"
      @resume="handleResume"
      @restart="handleRestartFromPause"
      @return="handleReturnFromPause"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, onUnmounted } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ChallengeConfig from './components/ChallengeConfig.vue'
import ChallengeGame from './components/ChallengeGame.vue'
import ChallengeResult from './components/ChallengeResult.vue'
import ChallengeHistory from './components/ChallengeHistory.vue'
import ChallengePauseDialog from './components/ChallengePauseDialog.vue'
import { startChallenge } from '@/api/challenge'
import { useChallengeConfig } from './composables/useChallengeConfig'
import { useChallengeGame } from './composables/useChallengeGame'

// 使用 composables
const configComposable = useChallengeConfig()
const {
  showConfig,
  challengeMode,
  selectedQuestionSetId,
  challengeTime,
  questionSetList,
  config,
  currentQuestionSetName,
  handleConfigUpdate,
  loadQuestionSets,
  loadQuestions
} = configComposable

// 传入 challengeTime 引用给游戏 composable
const gameComposable = useChallengeGame(challengeTime)
const {
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
  totalWords,
  currentWordOriginal,
  currentTargetSequence,
  currentTargetChar,
  startGame,
  stopGame,
  resumeGame,
  abandonChallenge,
  handleMatchSuccess,
  updateCurrentMode,
  getRank
} = gameComposable

const showHistoryDialog = ref(false)

// 开始挑战
const handleStartChallenge = async () => {
  const questions = await loadQuestions()
  if (!questions || questions.length === 0) {
    return
  }

  // 设置题目到游戏 composable
  currentQuestionList.value = questions
  currentWordIndex.value = 0
  currentQuestion.value = questions[0]
  updateCurrentMode()

  try {
    const questionIds = questions.map((q: any) => q.id)
    const res = await startChallenge({
      mode: challengeMode.value,
      questionSetId: challengeMode.value === 'questionSet' ? selectedQuestionSetId.value : null,
      questionIds,
      timeLimit: challengeTime.value
    })

    const data = res.data || {}
    gameComposable.challengeId.value = data.challengeId || ''
    
    showConfig.value = false
    setTimeout(() => {
      gameComposable.startGame()
    }, 100)
  } catch (error) {
    console.error('开始挑战失败', error)
    ElMessage.error('开始挑战失败，请稍后重试')
  }
}

// 继续挑战
const handleResume = () => {
  gameComposable.resumeGame()
}

// 从暂停对话框重新开始
const handleRestartFromPause = async () => {
  showPauseDialog.value = false
  
  if (challengeId.value) {
    await abandonChallenge()
  }
  
  challengeId.value = ''
  currentQuestionList.value = []
  
  await handleStartChallenge()
}

// 从暂停对话框返回
const handleReturnFromPause = async () => {
  showPauseDialog.value = false
  
  if (challengeId.value) {
    await abandonChallenge()
  }
  
  showConfig.value = true
  currentQuestionList.value = []
  challengeId.value = ''
}

// 返回配置
const handleBackToConfig = async () => {
  if (isPlaying.value && challengeId.value) {
    await abandonChallenge()
  }
  showResult.value = false
  showConfig.value = true
  stopGame(false)
  currentQuestionList.value = []
  challengeId.value = ''
}

// 重新开始
const handleRestart = async () => {
  showResult.value = false
  const questions = await loadQuestions()
  if (questions && questions.length > 0) {
    currentQuestionList.value = questions
    currentWordIndex.value = 0
    currentQuestion.value = questions[0]
    updateCurrentMode()
    
    try {
      const questionIds = questions.map((q: any) => q.id)
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

// 初始化
onMounted(() => {
  loadQuestionSets()
})

// 路由离开前，放弃进行中的挑战
onBeforeRouteLeave(async (to, from, next) => {
  if (isPlaying.value && challengeId.value) {
    await abandonChallenge()
  }
  next()
})

// 组件卸载时，放弃进行中的挑战
onBeforeUnmount(async () => {
  if (isPlaying.value && challengeId.value) {
    await abandonChallenge()
  }
  stopGame(false)
})

onUnmounted(() => {
  stopGame(false)
})
</script>

<style scoped lang="scss">
.challenge-container {
  padding: 0 24px 24px 24px;
  min-height: calc(100vh - 84px);
  background-color: #f5f7fa;
  margin-top: -84px;
  padding-top: 84px;
}

.top-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  margin-bottom: 5px;
}
</style>
