<template>
  <div class="video-panel">
    <div class="stage-shell">
      <div class="video-stage">
        <template v-if="isCameraActive">
          <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
          <canvas ref="overlayCanvasRef" class="overlay-canvas"></canvas>

          <div v-if="isRecognitionReady && actionToast" class="action-toast">
            <div class="action-toast-backdrop"></div>
            <div class="action-scan-line"></div>
            <div class="action-toast-card">
              <div class="action-toast-ring"></div>
              <div class="action-toast-title">{{ actionTitle || '动作反馈' }}</div>
              <div class="action-toast-text">{{ actionToast }}</div>
            </div>
          </div>

          <div v-if="!isRecognitionReady" class="startup-state">
            <div class="startup-card">
              <div class="startup-dot"></div>
              <p class="startup-title">正在连接识别服务</p>
              <p class="startup-text">
                摄像头开启后，系统会先完成连接与模型初始化，再开始显示识别结果。
              </p>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="placeholder-state">
            <div class="illustration-circle">
              <el-icon><VideoCameraFilled /></el-icon>
            </div>
            <p class="placeholder-title">开启摄像头后开始识别</p>
            <p class="placeholder-text">识别画面、坐标框和动作反馈会显示在这里。</p>
            <button class="text-trigger" type="button" @click="$emit('start')">
              开启摄像头
            </button>
          </div>
        </template>

        <div v-if="isCameraActive" class="status-strip">
          <div class="strip-main">
            <span class="live-chip">识别进行中</span>
            <span class="strip-text">正在持续接收视频并返回检测结果</span>
          </div>
          <div class="strip-metrics">
            <span>输入帧率 {{ inputFps > 0 ? inputFps : '--' }}</span>
            <span>识别帧率 {{ processedFps > 0 ? processedFps : '--' }}</span>
            <span>延迟 {{ latency > 0 ? `${latency}ms` : '--' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="control-zone">
      <p class="footer-tip">
        {{ isCameraActive ? '识别结果将通过 app_webrtc 实时返回。' : '开启摄像头后即可在当前页面进行识别。' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { VideoCameraFilled } from '@element-plus/icons-vue'

const props = defineProps({
  isCameraActive: {
    type: Boolean,
    default: false,
  },
  isRecognitionReady: {
    type: Boolean,
    default: false,
  },
  inputFps: {
    type: Number,
    default: 0,
  },
  processedFps: {
    type: Number,
    default: 0,
  },
  latency: {
    type: Number,
    default: 0,
  },
  videoStream: {
    type: MediaStream,
    default: null,
  },
  overlayResult: {
    type: Object,
    default: null,
  },
  actionToast: {
    type: String,
    default: '',
  },
  actionTitle: {
    type: String,
    default: '',
  },
})

defineEmits(['start', 'stop'])

const videoRef = ref(null)
const overlayCanvasRef = ref(null)

const syncVideoStream = async () => {
  await nextTick()
  if (!videoRef.value) {
    return
  }
  videoRef.value.srcObject = props.videoStream || null
}

const resizeOverlay = () => {
  const canvas = overlayCanvasRef.value
  const video = videoRef.value

  if (!canvas || !video) {
    return
  }

  const width = video.clientWidth || video.videoWidth || 0
  const height = video.clientHeight || video.videoHeight || 0

  if (!width || !height) {
    return
  }

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width
    canvas.height = height
  }
}

const clearOverlay = () => {
  const canvas = overlayCanvasRef.value
  if (!canvas) {
    return
  }
  const context = canvas.getContext('2d')
  context.clearRect(0, 0, canvas.width, canvas.height)
}

const mapBoxToCanvas = (box, sourceWidth, sourceHeight, displayWidth, displayHeight) => {
  const scale = Math.max(displayWidth / sourceWidth, displayHeight / sourceHeight)
  const renderedWidth = sourceWidth * scale
  const renderedHeight = sourceHeight * scale
  const offsetX = (displayWidth - renderedWidth) / 2
  const offsetY = (displayHeight - renderedHeight) / 2
  const x = offsetX + box[0] * scale
  const y = offsetY + box[1] * scale
  const width = (box[2] - box[0]) * scale
  const height = (box[3] - box[1]) * scale

  return [displayWidth - x - width, y, width, height]
}

const drawLabel = (context, x, y, text, color) => {
  const labelY = Math.max(16, y - 6)
  context.font = '700 14px "Microsoft YaHei", "Segoe UI", sans-serif'
  context.lineWidth = 3
  context.strokeStyle = 'rgba(0, 0, 0, 0.9)'
  context.strokeText(text, x, labelY)
  context.fillStyle = color
  context.fillText(text, x, labelY)
}

const renderOverlay = async () => {
  await nextTick()
  resizeOverlay()
  clearOverlay()

  const result = props.overlayResult
  const canvas = overlayCanvasRef.value

  if (!result || !canvas || !result.hands || !result.imageWidth || !result.imageHeight) {
    return
  }

  const context = canvas.getContext('2d')
  const displayWidth = canvas.width
  const displayHeight = canvas.height

  context.lineWidth = 3
  context.textBaseline = 'top'

  result.hands.forEach((hand) => {
    if (!hand.box || hand.box.length < 4) {
      return
    }

    const [x, y, width, height] = mapBoxToCanvas(
      hand.box,
      result.imageWidth,
      result.imageHeight,
      displayWidth,
      displayHeight,
    )

    context.strokeStyle = '#3ddc97'
    context.strokeRect(x, y, width, height)

    const confidence =
      typeof hand.confidence === 'number' ? ` ${hand.confidence.toFixed(2)}` : ''
    const labelText = `${hand.text || '手势'}${confidence}`
    drawLabel(context, x, y, labelText, '#3ddc97')
  })
}

watch(
  () => props.videoStream,
  () => {
    syncVideoStream()
  },
  { immediate: true },
)

watch(
  () => props.isCameraActive,
  () => {
    syncVideoStream()
    if (!props.isCameraActive) {
      clearOverlay()
    }
  },
  { immediate: true },
)

watch(
  () => props.overlayResult,
  () => {
    renderOverlay()
  },
  { deep: true },
)
</script>

<style lang="scss" scoped>
.video-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 24px;
  background: #ffffff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 14px 32px rgba(28, 43, 36, 0.06);
}

.stage-shell {
  width: 100%;
}

.video-stage {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 22px;
  overflow: hidden;
  background: linear-gradient(180deg, #eff4f1 0%, #e7eeea 100%);
}

.placeholder-state {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
}

.startup-state {
  position: absolute;
  inset: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 20, 16, 0.42);
  backdrop-filter: blur(6px);
}

.action-toast {
  position: absolute;
  inset: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  pointer-events: none;
  overflow: hidden;
}

.action-toast-backdrop {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at center, rgba(30, 122, 82, 0.22) 0%, rgba(30, 122, 82, 0.08) 32%, rgba(9, 18, 14, 0.56) 100%);
  animation: actionBackdropPulse 1.5s ease forwards;
}

.action-scan-line {
  position: absolute;
  left: -12%;
  right: -12%;
  top: 50%;
  height: 96px;
  transform: translateY(-50%) rotate(-8deg);
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(121, 237, 176, 0.1) 28%,
    rgba(121, 237, 176, 0.5) 50%,
    rgba(121, 237, 176, 0.1) 72%,
    rgba(255, 255, 255, 0) 100%
  );
  filter: blur(10px);
  animation: actionScanSweep 1.5s ease forwards;
}

