<template>
  <div class="dashboard-container">
    <github-corner class="github-corner" />

    <!-- 手语识别入口卡片 -->
    <el-card class="recognition-card" shadow="hover">
      <div class="recognition-content">
        <div class="recognition-icon">
          <el-icon :size="60" color="#409eff">
            <VideoCamera />
          </el-icon>
        </div>
        <div class="recognition-info">
          <h2 class="recognition-title">ASL 实时手语交互系统</h2>
          <p class="recognition-desc">点击进入手语识别终端，开始实时手语交互体验</p>
        </div>
        <div class="recognition-action">
          <el-button type="primary" size="large" round @click="goToRecognition">
            <el-icon><VideoCamera /></el-icon>
            进入识别系统
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 欢迎信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>欢迎使用系统</span>
            </div>
          </template>
          <div class="welcome-content">
            <p>这里是系统首页，您可以通过上方的手语识别入口进入实时手语交互系统。</p>
            <p>系统会根据您的权限动态显示相应的功能菜单。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import GithubCorner from '@/components/GithubCorner';
import { defineComponent } from 'vue';
import { VideoCamera } from '@element-plus/icons-vue';

export default defineComponent({
  name: 'Dashboard',
  components: {
    GithubCorner
  },
  methods: {
    goToRecognition() {
      this.$router.push('/recognition');
    }
  }
});
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;
  min-height: calc(100vh - 84px);

  .github-corner {
    position: absolute;
    top: 0px;
    border: 0;
    right: 0;
  }

  .recognition-card {
    margin-bottom: 32px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    overflow: hidden;
    
    :deep(.el-card__body) {
      padding: 0;
    }

    .recognition-content {
      display: flex;
      align-items: center;
      padding: 30px 40px;
      color: #fff;
      gap: 30px;

      .recognition-icon {
        flex-shrink: 0;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        backdrop-filter: blur(10px);
      }

      .recognition-info {
        flex: 1;

        .recognition-title {
          margin: 0 0 10px 0;
          font-size: 28px;
          font-weight: 600;
          color: #fff;
        }

        .recognition-desc {
          margin: 0;
          font-size: 16px;
          color: rgba(255, 255, 255, 0.9);
          line-height: 1.6;
        }
      }

      .recognition-action {
        flex-shrink: 0;

        :deep(.el-button) {
          height: 50px;
          padding: 0 30px;
          font-size: 16px;
          font-weight: 600;
          background: #fff;
          color: #667eea;
          border: none;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
          transition: all 0.3s;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
          }

          .el-icon {
            margin-right: 8px;
          }
        }
      }
    }
  }

  .welcome-content {
    padding: 20px 0;
    line-height: 1.8;
    color: #606266;
    font-size: 14px;

    p {
      margin: 10px 0;
    }
  }

  .card-header {
    font-weight: 600;
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 20px;

    .recognition-card {
      .recognition-content {
        flex-direction: column;
        text-align: center;
        padding: 25px 20px;

        .recognition-info {
          .recognition-title {
            font-size: 22px;
          }

          .recognition-desc {
            font-size: 14px;
          }
        }
      }
    }
  }
}
</style>
