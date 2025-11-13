<template>
  <div class="user-page">
    <el-card class="search-card" shadow="hover">
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="用户名">
            <el-input
              v-model="searchForm.username"
              placeholder="输入用户名"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input
              v-model="searchForm.email"
              placeholder="输入邮箱"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="电话">
            <el-input
              v-model="searchForm.phone"
              placeholder="输入电话"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">
              查询
            </el-button>
            <el-button :icon="RefreshRight" @click="handleReset">
              重置
            </el-button>
          </el-form-item>
        </el-form>
        <div class="actions">
          <el-button type="primary" :icon="Plus" @click="openCreateDialog">
            新增用户
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="hover">
      <div class="table-toolbar">
        <div>
          <div class="table-title">用户列表</div>
          <div class="table-subtitle">
            共 {{ serverTotal }} 位用户，当前页显示 {{ pagedTableData.length }} 位
          </div>
        </div>
        <el-space>
          <el-button text :icon="RefreshRight" @click="handleRefresh">刷新</el-button>
        </el-space>
      </div>

      <el-table :data="pagedTableData" v-loading="loading" border>
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="username" label="用户名" min-width="140">
          <template #default="{ row }">
            <div class="username-cell">
              <el-avatar :size="32" :src="row.avatar" class="avatar" />
              <div class="username-info">
                <span class="username">{{ row.username }}</span>
                <span class="desc">{{ row.nickname }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.email || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" min-width="140">
          <template #default="{ row }">
            {{ row.phone || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="roleTitles" label="角色" min-width="180">
          <template #default="{ row }">
            <template v-if="row.roleTitles.length">
              <el-tag
                v-for="role in row.roleTitles"
                :key="role"
                type="info"
                class="role-tag"
              >
                {{ role }}
              </el-tag>
            </template>
            <span v-else class="text-muted">未分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status].type">
              {{ statusMap[row.status].text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip content="查看" effect="dark" placement="top">
                <el-button
                  circle
                  class="action-icon"
                  type="primary"
                  :icon="View"
                  @click="handleView(row)"
                />
              </el-tooltip>
              <el-tooltip :content="row.id === 1 ? '超级管理员不可修改' : '编辑'" effect="dark" placement="top">
                <el-button
                  circle
                  class="action-icon"
                  type="warning"
                  :icon="Edit"
                  :disabled="row.id === 1"
                  @click="handleEdit(row)"
                />
              </el-tooltip>
              <template v-if="row.id === 1">
                <el-button
                  circle
                  class="action-icon danger"
                  type="danger"
                  :icon="Delete"
                  @click="notifyAdminDelete()"
                />
              </template>
              <el-popconfirm
                v-else
                title="确认要删除该用户吗？"
                :confirm-button-text="'删除'"
                :cancel-button-text="'取消'"
                :teleported="false"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <el-button
                    circle
                    class="action-icon danger"
                    type="danger"
                    :loading="deleteLoadingId === row.id"
                    :icon="Delete"
                  />
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="serverTotal"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>

  <el-dialog
    v-model="createDialogVisible"
    title="新增用户"
    width="520px"
    destroy-on-close
    @closed="resetCreateForm"
  >
    <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="createForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="createForm.password"
          placeholder="请输入登录密码"
          type="password"
          show-password
        />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="createForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="createForm.phone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch
          v-model="createForm.status"
          active-text="启用"
          inactive-text="停用"
        />
      </el-form-item>
      <el-form-item label="分配角色">
        <el-select
          v-model="createForm.roleIds"
          multiple
          filterable
          placeholder="请选择角色"
          class="full-width"
        >
          <el-option
            v-for="role in roleOptions"
            :key="role.roleId"
            :label="role.roleDesc || role.roleName"
            :value="role.roleId"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createSubmitting" @click="handleCreateSubmit">提交</el-button>
      </span>
    </template>
  </el-dialog>

  <el-dialog
    v-model="editDialogVisible"
    title="修改用户"
    width="520px"
    destroy-on-close
    @closed="resetEditForm"
  >
    <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="90px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="editForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input
          v-model="editForm.password"
          placeholder="如需修改密码请输入新密码"
          type="password"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="editForm.confirmPassword"
          placeholder="请再次输入新密码"
          type="password"
          show-password
        />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="editForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="电话" prop="phone">
        <el-input v-model="editForm.phone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch
          v-model="editForm.status"
          active-text="启用"
          inactive-text="停用"
        />
      </el-form-item>
      <el-form-item label="分配角色">
        <el-select
          v-model="editForm.roleIds"
          multiple
          filterable
          placeholder="请选择角色"
          class="full-width"
        >
          <el-option
            v-for="role in roleOptions"
            :key="role.roleId"
            :label="role.roleDesc || role.roleName"
            :value="role.roleId"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="handleEditSubmit">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>

  <el-dialog
    v-model="viewDialogVisible"
    title="用户详情"
    width="520px"
    destroy-on-close
    v-loading="viewLoading"
  >
    <el-skeleton v-if="viewLoading" rows="6" animated />
    <el-descriptions
      v-else-if="viewDetail"
      :column="1"
      border
      label-width="90px"
      class="detail-descriptions"
    >
      <el-descriptions-item label="用户名">{{ viewDetail.username }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">
        {{ viewDetail.email || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="电话">
        {{ viewDetail.phone || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="头像">
        <el-avatar v-if="viewDetail.avatar" :src="viewDetail.avatar" size="large" />
        <span v-else>—</span>
      </el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="viewDetail.statusNumber === 1 ? 'success' : 'danger'">
          {{ viewDetail.statusNumber === 1 ? '启用' : '停用' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="角色">
        <template v-if="viewDetail.roleTitles?.length">
          <el-tag
            v-for="role in viewDetail.roleTitles"
            :key="role"
            type="info"
            class="role-tag"
          >
            {{ role }}
          </el-tag>
        </template>
        <span v-else>未分配</span>
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">
        {{ viewDetail.createdAt || '—' }}
      </el-descriptions-item>
    </el-descriptions>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { Edit, Delete, Plus, RefreshRight, Search, View } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { computed, reactive, ref, onMounted } from 'vue'
import userManageApi from '@/api/userManage'
import roleManageApi from '@/api/roleManage'

// 用户信息接口返回的数据结构
interface RawUserItem {
  id: number
  username: string
  email: string | null
  phone: string | null
  status: number
  avatar: string | null
  roleIdList: Array<number> | null
  password?: string
  deleted?: number
  [key: string]: unknown
}

// 用户信息
interface User {
  id: number
  username: string
  nickname: string
  email: string
  phone: string
  status: 'enabled' | 'disabled'
  statusNumber: number
  roleTitles: string[]
  roleIds: number[]
  createdAt: string
  avatar?: string
}

// 角色信息
interface RoleItem {
  roleId: number
  roleName: string
  roleDesc?: string
}

const loading = ref(false)
const tableData = ref<User[]>([])
const serverTotal = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索表单：支持用户名 / 邮箱 / 电话 任意组合
const searchForm = reactive({
  username: '',
  email: '',
  phone: '',
})

// 后端状态 -> 前端状态映射
const statusMap = {
  enabled: { text: '启用', type: 'success' as const },
  disabled: { text: '停用', type: 'danger' as const },
}

// 角色字典：用于根据 roleId 映射到角色名称
const roleDict = ref<Record<number, RoleItem>>({})

const roleOptions = computed(() => Object.values(roleDict.value))

// 新增用户弹窗状态 & 表单
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createFormDefault = {
  username: '',
  password: '',
  email: '',
  phone: '',
  status: true,
  roleIds: [] as number[],
  avatar: '',
}
const createForm = reactive({ ...createFormDefault })
// 用户名唯一性校验（后端 message: '0' 表示存在，'1' 表示可用）
const validateUsernameUnique = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  const username = value?.trim()
  if (!username) {
    callback(new Error('请输入用户名'))
    return
  }
  userManageApi.checkUsername(username)
    .then((res) => {
      const { message } = (res as { message?: string })
      if (message === '0') {
        callback(new Error('用户名已存在'))
      } else {
        callback()
      }
    })
    .catch(error => {
      console.error('校验用户名失败', error)
      callback(new Error('校验失败，请稍后重试'))
    })
}
const createRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUsernameUnique, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ]
}
const createSubmitting = ref(false)

// 编辑用户弹窗状态 & 表单
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editFormDefault = {
  id: 0,
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: '',
  status: true,
  roleIds: [] as number[],
  avatar: '',
}
const editForm = reactive({ ...editFormDefault })
const editOriginalUsername = ref('')
const emailPattern = /^[\w.+-]+@[\w-]+(\.[\w-]+)+$/
const phonePattern = /^\d{5,20}$/

const validateUsernameForEdit = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  const username = value?.trim()
  if (!username) {
    callback(new Error('请输入用户名'))
    return
  }
  if (username === editOriginalUsername.value) {
    callback()
    return
  }
  userManageApi.checkUsername(username)
    .then((res) => {
      const { message } = (res as { message?: string })
      if (message === '0') {
        callback(new Error('用户名已存在'))
      } else {
        callback()
      }
    })
    .catch(error => {
      console.error('校验用户名失败', error)
      callback(new Error('校验失败，请稍后重试'))
    })
}
const validateEditPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value && value.length < 6) {
    callback(new Error('密码至少 6 位'))
    return
  }
  callback()
}
const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (editForm.password && !value) {
    callback(new Error('请再次输入新密码'))
    return
  }
  if (value && value !== editForm.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}
const validateOptionalEmail = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value && !emailPattern.test(value)) {
    callback(new Error('邮箱格式不正确'))
    return
  }
  callback()
}
const validateOptionalPhone = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value && !phonePattern.test(value)) {
    callback(new Error('电话格式不正确'))
    return
  }
  callback()
}
const editRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUsernameForEdit, trigger: 'blur' }
  ],
  password: [{ validator: validateEditPassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  email: [{ validator: validateOptionalEmail, trigger: 'blur' }],
  phone: [{ validator: validateOptionalPhone, trigger: 'blur' }]
}
const editSubmitting = ref(false)

const viewDialogVisible = ref(false)
const viewDetail = ref<User & { raw?: RawUserItem } | null>(null)
const viewLoading = ref(false)

// 后端已实现分页+筛选，因此直接使用接口返回的数据
const pagedTableData = computed(() => tableData.value)

const loadRoleDict = async () => {
  try {
    const res = await roleManageApi.getAllRoleList()
    const list: RoleItem[] = res.data || []
    roleDict.value = list.reduce((acc, role) => {
      acc[role.roleId] = role
      return acc
    }, {} as Record<number, RoleItem>)
  } catch (error) {
    console.error('获取角色列表失败', error)
    ElMessage.warning('角色信息获取失败，显示的角色名称可能不完整')
  }
}

// 映射用户记录
const mapUserRecord = (record: RawUserItem): User => {
  const statusNumber = Number(record.status ?? 0)
  const status = statusNumber === 1 ? 'enabled' : 'disabled'
  const roleIds = Array.isArray(record.roleIdList) ? record.roleIdList : []
  const roleNames = roleIds
    .map((roleId) => roleDict.value[roleId]?.roleDesc || roleDict.value[roleId]?.roleName)
    .filter(Boolean) as string[]

  return {
    id: record.id,
    username: record.username || '',
    nickname: record.username || '',
    email: record.email || '',
    phone: record.phone || '',
    status,
    statusNumber,
    roleTitles: roleNames,
    roleIds,
    createdAt: (record as Record<string, string>).createTime || '',
    avatar: record.avatar || 'https://avatars.githubusercontent.com/u/9919?s=200&v=4',
  }
}

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true
  try {
    // 调用后端分页接口，传入分页信息 + 搜索条件
    const res = await userManageApi.getUserList({
      pageNo: currentPage.value,
      pageSize: pageSize.value,
      username: searchForm.username.trim(),
      email: searchForm.email.trim(),
      phone: searchForm.phone.trim(),
    })
    const data = res.data || { total: 0, row: [] }
    tableData.value = Array.isArray(data.row) ? data.row.map(mapUserRecord) : []
    serverTotal.value = Number(data.total) || 0
  } catch (error) {
    console.error('获取用户列表失败', error)
    ElMessage.error('获取用户列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchUserList()
}

// 重置
const handleReset = () => {
  searchForm.username = ''
  searchForm.email = ''
  searchForm.phone = ''
  currentPage.value = 1
  fetchUserList()
}

// 新增用户（打开弹窗）
const openCreateDialog = () => {
  createDialogVisible.value = true
}

// 新增用户提交（当前仅模拟提示）
const handleCreateSubmit = () => {
  if (!createFormRef.value) return
  createFormRef.value.validate((valid) => {
    if (valid) {
      createSubmitting.value = true
      // 调用后端新增接口
      userManageApi.addUser({
        id: 0,
        username: createForm.username.trim(),
        password: createForm.password,
        email: createForm.email || '',
        phone: createForm.phone || '',
        status: createForm.status ? 1 : 0,
        avatar: createForm.avatar || '',
        deleted: 0,
        roleIdList: createForm.roleIds
      }).then(() => {
        ElMessage.success('新增用户成功')
        createDialogVisible.value = false
        fetchUserList()
      }).catch((error) => {
        console.error('新增用户失败', error)
        ElMessage.error('新增用户失败，请稍后重试')
      }).finally(() => {
        createSubmitting.value = false
      })
    }
  })
}

// 重置新增弹窗表单
const resetCreateForm = () => {
  Object.assign(createForm, { ...createFormDefault, roleIds: [] })
  createFormRef.value?.clearValidate()
}

// 编辑用户（打开弹窗）
const handleEdit = (row: User) => {
  if (row.id === 1) {
    ElMessage.warning('超级管理员不可修改')
    return
  }
  Object.assign(editForm, { ...editFormDefault, roleIds: [] })
  editOriginalUsername.value = row.username
  Object.assign(editForm, {
    id: row.id,
    username: row.username,
    password: '',
    confirmPassword: '',
    email: row.email,
    phone: row.phone,
    status: row.status === 'enabled',
    roleIds: [...row.roleIds],
    avatar: row.avatar || '',
  })
  editFormRef.value?.clearValidate()
  editDialogVisible.value = true
}
// 编辑用户提交
const handleEditSubmit = () => {
  if (!editFormRef.value) return
  editFormRef.value.validate((valid) => {
    if (!valid) return
    editSubmitting.value = true
    const payload: Record<string, unknown> = {
      id: editForm.id,
      username: editForm.username.trim(),
      email: editForm.email?.trim() || '',
      phone: editForm.phone?.trim() || '',
      status: editForm.status ? 1 : 0,
      avatar: editForm.avatar || '',
      roleIdList: editForm.roleIds
    }
    if (editForm.password) {
      payload['password'] = editForm.password
    }

    userManageApi.updateUser(payload)
      .then(() => {
        ElMessage.success('修改用户成功')
        editDialogVisible.value = false
        fetchUserList()
      })
      .catch(error => {
        console.error('修改用户失败', error)
        ElMessage.error('修改用户失败，请稍后重试')
      })
      .finally(() => {
        editSubmitting.value = false
      })
  })
}

const deleteLoadingId = ref<number | null>(null)
const notifyAdminDelete = () => {
  ElMessage.warning('超级管理员不可删除')
}

// 删除用户
const handleDelete = (row: User) => {
  if (row.id === 1) {
    ElMessage.warning('超级管理员不可删除')
    return
  }
  console.log('删除用户确认', row)
  deleteLoadingId.value = row.id
  userManageApi.deleteUser(row.id)
    .then(() => {
      ElMessage.success('删除用户成功')
      fetchUserList()
    })
    .catch(error => {
      console.error('删除用户失败', error)
      ElMessage.error('删除用户失败，请稍后重试')
    })
    .finally(() => {
      deleteLoadingId.value = null
    })
}

// 刷新
const handleRefresh = () => {
  fetchUserList()
}

// 分页大小改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchUserList()
}

// 当前页改变
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchUserList()
}

