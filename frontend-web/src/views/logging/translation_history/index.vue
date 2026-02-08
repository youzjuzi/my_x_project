<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>手语翻译历史</span>
        </div>
      </template>
      <div class="content">
        <p>这是手语翻译历史页面</p>
        <p>菜单ID: 8</p>
        <p>路径: /logging/translation_history</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 手语翻译历史页面
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.content {
  padding: 20px 0;
}
</style>

