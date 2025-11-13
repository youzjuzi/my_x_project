<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统日志</span>
        </div>
      </template>
      <div class="content">
        <p>这是系统日志页面</p>
        <p>菜单ID: 9</p>
        <p>路径: /logging/system_logs</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 系统日志页面
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

