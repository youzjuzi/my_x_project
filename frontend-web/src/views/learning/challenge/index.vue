<template>
  <div class="challenge-container">
    <div class="top-actions" v-if="showConfig">
      <el-button type="info" :icon="Clock" @click="showHistoryDialog = true">
        查看挑战记录
      </el-button>
    </div>

    <ChallengeConfig
      v-if="showConfig"
      :config="config"
      :question-set-list="questionSetList"
      @update:config="handleConfigUpdate"
      @start="handleStartChallenge"
    />

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
      :stream="localStream"
      :connection-state="connectionState"
      :is-recognition-ready="isRecognitionReady"
      :stability-progress="stabilityProgress"
      :overlay-result="overlayResult"
      @start-game="handleManualStart"
      @stop-game="() => stopGame(true)"
    />

    <ChallengeResult
      v-model="showResult"
      :score="score"
      :completed-count="completedCount"
      :total-count="totalWords"
      :challenge-mode="challengeMode"
      :time-used="challengeTime - timeLeft"
      :accuracy="totalWords > 0 ? completedCount / totalWords : 0"
      :rank="getRank(totalWords > 0 ? completedCount / totalWords : 0)"
      @back-to-config="handleBackToConfig"
      @restart="handleRestart"
    />

    <ChallengeHistory v-model="showHistoryDialog" />

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
  loadQuestions,
} = configComposable

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
  updateCurrentMode,
  getRank,
} = gameComposable

const showHistoryDialog = ref(false)

const beginChallengePlay = async () => {
  const started = await startGame()
  if (started) {
    return true
  }

  if (challengeId.value) {
    await abandonChallenge()
  }
  challengeId.value = ''
  showConfig.value = true
  ElMessage.warning('挑战识别未连接成功，已返回配置页')
  return false
}

const handleStartChallenge = async () => {
  const questions = await loadQuestions()
  if (!questions || questions.length === 0) {
    return
  }

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
      timeLimit: challengeTime.value,
    })

    const data = res.data || {}
    challengeId.value = data.challengeId || ''
    showConfig.value = false
    await beginChallengePlay()
  } catch (error) {
    console.error('开始挑战失败', error)
    ElMessage.error('开始挑战失败，请稍后重试')
  }
}

const handleManualStart = async () => {
  await beginChallengePlay()
}

const handleResume = async () => {
  const resumed = await resumeGame()
  if (!resumed) {
    ElMessage.warning('挑战识别未恢复成功，请重新开始')
  }
}

const handleRestartFromPause = async () => {
  showPauseDialog.value = false

  if (challengeId.value) {
    await abandonChallenge()
  }

  challengeId.value = ''
  currentQuestionList.value = []
  await handleStartChallenge()
}

const handleReturnFromPause = async () => {
  showPauseDialog.value = false

  if (challengeId.value) {
    await abandonChallenge()
  }

  showConfig.value = true
  currentQuestionList.value = []
  challengeId.value = ''
}

const handleBackToConfig = async () => {
  if (challengeId.value && !showResult.value) {
    await abandonChallenge()
  }
  showResult.value = false
  showConfig.value = true
  stopGame(false)
  currentQuestionList.value = []
  challengeId.value = ''
}

const handleRestart = async () => {
  challengeId.value = ''
  showResult.value = false
  const questions = await loadQuestions()
  if (!questions || questions.length === 0) {
    return
  }

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
      timeLimit: challengeTime.value,
    })
    const data = res.data || {}
    challengeId.value = data.challengeId || ''
    await beginChallengePlay()
  } catch (error) {
    console.error('重新开始挑战失败', error)
    ElMessage.error('重新开始挑战失败，请稍后重试')
  }
}

onMounted(() => {
  loadQuestionSets()
})

onBeforeRouteLeave(async (to, from, next) => {
  if (challengeId.value && !showResult.value) {
    await abandonChallenge()
  }
  next()
})

onBeforeUnmount(async () => {
  if (challengeId.value && !showResult.value) {
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

