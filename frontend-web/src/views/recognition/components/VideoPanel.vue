<template>
  <div class="video-panel">
    <div class="stage-shell">
      <div class="video-stage">
        <template v-if="isCameraActive">
          <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
        </template>
        <template v-else>
          <div class="placeholder-state">
            <div class="illustration-circle">
              <el-icon><VideoCameraFilled /></el-icon>
            </div>
            <p class="placeholder-title">开启摄像头后开始识别</p>
            <p class="placeholder-text">系统会在此区域实时显示识别画面与反馈效果。</p>
            <button class="text-trigger" type="button" @click="$emit('start')">
              开启摄像头
            </button>
          </div>
        </template>

        <div v-if="isCameraActive" class="status-strip">
          <div class="strip-main">
            <span class="live-chip">实时识别</span>
            <span class="strip-text">摄像头画面已开启</span>
          </div>
          <div class="strip-metrics">
            <span>帧率 {{ fps > 0 ? fps : '--' }}</span>
            <span>延迟 {{ latency > 0 ? `${latency}ms` : '--' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="control-zone">
      <p class="footer-tip">
        {{ isCameraActive ? '关闭后会停止当前采集，页面中的识别信息会继续保留。' : '可在顶部标题栏右侧开启摄像头并开始识别。' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { VideoCameraFilled } from '@element-plus/icons-vue'

const props = defineProps({
  isCameraActive: {
    type: Boolean,
    default: false
  },
  fps: {
    type: Number,
    default: 0
  },
  latency: {
    type: Number,
    default: 0
  },
  videoStream: {
    type: MediaStream,
    default: null
  }
})

defineEmits(['start', 'stop'])

const videoRef = ref(null)

const syncVideoStream = async () => {
  await nextTick()

  if (!videoRef.value) {
    return
  }

  videoRef.value.srcObject = props.videoStream || null
}

watch(
  () => props.videoStream,
  () => {
    syncVideoStream()
  },
  { immediate: true }
)

watch(
  () => props.isCameraActive,
  () => {
    syncVideoStream()
  },
  { immediate: true }
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
  z-index: 1;
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

.camera-feed {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
  background: #0e1512;
}

.status-strip {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 16px;
  background: rgba(17, 26, 22, 0.62);
  color: #f6fbf8;
  z-index: 3;
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

  .panel-header h2 {
    font-size: 20px;
  }

  .video-stage {
    border-radius: 18px;
  }

  .status-strip {
    flex-direction: column;
    align-items: flex-start;
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
