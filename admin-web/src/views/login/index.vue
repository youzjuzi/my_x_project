<template>
  <div class="login-container">
    <el-form
      ref="loginForm"
      :model="loginForm"
      :rules="loginRules"
      class="login-form"
      auto-complete="on"
      label-position="left"
    >

      <div class="title-container">
        <h3 v-if="!showRegisterForm" class="title">虚拟手语交流平台</h3>
        <h3 v-if="showRegisterForm" class="title">注册</h3>
      </div>

      <div v-if="!showRegisterForm">
        <el-form-item prop="username">
          <span class="svg-container">
            <svg-icon icon-class="user" />
          </span>
          <el-input
            ref="username"
            v-model="loginForm.username"
            placeholder="登录名"
            name="username"
            type="text"
            tabindex="1"
            auto-complete="off"
          />
        </el-form-item>
        <el-form-item prop="password">
          <span class="svg-container">
            <svg-icon icon-class="password" />
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="loginForm.password"
            :type="passwordType"
            placeholder="密码"
            name="password"
            tabindex="2"
            auto-complete="on"
            @keyup.enter.native="handleLogin"
          />
          <span class="show-pwd" @click="showPwd">
            <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
          </span>
        </el-form-item>
        <el-form-item prop="captcha">
          <div style="display: flex; align-items: center;">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入验证码"
              name="captcha"
              type="text"
              tabindex="5"
              auto-complete="on"
              style="flex: 1"
            />
            <img
              @click="clickImg"
              :src="captchaUrl"
              style="width: 40%; height: 40px; cursor: pointer; margin-left: 15px;"
              alt="验证码"
            >
          </div>
        </el-form-item>
        <el-button
          :loading="loading"
          type="primary"
          style="width:48%;margin-bottom:30px;"
          @click.native.prevent="handleLogin"
        >登录</el-button>
        <el-button
          :loading="loading"
          type="primary"
          style="width:48%;margin-bottom:30px;"
          @click.native.prevent="handleRegistered"
        >注册</el-button>
      </div>
      <el-form
        v-if="showRegisterForm"
        ref="form"
        :model="form"
        :rules="registerRules"
        class="register-form"
        auto-complete="on"
        label-position="left"
      >
        <el-form-item prop="username">
          <span class="svg-container">
            <svg-icon icon-class="user" />
          </span>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            name="username"
            type="text"
            tabindex="1"
            auto-complete="on"
          />
        </el-form-item>
        <el-form-item prop="password">
          <span class="svg-container">
            <svg-icon icon-class="password" />
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="form.password"
            :type="passwordType"
            placeholder="密码"
            name="password"
            tabindex="2"
            auto-complete="on"
          />
          <span class="show-pwd" @click="showPwd">
            <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
          </span>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <span class="svg-container">
            <svg-icon icon-class="password" />
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="form.confirmPassword"
            :type="passwordType"
            placeholder="确认密码"
            name="confirmPassword"
            tabindex="3"
            auto-complete="on"
          />
          <span class="show-pwd" @click="showPwd">
            <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
          </span>
        </el-form-item>
        <el-form-item prop="phone">
          <span class="svg-container">
            <svg-icon icon-class="phone" />
          </span>
          <el-input v-model="form.phone" placeholder="手机号" name="phone" type="text" tabindex="4" auto-complete="on" />
        </el-form-item>
        <el-form-item prop="captcha">
          <div style="display: flex; align-items: center;">
            <el-input
              v-model="form.captcha"
              placeholder="请输入验证码"
              name="captcha"
              type="text"
              tabindex="5"
              auto-complete="on"
              style="flex: 1"
            />
            <img
              @click="clickImg"
              :src="captchaUrl"
              style="width: 40%; height: 40px; cursor: pointer; margin-left: 15px;"
              alt="验证码"
            >
          </div>
        </el-form-item>
        <el-button
          :loading="loading"
          type="primary"
          style="width:48%;margin-bottom:30px;"
          @click.native.prevent="register"
        >注册</el-button>
        <el-button
          :loading="loading"
          type="primary"
          style="width:48%;margin-bottom:30px;"
          @click.native.prevent="cancelRegister"
        >取消</el-button>
        <el-link class="login-link" @click="showRegisterForm = false">已有账号？点击登录</el-link>
      </el-form>
    </el-form>
  </div>
</template>

<script>

