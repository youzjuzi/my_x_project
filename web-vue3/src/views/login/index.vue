<template>
  <div class="login-container">
    <div class="login-card">
      <!-- 标题区域 -->
      <div class="title-container">
        <h3 class="title">欢迎登录 <span class="system-name">Element后台管理系统</span></h3>
      </div>

      <!-- 登录表单 -->
      <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" label-position="top">

        <el-form-item prop="username" label="用户名">
          <el-input
            ref="username"
            v-model="loginForm.username"
            placeholder="请输入用户名"
            name="username"
            type="text"
            tabindex="1"
            autocomplete="on"
          >
            <template #prefix>
              <span class="svg-container"><svg-icon icon-class="user" /></span>
            </template>
          </el-input>
        </el-form-item>

        <el-tooltip v-model="capsTooltip" content="大写锁定已开启" placement="right" manual>
          <el-form-item prop="password" label="密码">
            <el-input
              :key="passwordType"
              ref="password"
              v-model="loginForm.password"
              :type="passwordType"
              placeholder="请输入密码"
              name="password"
              tabindex="2"
              autocomplete="on"
              @keyup="checkCapslock"
              @blur="capsTooltip = false"
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <span class="svg-container"><svg-icon icon-class="password" /></span>
              </template>
              <template #suffix>
                <span class="show-pwd" @click="showPwd">
                  <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
                </span>
              </template>
            </el-input>
          </el-form-item>
        </el-tooltip>
        <el-button :loading="loading" type="primary" style="width:100%;" @click.prevent="handleLogin">
          登 录
        </el-button>
         <!-- 添加注册相关文字 -->
        <div class="register-container">
          <span>还没有账号？</span>
          <el-button type="text" @click="handleRegister">立即注册</el-button>
          <el-divider direction="vertical"></el-divider>
          <el-button type="text" @click="handleForgetPassword">忘记密码</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script lang="ts">
// script部分与您提供的代码逻辑相同，此处不再赘述
import { validUsername } from '@/utils/validate';
import { defineComponent } from 'vue';
import type { FormItemRule } from 'element-plus';
import type { IForm } from '@/types/element-plus';
import store from '@/store';
import { ElMessage } from 'element-plus';

interface QueryType {
  [propname:string]:string
}

export default defineComponent({
  name: 'Login',
  data() {
    const validateUsername: FormItemRule['validator'] = (_rule, value, callback) => {
      if (!validUsername(value)) {
        callback(new Error('请输入正确的用户名'));
      } else {
        callback();
      }
    };
    const validatePassword: FormItemRule['validator'] = (_rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码不能少于6位'));
      } else {
        callback();
      }
    };
    return {
      loginForm: {
        username: 'admin',
        password: '123456'
      },
      loginRules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      passwordType: 'password',
      capsTooltip: false,
      loading: false,
      redirect: undefined,
      otherQuery: {}
    };
  },
  watch: {
    $route: {
      handler: function(route) {
        const query = route.query;
        if (query) {
          this.redirect = query.redirect;
          this.otherQuery = this.getOtherQuery(query);
        }
      },
      immediate: true
    }
  },
  mounted() {
    if (this.loginForm.username === '') {
      (this.$refs.username as any).focus();
    } else if (this.loginForm.password === '') {
      (this.$refs.password as any).focus();
    }
  },
  methods: {
    checkCapslock(e) {
      const { key } = e;
      this.capsTooltip = key && key.length === 1 && (key >= 'A' && key <= 'Z');
    },
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = '';
      } else {
        this.passwordType = 'password';
      }
      this.$nextTick(() => {
        (this.$refs.password as any).focus();
      });
    },
    // 登录
    handleLogin() {
      (this.$refs.loginForm as IForm).validate(valid => {
        return new Promise((resolve, reject) => {
          if (valid) {
            this.loading = true;
            store.user().login(this.loginForm)
              .then(() => {
                this.$router.push({ path: this.redirect || '/', query: this.otherQuery });
                this.loading = false;
              })
              .catch(() => {
                this.loading = false;
              }).finally(() => {
                resolve();
              });
          } else {
            console.log('error submit!!');
            reject();
          }
        });
      });
    },
    handleRegister() {
    ElMessage({
      message: '注册功能正在开发中，敬请期待！',
      type: 'info',
      duration: 3000
    });

    },
    handleForgetPassword() {
    ElMessage({
      message: '忘记密码正在开发中，敬请期待！',
      type: 'info',
      duration: 3000
    });
    },
    getOtherQuery(query:QueryType) {
      return Object.keys(query).reduce((acc:QueryType, cur) => {
        if (cur !== 'redirect') {
          acc[cur] = query[cur];
        }
        return acc;
      }, {});
    }
  }
});
</script>

