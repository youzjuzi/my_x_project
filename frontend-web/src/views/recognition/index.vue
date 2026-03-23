<template>
  <div class="recognition-container">
    <div class="page-shell">
      <div class="nav-header">
        <div class="back-capsule" @click="handleExit">
          <div class="icon-wrap">
            <el-icon><ArrowLeft /></el-icon>
          </div>
          <div class="text-content">
            <span class="title">结束识别</span>
            <span class="sub">返回上一页</span>
          </div>
        </div>
      </div>

      <div class="page-intro">
        <div>
          <p class="eyebrow">手势识别</p>
          <h1>通过摄像头实时识别手势内容</h1>
          <p class="description">
            开启摄像头后即可开始识别。页面右侧会同步展示识别过程、候选结果和最终输出内容。
          </p>
        </div>
        <div class="intro-badge">
          <span class="status-dot" :class="{ active: isCameraActive }"></span>
          {{ isCameraActive ? '摄像头已开启' : '等待开启摄像头' }}
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
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(12, 92, 70, 0.08), transparent 28%),
    linear-gradient(180deg, #f4f7f2 0%, #eef2ec 100%);
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.nav-header {
  margin-bottom: 24px;
}

.back-capsule {
  width: fit-content;
  display: flex;
  align-items: center;
  padding: 8px 20px 8px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 12px 30px rgba(28, 43, 36, 0.08);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  user-select: none;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 36px rgba(28, 43, 36, 0.12);
  }

  &:active {
    transform: scale(0.98);
  }
}

.icon-wrap {
  width: 38px;
  height: 38px;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #edf3ee;
  color: #24433b;
  font-size: 18px;
}

.text-content {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 14px;
  font-weight: 700;
  color: #17312b;
  line-height: 1.2;
}

.sub {
  font-size: 12px;
  color: #6d7f78;
}

.page-intro {
  margin-bottom: 24px;
  padding: 28px 32px;
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.94) 0%, rgba(247, 250, 248, 0.94) 100%);
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow: 0 20px 50px rgba(28, 43, 36, 0.08);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;

  h1 {
    margin: 8px 0 10px;
    font-size: 34px;
    line-height: 1.2;
    color: #132e28;
  }
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: #6b7f77;
  text-transform: uppercase;
}

.description {
  margin: 0;
  max-width: 720px;
  font-size: 15px;
  line-height: 1.7;
  color: #5c6f68;
}

.intro-badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 999px;
  background: #eef5f0;
  color: #23463d;
  font-size: 14px;
  font-weight: 600;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #c2cbc7;

  &.active {
    background: #28a36a;
    box-shadow: 0 0 0 6px rgba(40, 163, 106, 0.12);
  }
}

.main-layout {
  margin: 0;
}

@media (max-width: 992px) {
  .recognition-container {
    padding: 20px;
  }

  .page-intro {
    padding: 24px;
    flex-direction: column;

    h1 {
      font-size: 28px;
    }
  }
}

@media (max-width: 767px) {
  .recognition-container {
    padding: 16px;
  }

  .nav-header {
    margin-bottom: 16px;
  }

  .page-intro {
    margin-bottom: 16px;
    padding: 20px;
    border-radius: 22px;

    h1 {
      font-size: 24px;
    }
  }

  .description {
    font-size: 14px;
  }

  .intro-badge {
    width: 100%;
    justify-content: center;
  }
}
</style>
