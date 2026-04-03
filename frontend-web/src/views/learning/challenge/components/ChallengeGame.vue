<template>
  <el-row :gutter="24" class="game-layout">
    <el-col :span="10" :xs="24">
      <div class="task-panel">
        <div class="mode-display" v-if="isPlaying">
          <el-tag :type="getModeTagType(currentMode)" size="large">
            {{ getModeText(currentMode) }}
          </el-tag>
          <el-tag v-if="challengeMode === 'questionSet'" type="info" size="large" style="margin-left: 8px">
            {{ currentQuestionSetName }}
          </el-tag>
        </div>

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

        <div class="word-display-area">
          <div class="word-progress">
            第 {{ currentWordIndex + 1 }} / {{ totalWords }} 题
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
                matched: index < matchedCount,
                active: index === matchedCount,
              }"
            >
              {{ char }}
            </div>
          </div>

          <div v-if="currentQuestion" class="question-info">
            <el-tag :type="getDifficultyTagType(currentQuestion.difficulty)" size="small">
              {{ getDifficultyText(currentQuestion.difficulty) }}
            </el-tag>
            <el-tag :type="getTypeTagType(currentQuestion.type)" size="small" style="margin-left: 8px">
              {{ getTypeText(currentQuestion.type) }}
            </el-tag>
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
            @click="$emit('start-game')"
          >
            <el-icon class="mr-2"><VideoPlay /></el-icon> 开始挑战
          </el-button>
          <el-button v-else type="danger" plain @click="$emit('stop-game')">
            结束挑战
          </el-button>
        </div>
      </div>
    </el-col>

    <el-col :span="14" :xs="24">
      <div class="camera-panel">
        <div class="video-wrapper">
          <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
          <canvas ref="overlayCanvasRef" class="overlay-canvas"></canvas>

          <div class="live-badge" :class="connectionState">
            <span class="live-dot"></span>
            <span>{{
              connectionState === 'connected' ? '识别中' :
              connectionState === 'connecting' || connectionState === 'new' ? '连接中' :
              '未连接'
            }}</span>
          </div>

          <div class="recognition-feedback" v-if="isPlaying">
            <div class="detected-tag">
              识别中: <span class="highlight">{{ lastDetectedChar || '...' }}</span>
            </div>
          </div>

          <div v-if="isPlaying && isRecognitionReady" class="stability-hud">
            <div class="stability-fill" :style="{ transform: `scaleX(${stabilityProgress})` }"></div>
            <span class="stability-text">稳定度 {{ Math.round(stabilityProgress * 100) }}%</span>
          </div>

          <div class="overlay" v-if="!isPlaying">
            <el-icon :size="60" color="#fff"><Trophy /></el-icon>
            <p>准备开始挑战！</p>
          </div>

          <div class="startup-overlay" v-else-if="!isRecognitionReady">
            <div class="startup-card">
              <div class="startup-dot"></div>
              <p class="startup-title">正在连接挑战识别</p>
              <p class="startup-text">连接成功后将自动开始判题</p>
            </div>
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { VideoPlay, Trophy } from '@element-plus/icons-vue'

const props = defineProps<{
  isPlaying: boolean
  challengeMode: 'random' | 'questionSet'
  currentMode: 'english' | 'number' | 'chinese'
  currentQuestionSetName: string
  score: number
  currentWordIndex: number
  totalWords: number
  timeLeft: number
  currentWordOriginal: string
  currentTargetSequence: string[]
  matchedCount: number
  currentTargetChar: string
  lastDetectedChar: string
  currentQuestion: any
  stream: MediaStream | null
  connectionState: string
  isRecognitionReady: boolean
  stabilityProgress: number
  overlayResult: any
}>()

defineEmits<{
  'start-game': []
  'stop-game': []
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const overlayCanvasRef = ref<HTMLCanvasElement | null>(null)

const syncVideoStream = async () => {
  await nextTick()
  if (videoRef.value) {
    videoRef.value.srcObject = props.stream || null
  }
}

const resizeOverlay = () => {
  const canvas = overlayCanvasRef.value
  const video = videoRef.value
  if (!canvas || !video) return
  const width = video.clientWidth || video.videoWidth || 0
  const height = video.clientHeight || video.videoHeight || 0
  if (!width || !height) return
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width
    canvas.height = height
  }
}

const clearOverlay = () => {
  const canvas = overlayCanvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  ctx?.clearRect(0, 0, canvas.width, canvas.height)
}

const mapBoxToCanvas = (box: number[], srcW: number, srcH: number, dispW: number, dispH: number) => {
  const scale = Math.max(dispW / srcW, dispH / srcH)
  const renderedWidth = srcW * scale
  const renderedHeight = srcH * scale
  const offsetX = (dispW - renderedWidth) / 2
  const offsetY = (dispH - renderedHeight) / 2
  const x = offsetX + box[0] * scale
  const y = offsetY + box[1] * scale
  const width = (box[2] - box[0]) * scale
  const height = (box[3] - box[1]) * scale
  return [dispW - x - width, y, width, height]
}

const drawLabel = (ctx: CanvasRenderingContext2D, x: number, y: number, text: string, color: string) => {
  const labelY = Math.max(16, y - 6)
  ctx.font = '700 14px "Microsoft YaHei", "Segoe UI", sans-serif'
  ctx.lineWidth = 3
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.9)'
  ctx.strokeText(text, x, labelY)
  ctx.fillStyle = color
  ctx.fillText(text, x, labelY)
}