.action-toast-card {
  position: relative;
  z-index: 1;
  min-width: 220px;
  max-width: 80%;
  padding: 22px 28px 20px;
  border-radius: 24px;
  background: rgba(18, 93, 62, 0.9);
  color: #ffffff;
  text-align: center;
  box-shadow: 0 24px 50px rgba(10, 38, 28, 0.32);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  animation: actionCardReveal 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.action-toast-ring {
  position: absolute;
  inset: -18px;
  border-radius: 30px;
  border: 1px solid rgba(132, 244, 191, 0.3);
  animation: actionRingPulse 1.5s ease-out forwards;
}

.action-toast-title {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: rgba(226, 255, 240, 0.8);
}

.action-toast-text {
  font-size: 30px;
  font-weight: 800;
  line-height: 1.15;
  text-shadow: 0 6px 20px rgba(5, 23, 16, 0.32);
}

.startup-card {
  max-width: 360px;
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
  font-size: 18px;
  font-weight: 700;
  color: #17312b;
}

.startup-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: #5f746c;
}

.illustration-circle {
  width: 68px;
  height: 68px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 22px;
  background: linear-gradient(135deg, #dceee4 0%, #f5f8f6 100%);
  color: #206846;
  font-size: 30px;
}

.placeholder-title {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 700;
  color: #18332c;
}

.placeholder-text {
  margin: 0 0 10px;
  max-width: 360px;
  font-size: 13px;
  line-height: 1.5;
  color: #648078;
}

.text-trigger {
  appearance: none;
  border: none;
  background: rgba(255, 255, 255, 0.86);
  color: #24584b;
  font-size: 13px;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(18, 42, 35, 0.08);
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
  background: #0e1512;
}

.overlay-canvas {
  z-index: 2;
  pointer-events: none;
}

.status-strip {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 16px;
  background: rgba(17, 26, 22, 0.62);
  color: #f6fbf8;
  backdrop-filter: blur(10px);
}

.strip-main {
  display: flex;
  align-items: center;
  gap: 10px;
}

.live-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(73, 188, 118, 0.18);
  color: #99f0bc;
  font-size: 11px;
  font-weight: 700;
}

