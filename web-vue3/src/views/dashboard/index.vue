<template>
  <div class="dashboard-container">
    <github-corner class="github-corner" />

    <!-- 手语识别入口卡片 -->
    <el-card class="recognition-card" shadow="never">
      <div class="mesh-background"></div>
      <div class="recognition-content">
        <div class="recognition-left">
          <h2 class="recognition-title">欢迎使用<br>ASL 实时手语交互系统</h2>
          <p class="recognition-desc">开启您的手语识别之旅，体验智能交互的无限可能</p>
        </div>
        <div class="recognition-right">
          <button class="glass-button" @click="goToRecognition">
            <el-icon><VideoCamera/></el-icon>
            <span>开始识别</span>
          </button>
          <div class="hand-illustration">
            <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="handGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:rgba(255, 255, 255, 0.4);stop-opacity:1" />
                  <stop offset="100%" style="stop-color:rgba(255, 255, 255, 0.2);stop-opacity:1" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <!-- 手掌 -->
              <ellipse cx="100" cy="140" rx="50" ry="40" fill="url(#handGradient)" filter="url(#glow)" />
              <!-- 拇指 -->
              <ellipse cx="60" cy="120" rx="20" ry="30" fill="url(#handGradient)" filter="url(#glow)" transform="rotate(-30 60 120)" />
              <!-- 食指 -->
              <ellipse cx="100" cy="80" rx="15" ry="50" fill="url(#handGradient)" filter="url(#glow)" />
              <!-- 中指 -->
              <ellipse cx="120" cy="70" rx="15" ry="55" fill="url(#handGradient)" filter="url(#glow)" />
              <!-- 无名指 -->
              <ellipse cx="140" cy="75" rx="15" ry="50" fill="url(#handGradient)" filter="url(#glow)" />
              <!-- 小指 -->
              <ellipse cx="160" cy="85" rx="12" ry="40" fill="url(#handGradient)" filter="url(#glow)" />
            </svg>
        </div>
        </div>
      </div>
    </el-card>

    <!-- 数据看板 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in statsData" :key="index">
        <div class="stat-card" :class="`stat-card-${index}`">
          <div class="stat-icon">
            <el-icon :size="32">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-badge" v-if="stat.trend" :class="stat.trend < 0 ? 'negative' : ''">
            <el-icon :size="14" :class="stat.trend > 0 ? 'trend-up' : 'trend-down'">
              <component :is="stat.trend > 0 ? ArrowUp : ArrowDown" />
            </el-icon>
            <span>{{ Math.abs(stat.trend) }}%</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 游戏化挑战成就列表 -->
      <el-col :xs="24" :md="12">
        <div class="panel-card challenge-timeline-card">
          <div class="panel-header">
            <div class="panel-title">
              <el-icon :size="20" class="title-icon">
                <component :is="TrophyIcon" />
              </el-icon>
              <span>挑战成就</span>
            </div>
            <el-button text type="primary" size="small">查看全部</el-button>
          </div>
          <div class="panel-content timeline-content">
            <ChallengeTimeline :challenges="recentChallenges" />
          </div>
        </div>
      </el-col>

      <!-- 每日手语词汇 -->
      <el-col :xs="24" :md="12">
        <div class="panel-card daily-vocabulary">
          <div class="panel-header">
            <div class="panel-title">
              <el-icon :size="20" class="title-icon">
                <component :is="ReadingIcon" />
              </el-icon>
              <span>每日手语词汇</span>
            </div>
            <el-button text type="primary" size="small">学习更多</el-button>
          </div>
          <div class="panel-content">
            <div 
              v-for="(word, index) in dailyVocabulary" 
              :key="index" 
              class="vocab-item"
            >
              <div class="vocab-word">{{ word.word }}</div>
              <div class="vocab-meaning">{{ word.meaning }}</div>
              <div class="vocab-category">{{ word.category }}</div>
            </div>
            <div v-if="dailyVocabulary.length === 0" class="empty-state">
              <el-icon :size="48" color="#d1d5db">
                <component :is="Document" />
              </el-icon>
              <p>暂无词汇</p>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import GithubCorner from '@/components/GithubCorner';
