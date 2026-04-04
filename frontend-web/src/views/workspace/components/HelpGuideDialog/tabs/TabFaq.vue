<template>
  <div class="tab-faq">
    <el-collapse v-model="expandedFaq" accordion class="faq-collapse">
      <el-collapse-item
        v-for="faq in faqList"
        :key="faq.key"
        :name="faq.key"
      >
        <template #title>
          <div class="faq-title">
            <span class="faq-q-icon">Q</span>
            {{ faq.question }}
          </div>
        </template>
        <div class="faq-answer">{{ faq.answer }}</div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FAQ_LIST } from '../helpData'

const expandedFaq = ref('')
const faqList = FAQ_LIST
</script>

<style lang="scss" scoped>
.faq-collapse {
  border: none;

  :deep(.el-collapse-item) {
    margin-bottom: 8px;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(33, 109, 75, 0.08);
    background: #f9fbfa;

    .el-collapse-item__header {
      padding: 14px 18px;
      background: transparent;
      border: none;
      height: auto;
      line-height: 1.5;
      font-size: 14px;
    }

    .el-collapse-item__wrap {
      border: none;
      background: transparent;
    }

    .el-collapse-item__content {
      padding: 0 18px 16px;
    }

    &.is-active {
      background: #f4f9f6;
      border-color: rgba(33, 109, 75, 0.15);
    }
  }
}

.faq-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #18342c;
}

.faq-q-icon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: #216d4b;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.faq-answer {
  font-size: 13px;
  color: #5a7a6f;
  line-height: 1.7;
  padding-left: 32px;
}
</style>
