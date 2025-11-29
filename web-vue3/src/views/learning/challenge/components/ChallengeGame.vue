<template>
  <el-row :gutter="24" class="game-layout">
    <el-col :span="10" :xs="24">
      <div class="task-panel">
        <!-- 模式显示 -->
        <div class="mode-display" v-if="isPlaying">
          <el-tag :type="getModeTagType(currentMode)" size="large">
            {{ getModeText(currentMode) }}
          </el-tag>
          <el-tag v-if="challengeMode === 'questionSet'" type="info" size="large" style="margin-left: 8px">
            {{ currentQuestionSetName }}
          </el-tag>
        </div>

        <!-- 统计信息 -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="label">得分</span>
            <span class="value score">{{ score }}</span>
          </div>
          <div class="stat-item">
            <span class="label">进度</span>
            <span class="value progress">{{ currentWordIndex + 1 }} / {{ totalWords }}</span>
          </div>
          <div class="stat-item">
            <span class="label">倒计时</span>
            <span class="value time" :class="{ warning: timeLeft <= 10 }">
              {{ formatTime(timeLeft) }}
            </span>
          </div>
        </div>

        <!-- 题目显示区域 -->
        <div class="word-display-area">
          <div class="word-progress">
            第 {{ currentWordIndex + 1 }} / {{ totalWords }} 题
          </div>

          <!-- 中文模式显示汉字 -->
          <div v-if="currentMode === 'chinese'" class="chinese-char">
            {{ currentWordOriginal }}
          </div>

          <!-- 字母/数字容器 -->
          <div class="letter-container">
            <div
              v-for="(char, index) in currentTargetSequence"
              :key="index"
              class="letter-box"
              :class="{
                'matched': index < matchedCount,
                'active': index === matchedCount
              }"
            >
              {{ char }}
            </div>
          </div>

          <!-- 题目信息 -->
          <div v-if="currentQuestion" class="question-info">
            <el-tag :type="getDifficultyTagType(currentQuestion.difficulty)" size="small">
              {{ getDifficultyText(currentQuestion.difficulty) }}
            </el-tag>
            <el-tag :type="getTypeTagType(currentQuestion.type)" size="small" style="margin-left: 8px">
              {{ getTypeText(currentQuestion.type) }}
            </el-tag>
          </div>
        </div>

        <!-- 提示区域 -->
        <div class="hint-area" v-if="isPlaying">
          <p class="hint-text">
            {{ currentMode === 'chinese' ? '请打出对应拼音手势：' : '请做出手势：' }}
          </p>
          <div class="hint-card">
            <div class="target-char">{{ currentTargetChar }}</div>
            <img :src="getHintImage(currentTargetChar)" class="hint-img" />
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="control-area">
          <el-button
            v-if="!isPlaying"
            type="primary"
            size="large"
            class="start-btn"
            @click="$emit('start-game')"
          >
            <el-icon class="mr-2"><VideoPlay /></el-icon> 开始挑战
          </el-button>
          <el-button v-else type="danger" plain @click="$emit('stop-game')">
            结束挑战
          </el-button>
        </div>
      </div>
    </el-col>

    <el-col :span="14" :xs="24">
      <div class="camera-panel">
        <div class="video-wrapper">
          <video ref="videoRef" autoplay muted playsinline class="camera-feed"></video>
          <div class="overlay" v-if="!isPlaying">
            <el-icon :size="60" color="#fff"><Trophy /></el-icon>
            <p>准备开始挑战！</p>
          </div>
          <div class="recognition-feedback" v-if="isPlaying">
            <div class="detected-tag">
              识别中: <span class="highlight">{{ lastDetectedChar || '...' }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VideoPlay, Trophy } from '@element-plus/icons-vue'

defineProps<{
  isPlaying: boolean
  challengeMode: 'random' | 'questionSet'
  currentMode: 'english' | 'number' | 'chinese'
  currentQuestionSetName: string
  score: number
  currentWordIndex: number
  totalWords: number
  timeLeft: number
  currentWordOriginal: string
  currentTargetSequence: string[]
  matchedCount: number
  currentTargetChar: string
  lastDetectedChar: string
  currentQuestion: any
}>()

