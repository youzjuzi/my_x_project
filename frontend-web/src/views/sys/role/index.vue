<template>
  <div class="role-page">
    <el-card class="search-card" shadow="hover">
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="角色名称">
            <el-input
              v-model="searchForm.roleName"
              placeholder="输入角色名称"
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
            新增角色
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="hover">
      <div class="table-toolbar">
        <div class="table-title">角色列表</div>
        <div class="table-subtitle">共 {{ total }} 个角色</div>
      </div>
      <el-table :data="tableData" v-loading="loading" border>
        <el-table-column type="index" width="70" align="center" label="#" />
        <el-table-column prop="roleId" label="角色ID" width="120" align="center" />
        <el-table-column prop="roleName" label="角色名称" min-width="160" />
        <el-table-column prop="roleDesc" label="角色描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.roleDesc || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="center">
          <template #default="{ row }">
            <div class="action-links">
              <span class="action-link view-link" @click="handleViewMenus(row)">查看菜单</span>
              <el-divider direction="vertical" />
              <span 
                class="action-link edit-link" 
                @click="handleEdit(row)"
              >
                编辑
              </span>
              <el-divider direction="vertical" />
              <el-popconfirm
                title="确认要删除该角色吗？"
                :confirm-button-text="'删除'"
                :cancel-button-text="'取消'"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <span 
                    class="action-link delete-link"
                    :class="{ 'is-loading': deleteLoadingId === row.roleId }"
                    @click="handleDelete(row)"
                  >
                    {{ deleteLoadingId === row.roleId ? '删除中...' : '删除' }}
                  </span>
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
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="createDialogVisible"
      title="新增角色"
      width="520px"
      destroy-on-close
      @closed="resetCreateForm"
    >
      <el-form label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="createForm.roleName" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input
            v-model="createForm.roleDesc"
            placeholder="请输入角色描述"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="菜单权限">
          <div class="menu-tree-wrapper">
            <el-tree
              ref="createMenuTreeRef"
              :data="menuTree"
              node-key="value"
              show-checkbox
              default-expand-all
              :loading="menuLoading"
              check-on-click-node
              :props="treeProps"
              :default-checked-keys="createForm.menuIdList"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="createSubmitting" @click="handleCreateSubmit">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看角色菜单对话框 -->
    <el-dialog
      v-model="viewMenusDialogVisible"
      title="角色菜单权限"
      width="600px"
      destroy-on-close
    >
      <div v-if="viewMenusRole">
        <div class="role-info">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="角色ID">{{ viewMenusRole.roleId }}</el-descriptions-item>
            <el-descriptions-item label="角色名称">{{ viewMenusRole.roleName }}</el-descriptions-item>
            <el-descriptions-item label="角色描述">
              {{ viewMenusRole.roleDesc || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="菜单数量">
              <el-tag type="info">{{ viewMenusRole.menuIdList?.length || 0 }} 个菜单</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="menu-tree-section">
          <div class="section-title">可访问的菜单列表</div>
          <div class="menu-tree-wrapper view-only">
            <el-tree
              ref="viewMenuTreeRef"
              :data="menuTree"
              node-key="value"
              :loading="menuLoading"
              :props="treeProps"
              :default-checked-keys="viewMenusRole.menuIdList || []"
              show-checkbox
              default-expand-all
              :check-strictly="true"
              :disabled="true"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="viewMenusDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="editDialogVisible"
      title="编辑角色"
      width="520px"
      destroy-on-close
      @closed="resetEditForm"
    >
      <el-form label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="editForm.roleName" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input
            v-model="editForm.roleDesc"
            placeholder="请输入角色描述"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="菜单权限">
          <div class="menu-tree-wrapper">
            <el-tree
              ref="editMenuTreeRef"
              :data="menuTree"
              node-key="value"
              show-checkbox
              default-expand-all
              :loading="menuLoading"
              check-on-click-node
              :props="treeProps"
            />
          </div>
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
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'roleList' // ⚠️ 必须与路由 name 完全一致！
})

