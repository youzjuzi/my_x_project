<template>
  <div class="profile-form">
    <div class="form-header">
      <h3>基本资料</h3>
      <el-button v-if="!isEditing" type="primary" link @click="startEdit">
        修改资料
      </el-button>
    </div>
    <el-form :model="form" label-width="100px" class="profile-form__body">
      <el-form-item label="昵称">
        <el-input 
          v-model="form.name" 
          placeholder="请输入昵称" 
          :disabled="!isEditing"
          @blur="checkUsername"
          :loading="checkingUsername" />
        <div v-if="nameError" class="error-message">{{ nameError }}</div>
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

      <el-form-item label="邮箱">
        <div class="readonly-field">
          <span>{{ user.email || '未设置' }}</span>
          <el-button type="text" size="small" @click="goToSecurity">前往安全设置修改</el-button>
        </div>
      </el-form-item>

      <el-form-item label="手机号">
        <div class="readonly-field">
          <span>{{ user.phone || '未设置' }}</span>
          <el-button type="text" size="small" @click="goToSecurity">前往安全设置修改</el-button>
        </div>
      </el-form-item>

      <el-form-item label="注册时间">
        <span class="readonly-text">{{ user.createTime || '---' }}</span>
      </el-form-item>

      <el-form-item label="最后登录">
        <span class="readonly-text">{{ user.lastLoginTime || '---' }}</span>
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
import { checkUsername } from '@/api/profile';

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
      },
      checkingUsername: false,
      nameError: ''
    };
  },
  computed: {
    hasChanges() {
      return (this.form.name !== this.originalForm.name || this.form.bio !== this.originalForm.bio) && !this.nameError;
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
      this.nameError = '';
    },
    async checkUsername() {
      // 如果昵称没有变化，不需要检测
      if (this.form.name === this.originalForm.name || !this.form.name.trim()) {
        this.nameError = '';
        return;
      }

      // 如果昵称为空，不需要检测
      if (!this.form.name || !this.form.name.trim()) {
        this.nameError = '';
        return;
      }

      this.checkingUsername = true;
      this.nameError = '';

      try {
        const response = await checkUsername(this.form.name.trim());
        // 后端返回格式：{ code: 20000, message: "0"或"1", data: null }
        // message === "0" 表示账号已存在
        // message === "1" 表示账号不存在，可以使用
        const message = response.message;
        if (message === "0") {
          this.nameError = '该昵称已被使用，请更换其他昵称';
        } else if (message === "1") {
          this.nameError = '';
        } else {
          // 如果返回格式异常，不显示错误，允许用户继续
          console.warn('检测账号返回格式异常:', response);
          this.nameError = '';
        }
      } catch (error) {
        console.error('检测账号失败:', error);
        // 网络错误时不阻止用户，只提示
        ElMessage.warning('检测账号时出现错误，请稍后重试');
        this.nameError = '';
      } finally {
        this.checkingUsername = false;
      }
    },
    handleSubmit() {
      if (!this.isEditing) {
        ElMessage.info('请先点击"修改资料"进入编辑状态');
        return;
      }

      // 如果有错误，不允许提交
      if (this.nameError) {
        ElMessage.warning('请先解决昵称冲突问题');
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
      this.nameError = '';
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
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  
  &__body {
    max-width: 520px;
  }
  
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

  .readonly-field {
    display: flex;
    align-items: center;
    gap: 12px;
    
    span {
      color: #303133;
    }
  }

  .error-message {
    color: #f56c6c;
    font-size: 12px;
    margin-top: 4px;
    line-height: 1.5;
  }
}
</style>

