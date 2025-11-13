<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文字翻译手语</span>
        </div>
      </template>
      <div class="content">
        <p>这是文字翻译手语页面</p>
        <p>菜单ID: 6</p>
        <p>路径: /translation/reverse_translation</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 文字翻译手语页面
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

