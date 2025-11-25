<template>
  <div class="account-settings">
    <el-form :model="form" label-width="100px" style="max-width: 600px;">
      <el-form-item label="用户名">
        <el-input v-model="form.name" placeholder="请输入用户名" />
      </el-form-item>
      
      <el-form-item label="邮箱">
        <el-input :value="user.email || '未设置'" readonly placeholder="未设置">
          <template #append>
            <el-button type="text" size="small" @click="goToSecurity">前往安全设置修改</el-button>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="手机号">
        <el-input :value="user.phone || '未设置'" readonly placeholder="未设置">
          <template #append>
            <el-button type="text" size="small" @click="goToSecurity">前往安全设置修改</el-button>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item label="头像">
        <div class="avatar-upload">
          <img :src="form.avatar || defaultAvatar" class="avatar-preview" alt="头像" />
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            action="#">
            <el-button type="primary" size="small">更换头像</el-button>
          </el-upload>
        </div>
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
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import store from '@/store';
import { ElMessage } from 'element-plus';

export default defineComponent({
  name: 'Account',
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
      defaultAvatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
      form: {
        name: '',
        avatar: '',
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
            avatar: newVal.avatar || this.defaultAvatar,
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
        avatar: this.form.avatar,
        bio: this.form.bio
      });
      
      // 更新store中的用户信息
      if (this.form.name) {
        store.user().name = this.form.name;
      }
      if (this.form.avatar) {
        store.user().avatar = this.form.avatar;
      }
      
      ElMessage.success('用户信息更新成功');
    },
    handleReset() {
      this.form = {
        name: this.user.name || '',
        avatar: this.user.avatar || this.defaultAvatar,
        bio: this.user.bio || ''
      };
    },
    handleAvatarSuccess(res, file) {
      // TODO: 后续实现头像上传功能
      // 这里可以预览上传的头像
      this.form.avatar = URL.createObjectURL(file.raw);
      ElMessage.info('头像上传功能开发中，请使用图片URL');
    },
    beforeAvatarUpload(file) {
      const isImage = file.type.startsWith('image/');
      const isLt2M = file.size / 1024 / 1024 < 2;

      if (!isImage) {
        ElMessage.error('只能上传图片文件!');
        return false;
      }
      if (!isLt2M) {
        ElMessage.error('图片大小不能超过 2MB!');
        return false;
      }
      return true;
    },
    goToSecurity() {
      this.$emit('switch-tab', 'security');
    }
  }
});
</script>

<style lang="scss" scoped>
.account-settings {
  padding: 20px;
  
  .avatar-upload {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .avatar-preview {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid #dcdfe6;
    }
  }
}
</style>
