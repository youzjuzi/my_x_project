<template>
  <div class="dashboard">
    <div class="video">
      <div class="col-lg-8  offset-lg-2">
        <h3 class="mt-6">手语识别</h3>
      </div>
      <div class="video-container">
        <img v-if="isDetecting" :src="videoStreamUrl" alt="Video stream">
        <div v-else class="detection-message">
          当前未检测，请开启下方按钮进行手语识别
        </div>
      </div>
      <div class="controls">
        <el-switch
          v-model="isDetecting"
          active-color="#13ce66"
          inactive-color="#ff4949"
          active-text="检测中"
          inactive-text="未检测"
          @change="handleSwitchChange"
        />
      </div>
      <div class="new-box">
        <h3>检测结果</h3>
        <el-table :data="detections" style="width: 100%" height="350">
          <el-table-column prop="timestamp" label="时间" width="140">
            <template slot-scope="scope">
              {{ new Date(scope.row.timestamp).toLocaleTimeString() }}
            </template>
          </el-table-column>
          <el-table-column prop="class_name" label="类别" width="150" />
          <el-table-column prop="confidence" label="准确度" width="120">
            <template slot-scope="scope">
              {{ (scope.row.confidence * 100).toFixed(2) }}%
            </template>
          </el-table-column>
        </el-table>
        <div class="button-container">
          <el-link target="_blank" @click="goToTranslationHistory">翻译历史</el-link>
          <el-button type="danger" round :disabled="isDetecting" @click="clearDetections">清除</el-button>
        </div>
      </div>
      <div class="show">
        <div v-if="isDetecting && summaryResult" class="summary-content">
          <div class="summary-center">
            <div v-for="(item, index) in summaryResult.topClasses" :key="index" class="summary-item">
              <span :class="['class-name', `size-${index + 1}`]">{{ item.translation }}</span>
            </div>
          </div>
        </div>
        <p v-else>暂无检测结果</p>
      </div>
    </div>
  </div>
</template>
<script>

import { mapState } from 'vuex'
import detectionApi from '@/api/detection'

export default {
  data() {
    return {
      data: {},
      ip: null,
      // 识别视频流
      videoStreamUrl: 'http://localhost:5000/video_feed',
      isDetecting: false,
      detections: [],
      maxDetections: 8, // 最大显示的检测结果数量
      detectionInterval: null,
      summaryResult: null
    }
  },
  sockets: { // 定义socket连接
    connect: function() {
      console.log('连接成功') // 判断是否正确连接上后端
    },
    disconnect() {
      console.log('WebSocket 连接断开')
    }
  },

  mounted() { // 在组件开始渲染时进行调用
    this.initializeSocket() // 初始化socket连接
    this.startDetectionInterval()
    // 刷新当前页面
    if (!localStorage.getItem('pageReloaded')) {
      localStorage.setItem('pageReloaded', 'true');
      window.location.reload();
    } else {
      localStorage.removeItem('pageReloaded');
    }
  },
  destroyed() { // 当离开组件时，结束调用
    if (this.$socket) this.$socket.disconnect() // 如果socket连接存在，销毁socket连接
    console.log('连接已断开')
    this.stopDetectionInterval()
  },
  methods: {
    initializeSocket() {
      console.log('连接中')
      console.log('userId:', this.userId)
      this.$socket.io.opts.query = { userId: this.userId }
      this.$socket.connect()
    },
    handleSwitchChange(value) {
      if (value) {
        this.startDetection()
        this.startDetectionInterval()
      } else {
        this.stopDetection()
        this.stopDetectionInterval()
      }
    },
    startDetection() {
      this.$message({
        message: '开始检测',
        type: 'success'
      })
      this.isDetecting = true
      this.$socket.emit('start_detection', { userId: this.userId })
    },
    stopDetection() {
      this.$message({
        message: '关闭检测',
        type: 'warning'
      })
      this.isDetecting = false
      this.$socket.emit('stop_detection', { userId: this.userId })
    },
    fetchDetections() {
      detectionApi.getDetectionList().then(response => {
        // 假设 response.data 包含检测结果数组
        const newDetections = response.data
        // 添加新的检测结果到数组开头
        this.detections.unshift(...newDetections)
        // 如果检测结果超过最大数量，删除多余的
        if (this.detections.length > this.maxDetections) {
          this.detections = this.detections.slice(0, this.maxDetections)
        }
        this.updateSummaryResult()
      })
    },
    getTranslation(className) {
      const translationMap = {
        'ok': '好的',
        'like': '喜欢',
        'hello': '你好',
        'thank_you': '谢谢',
        'one': '1',
        'three': '3',
        'three2': '3',
        'four': '4',
        'fist': '拳头',
        'palm': '手掌',
        'peace': '安静、和平',
        'dislike': '不喜欢',
        'stop': '停',
        'call': '叫、打电话',
        'mute': '说不出话',
        'rock': '棒'
      }
      return translationMap[className] || className
    },
    updateSummaryResult() {
      if (this.detections.length === 0) {
        this.summaryResult = null
        return
      }

      const classData = {}

      this.detections.forEach(detection => {
        if (!classData[detection.class_name]) {
          classData[detection.class_name] = {
            count: 0,
            totalConfidence: 0
          }
        }
        classData[detection.class_name].count++
        classData[detection.class_name].totalConfidence += detection.confidence
      })

      const topClasses = Object.entries(classData)
        .map(([className, data]) => ({
          className,
          averageConfidence: data.totalConfidence / data.count,
          translation: this.getTranslation(className) // 获取翻译
        }))
        .sort((a, b) => b.averageConfidence - a.averageConfidence)
        .slice(0, 3) // 只取前三个

      this.summaryResult = {
        topClasses: topClasses
      }
    },
    startDetectionInterval() {
      this.detectionInterval = setInterval(() => {
        if (this.isDetecting) {
          this.fetchDetections()
        }
      }, 1000)
    },
    stopDetectionInterval() {
      if (this.detectionInterval) {
        clearInterval(this.detectionInterval)
      }
    },
    clearDetections() {
      this.detections = [] // 清空检测结果数组
      this.summaryResult = null
      this.$message({
        message: '检测数据已清除',
        type: 'success'
      })
    },
    watch: {
      detections: {
        handler() {
          this.updateSummaryResult()
        },
        deep: true
      }
    },
    goToTranslationHistory() {
      this.$router.push('/logging/translation_history')
    }
  },
  // eslint-disable-next-line vue/order-in-components
  computed: {
    ...mapState('user', ['userId'])
  }
}
</script>

