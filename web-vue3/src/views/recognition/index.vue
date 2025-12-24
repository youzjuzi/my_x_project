<template>
  <div class="recognition-container">

    <div class="nav-header">
      <div class="back-capsule" @click="handleExit">
        <div class="icon-wrap">
          <el-icon><ArrowLeft /></el-icon>
        </div>
        <div class="text-content">
          <span class="title">结束识别</span>
          <span class="sub">返回首页</span>
        </div>
      </div>
    </div>

    <el-row :gutter="24" class="main-layout">
      <el-col :span="16" :xs="24">
        <VideoPanel
          :is-camera-active="isCameraActive"
          :fps="fps"
          :latency="latency"
          :video-stream="localStream"
          @start="startCamera"
          @stop="stopCamera"
        />
      </el-col>

      <el-col :span="8" :xs="24">
        <InteractionPanel
          :gesture-stream="gestureStream"
          :pinyin-buffer="pinyinBuffer"
          :candidates="candidates"
          :final-sentence="finalSentence"
          @select-candidate="selectCandidate"
          @copy="copyResult"
          @clear="clearAll"
          @speak="speakResult"
        />
      </el-col>
    </el-row>

    <!-- 退出确认弹窗 -->
    <ExitConfirmDialog
      v-model="exitDialogVisible"
      @confirm="confirmExit"
      @cancel="exitDialogVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import VideoPanel from './components/VideoPanel.vue'
import InteractionPanel from './components/InteractionPanel.vue'
import ExitConfirmDialog from './components/ExitConfirmDialog.vue'

const router = useRouter()

// --- 状态管理 ---
const isCameraActive = ref(false)
const fps = ref(30)
const latency = ref(24)
const gestureStream = ref([])
const pinyinBuffer = ref('')
const candidates = ref([])
const finalSentence = ref('')
const exitDialogVisible = ref(false)
let streamTimer = null
let localStream = null

// --- 核心逻辑 ---

const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    localStream = stream
    isCameraActive.value = true
    startMockData()
  } catch (err) {
    console.error(err)
    ElMessage.error('无法访问摄像头，请检查权限')
    isCameraActive.value = false
  }
}

const stopCamera = () => {
  isCameraActive.value = false
  clearInterval(streamTimer)

  // 停止硬件流
  if (localStream) {
    localStream.getTracks().forEach(track => {
      track.stop()
    })
    localStream = null
  }
}

const handleExit = () => {
  if (isCameraActive.value) {
    // 显示自定义弹窗
    exitDialogVisible.value = true
  } else {
    // 摄像头没开，直接退
    navigateBack()
  }
}

const confirmExit = () => {
  stopCamera()
  exitDialogVisible.value = false
  navigateBack()
}

const navigateBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

// --- 业务逻辑 (保持不变) ---
const selectCandidate = (word) => {
  finalSentence.value += word
  pinyinBuffer.value = ''
  candidates.value = []
  gestureStream.value = []
}
const clearAll = () => {
  finalSentence.value = ''
  pinyinBuffer.value = ''
  gestureStream.value = []
}
const copyResult = () => {
  navigator.clipboard.writeText(finalSentence.value)
  ElMessage.success('已复制')
}
const speakResult = () => { ElMessage.success('正在朗读...') }

const startMockData = () => {
  const chars = ['N', 'I', 'H', 'A', 'O']
  let i = 0
  streamTimer = setInterval(() => {
    if (i < chars.length) {
      gestureStream.value.push({ id: Date.now(), char: chars[i] })
      pinyinBuffer.value += chars[i].toLowerCase()
      i++
      if (gestureStream.value.length > 6) gestureStream.value.shift()
      
      // 模拟 FPS 和延迟波动
      fps.value = 28 + Math.floor(Math.random() * 4)
      latency.value = 20 + Math.floor(Math.random() * 10)
    } else if (i === chars.length) {
      candidates.value = ['你好', '拟好', '泥豪']
      i++
    } else {
      if (Math.random() > 0.95) {
        i = 0
        pinyinBuffer.value = ''
        gestureStream.value = []
        candidates.value = []
      }
    }
  }, 800)
}

// 🟢 生命周期保险：组件销毁前（比如按了浏览器后退键），强制关摄像头
onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped lang="scss">
.recognition-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
  position: relative;
  padding-top: 80px;
}

.nav-header {
  position: absolute;
  top: 20px;
  left: 24px;
  z-index: 999;
}

.back-capsule {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 8px 20px 8px 8px;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(0, 0, 0, 0.02);
  user-select: none;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    .icon-wrap {
      background: #f2f6fc;
      color: #6956FF;
    }
  }

  &:active {
    transform: scale(0.98);
  }

  .icon-wrap {
    width: 36px;
    height: 36px;
    background: #f5f7fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
    color: #606266;
    transition: all 0.3s;
    font-size: 18px;
  }

  .text-content {
    display: flex;
    flex-direction: column;

    .title {
      font-size: 14px;
      font-weight: 700;
      color: #303133;
      line-height: 1.2;
    }

    .sub {
      font-size: 11px;
      color: #909399;
    }
  }
}
</style>