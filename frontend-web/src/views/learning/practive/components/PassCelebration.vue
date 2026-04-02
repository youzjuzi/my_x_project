<template>
  <!-- 过关庆祝覆盖层 -->
  <Transition name="celebration">
    <div v-if="visible" class="celebration-overlay" @click.self="onDismiss">

      <!-- 粒子特效 -->
      <div class="particles">
        <span v-for="i in 12" :key="i" class="particle" :style="particleStyle(i)" />
      </div>

      <!-- 主卡片 -->
      <div class="celebration-card">

        <!-- 动态 SVG 对勾圆环 -->
        <div class="check-ring">
          <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 外圆 -->
            <circle
              cx="40" cy="40" r="36"
              stroke="url(#ringGrad)"
              stroke-width="4"
              stroke-linecap="round"
              stroke-dasharray="226"
              class="ring-circle"
            />
            <!-- 对勾 -->
            <polyline
              points="22,42 35,55 58,28"
              stroke="url(#checkGrad)"
              stroke-width="5"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="check-mark"
            />
            <defs>
              <linearGradient id="ringGrad" x1="0" y1="0" x2="80" y2="80" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#4ade80" />
                <stop offset="100%" stop-color="#22c55e" />
              </linearGradient>
              <linearGradient id="checkGrad" x1="22" y1="28" x2="58" y2="55" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#ffffff" />
                <stop offset="100%" stop-color="#bbf7d0" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <!-- 过关文字 -->
        <p class="pass-label">过关！</p>
        <div class="char-badge">{{ char }}</div>
        <p class="pass-sub">已掌握 {{ passedCount }} / {{ totalCount }} 个{{ modeLabel }}</p>

        <!-- 操作按钮 -->
        <div class="btn-group">
          <button class="btn-next" @click="onNext">继续下一个</button>
          <button class="btn-stay" @click="onDismiss">继续练习</button>
        </div>
      </div>

    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible:     { type: Boolean, default: false },
  char:        { type: String,  default: '' },
  passedCount: { type: Number,  default: 0 },
  totalCount:  { type: Number,  default: 26 },
  mode:        { type: String,  default: 'letters' }, // 'letters' | 'numbers'
})

const emit = defineEmits(['next', 'dismiss'])

const modeLabel = computed(() => props.mode === 'numbers' ? '数字' : '字母')

const onNext    = () => emit('next')
const onDismiss = () => emit('dismiss')

// ========== 粒子样式：随机分布在周围 ==========
const COLORS = ['#4ade80', '#86efac', '#fde68a', '#fbbf24', '#a5f3fc', '#818cf8']

function particleStyle(i) {
  // 把 12 个粒子均匀分布在 360° 上，再加一点随机偏移
  const angle = (i / 12) * 360 + Math.random() * 15
  const dist  = 100 + Math.random() * 60   // 离中心的距离(px)
  const color = COLORS[i % COLORS.length]
  const delay = (Math.random() * 0.4).toFixed(2)
  const size  = 6 + Math.floor(Math.random() * 6)
  return {
    '--angle':  `${angle}deg`,
    '--dist':   `${dist}px`,
    '--color':  color,
    '--delay':  `${delay}s`,
    '--size':   `${size}px`,
  }
}
</script>

<style scoped lang="scss">
/* ========== 整体覆盖层 ========== */
.celebration-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(5, 15, 10, 0.78);
  backdrop-filter: blur(10px);
}

/* ========== Transition ========== */
.celebration-enter-active { animation: overlayIn 0.35s ease; }
.celebration-leave-active { animation: overlayOut 0.25s ease forwards; }

@keyframes overlayIn  { from { opacity: 0 } to { opacity: 1 } }
@keyframes overlayOut { from { opacity: 1 } to { opacity: 0 } }

/* ========== 粒子 ========== */
.particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.particle {
  position: absolute;
  width: var(--size);
  height: var(--size);
  border-radius: 50%;
  background: var(--color);
  animation: burst 0.9s cubic-bezier(0.22, 1, 0.36, 1) var(--delay) both;
}

@keyframes burst {
  0% {
    transform: translate(0, 0) scale(0);
    opacity: 1;
  }
  60% {
    opacity: 1;
  }
  100% {
    transform:
      translate(
        calc(cos(var(--angle)) * var(--dist)),
        calc(sin(var(--angle)) * var(--dist))
      )
      scale(1);
    opacity: 0;
  }
}

/* ========== 主卡片 ========== */
.celebration-card {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 32px 44px 28px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.10);
  border: 1px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(24px);
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(74, 222, 128, 0.12) inset;
  animation: cardPop 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes cardPop {
  from { transform: scale(0.7); opacity: 0 }
  to   { transform: scale(1);   opacity: 1 }
}

/* ========== SVG 对勾圆环 ========== */
.check-ring {
  width: 88px;
  height: 88px;
  margin: 0 auto 14px;

  svg { width: 100%; height: 100%; }
}

/* 圆环描边动画 */
.ring-circle {
  stroke-dashoffset: 226;
  animation: drawRing 0.6s ease 0.15s forwards;
  transform-origin: 40px 40px;
  transform: rotate(-90deg);
}

@keyframes drawRing {
  to { stroke-dashoffset: 0; }
}

/* 对勾描边动画 */
.check-mark {
  stroke-dasharray: 60;
  stroke-dashoffset: 60;
  animation: drawCheck 0.4s ease 0.55s forwards;
}

@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}

/* ========== 文字 ========== */
.pass-label {
  margin: 0 0 10px;
  font-size: 26px;
  font-weight: 900;
  color: #fff;
  letter-spacing: 2px;
  text-shadow: 0 0 20px rgba(74, 222, 128, 0.6);
  animation: textSlideUp 0.4s ease 0.4s both;
}

.char-badge {
  display: inline-block;
  margin-bottom: 10px;
  padding: 6px 24px;
  border-radius: 999px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  font-size: 32px;
  font-weight: 900;
  box-shadow: 0 8px 24px rgba(34, 197, 94, 0.4);
  animation: textSlideUp 0.4s ease 0.45s both;
}

.pass-sub {
  margin: 0 0 22px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  animation: textSlideUp 0.4s ease 0.5s both;
}

@keyframes textSlideUp {
  from { transform: translateY(12px); opacity: 0 }
  to   { transform: translateY(0);    opacity: 1 }
}

/* ========== 按钮 ========== */
.btn-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  animation: textSlideUp 0.4s ease 0.55s both;
}

.btn-next {
  padding: 10px 22px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(34, 197, 94, 0.35);
  transition: transform 0.15s, box-shadow 0.15s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 22px rgba(34, 197, 94, 0.45);
  }
}

.btn-stay {
  padding: 10px 22px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.75);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: rgba(255, 255, 255, 0.15); }
}
</style>