const renderOverlay = async () => {
  await nextTick()
  resizeOverlay()
  clearOverlay()

  const result = props.overlayResult
  const canvas = overlayCanvasRef.value
  if (!result || !canvas || !Array.isArray(result.hands) || !result.imageWidth || !result.imageHeight) {
    return
  }

  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.textBaseline = 'top'

  result.hands.forEach((hand: any) => {
    if (!Array.isArray(hand?.detections) || hand.detections.length === 0) return
    hand.detections.forEach((det: any) => {
      if (!det?.box || det.box.length < 4) return
      const [x, y, width, height] = mapBoxToCanvas(det.box, result.imageWidth, result.imageHeight, canvas.width, canvas.height)
      ctx.strokeStyle = '#ffb347'
      ctx.lineWidth = 3
      ctx.strokeRect(x, y, width, height)
      const confidence = typeof det.confidence === 'number' ? ` ${det.confidence.toFixed(2)}` : ''
      const label = `${det.label || ''}${confidence}`.trim()
      if (label) {
        drawLabel(ctx, x, y, label, '#ffb347')
      }
    })
  })
}

watch(() => props.stream, () => {
  void syncVideoStream()
}, { immediate: true })

watch(() => props.overlayResult, () => {
  void renderOverlay()
}, { deep: true })

watch(() => props.isPlaying, (playing) => {
  if (!playing) {
    clearOverlay()
  }
})

const getModeText = (mode: string) => {
  const map: Record<string, string> = {
    english: '英文拼写',
    number: '数字挑战',
    chinese: '中文拼音',
  }
  return map[mode] || mode
}

const getModeTagType = (mode: string) => {
  const map: Record<string, string> = {
    english: 'primary',
    number: 'warning',
    chinese: 'success',
  }
  return map[mode] || 'info'
}

const getTypeText = (type: number) => {
  const map: Record<number, string> = {
    1: '单词',
    2: '中文',
    3: '数字',
  }
  return map[type] || '未知'
}

const getTypeTagType = (type: number) => {
  const map: Record<number, string> = {
    1: 'primary',
    2: 'success',
    3: 'warning',
  }
  return map[type] || 'info'
}

const getDifficultyText = (difficulty: number) => {
  const map: Record<number, string> = {
    1: '简单',
    2: '中等',
    3: '困难',
  }
  return map[difficulty] || '未知'
}

const getDifficultyTagType = (difficulty: number) => {
  const map: Record<number, string> = {
    1: 'success',
    2: 'warning',
    3: 'danger',
  }
  return map[difficulty] || 'info'
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getHintImage = (char: string) => {
  if (/\d/.test(char)) {
    return `https://avatar.youzilite.us.kg/number/${char}.png`
  }
  return `https://avatar.youzilite.us.kg/letter/${char}.png`
}
</script>

<style scoped lang="scss">
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
        color: #6956ff;
      }

      &.progress {
        color: #67c23a;
      }

      &.time {
        color: #e6a23c;

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
      border: 2px solid #e4e7ed;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: bold;
      color: #c0c4cc;
      transition: all 0.3s;

      &.active {
        border-color: #6956ff;
        color: #6956ff;
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(105, 86, 255, 0.3);
      }

      &.matched {
        background-color: #67c23a;
        border-color: #67c23a;
        color: #fff;
      }
    }
  }

  .question-info {
    margin-top: 16px;
  }
}

.hint-area {
  background: #f2f3f5;
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
}

.video-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.camera-feed,
.overlay-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.camera-feed {
  object-fit: cover;
  transform: scaleX(-1);
}

.overlay-canvas {
  pointer-events: none;
  z-index: 2;
}

.overlay,
.startup-overlay {
  position: absolute;
  inset: 0;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4;
}

.overlay {
  background: rgba(0, 0, 0, 0.6);
  flex-direction: column;
  gap: 16px;

  p {
    font-size: 18px;
    margin: 0;
  }
}

.startup-overlay {
  background: rgba(11, 20, 16, 0.42);
  backdrop-filter: blur(6px);
}

.startup-card {
  max-width: 300px;
  padding: 18px 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 40px rgba(18, 42, 35, 0.16);
  text-align: center;
}

.startup-dot {
  width: 12px;
  height: 12px;
  margin: 0 auto 10px;
  border-radius: 50%;
  background: #2b8f61;
  box-shadow: 0 0 0 8px rgba(43, 143, 97, 0.14);
  animation: startupPulse 1.2s ease-in-out infinite;
}

.startup-title {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 700;
  color: #17312b;
}

.startup-text {
  margin: 0;
  font-size: 12px;
  color: #5f746c;
}

.live-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 4;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(17, 26, 22, 0.45);
  backdrop-filter: blur(8px);
  color: rgba(246, 251, 248, 0.9);
  font-size: 12px;
  font-weight: 600;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #3ddc97;
}

.live-badge.connecting,
.live-badge.new {
  .live-dot { background: #f0b54b; }
}

.live-badge.disconnected,
.live-badge.failed,
.live-badge.closed,
.live-badge.idle {
  .live-dot { background: #f25f5c; }
}

.recognition-feedback {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 4;
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
      color: #67c23a;
    }
  }
}

.stability-hud {
  position: absolute;
  left: 50%;
  bottom: 22px;
  transform: translateX(-50%);
  z-index: 4;
  min-width: 180px;
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.62);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.stability-fill {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(37, 161, 101, 0.18), rgba(103, 194, 58, 0.35));
  transform-origin: left center;
  transition: transform 0.15s ease;
}

.stability-text {
  position: relative;
  z-index: 1;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
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

@keyframes startupPulse {
  0%, 100% { box-shadow: 0 0 0 8px rgba(43, 143, 97, 0.14); }
  50% { box-shadow: 0 0 0 14px rgba(43, 143, 97, 0.05); }
}
</style>
