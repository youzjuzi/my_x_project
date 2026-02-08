<template>
  <div class="challenge-timeline">
    <div 
      v-for="(challenge, index) in challenges" 
      :key="challenge.id || index"
      class="timeline-item"
    >
      <!-- 左侧图标 -->
      <div class="icon-box" :class="getIconClass(challenge)">
        <el-icon :size="20">
          <component :is="getIcon(challenge)" />
        </el-icon>
      </div>

      <!-- 中间内容 -->
      <div class="content">
        <div class="content-top">
          <span class="mode-name">{{ challenge.mode }}</span>
          <span class="score" :class="getScoreClass(challenge)">+{{ challenge.score }}分</span>
        </div>
        <div class="content-bottom">
          <span class="meta-text">准确率 {{ challenge.accuracy }}</span>
          <span class="meta-separator">·</span>
          <span class="meta-text">{{ formatTime(challenge.time) }}</span>
        </div>
      </div>

      <!-- 右侧状态 -->
      <div class="status">
        <el-tag 
          :type="challenge.status === '已完成' ? 'success' : 'info'"
          size="small"
        >
          {{ challenge.status }}
        </el-tag>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!challenges || challenges.length === 0" class="empty-state">
      <el-icon :size="48" color="#d1d5db">
        <component :is="Document" />
      </el-icon>
      <p>暂无挑战记录</p>
    </div>
  </div>
</template>

<script>
import { defineComponent, markRaw } from 'vue';
import { Trophy, CircleCheck, CircleClose, Document } from '@element-plus/icons-vue';

export default defineComponent({
  name: 'ChallengeTimeline',
  props: {
    challenges: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      Trophy: markRaw(Trophy),
      CircleCheck: markRaw(CircleCheck),
      CircleClose: markRaw(CircleClose),
      Document: markRaw(Document)
    };
  },
  methods: {
    // 获取图标
    getIcon(challenge) {
      if (challenge.status === '已完成' && challenge.score > 500) {
        return this.Trophy;
      } else if (challenge.status === '已完成') {
        return this.CircleCheck;
      } else {
        return this.CircleClose;
      }
    },
    // 获取图标样式类
    getIconClass(challenge) {
      if (challenge.status === '已完成' && challenge.score > 500) {
        return 'icon-highlight';
      } else if (challenge.status === '已完成') {
        return 'icon-success';
      } else {
        return 'icon-failed';
      }
    },
    // 获取得分样式类
    getScoreClass(challenge) {
      if (challenge.score > 500) {
        return 'score-highlight';
      } else if (challenge.score > 0) {
        return 'score-normal';
      } else {
        return 'score-zero';
      }
    },
    // 格式化时间（相对时间）
    formatTime(timeStr) {
      if (!timeStr) return '未知时间';
      
      try {
        // 处理 'YYYY-MM-DD HH:mm' 格式
        let time;
        if (timeStr.includes(' ')) {
          // 将 'YYYY-MM-DD HH:mm' 转换为 'YYYY-MM-DDTHH:mm:00'
          time = new Date(timeStr.replace(' ', 'T') + ':00');
        } else {
          time = new Date(timeStr);
        }
        
        // 检查日期是否有效
        if (isNaN(time.getTime())) {
          return timeStr;
        }
        
        const now = new Date();
        const diff = now - time; // 毫秒差
        
        // 如果是未来时间，显示具体日期
        if (diff < 0) {
          const month = String(time.getMonth() + 1).padStart(2, '0');
          const day = String(time.getDate()).padStart(2, '0');
          return `${month}-${day}`;
        }
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) {
          return '刚刚';
        } else if (minutes < 60) {
          return `${minutes}分钟前`;
        } else if (hours < 24) {
          return `${hours}小时前`;
        } else if (days < 7) {
          return `${days}天前`;
        } else {
          // 超过7天，显示具体日期
          const month = String(time.getMonth() + 1).padStart(2, '0');
          const day = String(time.getDate()).padStart(2, '0');
          return `${month}-${day}`;
        }
      } catch (error) {
        console.warn('时间格式化错误:', error);
        return timeStr;
      }
    }
  }
});
</script>

<style lang="scss" scoped>
.challenge-timeline {
  width: 100%;
  
  .timeline-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 24px;
    min-height: 70px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    transition: background-color 0.2s ease;
    cursor: pointer;

    &:hover {
      background-color: #f9fafc;
    }

    &:last-child {
      border-bottom: none;
    }

    .icon-box {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      :deep(.el-icon) {
        color: #fff;
      }

      &.icon-highlight {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        box-shadow: 0 2px 8px rgba(251, 191, 36, 0.3);
      }

      &.icon-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
      }

      &.icon-failed {
        background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
        box-shadow: 0 2px 8px rgba(156, 163, 175, 0.2);
      }
    }

    .content {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 6px;

      .content-top {
        display: flex;
        align-items: center;
        gap: 12px;

        .mode-name {
          font-size: 15px;
          font-weight: 600;
          color: #1f2937;
        }

        .score {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
          font-size: 16px;
          font-weight: 700;
          letter-spacing: 0.5px;

          &.score-highlight {
            color: #f59e0b;
          }

          &.score-normal {
            color: #6366f1;
          }

          &.score-zero {
            color: #9ca3af;
          }
        }
      }

      .content-bottom {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #6b7280;

        .meta-separator {
          color: #d1d5db;
        }
      }
    }

    .status {
      flex-shrink: 0;
    }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    color: #9ca3af;

    p {
      margin-top: 16px;
      font-size: 14px;
    }
  }
}
</style>