<style lang="scss" scoped>

.show {
  border: 2px solid #000;
  border-radius: 8px;
  padding: 20px; // 增加内边距
  margin-top: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: auto;
  min-height: 120px; // 稍微增加最小高度
  overflow: auto;
}

.show h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  text-align: center;
}

.summary-content {
  display: flex;
  justify-content: center; // 改为左对齐
  align-items: center;
  flex-wrap: wrap;
}

.summary-item {
  margin: 0 20px 0 0; // 增加右边距，移除左边距
}

.class-name {
  font-weight: bold;
  color: #409EFF;
}

.summary-center {
  display: flex;
  flex-direction: column;
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  height: 100%; /* 确保占满父容器高度 */
}

.size-1 {
  font-size: 36px; /* 增大字体 */
}

.size-2 {
  font-size: 28px; /* 调整第二个大小 */
}

.size-3 {
  font-size: 20px; /* 减小第三个大小 */
}

.label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.show strong {
  font-size: 18px;
  color: #409EFF;
}

.controls {
  margin-top: 7px;
  margin-bottom: 10px;
  display: flex;
  padding-left: 150px;
}
.el-switch {
  transform: scale(1.2); // 将开关放大 1.2 倍
  margin-left: 15px;
}

button {
  margin-right: 10px;
  padding: 5px 10px;
  cursor: pointer;
  margin-left: 20px;
}

.video-container {
  width: 48%;
  height: 400px;
  overflow: hidden;
  padding: 0; /* 确保没有内边距 */
  //border: 1px solid #000; /* 给容器添加边框 */
  margin-top: -30px; /* 向上移动20px */
  margin-left: 8px;
  position: relative; // 添加这行以支持绝对定位的子元素
  border-radius: 6px; // 稍微小于 .new-box 的圆角
  overflow: hidden; // 确保表格内容不会超出圆角
}

.video-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block; /* 移除图片下方可能存在的小间隙 */

}
.detection-message {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.1); // 半透明背景
  color: #333;
  font-size: 18px;
  text-align: center;
  padding: 20px;
  box-sizing: border-box;
}

.dashboard {
  padding: 1vh; /* 使用视口高度的百分比作为内边距 */
  margin: 0; /* 边框填满整个浏览器窗口，不留外边距 */
  width: 100%; /* 宽度设为100%，占据整个视口宽度 */
  height: 90vh; /* 高度设为视口高度的100% */
  box-sizing: border-box; /* 边框计算在宽度和高度内 */
  border-radius: 5px; /* 由于占据全屏，不需要圆角 */
  overflow: hidden;
}
  /* 确保内部元素不超出父容器的宽度 */
  .video{
    position: relative;
    padding: 1vh; /* 使用视口高度的百分比作为内边距 */
    background-color: #d9e9f3;
    height: 500px;
    max-width: 100%;
    width: var(--video-width);
    border-radius: 5px;

  }
.col-lg-8, .offset-lg-2 {
  font-family: 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  font-size: 18px;
  line-height: 1.6;
  color: #333;
  letter-spacing: 0.5px;
  margin-top: -25px;
  margin-left: -19px;
  }
.mt-6 {
  margin-top: 15px;
  margin-left: 190px;
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.rounded {
  position: relative;
  border-radius: 5px; /* 圆角大小 */
  width: 48%; /* 保持图片宽度 */
  }
.new-box {
  position: absolute;
  right: 10px; // 给右边留一些空间
  top: -20px; // 从顶部留出一些空间
  width: 48%; // 稍微减小宽度
  height: 94%; // 使用百分比高度
  box-sizing: border-box;
  padding: 10px;
  overflow: auto; // 添加滚动条
  display: flex;
  flex-direction: column;
  height: 100%; // 确保 new-box 占满其父容器的高度
  padding-bottom: 60px; // 为按钮留出空间
}
.new-box h3 {
  text-align: center;
  margin-bottom: 3px;
  margin-top: 15px;
  font-size: 27px; // 增加字体大小
}

.el-table {
  flex: 1; // 让表格填充剩余空间
  border-radius: 6px; // 稍微小于 .new-box 的圆角
  overflow: hidden; // 确保表格内容不会超出圆角
}

// 调整表格样式
.el-table__header-wrapper th {
  background-color: #f2f6fc;
  color: #606266;
  font-weight: bold;
}

.el-table__body-wrapper {
  overflow-y: auto;
}

.el-table__row {
  &:nth-child(even) {
    background-color: #fafafa;
  }
}
.button-container {
  position: absolute;
  bottom: 15px;
  right: 15px;
}

.button-container .el-button {
  padding: 8px 15px; // 减小内边距
  font-size: 12px; // 减小字体大小
}

.button-container .el-button:hover {
  transform: scale(1.05);
}
</style>
