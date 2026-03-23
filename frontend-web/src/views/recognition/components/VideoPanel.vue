<template>
  <div class="video-panel">
    <div class="panel-header">
      <div>
        <p class="label">识别画面</p>
        <h2>{{ isCameraActive ? '正在采集摄像头画面' : '请先开启摄像头' }}</h2>
      </div>
      <div class="camera-state" :class="{ active: isCameraActive }">
        <span class="state-dot"></span>
        {{ isCameraActive ? '识别进行中' : '未开启' }}
      </div>
    </div>

    <div class="video-stage">
      <div v-if="!isCameraActive" class="placeholder-state">
        <div class="illustration-card">
          <div class="illustration-circle">
            <el-icon><VideoCameraFilled /></el-icon>
          </div>
          <h3>开启摄像头后开始识别</h3>
          <p>请保持环境光线稳定，并将手部放在画面中央区域，识别结果会实时显示在右侧。</p>
          <el-button class="primary-action" round size="large" @click="$emit('start')">
            <el-icon><VideoPlay /></el-icon>
            开启摄像头
          </el-button>
        </div>
      </div>

      <div v-else class="active-state">
        <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
        <div class="focus-frame"></div>

        <div class="status-strip">
          <div class="strip-main">
            <span class="live-chip">实时识别</span>
            <span class="strip-text">请保持手势稳定，识别结果将同步更新</span>
          </div>
          <div class="strip-metrics">
            <span>帧率 {{ fps > 0 ? fps : '--' }}</span>
            <span>延迟 {{ latency > 0 ? `${latency}ms` : '--' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="control-footer">
      <div class="footer-tip">
        {{ isCameraActive ? '识别完成后可直接关闭摄像头，页面内容会保留。' : '开启后可在当前页面持续进行识别。' }}
      </div>
      <div class="footer-actions">
        <el-button v-if="!isCameraActive" type="primary" round @click="$emit('start')">
          开启摄像头
        </el-button>
        <el-button v-else type="danger" plain round @click="$emit('stop')">
          关闭摄像头
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { VideoPlay, VideoCameraFilled } from '@element-plus/icons-vue'

const props = defineProps({
  isCameraActive: {
    type: Boolean,
    default: false
  },
  fps: {
    type: Number,
    default: 30
  },
  latency: {
    type: Number,
    default: 24
  },
  videoStream: {
    type: MediaStream,
    default: null
  }
})

defineEmits(['start', 'stop'])

const videoRef = ref(null)

watch(
  () => props.videoStream,
  (stream) => {
    if (stream && videoRef.value) {
      nextTick(() => {
        if (videoRef.value) {
          videoRef.value.srcObject = stream
        }
      })
      return
    }

    if (videoRef.value) {
      videoRef.value.srcObject = null
    }
  },
  { immediate: true }
)
</script>

<style lang="scss" scoped>
.video-panel {
  height: 680px;
  display: flex;
  flex-direction: column;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 24px 60px rgba(28, 43, 36, 0.08);
  overflow: hidden;
}

.panel-header {
  padding: 24px 28px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  h2 {
    margin: 6px 0 0;
    font-size: 24px;
    color: #152f29;
  }
}

.label {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6e837b;
}

.camera-state {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: #f1f4f2;
  color: #71817a;
  font-size: 13px;
  font-weight: 700;

  &.active {
    background: #edf7f0;
    color: #1b6a47;
  }
}

.state-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.video-stage {
  flex: 1;
  margin: 0 20px;
  border-radius: 24px;
  overflow: hidden;
  background:
    linear-gradient(180deg, #f6f8f7 0%, #eaf0ec 100%);
  position: relative;
}

.placeholder-state {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.illustration-card {
  max-width: 460px;
  text-align: center;

  h3 {
    margin: 0 0 10px;
    font-size: 28px;
    color: #16312a;
  }

  p {
    margin: 0 auto 28px;
    font-size: 15px;
    line-height: 1.7;
    color: #5f7069;
  }
}

.illustration-circle {
  width: 110px;
  height: 110px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 32px;
  background: linear-gradient(135deg, #dff0e8 0%, #f4f8f6 100%);
  color: #1d6a4a;
  font-size: 44px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.primary-action {
  min-width: 180px;
  height: 48px;
}

.active-state {
  width: 100%;
  height: 100%;
  position: relative;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
  background: #101614;
}

.focus-frame {
  position: absolute;
  inset: 11% 14%;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 28px;
  box-shadow:
    0 0 0 999px rgba(8, 15, 13, 0.14),
    inset 0 0 0 1px rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

.status-strip {
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: 20px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(18, 25, 23, 0.68);
  color: #f8fbf9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  backdrop-filter: blur(10px);
}

.strip-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.live-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(43, 182, 108, 0.16);
  color: #8af0b7;
  font-size: 12px;
  font-weight: 700;
}

.strip-text {
  font-size: 13px;
  color: rgba(248, 251, 249, 0.88);
}

.strip-metrics {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 12px;
  color: rgba(248, 251, 249, 0.72);
}

.control-footer {
  min-height: 86px;
  padding: 18px 28px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.footer-tip {
  font-size: 14px;
  line-height: 1.6;
  color: #6a7b74;
}

.footer-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

@media (max-width: 1200px) {
  .video-panel {
    height: 640px;
  }
}

@media (max-width: 767px) {
  .video-panel {
    height: auto;
    border-radius: 22px;
  }

  .panel-header {
    padding: 20px 20px 16px;
    flex-direction: column;
    align-items: flex-start;

    h2 {
      font-size: 20px;
    }
  }

  .video-stage {
    margin: 0 16px;
    min-height: 420px;
    border-radius: 20px;
  }

  .placeholder-state {
    padding: 24px 20px;
  }

  .illustration-card h3 {
    font-size: 24px;
  }

  .status-strip {
    left: 12px;
    right: 12px;
    bottom: 12px;
    flex-direction: column;
    align-items: flex-start;
  }

  .strip-main,
  .strip-metrics {
    width: 100%;
    flex-wrap: wrap;
  }

  .control-footer {
    padding: 16px 20px 20px;
    flex-direction: column;
    align-items: stretch;
  }

  .footer-actions {
    width: 100%;
  }

  .footer-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