defineEmits<{
  'start-game': []
  'stop-game': []
}>()

const getModeText = (mode: string) => {
  const map: Record<string, string> = {
    english: '英文拼写',
    number: '数字挑战',
    chinese: '中文拼音'
  }
  return map[mode] || mode
}

const getModeTagType = (mode: string) => {
  const map: Record<string, string> = {
    english: 'primary',
    number: 'warning',
    chinese: 'success'
  }
  return map[mode] || 'info'
}

const getTypeText = (type: number) => {
  const map: Record<number, string> = {
    1: '单词',
    2: '中文',
    3: '数字'
  }
  return map[type] || '未知'
}

const getTypeTagType = (type: number) => {
  const map: Record<number, string> = {
    1: 'primary',
    2: 'success',
    3: 'warning'
  }
  return map[type] || 'info'
}

const getDifficultyText = (difficulty: number) => {
  const map: Record<number, string> = {
    1: '简单',
    2: '中等',
    3: '困难'
  }
  return map[difficulty] || '未知'
}

const getDifficultyTagType = (difficulty: number) => {
  const map: Record<number, string> = {
    1: 'success',
    2: 'warning',
    3: 'danger'
  }
  return map[difficulty] || 'info'
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getHintImage = (char: string) => {
  if (/\d/.test(char)) {
    return `https://avatar.youzilite.us.kg/number/${char}.png`
  }
  return `https://avatar.youzilite.us.kg/letter/${char}.png`
}
</script>

<style scoped lang="scss">
.game-layout {
  margin-top: 0;
}

.task-panel {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  min-height: 600px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.mode-display {
  margin-bottom: 20px;
  text-align: center;
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    
    .label {
      font-size: 14px;
      color: #909399;
    }
    
    .value {
      font-size: 28px;
      font-weight: bold;
      
      &.score {
        color: #6956FF;
      }
      
      &.progress {
        color: #67C23A;
      }
      
      &.time {
        color: #E6A23C;
        
        &.warning {
          color: #f56c6c;
          animation: pulse 1s infinite;
        }
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.word-display-area {
  text-align: center;
  margin-bottom: 30px;
  flex: 1;
  
  .word-progress {
    font-size: 14px;
    color: #909399;
    margin-bottom: 20px;
  }
  
  .chinese-char {
    font-size: 48px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 20px;
    letter-spacing: 8px;
    animation: fadeIn 0.5s ease;
  }
  
  .letter-container {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
    
    .letter-box {
      width: 50px;
      height: 50px;
      border: 2px solid #E4E7ED;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: bold;
      color: #C0C4CC;
      transition: all 0.3s;
      
      &.active {
        border-color: #6956FF;
        color: #6956FF;
        transform: scale(1.1);
        box-shadow: 0 0 10px rgba(105, 86, 255, 0.3);
      }
      
      &.matched {
        background-color: #67C23A;
        border-color: #67C23A;
        color: #fff;
      }
    }
  }
  
  .question-info {
    margin-top: 16px;
  }
}

.hint-area {
  background: #F2F3F5;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-top: auto;
  
  .hint-text {
    font-size: 14px;
    color: #606266;
    margin-bottom: 16px;
  }
  
  .hint-card {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    
    .target-char {
      font-size: 48px;
      font-weight: bold;
      color: #303133;
    }
    
    .hint-img {
      height: 80px;
      object-fit: contain;
    }
  }
}

.control-area {
  margin-top: 20px;
  text-align: center;
  
  .start-btn {
    width: 200px;
    height: 50px;
    font-size: 16px;
  }
}

.camera-panel {
  background: #000;
  border-radius: 16px;
  height: 600px;
  overflow: hidden;
  position: relative;
  
  .video-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
    
    .camera-feed {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      
      p {
        font-size: 18px;
        margin: 0;
      }
    }
    
    .recognition-feedback {
      position: absolute;
      top: 20px;
      right: 20px;
      background: rgba(0, 0, 0, 0.7);
      padding: 8px 20px;
      border-radius: 20px;
      color: #fff;
      backdrop-filter: blur(5px);
      
      .detected-tag {
        font-size: 14px;
        
        .highlight {
          font-size: 18px;
          font-weight: bold;
          color: #67C23A;
        }
      }
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