// 挂载
onMounted(async () => {
  await loadRoleDict()
  fetchUserList()
})
// 
const resetEditForm = () => {
  Object.assign(editForm, { ...editFormDefault, roleIds: [] })
  editOriginalUsername.value = ''
  editFormRef.value?.clearValidate()
}

const handleView = async (row: User) => {
  viewDialogVisible.value = true
  viewLoading.value = true
  try {
    const res = await userManageApi.getUserById(row.id)
    const detail = res.data as RawUserItem
    const mapped = mapUserRecord(detail)
    viewDetail.value = {
      ...mapped,
      raw: detail
    }
  } catch (error) {
    console.error('获取用户详情失败', error)
    ElMessage.error('获取用户详情失败，请稍后重试')
    viewDialogVisible.value = false
  } finally {
    viewLoading.value = false
  }
}
</script>

<style scoped>
.user-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: var(--el-bg-color-page);
  min-height: 100%;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.search-form {
  flex: 1;
  min-width: 280px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-card {
  flex: 1;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
}

.table-subtitle {
  color: var(--el-text-color-secondary);
  margin-top: 4px;
  font-size: 13px;
}

.username-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  border-radius: 50%;
}

.username-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.action-icon {
  width: 42px;
  height: 42px;
  font-size: 18px;
}

.action-icon:deep(.el-icon) {
  font-size: 20px;
}

.role-tag {
  margin-right: 6px;
  margin-bottom: 4px;
}

.text-muted {
  color: var(--el-text-color-secondary);
}

.full-width {
  width: 100%;
}

.detail-descriptions {
  margin-bottom: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}
</style>

