<template>
  <div class="tab-commands">
    <p class="section-intro">
      以下手势用于控制识别流程，进入<strong>命令模式</strong>后生效。
    </p>

    <div class="command-cards">
      <div
        v-for="cmd in commands"
        :key="cmd.key"
        class="command-card"
        :style="{ '--cmd-color': cmd.color, '--cmd-bg': cmd.bg }"
      >
        <div class="cmd-symbol">{{ cmd.symbol }}</div>
        <div class="cmd-info">
          <div class="cmd-name">{{ cmd.label }}</div>
          <div class="cmd-desc">{{ cmd.desc }}</div>
          <div class="cmd-action">
            <span class="action-label">怎么比：</span>
            <span>{{ cmd.action }}</span>
          </div>
        </div>
        <div class="cmd-hint-badge">{{ cmd.hint }}</div>
      </div>
    </div>

    <div class="tip-banner">
      <span class="tip-icon">🎯</span>
      <span>指令手势需持续保持一段时间才会触发，防止误操作。视频画面左上角会显示命令模式 HUD。</span>
    </div>
  </div>
</template>

<script setup>
import { COMMAND_GESTURES } from '../helpData'

const commands = COMMAND_GESTURES
</script>

<style lang="scss" scoped>
.section-intro {
  margin: 0 0 16px;
  font-size: 13.5px;
  color: #5a7a6f;
  line-height: 1.6;

  strong {
    color: #216d4b;
    font-weight: 700;
  }
}

.command-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.command-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 16px;
  background: var(--cmd-bg);
  border: 1px solid color-mix(in srgb, var(--cmd-color) 15%, transparent);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 16px color-mix(in srgb, var(--cmd-color) 12%, transparent);
  }
}

.cmd-symbol {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--cmd-color);
  color: #fff;
  font-size: 20px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px color-mix(in srgb, var(--cmd-color) 25%, transparent);
}

.cmd-info {
  flex: 1;
  min-width: 0;
}

.cmd-name {
  font-size: 15px;
  font-weight: 700;
  color: #18342c;
  margin-bottom: 2px;
}

.cmd-desc {
  font-size: 12.5px;
  color: #5a7a6f;
  line-height: 1.5;
  margin-bottom: 6px;
}

.cmd-action {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  color: color-mix(in srgb, var(--cmd-color) 90%, #000);
  background: rgba(255, 255, 255, 0.65);
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px dashed color-mix(in srgb, var(--cmd-color) 30%, transparent);

  .action-label {
    font-weight: 700;
    margin-right: 4px;
    color: var(--cmd-color);
  }
}

.cmd-hint-badge {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid color-mix(in srgb, var(--cmd-color) 18%, transparent);
  color: var(--cmd-color);
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
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
