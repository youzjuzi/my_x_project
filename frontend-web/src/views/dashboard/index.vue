<template>
  <div class="dashboard-container">

    <!-- 欢迎区 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h2 class="welcome-title">👋 欢迎回来，{{ userName || '同学' }}</h2>
        <p class="welcome-desc">查看你的学习进展，继续手语学习之旅吧！</p>
      </div>
      <el-button type="primary" round class="go-workspace-btn" @click="$router.push('/workspace')">
        <el-icon><VideoCamera /></el-icon>
        开始识别
      </el-button>
    </div>

    <!-- 四个数据卡片 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in statsCards" :key="index">
        <div class="stat-card" :class="`stat-card-${index}`" :style="{ animationDelay: `${index * 0.08}s` }">
          <div class="stat-icon">
            <span class="stat-emoji">{{ stat.emoji }}</span>
          </div>
          <div class="stat-content">
            <div class="stat-value">
              <span v-if="statsLoading" class="stat-skeleton"></span>
              <template v-else>{{ stat.value }}</template>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-badge" v-if="stat.trend !== null && stat.trend !== undefined && !statsLoading" :class="stat.trend < 0 ? 'negative' : ''">
            <el-icon :size="14">
              <component :is="stat.trend >= 0 ? ArrowUp : ArrowDown" />
            </el-icon>
            <span>{{ Math.abs(stat.trend) }}%</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 下方两栏 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 挑战成就（真实数据） -->
      <el-col :xs="24" :md="12">
        <div class="panel-card challenge-timeline-card">
          <div class="panel-header">
            <div class="panel-title">
              <span class="title-emoji">🏆</span>
              <span>挑战成就</span>
            </div>
            <el-button text type="primary" size="small" @click="$router.push('/learning/challenge')">查看全部</el-button>
          </div>
          <div class="panel-content timeline-content">
            <div v-if="challengeLoading" class="loading-state">
              <el-icon class="is-loading" :size="24"><Loading /></el-icon>
              <p>加载中...</p>
            </div>
            <ChallengeTimeline v-else :challenges="recentChallenges" />
          </div>
        </div>
      </el-col>

      <!-- 学习热力图 -->
      <el-col :xs="24" :md="12">
        <div class="panel-card heatmap-card">
          <div class="panel-header">
            <div class="panel-title">
              <span class="title-emoji">📅</span>
              <span>学习活跃度</span>
            </div>
            <div class="heatmap-month-nav">
              <el-button text size="small" @click="prevMonth">
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              <span class="month-label">{{ heatmapYear }}年{{ heatmapMonth }}月</span>
              <el-button text size="small" @click="nextMonth" :disabled="isCurrentMonth">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="panel-content heatmap-content">
            <div v-if="heatmapLoading" class="loading-state">
              <el-icon class="is-loading" :size="24"><Loading /></el-icon>
              <p>加载中...</p>
            </div>
            <template v-else>
              <!-- 星期标题行 -->
              <div class="heatmap-weekdays">
                <span v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="weekday-label">{{ day }}</span>
              </div>
              <!-- 日历格子 -->
              <div class="heatmap-grid">
                <!-- 月初之前的空白格 -->
                <div
                  v-for="n in firstDayOfWeek"
                  :key="'empty-' + n"
                  class="heatmap-cell empty"
                ></div>
                <!-- 每天一格 -->
                <div
                  v-for="day in daysInMonth"
                  :key="day"
                  class="heatmap-cell"
                  :class="{
                    'active': activeDatesSet.has(formatDateStr(day)),
                    'today': isToday(day)
                  }"
                  :title="formatDateStr(day) + (activeDatesSet.has(formatDateStr(day)) ? ' ✅ 已学习' : '')"
                >
                  <span class="day-num">{{ day }}</span>
                </div>
              </div>
              <!-- 统计摘要 -->
              <div class="heatmap-summary">
                <div class="summary-item">
                  <span class="summary-value">{{ activeDates.length }}</span>
                  <span class="summary-label">活跃天数</span>
                </div>
                <div class="summary-item">
                  <span class="summary-value">{{ daysInMonth }}</span>
                  <span class="summary-label">本月总天</span>
                </div>
                <div class="summary-item">
                  <span class="summary-value">{{ activityRate }}%</span>
                  <span class="summary-label">活跃率</span>
                </div>
              </div>
            </template>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import ChallengeTimeline from '@/components/ChallengeTimeline/index.vue';
