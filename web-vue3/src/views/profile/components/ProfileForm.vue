<template>
  <div class="profile-form">
    <div class="form-header">
      <h3>基本资料</h3>
      <el-button v-if="!isEditing" type="primary" link @click="startEdit">
        修改资料
      </el-button>
    </div>
    <el-form :model="form" label-width="100px" style="max-width: 500px;">
      <el-form-item label="用户名">
        <el-input v-model="form.name" placeholder="请输入用户名" :disabled="!isEditing" />
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
          show-word-limit
          :disabled="!isEditing" />
      </el-form-item>
      
      <el-form-item v-if="isEditing">
        <el-button type="primary" :disabled="!hasChanges" @click="handleSubmit">保存修改</el-button>
        <el-button @click="cancelEdit">取消</el-button>
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
      },
      isEditing: false,
      originalForm: {
        name: '',
        bio: ''
      }
    };
  },
  computed: {
    hasChanges() {
      return this.form.name !== this.originalForm.name || this.form.bio !== this.originalForm.bio;
    }
  },
  watch: {
    user: {
      handler(newVal) {
        if (newVal) {
          this.form = {
            name: newVal.name || '',
            bio: newVal.bio || ''
          };
          this.originalForm = { ...this.form };
          this.isEditing = false;
        }
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    startEdit() {
      this.isEditing = true;
      this.originalForm = { ...this.form };
    },
    cancelEdit() {
      this.form = { ...this.originalForm };
      this.isEditing = false;
    },
    handleSubmit() {
      if (!this.isEditing) {
        ElMessage.info('请先点击“修改资料”进入编辑状态');
        return;
      }
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
      this.isEditing = false;
      this.originalForm = { ...this.form };
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
  
  .form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .readonly-text {
    color: #606266;
    font-size: 14px;
  }
}
</style>