import { RefreshRight, Search, Edit, Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { reactive, ref, onMounted, nextTick } from 'vue'
import roleManageApi from '@/api/roleManage'
import menuManageApi from '@/api/menuManage'

interface RoleItem {
  roleId: number
  roleName: string
  roleDesc: string | null
  menuIdList: number[] | null
}

interface MenuTreeNode {
  label: string
  value: number
  children?: MenuTreeNode[]
}

const loading = ref(false)
const tableData = ref<RoleItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchForm = reactive({
  roleName: ''
})

const treeProps = {
  label: 'label',
  children: 'children'
}

const menuTree = ref<MenuTreeNode[]>([])
const menuLoading = ref(false)
const createMenuTreeRef = ref()
const editMenuTreeRef = ref()

const createDialogVisible = ref(false)
const createSubmitting = ref(false)
const createForm = reactive({
  roleName: '',
  roleDesc: '',
  menuIdList: [] as number[]
})

const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editForm = reactive({
  roleId: 0,
  roleName: '',
  roleDesc: '',
  menuIdList: [] as number[]
})

const deleteLoadingId = ref<number | null>(null)

// 查看角色菜单
const viewMenusDialogVisible = ref(false)
const viewMenusRole = ref<RoleItem | null>(null)
const viewMenuTreeRef = ref()

const fetchRoleList = async () => {
  loading.value = true
  try {
    const res = await roleManageApi.getRoleList({
      pageNo: currentPage.value,
      pageSize: pageSize.value,
      roleName: searchForm.roleName.trim() || undefined
    })
    const data = res.data || { total: 0, rows: [] }
    tableData.value = Array.isArray(data.rows) ? data.rows : []
    total.value = Number(data.total) || 0
  } catch (error) {
    console.error('获取角色列表失败', error)
    ElMessage.error('获取角色列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const loadMenuTree = async () => {
  if (menuTree.value.length) return
  menuLoading.value = true
  try {
    const res = await menuManageApi.getAllMenus()
    menuTree.value = transformMenuToTree(res.data || [])
  } catch (error) {
    console.error('获取菜单列表失败', error)
    ElMessage.error('获取菜单列表失败，请稍后重试')
  } finally {
    menuLoading.value = false
  }
}

const transformMenuToTree = (list: any[]): MenuTreeNode[] => {
  return list.map(item => ({
    label: item.title,
    value: item.menuId,
    children: item.children ? transformMenuToTree(item.children) : undefined
  }))
}

const handleSearch = () => {
  currentPage.value = 1
  fetchRoleList()
}

const handleReset = () => {
  searchForm.roleName = ''
  currentPage.value = 1
  fetchRoleList()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchRoleList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchRoleList()
}

const openCreateDialog = async () => {
  await loadMenuTree()
  createDialogVisible.value = true
  nextTick(() => {
    createForm.menuIdList = []
    createMenuTreeRef.value?.setCheckedKeys([])
  })
}

const resetCreateForm = () => {
  createForm.roleName = ''
  createForm.roleDesc = ''
  createForm.menuIdList = []
  createMenuTreeRef.value?.setCheckedKeys([])
}

const handleCreateSubmit = async () => {
  if (!createForm.roleName.trim()) {
    ElMessage.warning('请输入角色名称')
    return
  }
  const checkedKeys = (createMenuTreeRef.value?.getCheckedKeys() || []) as number[]
  createForm.menuIdList = checkedKeys
  if (!createForm.menuIdList.length) {
    ElMessage.warning('请选择菜单权限')
    return
  }
  createSubmitting.value = true
  try {
    await roleManageApi.addRole({
      roleName: createForm.roleName.trim(),
      roleDesc: createForm.roleDesc.trim(),
      menuIdList: createForm.menuIdList
    })
    ElMessage.success('新增角色成功')
    createDialogVisible.value = false
    resetCreateForm()
    fetchRoleList()
  } catch (error) {
    console.error('新增角色失败', error)
    ElMessage.error('新增角色失败，请稍后重试')
  } finally {
    createSubmitting.value = false
  }
}

const handleEdit = async (row: RoleItem) => {
  await loadMenuTree()
  try {
    const res = await roleManageApi.getRoleById(row.roleId)
    const data = res.data || {}
    editForm.roleId = data.roleId
    editForm.roleName = data.roleName
    editForm.roleDesc = data.roleDesc || ''
    editForm.menuIdList = Array.isArray(data.menuIdList) ? data.menuIdList : []
    editDialogVisible.value = true
    nextTick(() => {
      editMenuTreeRef.value?.setCheckedKeys(editForm.menuIdList, true)
    })
  } catch (error) {
    console.error('获取角色详情失败', error)
    ElMessage.error('获取角色详情失败，请稍后重试')
  }
}

const resetEditForm = () => {
  editForm.roleId = 0
  editForm.roleName = ''
  editForm.roleDesc = ''
  editForm.menuIdList = []
  editMenuTreeRef.value?.setCheckedKeys([])
}

const handleEditSubmit = async () => {
  if (!editForm.roleName.trim()) {
    ElMessage.warning('请输入角色名称')
    return
  }
  const checkedKeys = (editMenuTreeRef.value?.getCheckedKeys() || []) as number[]
  if (!checkedKeys.length) {
    ElMessage.warning('请选择菜单权限')
    return
  }
  editSubmitting.value = true
  try {
    await roleManageApi.updateRole({
      roleId: editForm.roleId,
      roleName: editForm.roleName.trim(),
      roleDesc: editForm.roleDesc.trim(),
      menuIdList: checkedKeys
    })
    ElMessage.success('修改角色成功')
    editDialogVisible.value = false
    resetEditForm()
    fetchRoleList()
  } catch (error) {
    console.error('修改角色失败', error)
    ElMessage.error('修改角色失败，请稍后重试')
  } finally {
    editSubmitting.value = false
  }
}

const handleDelete = async (row: RoleItem) => {
  deleteLoadingId.value = row.roleId
  try {
    await roleManageApi.deleteRole(row.roleId)
    ElMessage.success('删除角色成功')
    fetchRoleList()
  } catch (error) {
    console.error('删除角色失败', error)
    ElMessage.error('删除角色失败，请稍后重试')
  } finally {
    deleteLoadingId.value = null
  }
}

const handleViewMenus = async (row: RoleItem) => {
  await loadMenuTree()
  try {
    // 获取角色的完整信息（包含菜单列表）
    const res = await roleManageApi.getRoleById(row.roleId)
    const data = res.data || {}
    viewMenusRole.value = {
      roleId: data.roleId,
      roleName: data.roleName,
      roleDesc: data.roleDesc,
      menuIdList: Array.isArray(data.menuIdList) ? data.menuIdList : []
    }
    viewMenusDialogVisible.value = true
    nextTick(() => {
      viewMenuTreeRef.value?.setCheckedKeys(viewMenusRole.value?.menuIdList || [], true)
    })
  } catch (error) {
    console.error('获取角色菜单失败', error)
    ElMessage.error('获取角色菜单失败，请稍后重试')
  }
}

onMounted(() => {
  fetchRoleList()
})
</script>

<style scoped>
.role-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: var(--el-bg-color-page);
  min-height: 100%;
}

.search-card {
  flex: none;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-card {
  flex: 1;
  min-height: 0;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
}

.table-subtitle {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.action-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-link {
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  padding: 2px 4px;
  border-radius: 2px;
}

.action-link:hover:not(.is-disabled) {
  opacity: 0.8;
}

.action-link.is-disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.view-link {
  color: #409eff;
}

.view-link:hover:not(.is-disabled) {
  color: #66b1ff;
  background-color: rgba(64, 158, 255, 0.1);
}

.edit-link {
  color: #e6a23c;
}

.edit-link:hover:not(.is-disabled) {
  color: #ebb563;
  background-color: rgba(230, 162, 60, 0.1);
}

.delete-link {
  color: #f56c6c;
}

.delete-link:hover:not(.is-disabled) {
  color: #f78989;
  background-color: rgba(245, 108, 108, 0.1);
}

.delete-link.is-loading {
  color: #c0c4cc;
  cursor: not-allowed;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.menu-tree-wrapper {
  max-height: 260px;
  overflow: auto;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 8px;
}

.menu-tree-wrapper.view-only {
  max-height: 400px;
}

.role-info {
  margin-bottom: 20px;
}

.menu-tree-section {
  margin-top: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
}
</style>

