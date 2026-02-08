<template>
  <div class="debug-container">
    <el-row :gutter="20">
      <!-- 左侧：操作面板 -->
      <el-col :span="16">
        <el-card class="box-card main-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="title-area">
                <el-icon :size="24" class="mr-2"><Monitor /></el-icon>
                <span class="title-text">手语识别调试台 (WebSocket Mock)</span>
              </div>
              <el-tag :type="wsStatus === 'OPEN' ? 'success' : 'danger'" effect="dark" size="large">
                {{ wsStatus === 'OPEN' ? '已连接 Mock 服务' : '服务未连接' }}
              </el-tag>
            </div>
          </template>

          <!-- 模拟摄像头区域 -->
          <div class="camera-mock">
            <div class="scan-line"></div>
            <div class="mock-content">
              <el-icon class="camera-icon" :size="48"><VideoCamera /></el-icon>
              <p class="mock-text">模拟识别画面</p>
              <p class="last-key-display" v-if="lastKey">
                检测到输入: <span class="key-badge">{{ lastKey }}</span>
              </p>
              <p class="waiting-text" v-else>等待输入...</p>
            </div>
          </div>

          <!-- 结果展示区域 -->
          <div class="result-section">
            <el-row :gutter="15">
              <el-col :span="12">
                <div class="result-box buffer-box">
                  <div class="label">当前拼音缓冲区</div>
                  <div class="value">{{ pinyinBuffer || '-' }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="result-box sentence-box">
                  <div class="label">已生成句子</div>
                  <div class="value">{{ sentence || '-' }}</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 虚拟键盘区域 -->
          <div class="keyboard-area">
            <div class="keyboard-label">模拟输入控制台</div>
            
            <!-- 数字键 -->
            <div class="key-row">
              <el-button 
                v-for="num in '1234567890'" 
                :key="num" 
                @click="sendKey(num)" 
                size="large"
                class="key-btn"
              >{{ num }}</el-button>
            </div>

            <!-- 字母键第一行 -->
            <div class="key-row">
              <el-button 
                v-for="char in 'ABCDEFGHIJKLMN'" 
                :key="char" 
                @click="sendKey(char)" 
                type="primary" 
                plain 
                size="large"
                class="key-btn"
              >{{ char }}</el-button>
            </div>

            <!-- 字母键第二行 -->
            <div class="key-row">
              <el-button 
                v-for="char in 'OPQRSTUVWXYZ'" 
                :key="char" 
                @click="sendKey(char)" 
                type="primary" 
                plain 
                size="large"
                class="key-btn"
              >{{ char }}</el-button>
            </div>

            <!-- 功能键 -->
            <div class="key-row action-keys">
              <el-button type="warning" @click="sendKey('Backspace')" icon="Back" size="large" class="action-btn">删除 (BS)</el-button>
              <el-button type="info" @click="sendKey('Null')" icon="VideoPause" size="large" class="action-btn">空 (Null)</el-button>
              <el-button type="success" @click="sendKey('Space')" icon="Check" size="large" class="action-btn">确认拼音 (Space)</el-button>
              <el-button type="danger" @click="sendKey('Enter')" icon="Promotion" size="large" class="action-btn">提交整句 (Enter)</el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：日志面板 -->
      <el-col :span="8">
        <el-card class="box-card log-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="log-title"><el-icon><List /></el-icon> 系统交互日志</span>
              <el-button link type="primary" @click="clearLogs">清空</el-button>
            </div>
          </template>
          <div class="log-container" ref="logContainerRef">
            <div v-if="logs.length === 0" class="empty-log">暂无日志</div>
            <div v-for="(log, i) in logs" :key="i" class="log-item">
              <span class="log-time">[{{ log.time }}]</span>
              <span class="log-content">{{ log.msg }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { VideoCamera, Back, VideoPause, Check, Promotion, Monitor, List } from '@element-plus/icons-vue'

// 状态定义
const ws = ref<WebSocket | null>(null)
const wsStatus = ref('CLOSED')
// 日志结构改为对象以便处理
interface LogItem {
  time: string
  msg: string
}
const logs = ref<LogItem[]>([])
const lastKey = ref('')
const pinyinBuffer = ref('') 
const sentence = ref('')
const logContainerRef = ref<HTMLElement | null>(null)

// 连接 WebSocket
const connectWs = () => {
  ws.value = new WebSocket('ws://localhost:8000/ws')

  ws.value.onopen = () => {
    wsStatus.value = 'OPEN'
    addLog('System: WebSocket 连接成功')
  }

  ws.value.onclose = () => {
    wsStatus.value = 'CLOSED'
    addLog('System: WebSocket 连接断开')
  }

  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      addLog(`Received: ${JSON.stringify(data)}`)
      if(data.buffer !== undefined) pinyinBuffer.value = data.buffer
      if(data.sentence !== undefined) sentence.value = data.sentence
    } catch (e) {
      addLog(`Received Raw: ${event.data}`)
    }
  }
  
  ws.value.onerror = (error) => {
    addLog('System: WebSocket 发生错误')
    console.error('WebSocket Error:', error)
  }
}

