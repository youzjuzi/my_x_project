<template>
  <div class="camera-panel">

    <!-- 摄像头画面 -->
    <template v-if="isCameraActive">
      <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
      <!-- YOLO 检测框 canvas overlay -->
      <canvas ref="overlayCanvasRef" class="overlay-canvas"></canvas>

      <!-- 连接中 overlay（摄像头已开，还未就绪） -->
      <div v-if="!isRecognitionReady" class="startup-overlay">
        <div class="startup-card">
          <div class="startup-dot"></div>
          <p class="startup-title">正在连接识别服务</p>
          <p class="startup-text">连接成功后将自动开始识别</p>
        </div>
      </div>

      <!-- 右上角：连接状态徽章 -->
      <div class="live-badge" :class="connectionState">
        <span class="live-dot"></span>
        <span>{{
          connectionState === 'connected' ? '识别中' :
          connectionState === 'connecting' || connectionState === 'new' ? '连接中' :
          '断开连接'
        }}</span>
      </div>

      <!-- 底部：稳定度进度浮层（复用 VideoPanel 设计） -->
      <div v-if="isRecognitionReady" class="stability-hud">
        <div class="input-display">
          <div class="stability-track" :style="{ transform: `scaleX(${stabilityProgress})` }"></div>
          <span class="detected-char" :style="detectedCharStyle">
            {{ pinyinBuffer ? pinyinBuffer.toUpperCase() : '…' }}
          </span>
        </div>

        <!-- 过关进度点 -->
        <div class="progress-dots">
          <span
            v-for="n in requiredCount"
            :key="n"
            class="dot"
            :class="{ filled: hitCount >= n }"
          ></span>
        </div>
      </div>
    </template>

    <!-- 摄像头未开启：占位 -->
    <template v-else>
      <div class="placeholder-state">
        <div class="placeholder-icon">
          <el-icon :size="40"><VideoCameraFilled /></el-icon>
        </div>
        <p class="placeholder-title">开启摄像头开始练习</p>
        <button class="start-btn" @click="$emit('start-camera')">开启摄像头</button>
      </div>
    </template>

    <!-- 左上角：标签 -->
    <div class="panel-label">我的练习</div>

    <!-- 过关庆祝层 -->
    <PassCelebration
      :visible="showCelebration"
      :char="targetLabel"
      :passed-count="passedCountForMode"
      :total-count="totalCount"
      :mode="mode"
      @next="$emit('next-char')"
      @dismiss="$emit('dismiss-celebration')"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { VideoCameraFilled } from '@element-plus/icons-vue'
import PassCelebration from './PassCelebration.vue'

const props = defineProps({
  stream:             { type: MediaStream, default: null },
  isCameraActive:     { type: Boolean, default: false },
  isRecognitionReady: { type: Boolean, default: false },
  connectionState:    { type: String, default: 'idle' },
  pinyinBuffer:       { type: String, default: '' },
  stabilityProgress:  { type: Number, default: 0 },
  hitCount:           { type: Number, default: 0 },
  requiredCount:      { type: Number, default: 3 },
  overlayResult:      { type: Object, default: null },
  // ----- 新增 -----
  showCelebration:    { type: Boolean, default: false },
  targetLabel:        { type: String, default: '' },
  passedCount:        { type: Number, default: 0 },   // 当前模式已掌握数
  totalCount:         { type: Number, default: 26 },  // 当前模式总数
  mode:               { type: String, default: 'letters' },
})

defineEmits(['start-camera', 'next-char', 'dismiss-celebration'])

// 透传给 PassCelebration 的已掌握数量
const passedCountForMode = computed(() => props.passedCount)

const videoRef = ref(null)
const overlayCanvasRef = ref(null)

// 同时监听 videoRef（元素挂载）和 stream（数据到来）
watch(
  [videoRef, () => props.stream],
  ([el, newStream]) => {
    if (el) el.srcObject = newStream || null
  },
  { immediate: true }
)

// ========== canvas 监测诊断框绘制（复用 VideoPanel 逻辑） ==========
const resizeOverlay = () => {
  const canvas = overlayCanvasRef.value
  const video = videoRef.value
  if (!canvas || !video) return
  const w = video.clientWidth || video.videoWidth || 0
  const h = video.clientHeight || video.videoHeight || 0
  if (!w || !h) return
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w
    canvas.height = h
  }
}

const clearOverlay = () => {
  const canvas = overlayCanvasRef.value
  if (!canvas) return
  canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
}

const mapBoxToCanvas = (box, srcW, srcH, dispW, dispH) => {
  const scale = Math.max(dispW / srcW, dispH / srcH)
  const rW = srcW * scale
  const rH = srcH * scale
  const offX = (dispW - rW) / 2
  const offY = (dispH - rH) / 2
  const x = offX + box[0] * scale
  const y = offY + box[1] * scale
  const w = (box[2] - box[0]) * scale
  const h = (box[3] - box[1]) * scale
  return [dispW - x - w, y, w, h] // 镜像补偿
}

