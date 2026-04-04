<template>
  <div class="tab-pinyin">
    <p class="section-intro">
      系统将手势字母拼成拼音，自动匹配汉字候选词，实现从手势到中文句子的完整转换。
    </p>

    <!-- 流程图 -->
    <div class="flow-pipeline">
      <div v-for="(node, idx) in flowNodes" :key="node.title" class="flow-node">
        <div class="flow-icon">{{ node.icon }}</div>
        <div class="flow-title">{{ node.title }}</div>
        <div class="flow-detail">{{ node.detail }}</div>
        <div v-if="idx < flowNodes.length - 1" class="flow-connector">
          <svg width="24" height="16" viewBox="0 0 24 16">
            <path d="M4 8 H18 M14 4 L18 8 L14 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 重点说明卡片 -->
    <div class="explain-cards">
      <div class="explain-card">
        <div class="explain-title">📊 稳定性进度条</div>
        <div class="explain-text">
          视频画面底部会出现进度条。手势保持不变时进度累加，超过阈值后该字母被确认进入缓存区。进度条颜色从绿（稳定）渐变为红（即将确认）。
        </div>
      </div>
      <div class="explain-card">
        <div class="explain-title">🔤 拼音缓冲区</div>
        <div class="explain-text">
          被确认的字母按顺序拼接成拼音串（如 <code>nihao</code>），系统自动匹配候选汉字。连续拼写即可输入多音节词。
        </div>
      </div>
      <div class="explain-card">
        <div class="explain-title">📋 候选词切换</div>
        <div class="explain-text">
          拼音匹配到多个候选词时，使用「下一个 →」手势在候选词之间切换，然后用「确认 ✓」手势选定词语。
        </div>
      </div>
      <div class="explain-card">
        <div class="explain-title">🤖 AI 润色</div>
        <div class="explain-text">
          积累多个词语后，使用「提交 ↑」手势提交，AI 会将离散词语润色为通顺的中文句子，显示在识别结果区。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { PINYIN_FLOW_NODES } from '../helpData'

const flowNodes = PINYIN_FLOW_NODES
</script>

<style lang="scss" scoped>
.section-intro {
  margin: 0 0 16px;
  font-size: 13.5px;
  color: #5a7a6f;
  line-height: 1.6;
}

.flow-pipeline {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0;
  margin-bottom: 20px;
  padding: 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f0f6f3 0%, #e8f0ec 100%);
  border: 1px solid rgba(33, 109, 75, 0.08);
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.flow-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid rgba(33, 109, 75, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 2px 6px rgba(33, 109, 75, 0.06);
}

.flow-title {
  font-size: 12px;
  font-weight: 700;
  color: #18342c;
  white-space: nowrap;
}

.flow-detail {
  font-size: 10px;
  color: #7a958c;
  white-space: nowrap;
}

.flow-connector {
  display: flex;
  align-items: center;
  padding-top: 10px;
  color: rgba(33, 109, 75, 0.3);
}

.explain-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.explain-card {
  padding: 14px 16px;
  border-radius: 14px;
  background: #f9fbfa;
  border: 1px solid rgba(33, 109, 75, 0.08);
}

.explain-title {
  font-size: 13px;
  font-weight: 700;
  color: #18342c;
  margin-bottom: 6px;
}

.explain-text {
  font-size: 12px;
  color: #5a7a6f;
  line-height: 1.65;

  code {
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(33, 109, 75, 0.08);
    color: #216d4b;
    font-size: 11px;
    font-weight: 600;
  }
}

@media (max-width: 767px) {
  .explain-cards {
    grid-template-columns: 1fr;
  }

  .flow-pipeline {
    flex-direction: column;
    align-items: center;
  }

  .flow-connector {
    transform: rotate(90deg);
    padding-top: 0;
  }
}
</style>
