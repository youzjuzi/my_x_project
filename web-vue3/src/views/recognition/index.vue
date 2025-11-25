<template>
  <div class="immersive-container">
    <header class="header">
      <div class="brand">
        <img src="@/assets/logo.svg" class="logo" alt="Logo" />
        <h1>ASL 实时手语交互系统</h1>
      </div>
      <div class="status-bar">
        <el-tag :type="wsStatus === 'connected' ? 'success' : 'danger'" effect="dark" round>
          <el-icon class="is-loading" v-if="wsStatus === 'connecting'"><Loading /></el-icon>
          {{ wsStatusText }}
        </el-tag>
        <el-button type="info" circle plain @click="goBack">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </header>

    <main class="main-content">
      <div class="glass-panel">

        <div class="vision-section">
          <div class="camera-wrapper">
            <video ref="videoElement" autoplay playsinline muted class="video-stream"></video>
            <canvas ref="canvasOverlay" class="canvas-overlay"></canvas>

            <div v-if="!isCameraOpen" class="camera-placeholder">
              <el-icon :size="60"><VideoCamera /></el-icon>
              <p>点击下方按钮启动视觉引擎</p>
              <el-button type="primary" size="large" round @click="toggleCamera(true)">
                启动识别
              </el-button>
            </div>

            <div v-if="isCameraOpen" class="fsm-badge" :class="fsmState">
              {{ fsmStateText }}
            </div>
          </div>

          <div class="control-bar">
            <el-button-group>
              <el-button :type="isCameraOpen ? 'danger' : 'success'" round @click="toggleCamera(!isCameraOpen)">
                {{ isCameraOpen ? '停止识别' : '开启摄像头' }}
              </el-button>
              <el-button type="primary" round plain @click="clearBuffer">清空输入</el-button>
            </el-button-group>
            <div class="metrics">
              <span>FPS: {{ fps }}</span>
              <el-divider direction="vertical" />
              <span>延迟: {{ latency }}ms</span>
            </div>
          </div>
        </div>

        <div class="interaction-section">
          <div class="current-sign">
            <div class="label">当前手势</div>
            <div class="char-display" :class="{ 'highlight': currentConf > 0.8 }">
              {{ currentChar || '--' }}
            </div>
            <div class="confidence-bar">
              <div class="bar-fill" :style="{ width: (currentConf * 100) + '%' }"></div>
            </div>
          </div>

          <div class="input-stream">
            <div class="stream-label">拼音序列</div>
            <div class="pinyin-box">
              {{ pinyinBuffer || '等待输入...' }}
              <span class="cursor">|</span>
            </div>
          </div>

          <div class="candidates">
            <div class="stream-label">AI 联想</div>
            <div class="word-list">
              <div
                v-for="(word, idx) in candidateWords"
                :key="idx"
                class="word-item"
                @click="confirmWord(word)"
              >
                <span class="idx">{{ idx + 1 }}</span>
                <span class="text">{{ word }}</span>
              </div>
            </div>
          </div>

          <div class="final-result">
            <div class="stream-label">翻译结果</div>
            <el-input
              v-model="finalText"
              type="textarea"
              :rows="3"
              readonly
              class="result-textarea"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { VideoCamera, SwitchButton, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

// --- 状态数据 ---
const videoElement = ref(null)
const canvasOverlay = ref(null)
const isCameraOpen = ref(false)
const ws = ref(null)
const wsStatus = ref('disconnected')

const currentChar = ref('')
const currentConf = ref(0)
const pinyinBuffer = ref('')
const finalText = ref('')
const candidateWords = ref(['你好', '拟好', '泥好']) // 模拟数据
const fsmState = ref('IDLE')
const fps = ref(0)
const latency = ref(35)

// --- 计算属性 ---
const wsStatusText = computed(() => {
  const map = { disconnected: '服务断开', connecting: '连接中...', connected: 'AI 在线' }
  return map[wsStatus.value]
})

const fsmStateText = computed(() => {
  const map = { IDLE: '空闲', PRE_ACTIVATE: '检测中...', TRIGGERED: '输入确认', LOCKED: '锁定' }
  return map[fsmState.value] || fsmState.value
})

// --- 核心方法 (简化版逻辑，核心WebSocket代码同上一个回答) ---
const toggleCamera = (status) => {
  if (status) {
    // 模拟开启摄像头逻辑
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
      videoElement.value.srcObject = stream
      isCameraOpen.value = true
      wsStatus.value = 'connected' // 模拟连接成功
    }).catch(() => ElMessage.error('无法调用摄像头'))
  } else {
    // 模拟关闭
    if(videoElement.value?.srcObject) {
      videoElement.value.srcObject.getTracks().forEach(t => t.stop())
    }
    isCameraOpen.value = false
    wsStatus.value = 'disconnected'
  }
}

