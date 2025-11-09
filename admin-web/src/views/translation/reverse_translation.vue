<template>
  <div>
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 多行输入框 -->
      <el-col :span="12">
        <el-input
          v-model="textInput"
          type="textarea"
          :rows="4"
          :max-length="200"
          placeholder="请输入文字以翻译为手语"
          clearable
        />
        <el-button
          type="primary"
          style="margin-top: 10px;"
          @click="handleGenerate"
        >
          生成
        </el-button>
        <el-button
          type="primary"
          icon="el-icon-microphone"
          style="margin-top: 10px; margin-left: 10px;"
          @click="startSpeechRecognition"
        >
          语音输入
        </el-button>
        <el-button
          type="danger"
          icon="el-icon-delete"
          style="margin-top: 10px; margin-left: 10px;"
          @click="clearInput"
        >
          清除
        </el-button>
      </el-col>

      <!-- 手语翻译视频区域 -->
      <el-col :span="12">
        <div v-if="translationVideoUrl" class="video-container">
          <video
            controls
            :src="translationVideoUrl"
            width="100%"
            height="300"
          />
        </div>
        <div v-else class="video-placeholder">
          <h3>待输入</h3>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'SignLanguageTranslator',
  data() {
    return {
      textInput: '', // 用户输入的文字
      translationVideoUrl: '' // 翻译后的手语视频URL
    }
  },
  methods: {
    // 清除输入框内容
    clearInput() {
      this.textInput = '';
    },

    // 检查输入并生成手语翻译
    handleGenerate() {
      if (!this.textInput.trim()) {
        this.$message.warning('请输入文字')
        return
      }
      this.translationVideoUrl = '' // 清空之前的翻译视频
      this.$message.loading('生成中...')
      this.translateTextToSignLanguage()
    },

    // 语音识别功能
    startSpeechRecognition() {
      console.log('开始语音识别...')
      // 实际项目中会将识别到的内容赋值给textInput
      // this.textInput = recognizedText;
    },

    // 文字翻译为手语的功能
    translateTextToSignLanguage() {
      // 模拟生成视频的延迟
      setTimeout(() => {
        // 请求翻译接口，将返回的手语视频URL赋值给translationVideoUrl
        this.translationVideoUrl = 'your_video_url_here.mp4' // 替换为实际的视频URL
        this.$message.success('生成完成')
      }, 2000) // 假设生成耗时2秒
    }
  }
}
</script>

<style scoped>
.video-container {
  border-radius: 10px; /* 圆角 */
  overflow: hidden;
}

.video-placeholder {
  width: 100%;
  height: 300px;
  border: 2px dashed #ccc; /* 虚线框 */
  border-radius: 10px; /* 圆角 */
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}
</style>
