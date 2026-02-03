<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- 左侧用户信息卡片 -->
      <el-col :span="6" :xs="24">
        <el-card class="user-card">
          <div class="user-profile">
            <div class="avatar-wrapper" @click="triggerAvatarUpload">
              <img :src="user.avatar || defaultAvatar" class="user-avatar" alt="头像" />
              <div class="avatar-overlay">
                <el-icon :size="30" color="#fff"><Camera /></el-icon>
                <span>更换头像</span>
              </div>
              <input
                ref="avatarInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleAvatarChange"
              />
            </div>
            <div class="user-info">
              <h3 class="user-name">{{ user.name || '未设置' }}</h3>
              <el-tag :type="getRoleTagType(user.role)" size="small" style="margin: 8px 0;">
                {{ user.role || '普通用户' }}
              </el-tag>
              <p class="user-email">{{ user.email || '未设置' }}</p>
            </div>
          </div>
          
          <el-divider />
          
          <div class="user-meta">
            <div class="meta-item">
              <span class="meta-label">注册时间</span>
              <span class="meta-value">{{ user.createTime || '未知' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">最后登录</span>
              <span class="meta-value">{{ user.lastLoginTime || '未知' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧内容区域 -->
      <el-col :span="18" :xs="24">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本资料" name="profile">
              <profile-form :user="user" @update="handleUserUpdate" @switch-tab="handleSwitchTab" />
            </el-tab-pane>
            <el-tab-pane label="安全设置" name="security">
              <security-settings :user="user" @update="handleUserUpdate" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 头像预览对话框 -->
    <el-dialog
      v-model="showAvatarPreview"
      title="预览头像"
      width="400px"
      @close="cancelAvatarPreview">
      <div class="avatar-preview-container">
        <img :src="previewAvatarUrl" alt="预览头像" class="preview-avatar" />
        <p class="preview-tip">确认使用此头像吗？</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelAvatarPreview">取消</el-button>
          <el-button type="primary" :loading="uploadingAvatar" @click="confirmUploadAvatar">确认上传</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { mapState } from 'pinia';
import ProfileForm from './components/ProfileForm';
import SecuritySettings from './components/SecuritySettings';
import { defineComponent } from 'vue';
import { Camera } from '@element-plus/icons-vue';
import store from '@/store';
import { ElMessage } from 'element-plus';
import { getProfileInfo, uploadAvatar } from '@/api/profile';

export default defineComponent({
  name: 'Profile',
  components: { 
    ProfileForm,
    SecuritySettings,
    Camera
  },
  data() {
    return {
      user: {},
      activeTab: 'profile',
      defaultAvatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
      loading: false,
      showAvatarPreview: false,
      previewAvatarUrl: '',
      selectedFile: null,
      uploadingAvatar: false
    };
  },
  computed: {
    ...mapState(store.user, [
      'name',
      'avatar',
      'roles',
      'token'
    ])
  },
  watch: {
    name(newVal) {
      if (this.user) {
        this.user.name = newVal;
      }
    }
  },
  created() {
    this.getUser();
  },
  methods: {
    // 获取用户信息
    async getUser() {
      this.loading = true;
      try {
        const response = await getProfileInfo();
        const data = response?.data || {};
        this.user = {
          id: data.id || null,
          name: data.name || '未设置',
          role: data.role || (Array.isArray(data.roles) && data.roles.length ? data.roles[0] : '普通用户'),
          roles: data.roles || [],
          email: data.email || '',
          phone: data.phone || '',
          avatar: data.avatar || this.avatar || this.defaultAvatar,
          createTime: data.createTime || '',
          lastLoginTime: data.lastLoginTime || '',
          bio: data.bio || ''
        };

        if (data.name) {
          store.user().name = data.name;
        }
        if (data.avatar) {
          store.user().avatar = data.avatar;
        }
      } catch (error) {
        console.error('获取用户信息失败', error);
        ElMessage.error('获取用户信息失败，请稍后重试');
      } finally {
        this.loading = false;
      }
    },
    handleUserUpdate(updatedUser) {
      // 更新成功后重新从后端获取最新数据
      this.getUser();
    },
    handleSwitchTab(tabName) {
      this.activeTab = tabName;
    },
    getRoleTagType(role) {
      if (role && role.includes('管理员')) {
        return 'danger';
      } else if (role && role.includes('编辑')) {
        return 'warning';
      }
      return 'info';
    },
    triggerAvatarUpload() {
      this.$refs.avatarInput.click();
    },
    handleAvatarChange(event) {
      const file = event.target.files[0];
      if (!file) return;

      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        ElMessage.error('只能上传图片文件!');
        event.target.value = '';
        return;
      }

      // 验证文件大小
      if (file.size / 1024 / 1024 > 5) {
        ElMessage.error('图片大小不能超过 5MB!');
        event.target.value = '';
        return;
      }

      // 保存选中的文件
      this.selectedFile = file;

      // 预览头像
      const reader = new FileReader();
      reader.onload = (e) => {
        this.previewAvatarUrl = e.target.result;
        this.showAvatarPreview = true;
      };
      reader.readAsDataURL(file);

      // 清空input，以便可以重复选择同一文件
      event.target.value = '';
    },
    cancelAvatarPreview() {
      this.showAvatarPreview = false;
      this.previewAvatarUrl = '';
      this.selectedFile = null;
    },
    async confirmUploadAvatar() {
      if (!this.selectedFile) {
        ElMessage.error('请先选择图片');
        return;
      }

      try {
        this.uploadingAvatar = true;
        const response = await uploadAvatar(this.selectedFile);
        if (response.code === 20000 && response.data) {
          const avatarUrl = response.data.url;
          this.user.avatar = avatarUrl;
          this.handleUserUpdate({ avatar: avatarUrl });
          ElMessage.success('头像上传成功');
          this.cancelAvatarPreview();
        } else {
          ElMessage.error(response.message || '头像上传失败');
        }
      } catch (error) {
        console.error('头像上传失败:', error);
        const errorMessage = error.response?.data?.message || error.message || '头像上传失败，请稍后重试';
        ElMessage.error(errorMessage);
      } finally {
        this.uploadingAvatar = false;
      }
    }
  }
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.avatar-preview-container {
  text-align: center;
  padding: 20px;

  .preview-avatar {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #e4e7ed;
    margin-bottom: 20px;
  }

  .preview-tip {
    color: #606266;
    font-size: 14px;
    margin: 0;
  }
}

.user-card {
  .user-profile {
    text-align: center;
    
    .avatar-wrapper {
      position: relative;
      display: inline-block;
      margin-bottom: 20px;
      cursor: pointer;
      
      .user-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 3px solid #f0f0f0;
        object-fit: cover;
        transition: all 0.3s;
      }

      .avatar-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;
        color: #fff;

        span {
          font-size: 12px;
          margin-top: 5px;
        }
      }

      &:hover .avatar-overlay {
        opacity: 1;
      }

      &:hover .user-avatar {
        border-color: #409eff;
      }
    }
    
    .user-info {
      .user-name {
        margin: 10px 0 5px;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
      
      .user-email {
        margin: 8px 0;
        font-size: 13px;
        color: #606266;
      }
    }
  }
  
  .user-meta {
    padding: 10px 0;
    
    .meta-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      font-size: 13px;
      
      .meta-label {
        color: #909399;
      }
      
      .meta-value {
        color: #606266;
        font-weight: 500;
      }
    }
  }
}
</style>
