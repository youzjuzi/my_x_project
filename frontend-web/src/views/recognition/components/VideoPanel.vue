<template>
  <div class="video-panel">
    <div class="video-stage">
      <div v-if="!isCameraActive" class="placeholder-state">
        <div class="illustration-circle">
          <img src="https://cdn-icons-png.flaticon.com/512/2620/2620582.png" alt="Hand Gesture" />
        </div>
        <h2>准备启动视觉引擎</h2>
        <p>请确保光线充足，并将手部置于摄像头可视范围内</p>
        <button class="pulse-button" @click="$emit('start')">
          <el-icon><VideoPlay /></el-icon> 启动识别
        </button>
      </div>

      <div v-else class="active-state">
        <video ref="videoRef" autoplay muted class="camera-feed"></video>
        <div class="scan-grid"></div>
        <div class="status-bar-glass">
          <div class="status-left">
            <span class="indicator blink"></span>
            <span class="text">AI Engine Running</span>
          </div>
          <div class="status-right">
            <span class="metric">FPS: <strong>{{ fps }}</strong></span>
            <span class="divider">|</span>
            <span class="metric">延迟: <strong>{{ latency }}ms</strong></span>
          </div>
        </div>
      </div>
    </div>

    <div class="control-footer" v-if="isCameraActive">
      <el-button type="danger" plain round icon="SwitchButton" @click="$emit('stop')">
        停止服务
      </el-button>
      <el-button type="info" text round icon="Setting">引擎配置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { VideoPlay, SwitchButton, Setting } from '@element-plus/icons-vue'

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

const emit = defineEmits(['start', 'stop'])

const videoRef = ref(null)

watch(() => props.videoStream, (stream) => {
  if (stream && videoRef.value) {
    nextTick(() => {
      videoRef.value.srcObject = stream
    })
  } else if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
.video-panel {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 640px;
  display: flex;
  flex-direction: column;
}

.video-stage {
  flex: 1;
  background: #000;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.placeholder-state {
  background: linear-gradient(135deg, #fff 0%, #f0f2f5 100%);
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;

  .illustration-circle {
    width: 120px;
    height: 120px;
    background: #F2F0FF;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    img {
      width: 60px;
      opacity: 0.8;
    }
  }

  h2 {
    color: #303133;
    margin-bottom: 10px;
    font-weight: 600;
  }

  p {
    color: #909399;
    margin-bottom: 30px;
    font-size: 14px;
  }

  .pulse-button {
    background: linear-gradient(90deg, #6956FF, #5340E8);
    color: #fff;
    border: none;
    padding: 15px 40px;
    border-radius: 50px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 10px 20px rgba(105, 86, 255, 0.3);
    transition: transform 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: pulse 2s infinite;

    &:hover {
      transform: scale(1.05);
    }

    &:active {
      transform: scale(0.95);
    }
  }
}

.active-state {
  width: 100%;
  height: 100%;
  position: relative;

  .camera-feed {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scaleX(-1);
  }

  .scan-grid {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(105, 86, 255, 0.1) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.5;
    pointer-events: none;
  }

  .status-bar-glass {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(10px);
    padding: 8px 20px;
    border-radius: 20px;
    display: flex;
    gap: 20px;
    color: #fff;
    font-size: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);

    .status-left,
    .status-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .indicator {
      width: 8px;
      height: 8px;
      background: #67C23A;
      border-radius: 50%;
      &.blink {
        animation: blink 1.5s infinite;
      }
    }

    .divider {
      opacity: 0.3;
    }
  }
}

.control-footer {
  height: 70px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(105, 86, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 15px rgba(105, 86, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(105, 86, 255, 0);
  }
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>

