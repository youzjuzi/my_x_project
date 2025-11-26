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
      defaultAvatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
    };
  },
  computed: {
    ...mapState(store.user, [
      'name',
      'avatar',
      'roles'
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
    getUser() {
      this.user = {
        name: this.name || '未设置',
        role: this.roles && this.roles.length > 0 ? this.roles[0] : '普通用户',
        email: 'admin@test.com', // 这里后续可以从API获取
        phone: '', // 这里后续可以从API获取
        avatar: this.avatar || this.defaultAvatar,
        createTime: '2024-01-01 10:00:00', // 这里后续可以从API获取
        lastLoginTime: '2024-12-20 15:30:00' // 这里后续可以从API获取
      };
    },
    handleUserUpdate(updatedUser) {
      this.user = { ...this.user, ...updatedUser };
      // 更新store中的用户信息
      if (updatedUser.name) {
        store.user().name = updatedUser.name;
      }
      if (updatedUser.avatar) {
        store.user().avatar = updatedUser.avatar;
      }
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
        return;
      }

      // 验证文件大小
      if (file.size / 1024 / 1024 > 2) {
        ElMessage.error('图片大小不能超过 2MB!');
        return;
      }

      // 预览头像
      const reader = new FileReader();
      reader.onload = (e) => {
        this.user.avatar = e.target.result;
        this.handleUserUpdate({ avatar: e.target.result });
        ElMessage.success('头像更新成功');
      };
      reader.readAsDataURL(file);

      // 清空input，以便可以重复选择同一文件
      event.target.value = '';
    }
  }
});
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
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