.strip-text,
.strip-metrics {
  font-size: 12px;
  color: rgba(246, 251, 248, 0.86);
}

.strip-metrics {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(246, 251, 248, 0.72);
}

.control-zone {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.footer-tip {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #6f817a;
}

@keyframes startupPulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.12);
    opacity: 0.72;
  }
}

@keyframes actionBackdropPulse {
  0% {
    opacity: 0;
  }

  15% {
    opacity: 1;
  }

  85% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
}

@keyframes actionScanSweep {
  0% {
    opacity: 0;
    transform: translate(-24%, -50%) rotate(-8deg);
  }

  18% {
    opacity: 1;
  }

  70% {
    opacity: 1;
  }

  100% {
    opacity: 0;
    transform: translate(24%, -50%) rotate(-8deg);
  }
}

@keyframes actionCardReveal {
  0% {
    opacity: 0;
    transform: translateY(18px) scale(0.92);
  }

  16% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  82% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  100% {
    opacity: 0;
    transform: translateY(-10px) scale(1.03);
  }
}

@keyframes actionRingPulse {
  0% {
    opacity: 0;
    transform: scale(0.92);
  }

  18% {
    opacity: 1;
    transform: scale(1);
  }

  100% {
    opacity: 0;
    transform: scale(1.08);
  }
}

@media (max-width: 992px) {
  .video-panel {
    padding: 16px;
  }
}

@media (max-width: 767px) {
  .video-panel {
    padding: 16px;
    border-radius: 20px;
  }

  .video-stage {
    border-radius: 18px;
  }

  .status-strip {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-toast-card {
    min-width: 0;
    width: 100%;
    padding: 18px 20px 16px;
  }

  .action-toast-text {
    font-size: 24px;
  }

  .strip-main,
  .strip-metrics {
    flex-wrap: wrap;
  }

  .control-zone {
    align-items: stretch;
  }
}
</style>
