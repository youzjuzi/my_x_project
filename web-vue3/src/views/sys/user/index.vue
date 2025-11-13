<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
        </div>
      </template>
      <div class="content">
        <p>这是用户列表页面</p>
        <p>菜单ID: 2</p>
        <p>路径: /sys/user</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 用户列表页面
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

