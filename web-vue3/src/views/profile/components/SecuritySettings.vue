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
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { ElMessage } from 'element-plus';
import { Lock, Iphone, Message } from '@element-plus/icons-vue';

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
      if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    };

    return {
      showPasswordDialog: false,
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
          ElMessage.success('密码修改成功');
          this.showPasswordDialog = false;
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
