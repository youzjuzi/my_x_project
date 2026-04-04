<template>
  <div class="workspace-page">
    <div class="page-shell">
      <!-- 全局大标题，居中显示，全幅 -->
      <div class="global-page-title">
        <h1>AI 实时手语解析舱<span class="title-dot"> · </span>让每次挥手都有回音</h1>
      </div>

      <div class="main-layout">
        <!-- 左列：视频识别区 + 快捷导航（摆在视频下方空白处） -->
        <div class="left-col">
          <VideoPanel
            :is-camera-active="isCameraActive"
            :connection-state="connectionState"
            :is-recognition-ready="isRecognitionReady"
            :input-fps="inputFps"
            :processed-fps="processedFps"
            :latency="latency"
            :video-stream="localStream || undefined"
            :overlay-result="overlayResult || undefined"
            :action-toast="actionToast"
            :action-title="actionTitle"
            :action-type="actionType"
            :action-tick="actionTick"
            :command-mode-active="commandModeActive"
            :command-candidate="commandCandidate"
            :command-candidate-progress="commandCandidateProgress"
            :pinyin-buffer="pinyinBuffer"
            :cached-buffer="cachedBuffer"
            :deleted-cache-char="deletedCacheChar"
            :deleted-cache-tick="deletedCacheTick"
            :delete-progress-tick="deleteProgressTick"
            :delete-progress-value="deleteProgressValue"
            :stability-progress="stabilityProgress"
            @start="startCamera"
            @stop="stopCamera"
          />
          <!-- 快捷导航放在视频下方空白处 -->
          <QuickNav />
        </div>

        <!-- 右列：控制栏 + 拼音/识别结果面板，左边缘与下方卡片对齐 -->
        <div class="right-col">
          <WorkspaceHeader
            :selected-mode="selectedMode"
            @change-mode="changeMode"
          />
          <InteractionPanel
            :gesture-stream="gestureStream"
            :hanzi-candidate="hanziCandidate"
            :candidates="hanziCandidates"
            :candidate-index="candidateIndex"
            :pending-words="pendingWords"
            :final-sentence="finalSentence"
            :stability-progress="stabilityProgress"
            :cached-buffer="cachedBuffer"
            @copy="copyResult"
            @clear="clearAll"
            @speak="speakResult"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import WorkspaceHeader from './components/WorkspaceHeader/index.vue'
import VideoPanel from '../recognition/components/VideoPanel.vue'
import InteractionPanel from '../recognition/components/InteractionPanel.vue'
import QuickNav from './components/QuickNav/index.vue'
import { useWorkspace } from './composables/useWorkspace'

const {
  // 识别相关状态
  isCameraActive,
  connectionState,
  connectionText,
  selectedMode,
  inputFps,
  processedFps,
  latency,
  gestureStream,
  pinyinBuffer,
  cachedBuffer,
  hanziCandidate,
  hanziCandidates,
  candidateIndex,
  deletedCacheChar,
  deletedCacheTick,
  deleteProgressTick,
  deleteProgressValue,
  stabilityProgress,
  localStream,
  overlayResult,
  isRecognitionReady,
  actionToast,
  actionTitle,
  actionType,
  actionTick,
  startCamera,
  stopCamera,
  changeMode,
  commandModeActive,
  commandCandidate,
  commandCandidateProgress,

  // UI 与提交交互
  pendingWords,
  finalSentence,
  clearAll,
  copyResult,
  speakResult
} = useWorkspace()
</script>

<style scoped lang="scss">
.workspace-page {
  min-height: calc(100vh - 84px);
  min-width: 480px; /* 缩放过小时触发横向滚动，而不是内容崩裂 */
  padding: 16px 20px 18px;
  background-color: #edf2f0;
  background-image:
    radial-gradient(at 0% 0%, rgba(200, 230, 215, 0.4) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(210, 235, 230, 0.4) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(195, 225, 205, 0.3) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(215, 240, 225, 0.4) 0px, transparent 50%),
    radial-gradient(rgba(45, 105, 80, 0.05) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 24px 24px;
  background-position: 0 0, 0 0, 0 0, 0 0, -1px -1px;
  overflow-x: hidden;
  overflow-y: auto;
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

/* 全局大标题 */
.global-page-title {
  text-align: center;
  margin-bottom: 24px;
  margin-top: 8px;

  h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
    line-height: 1.2;
    color: #122b25;
    letter-spacing: -0.02em;
    font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    /* 深绿渐变文字 */
    background: linear-gradient(135deg, #0d2b22 0%, #1e5c40 60%, #25a165 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* 中间分隔符「·」单独上色 */
  .title-dot {
    -webkit-text-fill-color: #25a165;
    opacity: 0.7;
  }
}

/* 主体两栏 flex 布局 */
.main-layout {
  display: flex;
  gap: 18px;
  align-items: stretch;
}

/* 左列：视频区 + 快捷导航，比例 2（对应原 span=16） */
.left-col {
  flex: 2;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  /* 移除原来的 > * { flex:1 }，让 VideoPanel 以 16:9 自然高度显示 */
}

/* 右列：控制栏 + 结果面板，比例 1（对应原 span=8） */
.right-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

@media (max-width: 992px) {
  .workspace-page {
    padding: 16px;
    overflow: auto;
  }

  .main-layout {
    flex-direction: column;
  }
}

@media (max-width: 767px) {
  .workspace-page {
    min-height: auto;
    padding: 14px;
  }

  .global-page-title h1 {
    font-size: 22px;
  }
}
</style>