<style lang="scss" scoped>
// 登录容器 - 页面整体布局
.login-container {
  display: flex;
  justify-content: center;     // 水平居中
  align-items: center;        // 垂直居中
  width: 100%;                // 占满整个视窗宽度
  min-height: 100vh;          // 最小高度为视窗高度
  background: linear-gradient(135deg, #cbecff 0%, #00f2fe 100%);  // 渐变背景色
  overflow: hidden;           // 隐藏溢出内容
}

// 注册相关文字 - 登录表单下方的注册提示区域
.register-container {
  display: flex;
  justify-content: center;    // 水平居中内容
  align-items: center;        // 垂直居中内容
  margin-top: 20px;           // 上边距20px
  font-size: 14px;            // 字体大小14px
  color: #666;                // 字体颜色灰色

  // 确保文本垂直居中对齐
  span {
    display: inline-flex;
    align-items: center;
  }

  // 文本按钮样式
  .el-button--text {
    padding: 0;               // 无内边距
    margin: 0 5px;            // 左右外边距5px
    font-size: 14px;          // 字体大小14px
    color: var(--el-color-primary);  // 主题色

    &:hover {
      color: var(--el-color-primary-light-3);  // 悬停时的颜色
    }
  }

  // 分割线样式
  .el-divider--vertical {
    margin: 0 2px;            // 左右外边距2px
  }
}

// 登录卡片 - 表单容器
.login-card {
  width: 520px;               // 固定宽度520px
  background-color: #ffffff;  // 白色背景
  border-radius: 16px;        // 圆角16px
  padding: 60px 50px 50px;    // 内边距：上60px，左右50px，下50px
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);  // 阴影效果
}

// 标题容器
.title-container {
  text-align: center;         // 文本居中
  margin-bottom: 40px;        // 下边距40px

  .title {
    font-size: 32px;          // 标题字体大小32px
    font-weight: 600;         // 字体粗细600
    color: #333;              // 深灰色字体
    margin: 0;                // 无外边距
  }

  .system-name {
    font-weight: normal;      // 正常字体粗细
    font-size: 20px;          // 副标题字体大小20px
    color: #555;              // 灰色字体
  }
}

// SVG图标容器
.svg-container {
  padding: 0 5px 0 10px;      // 内边距设置
  color: #889aa4;             // 图标颜色
  vertical-align: middle;     // 垂直居中
  display: inline-block;      // 行内块元素
}

// 显示密码图标
.show-pwd {
  font-size: 16px;            // 字体大小16px
  color: #889aa4;             // 图标颜色
  cursor: pointer;            // 鼠标指针样式
  user-select: none;          // 禁止文本选择
  // 使用flex布局让图标垂直居中
  display: flex;
  align-items: center;
  height: 100%;               // 占满父元素高度
  padding-right: 10px;        // 右内边距10px
}

// 使用 :deep() 修改 Element Plus 组件内部样式
:deep() {
  .login-form {
    .el-form-item {
      margin-bottom: 25px;      // 表单项下边距25px
    }

    .el-form-item__label {
      padding: 0;               // 无内边距
      line-height: 1.2px;         // 行高1.5倍
      padding-bottom: 8px;      // 下内边距8px
      color: #333;              // 深灰色字体
      font-weight: 500;         // 字体粗细500
      font-size: 18px;
    }

    .el-input__wrapper {
      height: 52px;             // 输入框高度52px
      border-radius: 20px;       // 圆角8px
      padding-left: 0;          // 无左内边距
      padding-right: 0;         // 无右内边距
      border: 1px solid #dcdfe6; // 边框样式
      box-shadow: none !important; // 无阴影
      transition: border-color 0.2s; // 边框颜色过渡动画

      &:hover {
        border-color: #c0c4cc;  // 悬停时边框颜色
      }

      &.is-focus {
        border-color: var(--el-color-primary);  // 聚焦时边框颜色
      }
    }

    // 登录按钮样式
    .el-button {
      margin-top: 5px;          // 上外边距5px
      height: 50px;             // 按钮高度50px
      border-radius: 40px;      // 大圆角40px
      font-size: 18px;          // 字体大小18px
      font-weight: 100;         // 极细字体
      letter-spacing: 3px;      // 字母间距3px
    }
  }
}

// 响应式设计 - 移动端适配
@media (max-width: 500px) {
  .login-card {
    width: 90%;                 // 宽度占90%
    padding: 40px 25px 30px;    // 调整内边距适应小屏幕
  }

  .title-container .title {
    font-size: 24px;            // 调小标题字体
  }

  .system-name {
    font-size: 16px;            // 调小副标题字体
  }
}
</style>
