<template>
  <div class="recognition-container">
    <div class="page-shell">
      <div class="hero-row">
        <div class="nav-header">
          <div class="back-capsule" @click="handleExit" aria-label="返回上一页">
            <div class="icon-wrap">
              <el-icon><ArrowLeft /></el-icon>
            </div>
          </div>
        </div>

        <div class="page-intro">
          <div class="intro-main">
            <p class="eyebrow">手势识别</p>
            <h1>通过摄像头实时识别手势内容</h1>
            <p class="description">
              开启摄像头后即可开始识别。左侧显示实时画面与追踪反馈，右侧同步展示识别过程、拼写状态和最终结果。
            </p>
          </div>
          <div class="intro-actions">
            <div class="intro-badge">
              <span class="status-dot" :class="{ active: isCameraActive }"></span>
              {{ isCameraActive ? '摄像头已开启' : '等待开启摄像头' }}
            </div>
            <el-button
              v-if="!isCameraActive"
              type="primary"
              class="hero-action"
              @click="startCamera"
            >
              开启摄像头
            </el-button>
            <el-button
              v-else
              type="danger"
              plain
              class="hero-action"
              @click="stopCamera"
            >
              关闭摄像头
            </el-button>
          </div>
        </div>
      </div>

      <el-row :gutter="18" class="main-layout">
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
    </div>

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

const isCameraActive = ref(false)
const fps = ref(0)
const latency = ref(0)
const gestureStream = ref([])
const pinyinBuffer = ref('')
const candidates = ref([])
const finalSentence = ref('')
const exitDialogVisible = ref(false)
const localStream = ref(null)

const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    localStream.value = stream
    isCameraActive.value = true
    fps.value = 0
    latency.value = 0
  } catch (err) {
    console.error(err)
    ElMessage.error('无法开启摄像头，请检查浏览器权限和设备是否可用。')
    isCameraActive.value = false
    localStream.value = null
  }
}

const stopCamera = () => {
  isCameraActive.value = false
  fps.value = 0
  latency.value = 0

  if (localStream.value) {
    localStream.value.getTracks().forEach((track) => {
      track.stop()
    })
    localStream.value = null
  }
}

const handleExit = () => {
  if (isCameraActive.value) {
    exitDialogVisible.value = true
    return
  }

  navigateBack()
}

const confirmExit = () => {
  stopCamera()
  exitDialogVisible.value = false
  navigateBack()
}

const navigateBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
    return
  }

  router.push('/')
}

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

const copyResult = async () => {
  if (!finalSentence.value) {
    return
  }

  await navigator.clipboard.writeText(finalSentence.value)
  ElMessage.success('识别结果已复制')
}

const speakResult = () => {
  ElMessage.success('正在朗读识别结果')
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped lang="scss">
.recognition-container {
  min-height: calc(100vh - 84px);
  padding: 16px 20px 18px;
  background: #f8faf9;
  overflow: hidden;
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.hero-row {
  display: flex;
  align-items: stretch;
  gap: 10px;
  margin-bottom: 10px;
}

.nav-header {
  flex-shrink: 0;
}

.back-capsule {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(26, 64, 50, 0.08);
  box-shadow: 0 6px 18px rgba(28, 43, 36, 0.05);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  user-select: none;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(28, 43, 36, 0.1);
  }
}

.icon-wrap {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #edf4f1;
  color: #22463b;
  font-size: 15px;
}

.page-intro {
  flex: 1;
  padding: 12px 16px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 10px 26px rgba(28, 43, 36, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.intro-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.intro-main {
  min-width: 0;
}

.eyebrow {
  margin: 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #688178;
}

.page-intro h1 {
  margin: 4px 0 4px;
  font-size: 24px;
  line-height: 1.15;
  color: #16312a;
}

.description {
  margin: 0;
  max-width: 760px;
  font-size: 13px;
  line-height: 1.5;
  color: #5d7169;
}

.intro-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  background: #eef5f1;
  color: #24463d;
  font-size: 12px;
  font-weight: 700;
}

.hero-action {
  min-width: 124px;
  height: 36px;
  border-radius: 999px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c7d0cc;

  &.active {
    background: #25a165;
    box-shadow: 0 0 0 4px rgba(37, 161, 101, 0.12);
  }
}

.main-layout {
  margin: 0;
}

@media (max-width: 992px) {
  .recognition-container {
    padding: 16px;
    overflow: auto;
  }

  .hero-row {
    flex-direction: column;
    gap: 10px;
  }

  .page-intro {
    flex-direction: column;
    align-items: stretch;
  }

  .intro-actions {
    width: 100%;
    justify-content: space-between;
  }

  .page-intro h1 {
    font-size: 22px;
  }
}

@media (max-width: 767px) {
  .recognition-container {
    min-height: auto;
    padding: 14px;
  }

  .nav-header {
    align-self: flex-start;
  }

  .page-intro {
    padding: 14px;
    border-radius: 18px;
  }

  .page-intro h1 {
    font-size: 20px;
  }

  .description {
    font-size: 13px;
  }

  .intro-badge {
    justify-content: center;
  }

  .intro-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-action {
    width: 100%;
  }
}
</style>