import { defineComponent, markRaw } from 'vue';
import { getDashboardStats } from '@/api/dashboard';
import { getChallengeHistory } from '@/api/challenge';
import { getActivityDates } from '@/api/translationHistory';
import useUserStore from '@/store/modules/user';
import {
  VideoCamera,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Loading
} from '@element-plus/icons-vue';

export default defineComponent({
  name: 'Dashboard',
  components: {
    ChallengeTimeline,
    VideoCamera,
    ArrowLeft,
    ArrowRight,
    Loading
  },
  data() {
    const now = new Date();
    return {
      // 图标组件引用
      ArrowUp: markRaw(ArrowUp),
      ArrowDown: markRaw(ArrowDown),

      // 统计数据
      statsLoading: true,
      streakDays: 0,
      totalRecognitions: 0,
      challengeAccuracy: 0,
      bestScore: 0,
      recognitionTrend: null,
      accuracyTrend: null,

      // 挑战记录
      challengeLoading: true,
      recentChallenges: [],

      // 热力图
      heatmapLoading: true,
      heatmapYear: now.getFullYear(),
      heatmapMonth: now.getMonth() + 1,
      activeDates: [] // 活跃日期字符串数组
    };
  },
  computed: {
    userName() {
      const userStore = useUserStore();
      return userStore.name;
    },
    userId() {
      const userStore = useUserStore();
      return userStore.userId;
    },
    /** 四个统计卡片 */
    statsCards() {
      return [
        {
          label: '连续学习',
          value: this.streakDays + '天',
          emoji: '🔥',
          trend: null, // 连续天数不需要趋势
          color: '#f59e0b'
        },
        {
          label: '总识别次数',
          value: this.formatNumber(this.totalRecognitions),
          emoji: '📝',
          trend: this.recognitionTrend,
          color: '#6366f1'
        },
        {
          label: '挑战准确率',
          value: this.challengeAccuracy + '%',
          emoji: '🎯',
          trend: this.accuracyTrend,
          color: '#ec4899'
        },
        {
          label: '最高分',
          value: this.formatNumber(this.bestScore),
          emoji: '🏆',
          trend: null, // 最高分只有新纪录才变，不做趋势
          color: '#06b6d4'
        }
      ];
    },
    /** 活跃日期 Set（用于快速查找） */
    activeDatesSet() {
      return new Set(this.activeDates);
    },
    /** 当前月的天数 */
    daysInMonth() {
      return new Date(this.heatmapYear, this.heatmapMonth, 0).getDate();
    },
    /** 当前月第一天是星期几 (0=日, 1=一, ...) */
    firstDayOfWeek() {
      return new Date(this.heatmapYear, this.heatmapMonth - 1, 1).getDay();
    },
    /** 是否是当前月 */
    isCurrentMonth() {
      const now = new Date();
      return this.heatmapYear === now.getFullYear() && this.heatmapMonth === now.getMonth() + 1;
    },
    /** 活跃率 */
    activityRate() {
      if (this.daysInMonth === 0) return 0;
      return Math.round((this.activeDates.length / this.daysInMonth) * 100);
    }
  },
  created() {
    this.fetchAllData();
  },
  methods: {
    /** 获取所有数据 */
    async fetchAllData() {
      await Promise.all([
        this.fetchStats(),
        this.fetchChallenges(),
        this.fetchHeatmap()
      ]);
    },

    /** 获取统计数据（P1 接口） */
    async fetchStats() {
      this.statsLoading = true;
      try {
        const res = await getDashboardStats();
        if (res.data) {
          const d = res.data;
          this.streakDays = d.streakDays || 0;
          this.totalRecognitions = d.totalRecognitions || 0;
          this.challengeAccuracy = d.challengeAccuracy || 0;
          this.bestScore = d.bestScore || 0;
          this.recognitionTrend = d.recognitionTrend;
          this.accuracyTrend = d.accuracyTrend;
        }
      } catch (e) {
        console.error('获取仪表盘统计失败:', e);
      } finally {
        this.statsLoading = false;
      }
    },

    /** 获取挑战记录（P0，已有接口） */
    async fetchChallenges() {
      this.challengeLoading = true;
      try {
        const res = await getChallengeHistory({ pageNo: 1, pageSize: 5 });
        if (res.data && res.data.rows) {
          // 将后端字段映射为 ChallengeTimeline 组件所需格式
          this.recentChallenges = res.data.rows.map(row => ({
            id: row.id,
            mode: row.mode === 'random' ? '随机挑战' : '题库挑战',
            score: row.score || 0,
            accuracy: row.totalCount > 0
              ? Math.round((row.completedCount / row.totalCount) * 100) + '%'
              : '0%',
            status: row.status === 1 ? '已完成' : row.status === 2 ? '已放弃' : '进行中',
            time: row.createTime
          }));
        }
      } catch (e) {
        console.error('获取挑战记录失败:', e);
        this.recentChallenges = [];
      } finally {
        this.challengeLoading = false;
      }
    },

    /** 获取热力图数据（P0，已有接口） */
    async fetchHeatmap() {
      if (!this.userId) return;
      this.heatmapLoading = true;
      try {
        const res = await getActivityDates({
          userId: this.userId,
          year: this.heatmapYear,
          month: this.heatmapMonth
        });
        this.activeDates = res.data || [];
      } catch (e) {
        console.error('获取活跃日期失败:', e);
        this.activeDates = [];
      } finally {
        this.heatmapLoading = false;
      }
    },

    /** 上一月 */
    prevMonth() {
      if (this.heatmapMonth === 1) {
        this.heatmapYear--;
        this.heatmapMonth = 12;
      } else {
        this.heatmapMonth--;
      }
      this.fetchHeatmap();
    },
    /** 下一月 */
    nextMonth() {
      if (this.isCurrentMonth) return;
      if (this.heatmapMonth === 12) {
        this.heatmapYear++;
        this.heatmapMonth = 1;
      } else {
        this.heatmapMonth++;
      }
      this.fetchHeatmap();
    },

    /** 格式化日期字符串 */
    formatDateStr(day) {
      const m = String(this.heatmapMonth).padStart(2, '0');
      const d = String(day).padStart(2, '0');
      return `${this.heatmapYear}-${m}-${d}`;
    },
    /** 是否是今天 */
    isToday(day) {
      const now = new Date();
      return this.heatmapYear === now.getFullYear()
        && this.heatmapMonth === now.getMonth() + 1
        && day === now.getDate();
    },
    /** 数字格式化（千分位） */
    formatNumber(num) {
      if (num === null || num === undefined) return '0';
      return num.toLocaleString();
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

  /* 欢迎区 */
  .welcome-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 32px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    color: #fff;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.25);
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      right: -60px;
      top: -60px;
      width: 200px;
      height: 200px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
    }
    &::after {
      content: '';
      position: absolute;
      right: 60px;
      bottom: -40px;
      width: 140px;
      height: 140px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.05);
    }

    .welcome-text {
      position: relative;
      z-index: 1;

      .welcome-title {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
      }

      .welcome-desc {
        margin: 8px 0 0;
        font-size: 14px;
        opacity: 0.85;
      }
    }

    .go-workspace-btn {
      position: relative;
      z-index: 1;
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      backdrop-filter: blur(10px);
      color: #fff;
      font-weight: 600;
      font-size: 15px;
      padding: 12px 24px;
      transition: all 0.3s ease;

      &:hover {
        background: rgba(255, 255, 255, 0.35);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
      }
    }
  }

  /* 统计卡片 */
  .stat-card {
    position: relative;
    border: none;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 24px;
    cursor: default;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    height: 100%;
    animation: fadeInUp 0.5s ease both;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
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
        transform: scale(1.15);
      }
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      .stat-emoji {
        font-size: 28px;
        line-height: 1;
      }
    }

    .stat-content {
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 8px;
        line-height: 1.2;
        min-height: 38px;
      }

      .stat-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
      }

      .stat-skeleton {
        display: inline-block;
        width: 80px;
        height: 32px;
        border-radius: 6px;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
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

      &.negative {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
      }
    }

    /* 不同卡片的顶部彩条颜色 */
    &.stat-card-0::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    &.stat-card-1::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
    &.stat-card-2::before { background: linear-gradient(90deg, #ec4899, #f472b6); }
    &.stat-card-3::before { background: linear-gradient(90deg, #06b6d4, #22d3ee); }

    /* 不同卡片的图标背景 */
    &.stat-card-0 .stat-icon { background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(251, 191, 36, 0.08) 100%); }
    &.stat-card-1 .stat-icon { background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(129, 140, 248, 0.08) 100%); }
    &.stat-card-2 .stat-icon { background: linear-gradient(135deg, rgba(236, 72, 153, 0.12) 0%, rgba(244, 114, 182, 0.08) 100%); }
    &.stat-card-3 .stat-icon { background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(34, 211, 238, 0.08) 100%); }
  }

  /* 面板卡片 */
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

        .title-emoji {
          font-size: 20px;
        }
      }
    }

    .panel-content {
      flex: 1;
      padding: 20px 24px;
      overflow-y: auto;
      max-height: 400px;

      &::-webkit-scrollbar { width: 6px; }
      &::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
      &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
        &:hover { background: #a8a8a8; }
      }
    }

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
      color: #9ca3af;

      p {
        margin-top: 12px;
        font-size: 14px;
      }
    }
  }

  .challenge-timeline-card {
    .timeline-content {
      padding: 0;
    }
  }

  /* 热力图 */
  .heatmap-card {
    .heatmap-month-nav {
      display: flex;
      align-items: center;
      gap: 8px;

      .month-label {
        font-size: 13px;
        font-weight: 600;
        color: #4b5563;
        min-width: 80px;
        text-align: center;
      }
    }

    .heatmap-content {
      padding: 16px 24px 20px;
    }

    .heatmap-weekdays {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 4px;
      margin-bottom: 8px;

      .weekday-label {
        text-align: center;
        font-size: 11px;
        font-weight: 600;
        color: #9ca3af;
        padding: 4px 0;
      }
    }

    .heatmap-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 4px;
    }

    .heatmap-cell {
      aspect-ratio: 1;
      border-radius: 6px;
      background: #f3f4f6;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      cursor: default;

      .day-num {
        font-size: 11px;
        font-weight: 500;
        color: #6b7280;
      }

      &.empty {
        background: transparent;
      }

      &.active {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);

        .day-num {
          color: #fff;
          font-weight: 700;
        }
      }

      &.today {
        border: 2px solid #6366f1;
      }

      &.today.active {
        border-color: #fff;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25), 0 0 0 2px #6366f1;
      }
    }

    .heatmap-summary {
      display: flex;
      justify-content: space-around;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid rgba(0, 0, 0, 0.06);

      .summary-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;

        .summary-value {
          font-size: 22px;
          font-weight: 700;
          color: #1f2937;
        }

        .summary-label {
          font-size: 12px;
          color: #9ca3af;
          font-weight: 500;
        }
      }
    }
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 20px;

    .welcome-section {
      flex-direction: column;
      text-align: center;
      gap: 16px;

      .welcome-title {
        font-size: 20px;
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
