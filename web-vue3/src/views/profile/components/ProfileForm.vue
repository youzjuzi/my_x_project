<template>
  <div class="profile-form">
    <el-form :model="form" label-width="100px" style="max-width: 500px;">
      <el-form-item label="用户名">
        <el-input v-model="form.name" placeholder="请输入用户名" />
      </el-form-item>
      
      <el-form-item label="邮箱">
        <span class="readonly-text">{{ user.email || '未设置' }}</span>
        <el-button type="text" size="small" style="margin-left: 10px;" @click="goToSecurity">
          前往安全设置修改
        </el-button>
      </el-form-item>
      
      <el-form-item label="手机号">
        <span class="readonly-text">{{ user.phone || '未设置' }}</span>
        <el-button type="text" size="small" style="margin-left: 10px;" @click="goToSecurity">
          前往安全设置修改
        </el-button>
      </el-form-item>
      
      <el-form-item label="个人简介">
        <el-input
          v-model="form.bio"
          type="textarea"
          :rows="4"
          placeholder="请输入个人简介"
          maxlength="200"
          show-word-limit />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">保存修改</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import store from '@/store';
import { ElMessage } from 'element-plus';

export default defineComponent({
  name: 'ProfileForm',
  props: {
    user: {
      type: Object,
      default: () => ({
        name: '',
        email: '',
        phone: '',
        avatar: ''
      })
    }
  },
  emits: ['update', 'switch-tab'],
  data() {
    return {
      form: {
        name: '',
        bio: ''
      }
    };
  },
  watch: {
    user: {
      handler(newVal) {
        if (newVal) {
          this.form = {
            name: newVal.name || '',
            bio: newVal.bio || ''
          };
        }
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    handleSubmit() {
      // TODO: 后续调用API保存用户信息
      this.$emit('update', {
        name: this.form.name,
        bio: this.form.bio
      });
      
      // 更新store中的用户信息
      if (this.form.name) {
        store.user().name = this.form.name;
      }
      
      ElMessage.success('用户信息更新成功');
    },
    goToSecurity() {
      this.$emit('switch-tab', 'security');
    }
  }
});
</script>

<style lang="scss" scoped>
.profile-form {
  padding: 20px;
  
  .readonly-text {
    color: #606266;
    font-size: 14px;
  }
}
</style>