// 发送按键逻辑
const sendKey = (key: string) => {
  if (!ws.value || wsStatus.value !== 'OPEN') {
    addLog('Error: 服务未连接，无法发送')
    return
  }

  lastKey.value = key
  
  const payload = {
    type: "mock",
    label: key,
    timestamp: Date.now()
  }

  ws.value.send(JSON.stringify(payload))
  addLog(`Sent: ${key}`)
}

// 键盘事件监听
const handleKeydown = (e: KeyboardEvent) => {
  const key = e.key.toUpperCase()
  if (key === ' ') {
    sendKey('Space')
    e.preventDefault() 
  } else if (key === 'ENTER') {
    sendKey('Enter')
  } else if (key === 'BACKSPACE') {
    sendKey('Backspace')
  } else if (key === 'ESCAPE') {
    sendKey('Null')
  } else if (/^[A-Z0-9]$/.test(key)) {
    sendKey(key)
  }
}

// 日志辅助
const addLog = (msg: string) => {
  const time = new Date().toLocaleTimeString()
  // Unshift 到开头 (最新消息置顶)
  logs.value.unshift({ time, msg })
  // 保持最多 100 条
  if (logs.value.length > 100) logs.value.pop()
}

const clearLogs = () => {
  logs.value = []
}

onMounted(() => {
  connectWs()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (ws.value) ws.value.close()
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.debug-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 84px); /* 减去顶部导航高度 */
}

/* 卡片通用样式 */
.box-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-area {
  display: flex;
  align-items: center;
}

.title-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.mr-2 {
  margin-right: 8px;
}

/* 摄像头模拟区 */
.camera-mock {
  background: #000;
  height: 240px;
  border-radius: 8px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0f0;
  margin-bottom: 24px;
  overflow: hidden;
  border: 2px solid #333;
  box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.1);
}

.mock-content {
  z-index: 2;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.camera-icon {
  margin-bottom: 10px;
  opacity: 0.8;
}

.mock-text {
  font-family: 'Consolas', monospace;
  font-size: 1.2em;
  letter-spacing: 2px;
  margin-bottom: 5px;
}

.last-key-display {
  font-size: 1.1em;
  margin-top: 10px;
  color: #fff;
}

.key-badge {
  background: #409EFF;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.waiting-text {
  color: #666;
  font-size: 0.9em;
  margin-top: 10px;
}

.scan-line {
  position: absolute;
  width: 100%;
  height: 2px;
  background: rgba(0, 255, 0, 0.6);
  top: 0;
  animation: scan 2.5s linear infinite;
  box-shadow: 0 0 15px #0f0;
  z-index: 1;
}

@keyframes scan {
  0% { top: 0; }
  100% { top: 100%; }
}

/* 结果展示区 */
.result-section {
  margin-bottom: 24px;
}

.result-box {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  text-align: center;
  transition: all 0.3s;
}

.result-box:hover {
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #409EFF;
}

.result-box .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.result-box .value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  min-height: 28px;
}

.buffer-box .value {
  color: #409EFF;
}

.sentence-box .value {
  color: #67C23A;
}

/* 键盘区域 */
.keyboard-area {
  background: #fcfcfc;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #EBEEF5;
}

.keyboard-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 15px;
  font-weight: 500;
}

.key-row {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.key-btn {
  font-family: 'Consolas', monospace;
  font-weight: bold;
  min-width: 45px;
}

.action-keys {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #e4e7ed;
}

.action-btn {
  min-width: 140px;
  margin: 0 5px;
}

/* 日志面板 */
.log-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.log-card :deep(.el-card__body) {
  flex: 1;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-container {
  background: #2b2b2b;
  /* flex: 1; */
  overflow-y: auto;
  padding: 12px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #a9b7c6;
  height: 700px; /* 强制固定高度 */
  max-height: 700px; /* 防止被撑开 */
}

.log-item {
  margin-bottom: 4px;
  word-break: break-all;
  border-bottom: 1px solid #3c3f41;
  padding-bottom: 2px;
}

.log-time {
  color: #cc7832; /* Orange-ish for time */
  margin-right: 8px;
}

.log-content {
  color: #a9b7c6;
}

.empty-log {
  color: #555;
  text-align: center;
  margin-top: 20px;
}
</style>