export default {
  name: 'Login',
  data() {
    // 用户名验证
    const validateUsername = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入正确的用户名'))
      } else {
        callback()
      }
    }
    // 密码验证
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码至少6位'))
      } else {
        callback()
      }
    }
    // 二次密码验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.form.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    // 手机号验证
    const validatePhone = (rule, value, callback) => {
      if (!value) {
        return callback(new Error('请输入手机号'))
      }
      const reg = /^1[3|4|5|7|8][0-9]\d{8}$/
      if (reg.test(value)) {
        callback()
      } else {
        return callback(new Error('请输入正确的手机号'))
      }
    }

    const key = Math.floor(Math.random() * 9000) + 1000
    // 单独处理验证码
    const captchaBaseUrl = process.env.VUE_APP_BASE_API
    return {
      captchaBaseUrl: captchaBaseUrl,
      key: key,
      // 验证码地址
      captchaUrl: captchaBaseUrl + '/captcha?key=' + key,
      /* 注册表单*/
      showRegisterForm: false,
      dialogFormVisible: false,
      // 登录表单
      loginForm: {
        username: '',
        password: '',
        captcha: null,
        codeKey: key
      },
      // 登录表单验证规则
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      // 注册表单验证规则
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 12, message: '长度在 3 到 12 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 16, message: '长度在 6 到 16 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, trigger: 'blur', validator: validateConfirmPassword }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { validator: validatePhone, trigger: 'blur' }
        ]
      },
      // 登录表单加载状态
      loading: false,
      // 密码类型
      passwordType: 'password',
      // 重定向地址
      redirect: undefined,
      // 注册表单
      form: {
        username: '',
        password: '',
        confirmPassword: '',
        phone: '',
        captcha: null,
        codeKey: key
      }
    }
  },
  // 监听路由变化
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  // 事件处理
  methods: {
    // 显示注册表单
    handleRegistered() {
      this.showRegisterForm = true
    },
    // 取消注册
    cancelRegister() {
      this.showRegisterForm = false
      // eslint-disable-next-line no-sequences
      this.form.username = '',
      this.form.password = '',
      this.form.confirmPassword = '',
      this.form.phone = '',
      this.form.captcha = ''
      this.$refs.loginForm.resetFields()
      this.$refs.form.resetFields()
    },
    // 显示密码
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    // 验证码刷新
    clickImg() {
      this.loginForm.captcha = ''
      this.key = Math.floor(Math.random() * 9000) + 1000
      this.loginForm.codeKey = this.key
      this.captchaUrl = this.captchaBaseUrl + '/captcha?key=' + this.key
    },
    // 登录
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          this.$store.dispatch('user/login', this.loginForm)
            .then(() => {
              // return this.$store.dispatch('user/getInfo') // 获取用户信息
            })
            .then(() => {
              this.$router.push({ path: this.redirect || '/' })
              this.loading = false
              this.$message.success('登录成功')
            })
            .catch(() => {
              this.loading = false
              this.loginForm.captcha = ''
              this.key = Math.floor(Math.random() * 9000) + 1000
              this.loginForm.codeKey = this.key
              this.captchaUrl = this.captchaBaseUrl + '/captcha?key=' + this.key
            })
        } else {
          console.log('error submit!!')
        }
      })
    },
    // 注册
    register() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.loading = true
          // console.log('开始注册') // 添加这一行
          this.$store.dispatch('user/register', this.form).then(() => {
            // console.log('注册成功') // 添加这一行
            this.$router.push({ path: this.redirect || '/' })
            this.loading = false
            this.showRegisterForm = false // 注册成功后自动登录
            this.resetFormAndCaptcha()
            this.$message.success('注册成功')
          }).catch(() => {
            this.loading = false
            this.loading = false
            this.form.captcha = ''
            this.key = Math.floor(Math.random() * 9000) + 1000
            this.form.codeKey = this.key
            this.captchaUrl = this.captchaBaseUrl + '/captcha?key=' + this.key
          })
        } else {
          console.log('error submit!!')
          this.$message.error('请输入您的信息')
          return false
        }
      })
    },
    // 注册成功，重置表单和验证码
    resetFormAndCaptcha() {
      // 重置表单
      this.form = {
        username: '',
        password: '',
        captcha: ''
      }
      // 刷新验证码
      this.clickImg()
    }
  }
}
</script>

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

.register-form {
  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }

}

// 修复element-ui样式
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $cursor;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.login-link {
  color: white;
  font-size: 20px;
  border: none;
  background: none;
  cursor: pointer;
  text-decoration: underline;

  &:hover {
    color: #409EFF;
  }

  /*往上移动一点*/
  margin-top: -10px;
  /*再居中*/
  margin-left: 120px;
}

.login-container {
  min-height: 100%;
  width: 100%;
  background-color: $bg;
  overflow: hidden;

  background: url('~@/assets/screen.jpg') repeat-x;
  background-size: 100%;

  display: flex;
  align-items: center;

  .login-form {
    position: relative;
    width: 520px;
    max-width: 100%;
    padding: 35px 50px 10px;
    margin: 0 auto;
    overflow: hidden;
    //添加登录模块的背景颜色
    background-color: #3d678d;
    //圆角的设置
    border-radius: 8px;
    //添加透明度
    opacity: 0.95;

  }

  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;

    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 35px;
      color: #ffffff;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }
}
</style>