import ChallengeTimeline from '@/components/ChallengeTimeline/index.vue';
import { defineComponent, markRaw } from 'vue';
import { 
  VideoCamera, 
  Timer, 
  DataBoard, 
  PieChart,
  ArrowUp,
  ArrowDown,
  Clock,
  Reading,
  Document,
  Trophy
} from '@element-plus/icons-vue';

export default defineComponent({
  name: 'Dashboard',
  components: {
    GithubCorner,
    ChallengeTimeline
  },
  data() {
    return {
      statsData: [
        {
          label: '累计识别时长',
          value: '128.5h',
          icon: markRaw(Timer),
          trend: 12.5,
          color: '#6366f1'
        },
        {
          label: '今日练习',
          value: '45次',
          icon: markRaw(DataBoard),
          trend: 8.3,
          color: '#8b5cf6'
        },
        {
          label: '平均准确率',
          value: '92.8%',
          icon: markRaw(PieChart),
          trend: 5.2,
          color: '#ec4899'
        },
        {
          label: '总识别次数',
          value: '1,234',
          icon: markRaw(VideoCamera),
          trend: 15.6,
          color: '#06b6d4'
        }
      ],
      ArrowUp: markRaw(ArrowUp),
      ArrowDown: markRaw(ArrowDown),
      ClockIcon: markRaw(Clock),
      ReadingIcon: markRaw(Reading),
      Document: markRaw(Document),
      VideoCamera: markRaw(VideoCamera),
      TrophyIcon: markRaw(Trophy),
      // 最近挑战记录（Mock数据，实际应从API获取）
      recentChallenges: [
        { id: 1, mode: '题库挑战', score: 630, accuracy: '100%', status: '已完成', time: '2025-11-29 21:22' },
        { id: 2, mode: '随机挑战', score: 300, accuracy: '33%', status: '已完成', time: '2025-11-29 21:25' },
        { id: 3, mode: '随机挑战', score: 100, accuracy: '25%', status: '已放弃', time: '2025-11-29 21:16' },
        { id: 4, mode: '随机挑战', score: 20, accuracy: '8%', status: '已放弃', time: '2025-11-29 21:14' },
        { id: 5, mode: '随机挑战', score: 0, accuracy: '0%', status: '已放弃', time: '2025-11-29 21:10' }
      ],
      dailyVocabulary: [
        {
          word: '你好',
          meaning: 'Hello',
          category: '问候'
        },
        {
          word: '谢谢',
          meaning: 'Thank you',
          category: '礼貌'
        },
        {
          word: '再见',
          meaning: 'Goodbye',
          category: '告别'
        },
        {
          word: '请',
          meaning: 'Please',
          category: '礼貌'
        },
        {
          word: '对不起',
          meaning: 'Sorry',
          category: '道歉'
        }
      ]
    };
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
  background-color: #f5f7fa;
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
    border: none;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(79, 70, 229, 0.25);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    background: transparent;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 48px rgba(79, 70, 229, 0.35);
    }
    
    :deep(.el-card__body) {
      padding: 0;
      border: none;
      position: relative;
      z-index: 1;
    }

    :deep(.el-card__header) {
      border: none;
      padding: 0;
    }

    .mesh-background {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: 
        radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.8) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.8) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(79, 70, 229, 0.6) 0%, transparent 50%),
        linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #6366f1 100%);
      background-size: 200% 200%;
      animation: meshMove 15s ease infinite;
      z-index: 0;
    }

    @keyframes meshMove {
      0%, 100% {
        background-position: 0% 50%;
      }
      50% {
        background-position: 100% 50%;
      }
    }

    .recognition-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 50px 60px;
      color: #fff;
      gap: 40px;
      position: relative;
      z-index: 1;
      min-height: 200px;

      .recognition-left {
        flex: 1;
        max-width: 500px;

        .recognition-title {
          margin: 0 0 16px 0;
          font-size: 36px;
          font-weight: 700;
          color: #fff;
          text-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
          line-height: 1.3;
        }

        .recognition-desc {
          margin: 0;
          font-size: 18px;
          color: rgba(255, 255, 255, 0.95);
          line-height: 1.8;
        }
      }

      .recognition-right {
        display: flex;
        align-items: center;
        gap: 30px;
        flex-shrink: 0;

        .glass-button {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 16px 32px;
          font-size: 18px;
          font-weight: 600;
          color: #fff;
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
          white-space: nowrap;

          &:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            border-color: rgba(255, 255, 255, 0.5);
          }

          &:active {
            transform: translateY(0);
          }

          .el-icon {
            font-size: 20px;
          }
        }

        .hand-illustration {
          width: 180px;
          height: 180px;
          display: flex;
          align-items: center;
          justify-content: center;
          filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
          animation: float 3s ease-in-out infinite;
          transform-style: preserve-3d;
          perspective: 1000px;

          svg {
            width: 100%;
            height: 100%;
            transform: rotateY(-15deg) rotateX(5deg);
            transition: transform 0.3s ease;
          }

          &:hover svg {
            transform: rotateY(0deg) rotateX(0deg) scale(1.05);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }
      }
    }
  }

  .stat-card {
    position: relative;
    border: none;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    height: 100%;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899, #06b6d4);
      transform: scaleX(0);
      transform-origin: left;
      transition: transform 0.3s ease;
    }

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);

      &::before {
        transform: scaleX(1);
      }

      .stat-icon {
        transform: scale(1.1) rotate(5deg);
      }
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      z-index: 1;

      :deep(.el-icon) {
        color: #fff;
      }
    }

    .stat-content {
      position: relative;
      z-index: 1;

      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 8px;
        line-height: 1.2;
      }

      .stat-label {
    font-size: 14px;
        color: #6b7280;
        font-weight: 500;
      }
    }

    .stat-badge {
      position: absolute;
      top: 20px;
      right: 20px;
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;

      .trend-up {
        color: #10b981;
      }

      .trend-down {
        color: #ef4444;
      }

      &.negative {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
      }
    }

    &.stat-card-0 .stat-icon {
      background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
    }

    &.stat-card-1 .stat-icon {
      background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
    }

    &.stat-card-2 .stat-icon {
      background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
    }

    &.stat-card-3 .stat-icon {
      background: linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%);
    }
  }

  .panel-card {
    border: none;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 24px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.06);
      background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);

      .panel-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        font-size: 16px;
        color: #303133;

        .title-icon {
          color: #6366f1;
        }
    }
  }

    .panel-content {
      flex: 1;
      padding: 20px 24px;
      overflow-y: auto;
      max-height: 400px;

      &::-webkit-scrollbar {
        width: 6px;
      }

      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
      }

      &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;

        &:hover {
          background: #a8a8a8;
        }
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

  .challenge-timeline-card {
    .timeline-content {
      padding: 0;
      // 去除默认padding，让列表撑满
    }
  }

  .daily-vocabulary {
    .vocab-item {
      padding: 16px;
      border-radius: 12px;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
      border: 1px solid rgba(99, 102, 241, 0.1);
      transition: all 0.2s ease;
      cursor: pointer;

      &:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
      }

      &:last-child {
        margin-bottom: 0;
      }

      .vocab-word {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 8px;
      }

      .vocab-meaning {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 6px;
      }

      .vocab-category {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(99, 102, 241, 0.1);
        color: #6366f1;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
      }
    }
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 20px;

    .recognition-card {
      border-radius: 16px;
      
      .recognition-content {
        flex-direction: column;
        text-align: center;
        padding: 40px 30px;
        gap: 30px;

        .recognition-left {
          max-width: 100%;

          .recognition-title {
            font-size: 24px;
            margin-bottom: 12px;
          }

          .recognition-desc {
            font-size: 16px;
          }
        }

        .recognition-right {
          flex-direction: column;
          gap: 20px;

          .hand-illustration {
            width: 140px;
            height: 140px;
          }
        }
      }
    }
    .stat-card {
      margin-bottom: 20px;
    }

    .panel-card {
      margin-bottom: 20px;

      .panel-content {
        max-height: 300px;
      }
    }
  }
}
</style>
