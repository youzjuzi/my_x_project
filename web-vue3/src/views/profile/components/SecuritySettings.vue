<template>
  <div class="security-settings">
    <el-alert
      title="安全提示"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 20px;">
      <template #default>
        <p>为了您的账户安全，建议定期更换密码，并绑定手机号和邮箱。</p>
      </template>
    </el-alert>

    <el-divider content-position="left">密码管理</el-divider>
    <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px" style="max-width: 500px;">
      <el-form-item label="当前密码" prop="oldPassword">
        <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
        <el-button @click="resetPasswordForm">重置</el-button>
      </el-form-item>
    </el-form>

    <el-divider content-position="left">账户绑定</el-divider>
    <el-descriptions :column="1" border style="max-width: 500px;">
      <el-descriptions-item label="手机号">
        <span>{{ userInfo.phone || '未绑定' }}</span>
        <el-button type="text" size="small" style="margin-left: 10px;" @click="handleBindPhone">
          {{ userInfo.phone ? '修改' : '绑定' }}
        </el-button>
      </el-descriptions-item>
      <el-descriptions-item label="邮箱">
        <span>{{ userInfo.email || '未绑定' }}</span>
        <el-button type="text" size="small" style="margin-left: 10px;" @click="handleBindEmail">
          {{ userInfo.email ? '修改' : '绑定' }}
        </el-button>
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { ElMessage } from 'element-plus';

export default defineComponent({
  name: 'SecuritySettings',
  props: {
    user: {
      type: Object,
      default: () => ({
        email: '',
        phone: ''
      })
    }
  },
  emits: ['update'],
  watch: {
    user: {
      handler(newVal) {
        if (newVal) {
          this.userInfo = {
            email: newVal.email || '',
            phone: newVal.phone || ''
          };
        }
      },
      immediate: true,
      deep: true
    }
  },
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    };

    return {
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      passwordRules: {
        oldPassword: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      userInfo: {
        phone: '',
        email: ''
      }
    };
  },
  methods: {
    handleChangePassword() {
      this.$refs.passwordFormRef.validate((valid) => {
        if (valid) {
          // TODO: 后续调用API修改密码
          ElMessage.success('密码修改功能开发中...');
          this.resetPasswordForm();
        }
      });
    },
    resetPasswordForm() {
      this.passwordForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      this.$refs.passwordFormRef?.resetFields();
    },
    handleBindPhone() {
      // TODO: 后续实现手机号绑定/修改功能
      ElMessage.info('手机号绑定/修改功能开发中...');
    },
    handleBindEmail() {
      // TODO: 后续实现邮箱绑定/修改功能
      ElMessage.info('邮箱绑定/修改功能开发中...');
    }
  }
});
</script>

<style lang="scss" scoped>
.security-settings {
  padding: 20px;
}
</style>

