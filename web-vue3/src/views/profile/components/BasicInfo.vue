<template>
  <div class="basic-info">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="用户名">
        {{ user.name || '未设置' }}
      </el-descriptions-item>
      <el-descriptions-item label="用户角色">
        {{ user.role || '普通用户' }}
      </el-descriptions-item>
      <el-descriptions-item label="邮箱">
        {{ user.email || '未设置' }}
      </el-descriptions-item>
      <el-descriptions-item label="注册时间">
        {{ user.createTime || '未知' }}
      </el-descriptions-item>
      <el-descriptions-item label="最后登录">
        {{ user.lastLoginTime || '未知' }}
      </el-descriptions-item>
      <el-descriptions-item label="用户状态">
        <el-tag type="success" size="small">正常</el-tag>
      </el-descriptions-item>
    </el-descriptions>
    
    <div class="action-buttons" style="margin-top: 20px;">
      <el-button type="primary" @click="handleEdit">
        <el-icon><Edit /></el-icon>
        编辑信息
      </el-button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { Edit } from '@element-plus/icons-vue';

export default defineComponent({
  name: 'BasicInfo',
  components: {
    Edit
  },
  props: {
    user: {
      type: Object,
      default: () => ({
        name: '',
        role: '',
        email: '',
        createTime: '',
        lastLoginTime: ''
      })
    }
  },
  methods: {
    handleEdit() {
      this.$emit('update', {
        // TODO: 后续实现编辑功能
      });
      this.$message.info('编辑功能开发中...');
    }
  }
});
</script>

<style lang="scss" scoped>
.basic-info {
  padding: 20px;
}
</style>