const clearBuffer = () => {
  pinyinBuffer.value = ''
  finalText.value = ''
}

const goBack = () => {
  // 返回后台管理首页
  router.push('/')
}

const confirmWord = (word) => {
  finalText.value += word
  pinyinBuffer.value = ''
}

onUnmounted(() => {
  toggleCamera(false)
})
</script>

<style scoped lang="scss">
/* 全屏容器：深色科技背景 */
.immersive-container {
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle at top right, #1e2a3a, #0f172a);
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航 */
.header {
  height: 60px;
  padding: 0 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  .brand {
    display: flex;
    align-items: center;
    gap: 15px;
    .logo { height: 32px; }
    h1 { font-size: 18px; font-weight: 500; letter-spacing: 1px; margin: 0; }
  }

  .status-bar {
    display: flex;
    align-items: center;
    gap: 15px;
  }
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 磨砂玻璃面板 */
.glass-panel {
  width: 100%;
  max-width: 1400px;
  height: 85vh;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  display: flex;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* 左侧视觉区 */
.vision-section {
  flex: 2;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;

  .camera-wrapper {
    flex: 1;
    position: relative;
    background: #000;
    overflow: hidden;

    .video-stream, .canvas-overlay {
      width: 100%;
      height: 100%;
      object-fit: contain;
      position: absolute;
    }

    .camera-placeholder {
      position: absolute;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background: rgba(20, 20, 20, 0.9);
      z-index: 10;
      color: #666;
      p { margin: 20px 0; }
    }

    .fsm-badge {
      position: absolute;
      top: 20px;
      left: 20px;
      padding: 6px 16px;
      background: rgba(0,0,0,0.6);
      border-radius: 4px;
      font-size: 12px;
      font-weight: bold;
      border-left: 3px solid #666;

      &.PRE_ACTIVATE { border-color: #e6a23c; color: #e6a23c; }
      &.TRIGGERED { border-color: #409eff; color: #409eff; }
      &.LOCKED { border-color: #67c23a; color: #67c23a; }
    }
  }

  .control-bar {
    height: 80px;
    padding: 0 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0,0,0,0.2);

    .metrics {
      color: #666;
      font-family: monospace;
      font-size: 14px;
    }
  }
}

/* 右侧交互区 */
.interaction-section {
  flex: 1;
  padding: 30px;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.02);
  gap: 25px;

  .label, .stream-label {
    font-size: 12px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 8px;
    font-weight: bold;
  }

  /* 当前大字 */
  .current-sign {
    background: rgba(0,0,0,0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;

    .char-display {
      font-size: 100px;
      font-weight: 700;
      line-height: 1;
      color: #94a3b8;
      transition: all 0.2s;
      &.highlight { color: #38bdf8; text-shadow: 0 0 20px rgba(56, 189, 248, 0.5); }
    }

    .confidence-bar {
      height: 4px;
      background: #334155;
      margin-top: 10px;
      border-radius: 2px;
      .bar-fill { height: 100%; background: #38bdf8; transition: width 0.2s; }
    }
  }

  /* 拼音输入流 */
  .input-stream {
    .pinyin-box {
      font-size: 24px;
      font-family: monospace;
      padding: 15px;
      background: rgba(0,0,0,0.2);
      border-bottom: 2px solid #38bdf8;
      color: #fff;

      .cursor { animation: blink 1s infinite; color: #38bdf8; }
    }
  }

  /* 候选词 */
  .candidates {
    flex: 1;
    .word-list {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;

      .word-item {
        background: rgba(255,255,255,0.1);
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover { background: #38bdf8; color: #000; transform: translateY(-2px); }
        .idx { font-size: 12px; opacity: 0.7; margin-right: 5px; }
        .text { font-size: 16px; font-weight: 500; }
      }
    }
  }

  /* 最终结果 */
  .final-result {
    :deep(.el-textarea__inner) {
      background: rgba(0,0,0,0.3);
      border: 1px solid rgba(255,255,255,0.1);
      color: #fff;
      font-size: 16px;
      padding: 15px;
      box-shadow: none;

      &:focus { border-color: #38bdf8; }
    }
  }
}

@keyframes blink { 50% { opacity: 0; } }
</style>