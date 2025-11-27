<template>
  <div class="glossary-container">
    <div class="filter-bar">
      <div class="left-panel">
        <h2 class="page-title">🖐️ 基础手势图解</h2>
        <p class="sub-title">ASL 标准指拼字母表与数字图示</p>
      </div>
      <div class="right-panel">
        <el-radio-group v-model="activeTab" size="large" class="custom-tabs">
          <el-radio-button label="letters">字母 A-Z</el-radio-button>
          <el-radio-button label="numbers">数字 0-9</el-radio-button>
        </el-radio-group>
        <el-input
          v-model="searchKey"
          placeholder="搜索手势..."
          prefix-icon="Search"
          class="search-input"
          clearable
        />
      </div>
    </div>

    <div class="grid-content">
      <el-empty v-if="filteredList.length === 0" description="未找到相关手势" />

      <div
        v-for="(item, index) in filteredList"
        :key="index"
        class="gesture-card"
        @click="handleCardClick(item)"
      >
        <div class="card-image">
          <el-image
            :src="item.image"
            fit="contain"
            loading="lazy"
          >
            <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </div>

        <div class="card-footer">
          <div class="info">
            <span class="label">{{ item.label }}</span>
            <span class="desc">{{ item.desc }}</span>
          </div>
          <div class="action-btn">
            <el-button type="primary" circle size="small" icon="VideoPlay" />
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="手势详情" width="30%" align-center>
      <div class="detail-view">
        <img :src="currentItem.image" class="detail-img" />
        <h3>{{ currentItem.label }}</h3>
        <p>{{ currentItem.desc }}</p>
        <el-alert title="提示：请保持手掌正对摄像头，注意手指弯曲角度。" type="info" show-icon :closable="false" />
      </div>
      <template #footer>
        <el-button type="primary" @click="goToPractice(currentItem)">去跟读练习</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Picture, VideoPlay } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('letters')
const searchKey = ref('')
const dialogVisible = ref(false)
const currentItem = ref({})

// 使用 Cloudflare 上的字母图片
const glossaryData = {
  letters: Array.from({ length: 26 }, (_, i) => {
    const letter = String.fromCharCode(65 + i); // A-Z
    return {
      label: letter,
      desc: `ASL 字母 ${letter}`,
      // Cloudflare 图片路径，图片尺寸 775x804
      image: `https://avatar.youzilite.us.kg/letter/${letter}.png`
    };
  }),
  numbers: Array.from({ length: 10 }, (_, i) => ({
    label: String(i),
    desc: `数字手势 ${i}`,
    // Cloudflare 数字图片路径，图片尺寸 549x868
    image: `https://avatar.youzilite.us.kg/number/${i}.png`
  }))
}

// 过滤逻辑
const filteredList = computed(() => {
  const list = glossaryData[activeTab.value] || []
  if (!searchKey.value) return list
  return list.filter(item => item.label.toLowerCase().includes(searchKey.value.toLowerCase()))
})

// 点击交互
const handleCardClick = (item) => {
  currentItem.value = item
  dialogVisible.value = true
}

const goToPractice = (item) => {
  // 跳转到跟读页面，并把当前字母传过去
  router.push({ path: '/learning/practice', query: { target: item.label } })
}
</script>

<style scoped lang="scss">
.glossary-container {
  padding: 24px;
  min-height: calc(100vh - 84px);
  background-color: #f5f7fa; /* 与你的新侧边栏匹配的浅灰底色 */
}

/* 1. 顶部栏样式 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
  background: #fff;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #1e2a4a;
    margin: 0 0 8px 0;
  }
  .sub-title {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .right-panel {
    display: flex;
    gap: 16px;

    .search-input {
      width: 240px;
      :deep(.el-input__wrapper) {
        border-radius: 20px;
        box-shadow: 0 0 0 1px #e4e7ed inset;
      }
    }
  }
}

/* 2. 卡片网格 (Grid 布局) */
.grid-content {
  display: grid;
  /* 自适应列宽，最小 200px */
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
}

/* 3. 单个卡片样式 */
.gesture-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(83, 64, 232, 0.15); /* 悬停时的紫色光晕 */
    border-color: rgba(83, 64, 232, 0.2);

    .action-btn .el-button {
      background-color: #5340E8;
      border-color: #5340E8;
      color: #fff;
    }
  }

  .card-image {
    height: 260px; // 增加高度以适应数字图片 549x868 和字母图片 775x804
    padding: 20px;
    background: #fcfcfc;
    display: flex;
    justify-content: center;
    align-items: center;

    .el-image {
      width: 100%;
      height: 100%;
      transition: transform 0.3s;
      
      :deep(img) {
        object-fit: contain; // 保持图片比例，完整显示
      }
    }
  }

  .card-footer {
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #f0f2f5;

    .info {
      .label {
        display: block;
        font-size: 20px;
        font-weight: 700;
        color: #1e2a4a;
      }
      .desc {
        font-size: 12px;
        color: #909399;
      }
    }

    .action-btn .el-button {
      transition: all 0.3s;
      background-color: #f0f2f5;
      border: none;
      color: #909399;
    }
  }
}

/* 详情弹窗微调 */
.detail-view {
  text-align: center;
  .detail-img {
    max-width: 100%;
    max-height: 400px; // 增加高度以适应 775x804 的图片
    height: auto;
    margin-bottom: 20px;
    object-fit: contain;
  }
  h3 { font-size: 32px; margin: 10px 0; color: #5340E8; }
  p { color: #606266; margin-bottom: 20px; }
}

/* 定制 Element Tabs 样式 */
:deep(.el-radio-button__inner) {
  border: none;
  background: #f0f2f5;
  margin-right: 10px;
  border-radius: 8px;
  color: #606266;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #5340E8; /* 品牌紫 */
  color: #fff;
  box-shadow: none;
}
</style>