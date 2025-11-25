<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- 左侧用户信息卡片 -->
      <el-col :span="6" :xs="24">
        <el-card class="user-card">
          <div class="user-profile">
            <div class="avatar-wrapper">
              <img :src="user.avatar || defaultAvatar" class="user-avatar" alt="头像" />
            </div>
            <div class="user-info">
              <h3 class="user-name">{{ user.name || '未设置' }}</h3>
              <p class="user-role">{{ user.role || '普通用户' }}</p>
              <p class="user-email">{{ user.email || '未设置' }}</p>
            </div>
          </div>
          
          <el-divider />
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ userStats.totalRecords || 0 }}</div>
              <div class="stat-label">总记录数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.todayRecords || 0 }}</div>
              <div class="stat-label">今日记录</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧内容区域 -->
      <el-col :span="18" :xs="24">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="账户设置" name="account">
              <account :user="user" @update="handleUserUpdate" @switch-tab="handleSwitchTab" />
            </el-tab-pane>
            <el-tab-pane label="基本信息" name="basic">
              <basic-info :user="user" @update="handleUserUpdate" />
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
import Account from './components/Account';
import BasicInfo from './components/BasicInfo';
import SecuritySettings from './components/SecuritySettings';
import { defineComponent } from 'vue';
import store from '@/store';

export default defineComponent({
  name: 'Profile',
  components: { 
    Account,
    BasicInfo,
    SecuritySettings
  },
  data() {
    return {
      user: {},
      activeTab: 'account',
      defaultAvatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
      userStats: {
        totalRecords: 0,
        todayRecords: 0
      }
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
    this.getUserStats();
  },
  methods: {
    getUser() {
      this.user = {
        name: this.name || '未设置',
        role: this.roles && this.roles.length > 0 ? this.roles.join(' | ') : '普通用户',
        email: 'admin@test.com', // 这里后续可以从API获取
        phone: '', // 这里后续可以从API获取
        avatar: this.avatar || this.defaultAvatar
      };
    },
    getUserStats() {
      // TODO: 后续从API获取用户统计数据
      this.userStats = {
        totalRecords: 0,
        todayRecords: 0
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
      margin-bottom: 20px;
      
      .user-avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 3px solid #f0f0f0;
        object-fit: cover;
      }
    }
    
    .user-info {
      .user-name {
        margin: 10px 0 5px;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
      
      .user-role {
        margin: 5px 0;
        font-size: 14px;
        color: #909399;
      }
      
      .user-email {
        margin: 5px 0;
        font-size: 13px;
        color: #606266;
      }
    }
  }
  
  .user-stats {
    display: flex;
    justify-content: space-around;
    padding: 20px 0;
    
    .stat-item {
      text-align: center;
      
      .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #409eff;
        margin-bottom: 5px;
      }
      
      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}
</style>