const drawLabel = (ctx, x, y, text, color) => {
  const lY = Math.max(16, y - 6)
  ctx.font = '700 14px "Microsoft YaHei", "Segoe UI", sans-serif'
  ctx.lineWidth = 3
  ctx.strokeStyle = 'rgba(0,0,0,0.9)'
  ctx.strokeText(text, x, lY)
  ctx.fillStyle = color
  ctx.fillText(text, x, lY)
}

const drawDetection = (ctx, det, srcW, srcH, dispW, dispH) => {
  if (!det?.box || det.box.length < 4) return
  const [x, y, w, h] = mapBoxToCanvas(det.box, srcW, srcH, dispW, dispH)
  ctx.strokeStyle = '#ffb347'
  ctx.lineWidth = 3
  ctx.strokeRect(x, y, w, h)
  const conf = typeof det.confidence === 'number' ? ` ${det.confidence.toFixed(2)}` : ''
  const label = `${det.label || ''}${conf}`.trim()
  if (label) drawLabel(ctx, x, y, label, '#ffb347')
}

const renderOverlay = async () => {
  await nextTick()
  resizeOverlay()
  clearOverlay()
  const result = props.overlayResult
  const canvas = overlayCanvasRef.value
  if (!result || !canvas || !result.hands || !result.imageWidth || !result.imageHeight) return
  const ctx = canvas.getContext('2d')
  ctx.textBaseline = 'top'
  result.hands.forEach(hand => {
    if (!Array.isArray(hand?.detections) || hand.detections.length === 0) return
    hand.detections.forEach(det => {
      drawDetection(ctx, det, result.imageWidth, result.imageHeight, canvas.width, canvas.height)
    })
  })
}

// 监听 检测结果更新
watch(() => props.overlayResult, () => renderOverlay(), { deep: true })

// 稳定度样式：越稳定越偏绿，同时有小动画
const detectedCharStyle = computed(() => {
  const p = Math.max(0, Math.min(1, props.stabilityProgress))
  const hue = Math.round(140 - p * 140) // 红→绿
  const scale = 1 + p * 0.1
  return {
    color: `hsl(${hue} 72% 62%)`,
    transform: `scale(${scale})`,
  }
})
</script>

<style scoped lang="scss">
.camera-panel {
  flex: 1;
  position: relative;
  border-radius: 22px;
  background: #1a1e1c;
  overflow: hidden;
  box-shadow: 0 14px 40px rgba(10, 22, 18, 0.15);
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); /* 镜像翻转 */
}

/* YOLO 检测框 canvas，必须覆盖在 video 之上且尺寸完全一致 */
.overlay-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

/* 左上角标签 */
.panel-label {
  position: absolute;
  top: 14px;
  left: 14px;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
  z-index: 3;
}

/* 连接状态徽章 */
.live-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  color: rgba(255, 255, 255, 0.75);
  font-size: 12px;
  font-weight: 600;

  .live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #888;
  }

  &.connected {
    .live-dot {
      background: #25a165;
      box-shadow: 0 0 0 3px rgba(37, 161, 101, 0.3);
      animation: pulse 1.5s ease-in-out infinite;
    }
  }

  &.connecting, &.new {
    .live-dot { background: #e6a23c; }
  }
}

/* 连接中 overlay */
.startup-overlay {
  position: absolute;
  inset: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: center;
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

/* 稳定度悬浮 HUD */
.stability-hud {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
}

.input-display {
  position: relative;
  min-width: 60px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.stability-track {
  position: absolute;
  inset: 0;
  border-radius: 6px;
  background: rgba(37, 161, 101, 0.25);
  transform-origin: left;
  transition: transform 0.15s ease;
}

.detected-char {
  position: relative;
  z-index: 1;
  font-size: 22px;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.85);
  transition: color 0.2s ease, transform 0.15s ease;
  line-height: 1;
}

/* 过关进度点 */
.progress-dots {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  transition: all 0.25s ease;

  &.filled {
    background: #25a165;
    box-shadow: 0 0 0 3px rgba(37, 161, 101, 0.35);
  }
}

/* 占位状态 */
.placeholder-state {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.placeholder-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.4);
}

.placeholder-title {
  margin: 0;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.55);
  font-weight: 500;
}

.start-btn {
  padding: 9px 22px;
  border-radius: 999px;
  border: none;
  background: #216d4b;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;

  &:hover {
    background: #1a5a3c;
    transform: translateY(-1px);
  }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(37, 161, 101, 0.3); }
  50%       { box-shadow: 0 0 0 6px rgba(37, 161, 101, 0.1); }
}

@keyframes startupPulse {
  0%, 100% { box-shadow: 0 0 0 8px rgba(43, 143, 97, 0.14); }
  50%       { box-shadow: 0 0 0 14px rgba(43, 143, 97, 0.05); }
}
</style>
