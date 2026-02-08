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

    <!-- 列表式布局 -->
    <div class="security-list">
      <div class="security-item">
        <div class="item-content">
          <div class="item-label">
            <el-icon><Lock /></el-icon>
            <span>登录密码</span>
          </div>
          <div class="item-value">
            <span class="status-text">已设置</span>
            <el-button type="primary" size="small" @click="showPasswordDialog = true">修改</el-button>
          </div>
        </div>
      </div>

      <div class="security-item">
        <div class="item-content">
          <div class="item-label">
            <el-icon><Iphone /></el-icon>
            <span>手机绑定</span>
          </div>
          <div class="item-value">
            <span class="status-text">{{ formatPhone(userInfo.phone) || '未绑定' }}</span>
            <el-button type="primary" size="small" @click="handleBindPhone">
              {{ userInfo.phone ? '换绑' : '绑定' }}
            </el-button>
          </div>
        </div>
      </div>

      <div class="security-item">
        <div class="item-content">
          <div class="item-label">
            <el-icon><Message /></el-icon>
            <span>邮箱绑定</span>
          </div>
          <div class="item-value">
            <span class="status-text">{{ userInfo.email || '未绑定' }}</span>
            <el-button type="primary" size="small" @click="handleBindEmail">
              {{ userInfo.email ? '修改' : '绑定' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="500px"
      @close="resetPasswordForm">
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        ref="passwordFormRef"
        label-width="100px">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
            placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPasswordDialog = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 手机号绑定/修改弹窗 -->
    <el-dialog
      v-model="showPhoneDialog"
      :title="userInfo.phone ? '修改手机号' : '绑定手机号'"
      width="500px"
      @close="resetPhoneForm">
      <el-form
        :model="phoneForm"
        :rules="phoneRules"
        ref="phoneFormRef"
        label-width="100px">
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="phoneForm.phone"
            placeholder="请输入11位手机号"
            maxlength="11" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPhoneDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdatePhone">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 邮箱绑定/修改弹窗 -->
    <el-dialog
      v-model="showEmailDialog"
      :title="userInfo.email ? '修改邮箱' : '绑定邮箱'"
      width="500px"
      @close="resetEmailForm">
      <el-form
        :model="emailForm"
        :rules="emailRules"
        ref="emailFormRef"
        label-width="100px">
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="emailForm.email"
            placeholder="请输入邮箱地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEmailDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateEmail">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { ElMessage } from 'element-plus';
import { Lock, Iphone, Message } from '@element-plus/icons-vue';
import { changePassword, updatePhone, updateEmail } from '@/api/profile';
import store from '@/store';

export default defineComponent({
  name: 'SecuritySettings',
  components: {
    Lock,
    Iphone,
    Message
  },
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
      if (value === '') {
        callback(new Error('请再次输入新密码'));
      } else if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    };

    const validateNewPassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入新密码'));
      } else if (value.length < 6) {
        callback(new Error('密码长度至少6位'));
      } else if (value === this.passwordForm.oldPassword) {
        callback(new Error('新密码不能与旧密码相同'));
      } else {
        callback();
      }
    };

    const validatePhone = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入手机号'));
      } else if (!/^1[3-9]\d{9}$/.test(value)) {
        callback(new Error('请输入正确的11位手机号'));
      } else {
        callback();
      }
    };

    const validateEmail = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入邮箱地址'));
      } else if (!/^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(value)) {
        callback(new Error('请输入正确的邮箱地址'));
      } else {
        callback();
      }
    };

    return {
      showPasswordDialog: false,
      showPhoneDialog: false,
      showEmailDialog: false,
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      phoneForm: {
        phone: ''
      },
      emailForm: {
        email: ''
      },
      passwordRules: {
        oldPassword: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { validator: validateNewPassword, trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      phoneRules: {
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { validator: validatePhone, trigger: 'blur' }
        ]
      },
      emailRules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { validator: validateEmail, trigger: 'blur' }
        ]
      },
      userInfo: {
        phone: '',
        email: ''
      }
    };
  },
  methods: {
    async handleChangePassword() {
      this.$refs.passwordFormRef.validate(async (valid) => {
        if (valid) {
          try {
            // 调用API修改密码（token 会自动从请求头获取）
            await changePassword(
              this.passwordForm.oldPassword,
              this.passwordForm.newPassword
            );

            ElMessage.success('密码修改成功，请重新登录');
            this.showPasswordDialog = false;
            this.resetPasswordForm();
            
            // 延迟跳转到登录页，让用户看到成功提示
            setTimeout(() => {
              store.user().logout();
              this.$router.push('/login');
            }, 1500);
          } catch (error) {
            console.error('修改密码失败:', error);
            // 根据后端返回的错误信息显示提示
            const errorMessage = error.response?.data?.message || error.message || '修改密码失败，请稍后重试';
            ElMessage.error(errorMessage);
          }
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
      this.phoneForm.phone = this.userInfo.phone || '';
      this.showPhoneDialog = true;
    },
    async handleUpdatePhone() {
      this.$refs.phoneFormRef.validate(async (valid) => {
        if (valid) {
          try {
            await updatePhone(this.phoneForm.phone);
            ElMessage.success('手机号更新成功');
            this.showPhoneDialog = false;
            this.userInfo.phone = this.phoneForm.phone;
            // 通知父组件更新用户信息
            this.$emit('update', { phone: this.phoneForm.phone });
            this.resetPhoneForm();
          } catch (error) {
            console.error('更新手机号失败:', error);
            const errorMessage = error.response?.data?.message || error.message || '更新手机号失败，请稍后重试';
            ElMessage.error(errorMessage);
          }
        }
      });
    },
    resetPhoneForm() {
      this.phoneForm = {
        phone: ''
      };
      this.$refs.phoneFormRef?.resetFields();
    },
    handleBindEmail() {
      this.emailForm.email = this.userInfo.email || '';
      this.showEmailDialog = true;
    },
    async handleUpdateEmail() {
      this.$refs.emailFormRef.validate(async (valid) => {
        if (valid) {
          try {
            await updateEmail(this.emailForm.email);
            ElMessage.success('邮箱更新成功');
            this.showEmailDialog = false;
            this.userInfo.email = this.emailForm.email;
            // 通知父组件更新用户信息
            this.$emit('update', { email: this.emailForm.email });
            this.resetEmailForm();
          } catch (error) {
            console.error('更新邮箱失败:', error);
            const errorMessage = error.response?.data?.message || error.message || '更新邮箱失败，请稍后重试';
            ElMessage.error(errorMessage);
          }
        }
      });
    },
    resetEmailForm() {
      this.emailForm = {
        email: ''
      };
      this.$refs.emailFormRef?.resetFields();
    },
    formatPhone(phone) {
      if (!phone) return '';
      // 手机号脱敏：138****8888
      if (phone.length === 11) {
        return phone.substring(0, 3) + '****' + phone.substring(7);
      }
      return phone;
    }
  }
});
</script>

<style lang="scss" scoped>
.security-settings {
  padding: 20px;
}

.security-list {
  .security-item {
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    margin-bottom: 16px;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    }

    .item-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;

      .item-label {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        font-weight: 500;
        color: #303133;

        .el-icon {
          font-size: 18px;
          color: #409eff;
        }
      }

      .item-value {
        display: flex;
        align-items: center;
        gap: 15px;

        .status-text {
          color: #606266;
          font-size: 14px;
        }
      }
    }
  }
}
</style>
