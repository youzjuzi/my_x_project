<template>
  <div>
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="8">
        <div class="grid-content">
          <el-card class="box-card" shadow="hover">
            <div slot="header" class="clearfix">
              <span>个人中心</span>
            </div>
            <div class="avatar-container">
              <el-avatar size="100" :src="userForm.avatar || 'default-avatar.png'"/>
            </div>
            <div class="name-role">
              <span class="sender">{{ userForm.username }}</span>
            </div>
            <div class="personal-relation">
              <div class="relation-item">手机号: <div style="float: right; padding-right:20px;">{{ userForm.phone }}</div></div>
            </div>
            <div class="personal-relation">
              <div class="relation-item">邮箱: <div style="float: right; padding-right:20px;">{{ userForm.email }}</div></div>
            </div>
          </el-card>
        </div>
      </el-col>
      <el-col :span="16">
        <div class="grid-content">
          <el-card class="box-card" shadow="hover">
            <div slot="header" class="clearfix">
              <span>基本资料</span>
            </div>
            <div>
              <el-form :model="userForm" label-width="80px" size="small" label-position="right">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="userForm.username" :disabled="!isEditable" auto-complete="off" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="userForm.phone" :disabled="!isEditable" auto-complete="off" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="userForm.email" :disabled="!isEditable" auto-complete="off" />
                </el-form-item>
              </el-form>
              <div slot="footer" class="dialog-footer">
                <el-button size="mini" type="primary" :disabled="!isEditable" @click="updateUserInfo">提交</el-button>
                <el-button size="mini" type="warning" @click="toggleEdit">{{ isEditable ? '关闭' : '修改' }}</el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import userApi from '@/api/userManage'
import { mapState } from 'vuex'
export default {
  data() {
    return {
      userForm: {
        id: '',
        username: '',
        phone: '',
        email: '',
        address: ''
      },
      isEditable: false,
      originalUserForm: {}
    }
  },
  computed: {
    ...mapState('user', ['userId'])
  },
  created() {
    this.getUserInfo(this.userId)
  },
  methods: {
    getUserInfo(id) {
      if (id) {
        userApi.getUserById(id).then(response => {
          this.userForm = response.data
          this.originalUserForm = { ...response.data } // 保存原始数据
          console.log(this.userForm)
        }).catch(error => {
          console.error('获取用户信息失败:', error)
        })
      } else {
        console.error('用户 ID 不存在')
      }
    },
    updateUserInfo() {
      userApi.updateUser(this.userForm).then(response => {
        this.$message.success('用户信息更新成功')
        this.isEditable = false // 更新成功后禁用编辑
        this.originalUserForm = { ...this.userForm } // 更新成功后更新原始数据
      }).catch(() => {
        this.$message.error('用户信息更新失败')
      })
    },
    toggleEdit() {
      if (this.isEditable) {
        // 如果当前是编辑模式，点击关闭恢复原始数据
        this.userForm = { ...this.originalUserForm }
      }
      this.isEditable = !this.isEditable // 切换编辑状态
    }
  }
}
</script>

<style lang="scss" scoped>
.avatar-container {
  text-align: center;
  margin-bottom: 15px;
}

.name-role {
  font-size: 18px;
  padding: 5px;
  text-align:center;
  font-weight: bold;
}

.grid-content {
  border-radius: 10px;
  min-height: 36px;
  background: #f9f9f9;
}

.box-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.dialog-footer {
  padding-top: 10px;
  padding-left: 10%;
}

.el-col {
  border-radius: 4px;
}

.personal-relation {
  font-size: 14px;
  padding: 10px;
}

.relation-item {
  padding: 12px;
}

.bg-purple {
  background: #f4f7fc;
}
</style>
