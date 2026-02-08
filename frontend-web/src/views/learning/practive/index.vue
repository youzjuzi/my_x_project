<template>
  <div class="shadowing-container">

    <div class="top-bar">
      <div class="current-lesson">
        <el-tag effect="dark" type="primary" round>当前课程</el-tag>
        <span class="lesson-title">{{ currentLesson.title }}</span>
      </div>
      <div class="similarity-meter">
        <span>动作匹配度</span>
        <el-progress
          :percentage="similarityScore"
          :color="customColors"
          :stroke-width="18"
          :format="scoreFormat"
          class="score-progress"
        />
      </div>
    </div>

    <el-row :gutter="20" class="video-stage">
      <el-col :span="12">
        <div class="video-card teacher-side">
          <div class="label-badge">标准示范</div>
          <div class="video-placeholder teacher-bg">
            <el-icon :size="60"><VideoPlay /></el-icon>
            <p>老师正在演示...</p>
          </div>

          <div class="control-bar">
            <el-button-group>
              <el-button size="small" @click="playbackRate = 0.5">0.5x</el-button>
              <el-button size="small" type="primary">1.0x</el-button>
            </el-button-group>
            <span class="tips">建议初学者开启 0.5x 慢放</span>
          </div>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="video-card student-side" :class="{ 'good-job': similarityScore > 80 }">
          <div class="label-badge">我的练习</div>
          <div class="video-placeholder camera-bg">
            <video ref="cameraRef" autoplay muted class="real-camera"></video>
            <div class="yolo-box" v-if="isPlaying">
              <span class="yolo-label">Hand: {{ similarityScore }}%</span>
            </div>
          </div>
          <div class="feedback-text" v-if="similarityScore > 80">🌟 太棒了！动作很标准</div>
          <div class="feedback-text warning" v-else>💪 请抬高你的手臂</div>
        </div>
      </el-col>
    </el-row>

    <div class="playlist-section">
      <div class="section-header">
        <h3>推荐练习</h3>
        <el-link type="primary">查看全部 <el-icon><ArrowRight /></el-icon></el-link>
      </div>
      <div class="card-list">
        <div
          v-for="item in lessonList"
          :key="item.id"
          class="lesson-card"
          :class="{ active: currentLesson.id === item.id }"
          @click="switchLesson(item)"
        >
          <div class="card-cover">{{ item.icon }}</div>
          <div class="card-info">
            <div class="name">{{ item.title }}</div>
            <div class="duration">{{ item.duration }}</div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { VideoPlay, ArrowRight } from '@element-plus/icons-vue'

const similarityScore = ref(0)
const isPlaying = ref(true)
const cameraRef = ref(null)

// 模拟课程数据
const currentLesson = ref({ id: 1, title: '日常问候：你好，很高兴认识你', duration: '15s' })
const lessonList = [
  { id: 1, title: '日常问候：你好，很高兴认识你', duration: '15s', icon: '👋' },
  { id: 2, title: '紧急求助：请帮我叫救护车', duration: '30s', icon: '🚑' },
  { id: 3, title: '购物点餐：我要一杯冰咖啡', duration: '20s', icon: '☕' },
  { id: 4, title: '情感表达：我非常感谢你的帮助', duration: '25s', icon: '❤️' },
]

// 进度条颜色策略
const customColors = [
  { color: '#f56c6c', percentage: 40 },
  { color: '#e6a23c', percentage: 70 },
  { color: '#5cb87a', percentage: 100 },
]

const scoreFormat = (percentage) => (percentage === 100 ? '完美' : `${percentage}%`)

const switchLesson = (item) => {
  currentLesson.value = item
  similarityScore.value = 0
}

// 模拟实时评分逻辑 (实际需对接后端/YOLO)
onMounted(() => {
  // 开启摄像头
  navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    if (cameraRef.value) cameraRef.value.srcObject = stream
  })

  // 模拟分数波动
  setInterval(() => {
    const randomChange = Math.floor(Math.random() * 20) - 10
    let newScore = similarityScore.value + randomChange
    if (newScore > 100) newScore = 100
    if (newScore < 40) newScore = 40
    similarityScore.value = newScore
  }, 800)
})
</script>

<style scoped lang="scss">
.shadowing-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
  display: flex;
  flex-direction: column;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 15px 25px;
  border-radius: 16px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);

  .current-lesson {
    display: flex;
    align-items: center;
    gap: 12px;
    .lesson-title { font-size: 18px; font-weight: bold; color: #303133; }
  }

  .similarity-meter {
    display: flex;
    align-items: center;
    gap: 15px;
    span { font-size: 14px; color: #909399; }
    .score-progress { width: 300px; }
  }
}

/* 视频区域 */
.video-stage {
  flex: 1; /* 撑满剩余高度 */
}

.video-card {
  background: #000;
  border-radius: 16px;
  height: 500px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  transition: all 0.3s;

  .label-badge {
    position: absolute;
    top: 15px; left: 15px;
    background: rgba(0,0,0,0.6);
    color: #fff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    z-index: 10;
    backdrop-filter: blur(4px);
  }

  .video-placeholder {
    width: 100%; height: 100%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    color: rgba(255,255,255,0.7);

    &.teacher-bg { background: linear-gradient(45deg, #2c3e50, #3498db); }
    &.camera-bg { background: #1a1a1a; position: relative;}

    .real-camera {
      width: 100%; height: 100%; object-fit: cover;
      transform: scaleX(-1); /* 镜像翻转 */
    }

    .yolo-box {
      position: absolute;
      top: 30%; left: 40%; width: 20%; height: 30%;
      border: 2px solid #67C23A;
      .yolo-label { background: #67C23A; color: #fff; font-size: 12px; padding: 2px 4px; }
    }
  }

  /* 老师侧控制条 */
  .control-bar {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 15px;
    background: linear-gradient(transparent, rgba(0,0,0,0.8));
    display: flex;
    align-items: center;
    gap: 15px;
    .tips { color: #ccc; font-size: 12px; margin-left: auto; }
  }

  /* 学生侧反馈 */
  .feedback-text {
    position: absolute;
    bottom: 20px; left: 50%; transform: translateX(-50%);
    background: rgba(103, 194, 58, 0.9);
    color: #fff;
    padding: 8px 20px;
    border-radius: 30px;
    font-weight: bold;
    animation: bounceIn 0.5s;

    &.warning { background: rgba(230, 162, 60, 0.9); }
  }

  /* 高分时边框发光 */
  &.student-side.good-job {
    box-shadow: 0 0 0 4px rgba(103, 194, 58, 0.5);
  }
}

/* 底部选课 */
.playlist-section {
  margin-top: 20px;
  .section-header {
    display: flex; justify-content: space-between; margin-bottom: 15px;
    h3 { margin: 0; font-size: 16px; color: #303133; }
  }

  .card-list {
    display: flex; gap: 15px; overflow-x: auto; padding-bottom: 10px;

    .lesson-card {
      min-width: 200px;
      background: #fff;
      padding: 15px;
      border-radius: 12px;
      display: flex; align-items: center; gap: 12px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s;

      .card-cover { font-size: 32px; background: #f0f2f5; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 8px; }
      .card-info {
        .name { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
        .duration { font-size: 12px; color: #909399; }
      }

      &:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
      &.active { border-color: #6956FF; background: #F2F0FF; .name { color: #6956FF; } }
    }
  }
}

@keyframes bounceIn {
  0% { transform: translateX(-50%) scale(0.8); opacity: 0; }
  100% { transform: translateX(-50%) scale(1); opacity: 1; }
}
</style>