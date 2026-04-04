<template>
  <div class="tab-quickstart">
    <div class="steps-flow">
      <div
        v-for="(step, idx) in steps"
        :key="step.title"
        class="step-card"
      >
        <div class="step-number">{{ idx + 1 }}</div>
        <div class="step-body">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-desc">{{ step.desc }}</div>
        </div>
        <!-- 箭头连接线（最后一个不显示） -->
        <div v-if="idx < steps.length - 1" class="step-arrow">
          <svg width="20" height="20" viewBox="0 0 20 20">
            <path d="M10 4 L10 14 M6 10 L10 14 L14 10" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 小提示 -->
    <div class="tip-banner">
      <span class="tip-icon">💡</span>
      <span>整个流程无需键盘和触屏，全程通过手势完成交互。</span>
    </div>
  </div>
</template>

<script setup>
import { QUICK_START_STEPS } from '../helpData'

const steps = QUICK_START_STEPS
</script>

<style lang="scss" scoped>
.steps-flow {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.step-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 16px;
  background: #f9fbfa;
  border: 1px solid rgba(33, 109, 75, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(33, 109, 75, 0.08);
  }
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #216d4b, #1e5c40);
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-body {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 15px;
  font-weight: 700;
  color: #18342c;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 13px;
  color: #5a7a6f;
  line-height: 1.6;
}

/* 步骤间的箭头 */
.step-arrow {
  display: flex;
  justify-content: center;
  padding: 4px 0;
  color: rgba(33, 109, 75, 0.25);
}

/* 提示条 */
.tip-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(237, 247, 242, 0.9) 0%, rgba(232, 244, 239, 0.9) 100%);
  border: 1px solid rgba(33, 109, 75, 0.12);
  font-size: 12.5px;
  color: #3d6652;
  line-height: 1.6;
  margin-top: 16px;
}

.tip-icon {
  font-size: 16px;
  flex-shrink: 0;
}
</style>
