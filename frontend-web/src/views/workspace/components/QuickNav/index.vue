<template>
  <div class="quick-nav">

    <!-- 4 张功能卡片 -->
    <div class="nav-cards">
      <div
        v-for="item in navItems"
        :key="item.key"
        class="nav-card"
        :class="`nav-card--${item.key}`"
        role="button"
        tabindex="0"
        :aria-label="item.title"
        @click="handleClick(item)"
        @keydown.enter="handleClick(item)"
      >
        <!-- 图标区 -->
        <div class="card-icon-wrap">
          <el-icon class="card-icon"><component :is="item.icon" /></el-icon>
        </div>

        <!-- 文字区 -->
        <div class="card-body">
          <span class="card-title">{{ item.title }}</span>
          <span class="card-desc">{{ item.desc }}</span>
        </div>

        <!-- 跳转箭头 -->
        <el-icon class="card-arrow"><ArrowRight /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight, Memo, EditPen, Trophy, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()

/* 快捷导航项定义 */
const navItems = [
  {
    key: 'history',
    icon: Memo,
    title: '历史记录',
    desc: '查看过往识别结果',
    path: '/logging/translation_history'
  },
  {
    key: 'practice',
    icon: EditPen,
    title: '手势练习',
    desc: '闯关式字母练习',
    path: '/learning/practice'
  },
  {
    key: 'challenge',
    icon: Trophy,
    title: '挑战赛',
    desc: '测试识别速度与准确率',
    path: '/learning/challenge'
  },
  {
    key: 'profile',
    icon: UserFilled,
    title: '个人中心',
    desc: '账号信息与设置',
    path: '/profile/index'
  }
]

const handleClick = (item: typeof navItems[0]) => {
  if (!item.path) {
    ElMessage.info('该模块正在建设中，敬请期待～')
    return
  }
  router.push(item.path)
}
</script>

<style scoped lang="scss">


/* 卡片行：自适应网格，宽度不够时自动换行 */
.nav-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
}

/* 单张卡片 */
.nav-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(18, 42, 35, 0.08);
  box-shadow:
    0 2px 4px rgba(28, 43, 36, 0.04),
    0 6px 18px rgba(28, 43, 36, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  cursor: pointer;
  user-select: none;
  /* 过渡动画 */
  transition:
    transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.22s ease,
    border-color 0.22s ease;
  outline: none;

  &:hover {
    transform: translateY(-4px);
    box-shadow:
      0 4px 8px rgba(28, 43, 36, 0.06),
      0 14px 32px rgba(28, 43, 36, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
    border-color: rgba(37, 161, 101, 0.22);

    .card-arrow {
      transform: translateX(3px);
      opacity: 1;
    }
  }

  &:active {
    transform: translateY(-1px);
  }

  &:focus-visible {
    outline: 2px solid rgba(37, 161, 101, 0.5);
    outline-offset: 2px;
  }
}

/* 图标容器 — 不同卡片用不同深浅绿 */
.card-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  .card-icon {
    font-size: 20px;
    color: #fff;
  }
}

.nav-card--history  .card-icon-wrap { background: linear-gradient(135deg, #5b8c6b, #3d6b52); }
.nav-card--practice .card-icon-wrap { background: linear-gradient(135deg, #216d4b, #174f36); }
.nav-card--challenge .card-icon-wrap { background: linear-gradient(135deg, #1a8a5f, #126644); }
.nav-card--profile  .card-icon-wrap { background: linear-gradient(135deg, #2e7d6e, #1d5c52); }

/* 文字区 */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: #122b25;
  white-space: nowrap;
}

.card-desc {
  font-size: 11px;
  color: #688178;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 跳转箭头 */
.card-arrow {
  font-size: 14px;
  color: #a0b8ae;
  flex-shrink: 0;
  opacity: 0.6;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

/* 响应式：平板折两列，移动端两列 */
@media (max-width: 992px) {
  .nav-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .nav-cards {
    grid-template-columns: 1fr;
  }
}
</style>
