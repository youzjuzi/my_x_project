<template>
  <div class="navbar">
    <hamburger id="hamburger-container" :is-active="sidebar.opened" class="hamburger-container"
               @toggleClick="toggleSidebar" />

    <breadcrumb id="breadcrumb-container" class="breadcrumb-container" />

    <div class="right-menu">
      <template v-if="device !== 'mobile'">
        <search id="header-search" class="right-menu-item" />

        <error-log class="errLog-container right-menu-item hover-effect" />

        <screenfull id="screenfull" class="right-menu-item hover-effect" />

      </template>

      <el-dropdown class="avatar-container right-menu-item hover-effect" trigger="click">
        <div class="avatar-wrapper">
          <img :src="avatar + '?imageView2/1/w/80/h/80'" class="user-avatar">
          <el-icon class="el-icon-caret-bottom" size="small">
            <CaretBottom />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <router-link to="/profile/index">
              <el-dropdown-item>个人中心</el-dropdown-item>
            </router-link>
            <router-link to="/">
              <el-dropdown-item>首页</el-dropdown-item>
            </router-link>
            <a target="_blank" href="https://github.com/midfar/vue3-element-admin">
              <el-dropdown-item>项目地址</el-dropdown-item>
            </a>
            <a target="_blank" href="https://vue3-element-admin-site.midfar.com/">
              <el-dropdown-item>文档地址</el-dropdown-item>
            </a>
            <el-dropdown-item divided @click="logout">
              <span style="display:block;">退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { mapState } from 'pinia';
import store from '@/store';
import Breadcrumb from '@/components/Breadcrumb';
import Hamburger from '@/components/Hamburger';
import ErrorLog from '@/components/ErrorLog';
import Screenfull from '@/components/Screenfull';
import SizeSelect from '@/components/SizeSelect';
import Search from '@/components/HeaderSearch';
import { defineComponent } from 'vue';
import { CaretBottom } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

export default defineComponent({
  components: {
    Breadcrumb,
    Hamburger,
    ErrorLog,
    Screenfull,
    SizeSelect,
    Search,
    CaretBottom
  },
  computed: {
    ...mapState(store.app, [
      'sidebar',
      'device'
    ]),
    ...mapState(store.user, [
      'avatar'
    ])
  },
  methods: {
    toggleSidebar() {
      store.app().toggleSidebar();
    },
    async logout() {
      try {
        await store.user().logout();
        ElMessage.success('退出登录成功');
        // 清除路由历史，跳转到登录页（不保留 redirect 参数）
        this.$router.replace('/login');
      } catch (error) {
        ElMessage.error('退出登录失败，请稍后重试');
      }
    }
  }
});
</script>

<style lang="scss" scoped>
.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, .04);

  .hamburger-container {
    line-height: 46px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color: transparent;

    &:hover {
      background: rgba(0, 0, 0, .025)
    }
  }

  .breadcrumb-container {
    float: left;
  }

  .errLog-container {
    display: inline-block;
    vertical-align: top;
  }

  .right-menu {
    float: right;
    height: 100%;
    line-height: 50px;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      line-height: 50px;
      font-size: 18px;
      color: #5a5e66;
      vertical-align: text-bottom;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

      .nav-icon {
        font-size: 18px;
        transition: color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      }

      &.hover-effect {
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          background: rgba(99, 102, 241, 0.08);
          color: #5340E8;
          
          // 所有类型的图标都变为主题紫色
          :deep(.el-icon),
          :deep(svg),
          :deep(.svg-icon),
          :deep(.search-icon),
          :deep(.size-icon),
          :deep(.el-button) {
            color: #5340E8 !important;
            fill: #5340E8 !important;
          }
          
          // SVG 图标特殊处理
          :deep(svg.svg-icon) {
            fill: #5340E8 !important;
          }
        }
      }
    }
    
    // 搜索组件特殊处理
    #header-search {
      &.hover-effect:hover {
        :deep(.search-icon),
        :deep(.svg-icon) {
          color: #5340E8 !important;
          fill: #5340E8 !important;
        }
      }
    }

    .avatar-container {
      margin-right: 30px;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

      .avatar-wrapper {
        margin-top: 5px;
        position: relative;
        height: 45px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

        .user-avatar {
          cursor: pointer;
          width: 40px;
          height: 40px;
          border-radius: 10px;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .el-icon-caret-bottom {
          cursor: pointer;
          position: absolute;
          right: -20px;
          top: 25px;
          font-size: 12px;
          transition: color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
      }
      
      &:hover {
        .avatar-wrapper {
          .user-avatar {
            box-shadow: 0 0 0 2px rgba(83, 64, 232, 0.2);
          }
          
          .el-icon-caret-bottom {
            color: #5340E8;
          }
        }
      }
    }
  }
}
</style>
