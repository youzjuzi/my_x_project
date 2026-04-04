<template>
  <div class="tab-alphabet">
    <!-- 字母/数字子切换 -->
    <div class="sub-switcher">
      <button
        class="sub-pill"
        :class="{ active: alphabetMode === 'letters' }"
        @click="alphabetMode = 'letters'"
      >
        Aa 字母
      </button>
      <button
        class="sub-pill"
        :class="{ active: alphabetMode === 'digits' }"
        @click="alphabetMode = 'digits'"
      >
        123 数字
      </button>
    </div>

    <!-- 字母卡片网格 -->
    <div class="alphabet-grid">
      <div
        v-for="item in currentAlphabet"
        :key="item.char"
        class="alpha-card"
      >
        <div class="alpha-visual">{{ item.char }}</div>
        <div class="alpha-label">{{ item.label }}</div>
      </div>
    </div>

    <div class="tip-banner">
      <span class="tip-icon">📸</span>
      <span>面对摄像头，用右手比划上方手势即可被识别（手势图片后续上线）。</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { LETTER_ALPHABET, DIGIT_ALPHABET } from '../helpData'

const alphabetMode = ref('letters')

const currentAlphabet = computed(() =>
  alphabetMode.value === 'letters' ? LETTER_ALPHABET : DIGIT_ALPHABET,
)
</script>

<style lang="scss" scoped>
.sub-switcher {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.sub-pill {
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(33, 109, 75, 0.12);
  background: #f4f7f5;
  color: #4a6b5f;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;

  &.active {
    background: #216d4b;
    color: #fff;
    border-color: #216d4b;
  }

  &:hover:not(.active) {
    background: #eaf3ee;
  }
}

.alphabet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(68px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.alpha-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px 10px;
  border-radius: 14px;
  background: linear-gradient(145deg, #f0f6f3 0%, #e8f0ec 100%);
  border: 1px solid rgba(33, 109, 75, 0.1);
  cursor: default;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(33, 109, 75, 0.1);
  }
}

.alpha-visual {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #216d4b 0%, #1a8a5f 100%);
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: -0.02em;
}

.alpha-label {
  font-size: 11px;
  font-weight: 700;
  color: #3d6652;
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

@media (max-width: 767px) {
  .alphabet-grid {
    grid-template-columns: repeat(auto-fill, minmax(56px, 1fr));
  }
}
</style>
